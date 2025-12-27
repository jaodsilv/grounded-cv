"""Tests for Profile model."""

import pytest
from pydantic import ValidationError

from app.models.profile import Address, Profile


class TestProfileValidation:
    """Tests for Profile field validation."""

    def test_valid_profile(self, sample_profile_data):
        """Test profile creates with valid data."""
        profile = Profile(**sample_profile_data)
        assert profile.name == "Jane Developer"
        assert profile.email == "jane@example.com"

    def test_missing_required_name(self, sample_profile_data):
        """Test name is required."""
        del sample_profile_data["name"]
        with pytest.raises(ValidationError, match="name"):
            Profile(**sample_profile_data)

    def test_missing_required_email(self, sample_profile_data):
        """Test email is required."""
        del sample_profile_data["email"]
        with pytest.raises(ValidationError, match="email"):
            Profile(**sample_profile_data)

    def test_invalid_email_format(self, sample_profile_data):
        """Test email format validation."""
        sample_profile_data["email"] = "not-an-email"
        with pytest.raises(ValidationError, match="email"):
            Profile(**sample_profile_data)

    def test_phone_validation(self, sample_profile_data):
        """Test phone number validation."""
        valid_phones = [
            "+1 (555) 123-4567",
            "555-123-4567",
            "+44 20 7123 4567",
        ]
        for phone in valid_phones:
            sample_profile_data["phone"] = phone
            profile = Profile(**sample_profile_data)
            assert profile.phone == phone

    def test_invalid_phone_rejected(self, sample_profile_data):
        """Test invalid phone numbers are rejected."""
        sample_profile_data["phone"] = "123"  # Too short
        with pytest.raises(ValidationError, match="phone"):
            Profile(**sample_profile_data)

    def test_linkedin_url_normalization(self, sample_profile_data):
        """Test LinkedIn URL is normalized."""
        sample_profile_data["linkedin"] = "janedeveloper"
        profile = Profile(**sample_profile_data)
        assert profile.linkedin == "https://linkedin.com/in/janedeveloper"

    def test_github_url_normalization(self, sample_profile_data):
        """Test GitHub URL is normalized."""
        sample_profile_data["github"] = "janedeveloper"
        profile = Profile(**sample_profile_data)
        assert profile.github == "https://github.com/janedeveloper"

    def test_optional_fields_default_none(self):
        """Test optional fields default to None."""
        profile = Profile(name="Test", email="test@example.com")
        assert profile.phone is None
        assert profile.location is None
        assert profile.linkedin is None
        assert profile.github is None
        assert profile.summary is None

    def test_target_roles_default_empty_list(self):
        """Test target_roles defaults to empty list."""
        profile = Profile(name="Test", email="test@example.com")
        assert profile.target_roles == []


class TestProfileSerialization:
    """Tests for Profile YAML serialization."""

    def test_yaml_roundtrip(self, sample_profile_data, temp_directory):
        """Test profile survives YAML round-trip."""
        profile = Profile(**sample_profile_data)

        # Write to YAML
        yaml_path = temp_directory / "profile.yaml"
        profile.to_yaml_file(yaml_path)

        # Read back
        loaded = Profile.from_yaml_file(yaml_path)

        assert loaded.name == profile.name
        assert loaded.email == profile.email
        assert loaded.target_roles == profile.target_roles

    def test_to_yaml_excludes_none_values(self, sample_profile_data):
        """Test that None values are excluded from YAML output."""
        profile = Profile(name="Test", email="test@example.com")
        yaml_output = profile.to_yaml()

        assert "phone:" not in yaml_output
        assert "linkedin:" not in yaml_output

    def test_source_tracking(self, sample_profile_data, temp_directory):
        """Test source file is tracked for anti-hallucination."""
        yaml_path = temp_directory / "profile.yaml"
        yaml_path.write_text(Profile(**sample_profile_data).to_yaml())

        loaded = Profile.from_yaml_file(yaml_path)

        assert loaded.get_source_file() == yaml_path


class TestAddress:
    """Tests for Address model."""

    def test_valid_address(self):
        """Test address creates with valid data."""
        address = Address(
            street="123 Main St",
            city="San Francisco",
            state="CA",
            zip="94102",
            country="USA",
        )
        assert address.city == "San Francisco"
        assert address.state == "CA"

    def test_address_required_fields(self):
        """Test city and state are required."""
        with pytest.raises(ValidationError, match="city"):
            Address(state="CA")

    def test_address_country_default(self):
        """Test country defaults to USA."""
        address = Address(city="Boston", state="MA")
        assert address.country == "USA"

    def test_zip_alias(self):
        """Test zip can be provided via zip_code alias."""
        address = Address(city="Boston", state="MA", zip_code="02101")
        assert address.zip == "02101"

"""Tests for base model error handling."""

import pytest
from pydantic import ValidationError

from app.models.profile import Profile


class TestYamlErrorHandling:
    """Tests for YAML loading error scenarios."""

    def test_empty_yaml_string_raises_valueerror(self):
        """Test empty YAML string raises clear ValueError."""
        with pytest.raises(ValueError, match="YAML content is empty"):
            Profile.from_yaml("")

    def test_whitespace_only_yaml_raises_valueerror(self):
        """Test whitespace-only YAML (spaces and newlines) raises clear ValueError."""
        with pytest.raises(ValueError, match="YAML content is empty"):
            Profile.from_yaml("   \n\n  ")

    def test_empty_yaml_error_includes_class_name(self):
        """Test error message includes the model class name."""
        with pytest.raises(ValueError, match="Profile"):
            Profile.from_yaml("")

    def test_empty_yaml_file_raises_valueerror(self, temp_directory):
        """Test empty YAML file raises clear ValueError."""
        empty_file = temp_directory / "empty.yaml"
        empty_file.write_text("")

        with pytest.raises(ValueError, match="YAML content is empty"):
            Profile.from_yaml_file(empty_file)

    def test_file_not_found_has_context(self, temp_directory):
        """Test FileNotFoundError includes file path."""
        missing_file = temp_directory / "does_not_exist.yaml"

        with pytest.raises(FileNotFoundError, match="does_not_exist.yaml"):
            Profile.from_yaml_file(missing_file)

        with pytest.raises(FileNotFoundError, match="Profile"):
            Profile.from_yaml_file(missing_file)


class TestWhitespaceValidation:
    """Tests for whitespace-only string validation."""

    def test_whitespace_name_rejected(self):
        """Test whitespace-only name is rejected."""
        with pytest.raises(ValidationError, match="name"):
            Profile(name="   ", email="test@example.com")

    def test_stripped_whitespace_is_valid(self):
        """Test strings with leading/trailing whitespace are stripped."""
        profile = Profile(name="  Jane  ", email="test@example.com")
        assert profile.name == "Jane"


class TestWriteErrorHandling:
    """Tests for write operation error scenarios."""

    def test_yaml_write_permission_error_includes_class_name(self, temp_directory):
        """Test PermissionError includes class name."""
        from pathlib import Path
        from unittest.mock import patch

        from app.models.profile import Profile

        profile = Profile(name="Test", email="test@example.com")
        yaml_path = temp_directory / "test.yaml"

        with patch.object(Path, "write_text", side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError, match="Profile"):
                profile.to_yaml_file(yaml_path)

    def test_yaml_write_permission_error_includes_path(self, temp_directory):
        """Test PermissionError includes file path."""
        from pathlib import Path
        from unittest.mock import patch

        from app.models.profile import Profile

        profile = Profile(name="Test", email="test@example.com")
        yaml_path = temp_directory / "test.yaml"

        with patch.object(Path, "write_text", side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError, match="test.yaml"):
                profile.to_yaml_file(yaml_path)

    def test_yaml_write_oserror_includes_context(self, temp_directory):
        """Test OSError includes class name and path."""
        from pathlib import Path
        from unittest.mock import patch

        from app.models.profile import Profile

        profile = Profile(name="Test", email="test@example.com")
        yaml_path = temp_directory / "test.yaml"

        error = OSError("Disk full")
        error.strerror = "No space left on device"
        with patch.object(Path, "write_text", side_effect=error):
            with pytest.raises(OSError, match="Profile"):
                profile.to_yaml_file(yaml_path)


class TestAddressValidation:
    """Tests for Address field validation."""

    def test_empty_city_rejected(self):
        """Test empty city string is rejected."""
        from app.models.profile import Address

        with pytest.raises(ValidationError, match="city"):
            Address(city="", state="CA")

    def test_whitespace_city_rejected(self):
        """Test whitespace-only city is rejected."""
        from app.models.profile import Address

        with pytest.raises(ValidationError, match="city"):
            Address(city="   ", state="CA")

    def test_empty_state_rejected(self):
        """Test empty state string is rejected."""
        from app.models.profile import Address

        with pytest.raises(ValidationError, match="state"):
            Address(city="Boston", state="")

    def test_whitespace_state_rejected(self):
        """Test whitespace-only state is rejected."""
        from app.models.profile import Address

        with pytest.raises(ValidationError, match="state"):
            Address(city="Boston", state="   ")

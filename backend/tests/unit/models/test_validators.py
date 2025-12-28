"""Tests for model validators."""

from datetime import date

import pytest
from pydantic_core import PydanticCustomError

from app.models.validators import (
    parse_date_flexible,
    validate_github_url,
    validate_linkedin_url,
    validate_phone,
)


class TestValidatePhone:
    """Tests for phone number validation."""

    def test_valid_us_phone_with_country_code(self):
        """Test US phone with +1 country code."""
        result = validate_phone("+1 (555) 123-4567")
        assert result == "+1 (555) 123-4567"

    def test_valid_us_phone_without_country_code(self):
        """Test US phone without country code."""
        result = validate_phone("555-123-4567")
        assert result == "555-123-4567"

    def test_valid_international_phone(self):
        """Test international phone format."""
        result = validate_phone("+44 20 7123 4567")
        assert result == "+44 20 7123 4567"

    def test_invalid_phone_too_short(self):
        """Test that short phone numbers are rejected."""
        with pytest.raises(PydanticCustomError, match="Invalid phone number"):
            validate_phone("123")

    def test_invalid_phone_contains_letters(self):
        """Test that phones with letters are rejected."""
        with pytest.raises(PydanticCustomError, match="Invalid phone number"):
            validate_phone("+1 (555) CALL-ME")


class TestValidateLinkedInUrl:
    """Tests for LinkedIn URL validation."""

    def test_full_https_url(self):
        """Test full HTTPS URL."""
        result = validate_linkedin_url("https://linkedin.com/in/janedeveloper")
        assert result == "https://linkedin.com/in/janedeveloper"

    def test_url_without_protocol(self):
        """Test URL without protocol is normalized."""
        result = validate_linkedin_url("linkedin.com/in/janedeveloper")
        assert result == "https://linkedin.com/in/janedeveloper"

    def test_www_url(self):
        """Test www URL is normalized."""
        result = validate_linkedin_url("www.linkedin.com/in/janedeveloper")
        assert result == "https://www.linkedin.com/in/janedeveloper"

    def test_username_only(self):
        """Test username only is normalized to full URL."""
        result = validate_linkedin_url("janedeveloper")
        assert result == "https://linkedin.com/in/janedeveloper"

    def test_invalid_linkedin_url(self):
        """Test invalid LinkedIn URL is rejected."""
        with pytest.raises(PydanticCustomError, match="Invalid LinkedIn URL"):
            validate_linkedin_url("https://twitter.com/janedeveloper")

    def test_username_with_period(self):
        """Test username with period is accepted."""
        result = validate_linkedin_url("https://linkedin.com/in/john.doe")
        assert result == "https://linkedin.com/in/john.doe"

    def test_linkedin_in_path_with_period(self):
        """Test linkedin.com/in/john.doe URL is accepted."""
        result = validate_linkedin_url("linkedin.com/in/john.doe")
        assert result == "https://linkedin.com/in/john.doe"


class TestValidateGitHubUrl:
    """Tests for GitHub URL validation."""

    def test_full_https_url(self):
        """Test full HTTPS URL."""
        result = validate_github_url("https://github.com/janedeveloper")
        assert result == "https://github.com/janedeveloper"

    def test_url_without_protocol(self):
        """Test URL without protocol is normalized."""
        result = validate_github_url("github.com/janedeveloper")
        assert result == "https://github.com/janedeveloper"

    def test_username_only(self):
        """Test username only is normalized to full URL."""
        result = validate_github_url("janedeveloper")
        assert result == "https://github.com/janedeveloper"

    def test_invalid_github_url(self):
        """Test invalid GitHub URL is rejected."""
        with pytest.raises(PydanticCustomError, match="Invalid GitHub URL"):
            validate_github_url("https://gitlab.com/janedeveloper")

    def test_username_with_period(self):
        """Test username with period is accepted."""
        result = validate_github_url("https://github.com/john.doe")
        assert result == "https://github.com/john.doe"

    def test_github_path_with_period(self):
        """Test github.com/john.doe URL is accepted."""
        result = validate_github_url("github.com/john.doe")
        assert result == "https://github.com/john.doe"


class TestParseDateFlexible:
    """Tests for flexible date parsing."""

    def test_iso_format(self):
        """Test ISO date format YYYY-MM-DD."""
        result = parse_date_flexible("2024-01-15")
        assert result == date(2024, 1, 15)

    def test_month_year_slash(self):
        """Test MM/YYYY format."""
        result = parse_date_flexible("01/2024")
        assert result == date(2024, 1, 1)

    def test_year_only(self):
        """Test YYYY format."""
        result = parse_date_flexible("2024")
        assert result == date(2024, 1, 1)

    def test_month_name_year(self):
        """Test 'Month YYYY' format."""
        result = parse_date_flexible("January 2024")
        assert result == date(2024, 1, 1)

    def test_month_name_case_insensitive(self):
        """Test month name is case insensitive."""
        result = parse_date_flexible("DECEMBER 2023")
        assert result == date(2023, 12, 1)

    def test_date_object_passthrough(self):
        """Test date object is passed through."""
        input_date = date(2024, 6, 15)
        result = parse_date_flexible(input_date)
        assert result == input_date

    def test_invalid_date_format(self):
        """Test invalid date format is rejected."""
        with pytest.raises(PydanticCustomError, match="Invalid date format"):
            parse_date_flexible("not-a-date")

    def test_invalid_month_name(self):
        """Test invalid month name is rejected."""
        with pytest.raises(PydanticCustomError, match="Invalid date format"):
            parse_date_flexible("Octember 2024")

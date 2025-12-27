"""Tests for Education model."""

from datetime import date

import pytest
from pydantic import ValidationError

from app.models.education import Certification, Degree, Education


class TestDegreeValidation:
    """Tests for Degree model validation."""

    def test_valid_degree(self, sample_degree_data):
        """Test degree creates with valid data."""
        degree = Degree(**sample_degree_data)
        assert degree.degree == "BS Computer Science"
        assert degree.institution == "State University"

    def test_missing_required_degree(self, sample_degree_data):
        """Test degree name is required."""
        del sample_degree_data["degree"]
        with pytest.raises(ValidationError, match="degree"):
            Degree(**sample_degree_data)

    def test_missing_required_institution(self, sample_degree_data):
        """Test institution is required."""
        del sample_degree_data["institution"]
        with pytest.raises(ValidationError, match="institution"):
            Degree(**sample_degree_data)

    def test_graduation_date_parsing(self):
        """Test graduation date is parsed correctly."""
        degree = Degree(
            degree="BS CS",
            institution="University",
            graduation_date="May 2020",
        )
        assert degree.graduation_date == date(2020, 5, 1)

    def test_gpa_bounds(self, sample_degree_data):
        """Test GPA must be between 0 and 4."""
        sample_degree_data["gpa"] = 4.0
        degree = Degree(**sample_degree_data)
        assert degree.gpa == 4.0

        sample_degree_data["gpa"] = 4.5
        with pytest.raises(ValidationError, match="gpa"):
            Degree(**sample_degree_data)

    def test_honors_default_empty_list(self):
        """Test honors defaults to empty list."""
        degree = Degree(degree="BS CS", institution="University")
        assert degree.honors == []


class TestCertificationValidation:
    """Tests for Certification model validation."""

    def test_valid_certification(self, sample_certification_data):
        """Test certification creates with valid data."""
        cert = Certification(**sample_certification_data)
        assert cert.name == "AWS Solutions Architect"
        assert cert.issuer == "Amazon Web Services"

    def test_missing_required_name(self, sample_certification_data):
        """Test name is required."""
        del sample_certification_data["name"]
        with pytest.raises(ValidationError, match="name"):
            Certification(**sample_certification_data)

    def test_missing_required_issuer(self, sample_certification_data):
        """Test issuer is required."""
        del sample_certification_data["issuer"]
        with pytest.raises(ValidationError, match="issuer"):
            Certification(**sample_certification_data)

    def test_is_expired_false_when_no_expiration(self, sample_certification_data):
        """Test is_expired returns False when no expiration date."""
        cert = Certification(**sample_certification_data)
        assert not cert.is_expired

    def test_is_expired_true_when_expired(self, sample_certification_data):
        """Test is_expired returns True for past expiration."""
        sample_certification_data["expiration_date"] = "2020-01-01"
        cert = Certification(**sample_certification_data)
        assert cert.is_expired

    def test_is_expired_false_when_future(self, sample_certification_data):
        """Test is_expired returns False for future expiration."""
        sample_certification_data["expiration_date"] = "2099-01-01"
        cert = Certification(**sample_certification_data)
        assert not cert.is_expired


class TestEducation:
    """Tests for Education collection model."""

    def test_empty_education(self):
        """Test empty education collection."""
        edu = Education()
        assert edu.degrees == []
        assert edu.certifications == []

    def test_get_highest_degree(self, sample_degree_data):
        """Test getting most recent degree."""
        older = Degree(
            degree="BS CS",
            institution="Old University",
            graduation_date="2015-05-01",
        )
        newer = Degree(
            degree="MS CS",
            institution="New University",
            graduation_date="2018-05-01",
        )
        edu = Education(degrees=[older, newer])
        highest = edu.get_highest_degree()
        assert highest is not None
        assert highest.degree == "MS CS"

    def test_get_highest_degree_empty(self):
        """Test get_highest_degree returns None when empty."""
        edu = Education()
        assert edu.get_highest_degree() is None

    def test_get_active_certifications(self, sample_certification_data):
        """Test filtering active certifications."""
        active = Certification(**sample_certification_data)
        expired = Certification(
            name="Old Cert",
            issuer="Some Org",
            expiration_date="2020-01-01",
        )
        edu = Education(certifications=[active, expired])
        active_certs = edu.get_active_certifications()
        assert len(active_certs) == 1
        assert active_certs[0].name == "AWS Solutions Architect"


class TestEducationSerialization:
    """Tests for Education YAML serialization."""

    def test_yaml_roundtrip(self, sample_degree_data, sample_certification_data, temp_directory):
        """Test education survives YAML round-trip."""
        edu = Education(
            degrees=[Degree(**sample_degree_data)],
            certifications=[Certification(**sample_certification_data)],
        )

        yaml_path = temp_directory / "education.yaml"
        edu.to_yaml_file(yaml_path)

        loaded = Education.from_yaml_file(yaml_path)

        assert len(loaded.degrees) == 1
        assert loaded.degrees[0].degree == "BS Computer Science"
        assert len(loaded.certifications) == 1
        assert loaded.certifications[0].name == "AWS Solutions Architect"

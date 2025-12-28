"""Tests for Experience model."""

from datetime import date

import pytest
from pydantic import ValidationError

from app.models.experience import Experience, ExperienceEntry


class TestExperienceEntryValidation:
    """Tests for ExperienceEntry field validation."""

    def test_valid_experience_entry(self, sample_experience_entry):
        """Test experience entry creates with valid data."""
        entry = ExperienceEntry(**sample_experience_entry)
        assert entry.title == "Senior Software Engineer"
        assert entry.company == "Tech Corp"

    def test_missing_required_title(self, sample_experience_entry):
        """Test title is required."""
        del sample_experience_entry["title"]
        with pytest.raises(ValidationError, match="title"):
            ExperienceEntry(**sample_experience_entry)

    def test_missing_required_company(self, sample_experience_entry):
        """Test company is required."""
        del sample_experience_entry["company"]
        with pytest.raises(ValidationError, match="company"):
            ExperienceEntry(**sample_experience_entry)

    def test_date_parsing_iso_format(self):
        """Test ISO date format is parsed correctly."""
        entry = ExperienceEntry(
            title="Engineer",
            company="Company",
            start_date="2020-01-15",
        )
        assert entry.start_date == date(2020, 1, 15)

    def test_date_parsing_month_year(self):
        """Test Month YYYY format is parsed correctly."""
        entry = ExperienceEntry(
            title="Engineer",
            company="Company",
            start_date="January 2020",
        )
        assert entry.start_date == date(2020, 1, 1)

    def test_date_parsing_present(self):
        """Test 'Present' is parsed as None for end_date."""
        entry = ExperienceEntry(
            title="Engineer",
            company="Company",
            start_date="2020-01-01",
            end_date="Present",
        )
        assert entry.end_date is None
        assert entry.is_current is True

    def test_is_current_auto_set_when_no_end_date(self):
        """Test is_current is set when end_date is None."""
        entry = ExperienceEntry(
            title="Engineer",
            company="Company",
            start_date="2020-01-01",
        )
        assert entry.is_current is True

    def test_end_date_before_start_date_rejected(self):
        """Test end_date before start_date is rejected."""
        with pytest.raises(ValidationError, match="end_date must be after start_date"):
            ExperienceEntry(
                title="Engineer",
                company="Company",
                start_date="2022-01-01",
                end_date="2020-01-01",
            )

    def test_duration_months_calculation(self):
        """Test duration is calculated correctly."""
        entry = ExperienceEntry(
            title="Engineer",
            company="Company",
            start_date="2020-01-01",
            end_date="2022-01-01",
        )
        assert entry.duration_months == 24

    def test_duration_months_current_position(self):
        """Test duration for current position uses today's date."""
        entry = ExperienceEntry(
            title="Engineer",
            company="Company",
            start_date="2020-01-01",
            is_current=True,
        )
        # Duration should be positive (from 2020 to today)
        assert entry.duration_months > 0

    def test_bullets_default_empty_list(self, sample_experience_entry):
        """Test bullets defaults to empty list."""
        del sample_experience_entry["bullets"]
        entry = ExperienceEntry(**sample_experience_entry)
        assert entry.bullets == []

    def test_relevance_score_bounds(self, sample_experience_entry):
        """Test relevance_score must be between 0 and 1."""
        sample_experience_entry["relevance_score"] = 0.5
        entry = ExperienceEntry(**sample_experience_entry)
        assert entry.relevance_score == 0.5

        sample_experience_entry["relevance_score"] = 1.5
        with pytest.raises(ValidationError, match="relevance_score"):
            ExperienceEntry(**sample_experience_entry)


class TestExperience:
    """Tests for Experience collection model."""

    def test_empty_experience(self):
        """Test empty experience collection."""
        exp = Experience()
        assert exp.entries == []

    def test_get_current_position(self, sample_experience_entry):
        """Test getting current position."""
        exp = Experience(entries=[ExperienceEntry(**sample_experience_entry)])
        current = exp.get_current_position()
        assert current is not None
        assert current.company == "Tech Corp"

    def test_get_current_position_none(self):
        """Test get_current_position returns None when no current job."""
        entry = ExperienceEntry(
            title="Engineer",
            company="Old Corp",
            start_date="2018-01-01",
            end_date="2020-01-01",
            is_current=False,
        )
        exp = Experience(entries=[entry])
        assert exp.get_current_position() is None

    def test_get_by_company(self, sample_experience_entry):
        """Test filtering by company name."""
        exp = Experience(entries=[ExperienceEntry(**sample_experience_entry)])
        results = exp.get_by_company("Tech")
        assert len(results) == 1
        assert results[0].company == "Tech Corp"

    def test_get_total_experience_years(self):
        """Test total experience calculation."""
        entries = [
            ExperienceEntry(
                title="Engineer",
                company="Company A",
                start_date="2018-01-01",
                end_date="2020-01-01",
            ),
            ExperienceEntry(
                title="Senior Engineer",
                company="Company B",
                start_date="2020-01-01",
                end_date="2022-01-01",
            ),
        ]
        exp = Experience(entries=entries)
        assert exp.get_total_experience_years() == 4.0


class TestExperienceSerialization:
    """Tests for Experience YAML serialization."""

    def test_yaml_roundtrip(self, sample_experience_entry, temp_directory):
        """Test experience survives YAML round-trip."""
        exp = Experience(entries=[ExperienceEntry(**sample_experience_entry)])

        yaml_path = temp_directory / "experience.yaml"
        exp.to_yaml_file(yaml_path)

        loaded = Experience.from_yaml_file(yaml_path)

        assert len(loaded.entries) == 1
        assert loaded.entries[0].company == "Tech Corp"
        assert loaded.entries[0].bullets == sample_experience_entry["bullets"]


class TestExperienceInvariantEnforcement:
    """Tests for date invariant enforcement after construction."""

    def test_end_date_before_start_date_rejected_on_assignment(self):
        """Test setting end_date before start_date raises error."""
        entry = ExperienceEntry(
            title="Engineer",
            company="Company",
            start_date="2022-01-01",
            end_date="2023-01-01",
        )

        # Attempting to set end_date before start_date should raise
        with pytest.raises(ValidationError, match="end_date must be after start_date"):
            entry.end_date = date(2020, 1, 1)

    def test_valid_end_date_assignment_accepted(self):
        """Test setting valid end_date is accepted."""
        entry = ExperienceEntry(
            title="Engineer",
            company="Company",
            start_date="2022-01-01",
            end_date="2023-01-01",
        )

        # Setting a valid end_date should work
        entry.end_date = date(2024, 1, 1)
        assert entry.end_date == date(2024, 1, 1)

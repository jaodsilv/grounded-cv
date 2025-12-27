"""Tests for Skills model."""

import pytest
from pydantic import ValidationError

from app.models.skills import Skill, Skills


class TestSkillValidation:
    """Tests for Skill model validation."""

    def test_valid_skill(self):
        """Test skill creates with valid data."""
        skill = Skill(
            name="Python",
            proficiency="expert",
            years_experience=10,
            aliases=["Python3", "Py"],
        )
        assert skill.name == "Python"
        assert skill.proficiency == "expert"

    def test_missing_required_name(self):
        """Test name is required."""
        with pytest.raises(ValidationError, match="name"):
            Skill(proficiency="expert")

    def test_invalid_proficiency(self):
        """Test invalid proficiency is rejected."""
        with pytest.raises(ValidationError, match="proficiency"):
            Skill(name="Python", proficiency="god-level")

    def test_valid_proficiency_levels(self):
        """Test all valid proficiency levels."""
        for level in ["beginner", "intermediate", "advanced", "expert"]:
            skill = Skill(name="Test", proficiency=level)
            assert skill.proficiency == level

    def test_years_experience_bounds(self):
        """Test years_experience must be non-negative."""
        with pytest.raises(ValidationError, match="years_experience"):
            Skill(name="Python", years_experience=-1)


class TestSkillsValidation:
    """Tests for Skills collection validation."""

    def test_valid_skills(self, sample_skills_data):
        """Test skills creates with valid data."""
        skills = Skills(**sample_skills_data)
        assert "Python" in skills.languages
        assert "FastAPI" in skills.frameworks

    def test_empty_skills(self):
        """Test empty skills collection."""
        skills = Skills()
        assert skills.languages == []
        assert skills.frameworks == []

    def test_mixed_string_and_skill_objects(self):
        """Test skills accept both strings and Skill objects."""
        skills = Skills(
            languages=[
                "Python",
                {"name": "TypeScript", "proficiency": "advanced"},
            ]
        )
        assert len(skills.languages) == 2
        assert skills.languages[0] == "Python"
        assert isinstance(skills.languages[1], Skill)
        assert skills.languages[1].name == "TypeScript"


class TestSkillsMethods:
    """Tests for Skills helper methods."""

    def test_get_all_technical_skills(self, sample_skills_data):
        """Test getting all technical skill names."""
        skills = Skills(**sample_skills_data)
        all_skills = skills.get_all_technical_skills()

        assert "Python" in all_skills
        assert "FastAPI" in all_skills
        assert "Docker" in all_skills
        assert "PostgreSQL" in all_skills
        assert "AWS" in all_skills
        # Soft skills should NOT be included
        assert "Leadership" not in all_skills

    def test_get_all_technical_skills_with_skill_objects(self):
        """Test get_all_technical_skills extracts names from Skill objects."""
        skills = Skills(
            languages=[
                "Python",
                Skill(name="TypeScript", proficiency="advanced"),
            ]
        )
        all_skills = skills.get_all_technical_skills()
        assert "Python" in all_skills
        assert "TypeScript" in all_skills

    def test_search_skill_by_name(self, sample_skills_data):
        """Test searching skills by name."""
        skills = Skills(**sample_skills_data)
        matches = skills.search_skill("python")
        assert len(matches) == 1
        assert "Python" in matches

    def test_search_skill_case_insensitive(self, sample_skills_data):
        """Test skill search is case insensitive."""
        skills = Skills(**sample_skills_data)
        matches = skills.search_skill("PYTHON")
        assert len(matches) == 1

    def test_search_skill_by_alias(self):
        """Test searching skills by alias."""
        skills = Skills(languages=[Skill(name="JavaScript", aliases=["JS", "ECMAScript"])])
        matches = skills.search_skill("JS")
        assert len(matches) == 1
        assert isinstance(matches[0], Skill)
        assert matches[0].name == "JavaScript"

    def test_search_skill_no_matches(self, sample_skills_data):
        """Test search returns empty when no matches."""
        skills = Skills(**sample_skills_data)
        matches = skills.search_skill("COBOL")
        assert len(matches) == 0


class TestSkillsSerialization:
    """Tests for Skills YAML serialization."""

    def test_yaml_roundtrip(self, sample_skills_data, temp_directory):
        """Test skills survives YAML round-trip."""
        skills = Skills(**sample_skills_data)

        yaml_path = temp_directory / "skills.yaml"
        skills.to_yaml_file(yaml_path)

        loaded = Skills.from_yaml_file(yaml_path)

        assert loaded.languages == sample_skills_data["languages"]
        assert loaded.frameworks == sample_skills_data["frameworks"]
        assert loaded.soft_skills == sample_skills_data["soft_skills"]

    def test_yaml_roundtrip_with_skill_objects(self, temp_directory):
        """Test Skill objects survive YAML round-trip."""
        skills = Skills(
            languages=[
                "Python",
                Skill(name="TypeScript", proficiency="advanced", years_experience=5),
            ]
        )

        yaml_path = temp_directory / "skills.yaml"
        skills.to_yaml_file(yaml_path)

        loaded = Skills.from_yaml_file(yaml_path)

        assert loaded.languages[0] == "Python"
        # When loaded from YAML, nested objects become Skill instances
        assert isinstance(loaded.languages[1], Skill)
        assert loaded.languages[1].name == "TypeScript"
        assert loaded.languages[1].proficiency == "advanced"

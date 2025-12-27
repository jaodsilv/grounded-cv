"""Tests for MasterResume composite model."""

import pytest
from pydantic import ValidationError

from app.models.achievement import Achievement, Achievements
from app.models.education import Degree, Education
from app.models.experience import Experience, ExperienceEntry
from app.models.master_resume import MasterResume
from app.models.profile import Profile
from app.models.skills import Skills


class TestMasterResumeValidation:
    """Tests for MasterResume model validation."""

    def test_valid_master_resume(self, sample_profile_data):
        """Test master resume creates with valid data."""
        profile = Profile(**sample_profile_data)
        resume = MasterResume(profile=profile)
        assert resume.profile.name == "Jane Developer"

    def test_missing_required_profile(self):
        """Test profile is required."""
        with pytest.raises(ValidationError, match="profile"):
            MasterResume()

    def test_optional_sections_default_empty(self, sample_profile_data):
        """Test optional sections default to empty."""
        profile = Profile(**sample_profile_data)
        resume = MasterResume(profile=profile)

        assert resume.experience.entries == []
        assert resume.education.degrees == []
        assert resume.education.certifications == []
        assert resume.skills.languages == []
        assert resume.achievements.entries == []


class TestMasterResumeDirectoryOperations:
    """Tests for MasterResume directory load/save operations."""

    def test_from_directory_profile_only(self, sample_profile_data, temp_directory):
        """Test loading with only profile.yaml."""
        # Create profile.yaml
        profile_path = temp_directory / "profile.yaml"
        Profile(**sample_profile_data).to_yaml_file(profile_path)

        resume = MasterResume.from_directory(temp_directory)

        assert resume.profile.name == "Jane Developer"
        assert resume.experience.entries == []

    def test_from_directory_missing_profile_raises(self, temp_directory):
        """Test loading without profile.yaml raises error."""
        with pytest.raises(FileNotFoundError, match="profile.yaml"):
            MasterResume.from_directory(temp_directory)

    def test_from_directory_all_files(
        self,
        sample_profile_data,
        sample_experience_entry,
        sample_degree_data,
        sample_skills_data,
        sample_achievement_data,
        temp_directory,
    ):
        """Test loading with all files present."""
        # Create all files
        Profile(**sample_profile_data).to_yaml_file(temp_directory / "profile.yaml")

        Experience(entries=[ExperienceEntry(**sample_experience_entry)]).to_yaml_file(
            temp_directory / "experience.yaml"
        )

        Education(degrees=[Degree(**sample_degree_data)]).to_yaml_file(temp_directory / "education.yaml")

        Skills(**sample_skills_data).to_yaml_file(temp_directory / "skills.yaml")

        Achievements(entries=[Achievement(**sample_achievement_data)]).to_markdown_file(
            temp_directory / "achievements.md"
        )

        resume = MasterResume.from_directory(temp_directory)

        assert resume.profile.name == "Jane Developer"
        assert len(resume.experience.entries) == 1
        assert len(resume.education.degrees) == 1
        assert "Python" in resume.skills.languages
        assert len(resume.achievements.entries) == 1

    def test_to_directory(
        self,
        sample_profile_data,
        sample_experience_entry,
        sample_skills_data,
        temp_directory,
    ):
        """Test saving to directory structure."""
        resume = MasterResume(
            profile=Profile(**sample_profile_data),
            experience=Experience(entries=[ExperienceEntry(**sample_experience_entry)]),
            skills=Skills(**sample_skills_data),
        )

        output_dir = temp_directory / "output"
        resume.to_directory(output_dir)

        assert (output_dir / "profile.yaml").exists()
        assert (output_dir / "experience.yaml").exists()
        assert (output_dir / "skills.yaml").exists()
        # No education or achievements, so those files shouldn't exist
        assert not (output_dir / "education.yaml").exists()
        assert not (output_dir / "achievements.md").exists()

    def test_directory_roundtrip(
        self,
        sample_profile_data,
        sample_experience_entry,
        sample_degree_data,
        sample_skills_data,
        sample_achievement_data,
        temp_directory,
    ):
        """Test master resume survives directory round-trip."""
        original = MasterResume(
            profile=Profile(**sample_profile_data),
            experience=Experience(entries=[ExperienceEntry(**sample_experience_entry)]),
            education=Education(degrees=[Degree(**sample_degree_data)]),
            skills=Skills(**sample_skills_data),
            achievements=Achievements(entries=[Achievement(**sample_achievement_data)]),
        )

        output_dir = temp_directory / "roundtrip"
        original.to_directory(output_dir)

        loaded = MasterResume.from_directory(output_dir)

        assert loaded.profile.name == original.profile.name
        assert len(loaded.experience.entries) == len(original.experience.entries)
        assert len(loaded.education.degrees) == len(original.education.degrees)
        assert loaded.skills.languages == original.skills.languages
        assert len(loaded.achievements.entries) == len(original.achievements.entries)


class TestMasterResumeMethods:
    """Tests for MasterResume helper methods."""

    def test_get_all_keywords(
        self,
        sample_profile_data,
        sample_experience_entry,
        sample_skills_data,
        sample_achievement_data,
    ):
        """Test extracting all keywords for ATS matching."""
        resume = MasterResume(
            profile=Profile(**sample_profile_data),
            experience=Experience(entries=[ExperienceEntry(**sample_experience_entry)]),
            skills=Skills(**sample_skills_data),
            achievements=Achievements(entries=[Achievement(**sample_achievement_data)]),
        )

        keywords = resume.get_all_keywords()

        # From skills
        assert "Python" in keywords
        assert "FastAPI" in keywords
        assert "Leadership" in keywords  # soft skill

        # From experience keywords
        assert "Kubernetes" in keywords
        assert "CI/CD" in keywords

        # From achievement keywords
        assert "Architecture" in keywords

    def test_validate_completeness_complete_profile(
        self,
        sample_profile_data,
        sample_experience_entry,
        sample_skills_data,
    ):
        """Test completeness validation with complete data."""
        resume = MasterResume(
            profile=Profile(**sample_profile_data),
            experience=Experience(entries=[ExperienceEntry(**sample_experience_entry)]),
            skills=Skills(**sample_skills_data),
        )

        issues = resume.validate_completeness()

        # Should have no issues
        assert "profile" not in issues
        assert "experience" not in issues
        assert "skills" not in issues

    def test_validate_completeness_missing_phone(self, sample_profile_data):
        """Test completeness flags missing phone."""
        sample_profile_data["phone"] = None
        resume = MasterResume(
            profile=Profile(**sample_profile_data),
            skills=Skills(languages=["Python"]),
        )

        issues = resume.validate_completeness()

        assert "profile" in issues
        assert "Missing phone number" in issues["profile"]

    def test_validate_completeness_missing_linkedin(self):
        """Test completeness flags missing LinkedIn."""
        resume = MasterResume(
            profile=Profile(name="Test", email="test@example.com", phone="+1 555 123 4567"),
            skills=Skills(languages=["Python"]),
        )

        issues = resume.validate_completeness()

        assert "profile" in issues
        assert "Missing LinkedIn profile" in issues["profile"]

    def test_validate_completeness_no_experience(self, sample_profile_data):
        """Test completeness flags no experience."""
        resume = MasterResume(
            profile=Profile(**sample_profile_data),
            skills=Skills(languages=["Python"]),
        )

        issues = resume.validate_completeness()

        assert "experience" in issues
        assert "No work experience entries" in issues["experience"]

    def test_validate_completeness_no_bullets(self, sample_profile_data, sample_experience_entry):
        """Test completeness flags experience without bullets."""
        sample_experience_entry["bullets"] = []
        resume = MasterResume(
            profile=Profile(**sample_profile_data),
            experience=Experience(entries=[ExperienceEntry(**sample_experience_entry)]),
            skills=Skills(languages=["Python"]),
        )

        issues = resume.validate_completeness()

        assert "experience" in issues
        assert "has no achievement bullets" in issues["experience"][0]

    def test_validate_completeness_no_skills(self, sample_profile_data):
        """Test completeness flags no technical skills."""
        resume = MasterResume(
            profile=Profile(**sample_profile_data),
        )

        issues = resume.validate_completeness()

        assert "skills" in issues
        assert "No technical skills listed" in issues["skills"]

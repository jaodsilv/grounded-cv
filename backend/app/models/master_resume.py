"""Master Resume composite model."""

from pathlib import Path
from typing import ClassVar

from pydantic import Field

from app.models.achievement import Achievements
from app.models.base import GroundedModel
from app.models.education import Education
from app.models.experience import Experience
from app.models.profile import Profile
from app.models.skills import Skills


class MasterResume(GroundedModel):
    """Complete Master Resume aggregating all components.

    Directory structure:
    master-resume/
    ├── profile.yaml
    ├── experience.yaml
    ├── education.yaml
    ├── skills.yaml
    └── achievements.md
    """

    yaml_filename: ClassVar[str] = "master_resume"  # Directory name

    profile: Profile
    experience: Experience = Field(default_factory=Experience)
    education: Education = Field(default_factory=Education)
    skills: Skills = Field(default_factory=Skills)
    achievements: Achievements = Field(default_factory=Achievements)

    @classmethod
    def from_directory(cls, directory: Path) -> "MasterResume":
        """Load Master Resume from directory structure.

        Args:
            directory: Path to master-resume directory

        Returns:
            MasterResume with all components loaded

        Raises:
            FileNotFoundError: If required files are missing
            ValidationError: If file contents are invalid
        """
        # Profile is required
        profile_path = directory / "profile.yaml"
        if not profile_path.exists():
            raise FileNotFoundError(f"Required file not found: {profile_path}")
        profile = Profile.from_yaml_file(profile_path)

        # Other components are optional
        experience = Experience()
        experience_path = directory / "experience.yaml"
        if experience_path.exists():
            experience = Experience.from_yaml_file(experience_path)

        education = Education()
        education_path = directory / "education.yaml"
        if education_path.exists():
            education = Education.from_yaml_file(education_path)

        skills = Skills()
        skills_path = directory / "skills.yaml"
        if skills_path.exists():
            skills = Skills.from_yaml_file(skills_path)

        achievements = Achievements()
        achievements_path = directory / "achievements.md"
        if achievements_path.exists():
            achievements = Achievements.from_markdown_file(achievements_path)

        return cls(
            profile=profile,
            experience=experience,
            education=education,
            skills=skills,
            achievements=achievements,
        )

    def to_directory(self, directory: Path) -> None:
        """Save Master Resume to directory structure.

        Args:
            directory: Target directory (will be created if not exists)
        """
        directory.mkdir(parents=True, exist_ok=True)

        self.profile.to_yaml_file(directory / "profile.yaml")

        if self.experience.entries:
            self.experience.to_yaml_file(directory / "experience.yaml")

        if self.education.degrees or self.education.certifications:
            self.education.to_yaml_file(directory / "education.yaml")

        if any(
            [
                self.skills.languages,
                self.skills.frameworks,
                self.skills.tools,
                self.skills.soft_skills,
            ]
        ):
            self.skills.to_yaml_file(directory / "skills.yaml")

        if self.achievements.entries:
            self.achievements.to_markdown_file(directory / "achievements.md")

    def get_all_keywords(self) -> set[str]:
        """Extract all keywords for ATS matching."""
        keywords: set[str] = set()

        # From skills
        keywords.update(self.skills.get_all_technical_skills())
        keywords.update(self.skills.soft_skills)

        # From experience
        for exp in self.experience.entries:
            keywords.update(exp.keywords)

        # From achievements
        for achievement in self.achievements.entries:
            keywords.update(achievement.keywords)

        return keywords

    def validate_completeness(self) -> dict[str, list[str]]:
        """Check for missing or incomplete data.

        Returns:
            Dict of section -> list of issues
        """
        issues: dict[str, list[str]] = {}

        # Profile checks
        profile_issues = []
        if not self.profile.phone:
            profile_issues.append("Missing phone number")
        if not self.profile.linkedin:
            profile_issues.append("Missing LinkedIn profile")
        if not self.profile.summary:
            profile_issues.append("Missing professional summary")
        if profile_issues:
            issues["profile"] = profile_issues

        # Experience checks
        exp_issues = []
        if not self.experience.entries:
            exp_issues.append("No work experience entries")
        else:
            for i, exp in enumerate(self.experience.entries):
                if not exp.bullets:
                    exp_issues.append(f"Entry {i + 1} ({exp.company}) has no achievement bullets")
        if exp_issues:
            issues["experience"] = exp_issues

        # Skills checks
        skills_issues = []
        if not self.skills.languages and not self.skills.frameworks:
            skills_issues.append("No technical skills listed")
        if skills_issues:
            issues["skills"] = skills_issues

        return issues

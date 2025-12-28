"""Skills model for technical and soft skills inventory."""

from typing import Annotated, Any, ClassVar, Literal

from pydantic import BeforeValidator, Field

from app.models.base import GroundedModel


class Skill(GroundedModel):
    """Individual skill with proficiency level."""

    name: str = Field(..., min_length=1)
    proficiency: Literal["beginner", "intermediate", "advanced", "expert"] | None = None
    years_experience: float | None = Field(default=None, ge=0)
    last_used: int | None = Field(default=None, description="Year last used")

    # For keyword matching
    aliases: list[str] = Field(default_factory=list, description="Alternative names (e.g., 'JS' for 'JavaScript')")


def _normalize_skill(v: Any) -> str | Skill:
    """Normalize skill input to either string or Skill object."""
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        return Skill.model_validate(v)
    if isinstance(v, Skill):
        return v
    raise ValueError(f"Invalid skill type: {type(v)}")


SkillEntry = Annotated[str | Skill, BeforeValidator(_normalize_skill)]
"""Type for skill list entries.

Accepts either:
- A simple string: "Python" -> stored as-is
- A dict with skill details: {"name": "Python", "proficiency": "expert"} -> Skill object
- A Skill object directly

This allows flexible input while maintaining type safety. Simple skills can be
listed as strings for brevity, while detailed skills use the full Skill model.
"""


class Skills(GroundedModel):
    """Categorized skills inventory.

    Maps to: master-resume/skills.yaml
    """

    yaml_filename: ClassVar[str] = "skills.yaml"

    # Technical skills
    languages: list[SkillEntry] = Field(default_factory=list, description="Programming languages")
    frameworks: list[SkillEntry] = Field(default_factory=list, description="Frameworks and libraries")
    tools: list[SkillEntry] = Field(default_factory=list, description="Development tools and platforms")
    databases: list[SkillEntry] = Field(default_factory=list, description="Database technologies")
    cloud: list[SkillEntry] = Field(default_factory=list, description="Cloud platforms and services")

    # Soft skills
    soft_skills: list[str] = Field(default_factory=list, description="Interpersonal and professional skills")

    # Domain expertise
    domains: list[str] = Field(default_factory=list, description="Industry domains (e.g., 'FinTech', 'Healthcare')")

    # Methodologies
    methodologies: list[str] = Field(
        default_factory=list,
        description="Development methodologies (e.g., 'Agile', 'Scrum')",
    )

    def get_all_technical_skills(self) -> list[str]:
        """Get flat list of all technical skill names."""
        skills = []
        for category in [
            self.languages,
            self.frameworks,
            self.tools,
            self.databases,
            self.cloud,
        ]:
            for skill in category:
                if isinstance(skill, str):
                    skills.append(skill)
                else:
                    skills.append(skill.name)
        return skills

    def search_skill(self, query: str) -> list[str | Skill]:
        """Find skills matching a query (including aliases)."""
        query_lower = query.lower()
        matches: list[str | Skill] = []

        for category in [
            self.languages,
            self.frameworks,
            self.tools,
            self.databases,
            self.cloud,
        ]:
            for skill in category:
                if isinstance(skill, str):
                    if query_lower in skill.lower():
                        matches.append(skill)
                else:
                    if query_lower in skill.name.lower() or any(
                        query_lower in alias.lower() for alias in skill.aliases
                    ):
                        matches.append(skill)

        return matches

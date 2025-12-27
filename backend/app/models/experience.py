"""Experience model for work history."""

from datetime import date
from typing import ClassVar

from pydantic import Field, field_validator, model_validator

from app.models.base import GroundedModel
from app.models.validators import parse_date_flexible


class ExperienceEntry(GroundedModel):
    """Single work experience entry."""

    # Required fields
    title: str = Field(..., min_length=1, description="Job title")
    company: str = Field(..., min_length=1, description="Company name")

    # Dates
    start_date: date = Field(..., description="Start date (YYYY-MM-DD or 'Month YYYY')")
    end_date: date | None = Field(default=None, description="End date or None for current position")
    is_current: bool = Field(default=False, description="Currently employed here")

    # Location
    location: str | None = None
    remote: bool = False

    # Description
    bullets: list[str] = Field(default_factory=list, description="Achievement bullets (STAR format preferred)")

    # Metadata for tailoring
    keywords: list[str] = Field(default_factory=list, description="Keywords for ATS matching")
    relevance_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Relevance score for current application (set by tailoring)",
    )

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def parse_date(cls, v: str | date | None) -> date | None:
        if v is None:
            return None
        if isinstance(v, str) and v.lower() in ("present", "current"):
            return None
        return parse_date_flexible(v)

    @model_validator(mode="after")
    def validate_dates(self) -> "ExperienceEntry":
        """Ensure end_date is after start_date or is_current is set."""
        if self.end_date is None and not self.is_current:
            self.is_current = True
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self

    @property
    def duration_months(self) -> int:
        """Calculate duration in months."""
        end = self.end_date or date.today()
        return (end.year - self.start_date.year) * 12 + (end.month - self.start_date.month)


class Experience(GroundedModel):
    """Collection of work experience entries.

    Maps to: master-resume/experience.yaml
    """

    yaml_filename: ClassVar[str] = "experience.yaml"

    entries: list[ExperienceEntry] = Field(default_factory=list, description="Work history entries (most recent first)")

    def get_current_position(self) -> ExperienceEntry | None:
        """Get current position if any."""
        for entry in self.entries:
            if entry.is_current:
                return entry
        return None

    def get_by_company(self, company: str) -> list[ExperienceEntry]:
        """Get all positions at a company."""
        return [e for e in self.entries if company.lower() in e.company.lower()]

    def get_total_experience_years(self) -> float:
        """Calculate total years of experience."""
        total_months = sum(e.duration_months for e in self.entries)
        return round(total_months / 12, 1)

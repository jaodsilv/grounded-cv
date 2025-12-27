"""Education model for degrees and certifications."""

from datetime import date
from typing import ClassVar

from pydantic import Field, field_validator

from app.models.base import GroundedModel
from app.models.validators import parse_date_flexible


class Degree(GroundedModel):
    """Academic degree entry."""

    degree: str = Field(..., min_length=1, description="Degree name (e.g., 'BS Computer Science')")
    institution: str = Field(..., min_length=1, description="University/College name")
    location: str | None = None
    graduation_date: date | None = None
    gpa: float | None = Field(default=None, ge=0.0, le=4.0)
    honors: list[str] = Field(default_factory=list)
    relevant_coursework: list[str] = Field(default_factory=list)

    @field_validator("graduation_date", mode="before")
    @classmethod
    def parse_graduation_date(cls, v: str | date | None) -> date | None:
        if v is None:
            return None
        return parse_date_flexible(v)


class Certification(GroundedModel):
    """Professional certification entry."""

    name: str = Field(..., min_length=1, description="Certification name")
    issuer: str = Field(..., min_length=1, description="Issuing organization")
    date_obtained: date | None = None
    expiration_date: date | None = None
    credential_id: str | None = None
    url: str | None = Field(default=None, description="Verification URL")

    @field_validator("date_obtained", "expiration_date", mode="before")
    @classmethod
    def parse_dates(cls, v: str | date | None) -> date | None:
        if v is None:
            return None
        return parse_date_flexible(v)

    @property
    def is_expired(self) -> bool:
        """Check if certification is expired."""
        if self.expiration_date is None:
            return False
        return self.expiration_date < date.today()


class Education(GroundedModel):
    """Collection of education and certifications.

    Maps to: master-resume/education.yaml
    """

    yaml_filename: ClassVar[str] = "education.yaml"

    degrees: list[Degree] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)

    def get_highest_degree(self) -> Degree | None:
        """Get the highest/most recent degree."""
        if not self.degrees:
            return None
        # Sort by graduation date, most recent first
        sorted_degrees = sorted(
            self.degrees,
            key=lambda d: d.graduation_date or date.min,
            reverse=True,
        )
        return sorted_degrees[0]

    def get_active_certifications(self) -> list[Certification]:
        """Get non-expired certifications."""
        return [c for c in self.certifications if not c.is_expired]

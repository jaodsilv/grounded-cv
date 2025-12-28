"""Profile model for personal information."""

from typing import ClassVar

from pydantic import Field, field_validator

from app.models.base import GroundedModel
from app.models.validators import (
    validate_github_url,
    validate_linkedin_url,
    validate_phone,
)


class Address(GroundedModel):
    """Physical address for cover letters."""

    street: str | None = None
    city: str = Field(..., min_length=1, description="City name")
    state: str = Field(..., min_length=1, description="State/province")
    zip: str | None = Field(default=None, alias="zip_code")
    country: str = "USA"


class Profile(GroundedModel):
    """Personal profile information.

    Maps to: master-resume/profile.yaml
    """

    yaml_filename: ClassVar[str] = "profile.yaml"

    # Required fields
    name: str = Field(..., min_length=1, description="Full legal name")
    email: str = Field(..., pattern=r"^[\w\.\-\+]+@[\w\-]+\.[\w\-\.]+$")

    # Optional contact info
    phone: str | None = None
    location: str | None = Field(default=None, description="City, State format for resume header")

    # Online profiles
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None

    # Extended info (for cover letters)
    address: Address | None = None

    # Professional summary
    summary: str | None = Field(default=None, description="Base professional summary (will be tailored)")

    # Targeting
    target_roles: list[str] = Field(default_factory=list)
    target_industries: list[str] = Field(default_factory=list)

    @field_validator("phone")
    @classmethod
    def validate_phone_format(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return validate_phone(v)

    @field_validator("linkedin")
    @classmethod
    def validate_linkedin_format(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return validate_linkedin_url(v)

    @field_validator("github")
    @classmethod
    def validate_github_format(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return validate_github_url(v)

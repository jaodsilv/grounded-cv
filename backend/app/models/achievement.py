"""Achievement model with STAR format support."""

import logging
import re
from pathlib import Path
from typing import ClassVar, Self

from pydantic import Field, PrivateAttr, model_validator

from app.models.base import GroundedModel

logger = logging.getLogger(__name__)


class Achievement(GroundedModel):
    """Single achievement in STAR format.

    STAR = Situation, Task, Action, Result
    """

    # STAR components
    situation: str = Field(..., min_length=1, description="Context and challenge")
    task: str = Field(..., min_length=1, description="Your responsibility")
    action: str = Field(..., min_length=1, description="Steps you took")
    result: str = Field(..., min_length=1, description="Measurable outcome")

    # Metadata
    title: str | None = Field(default=None, description="Short title for reference")
    keywords: list[str] = Field(default_factory=list, description="Skills demonstrated")
    metrics: list[str] = Field(default_factory=list, description="Quantified results (e.g., '50% improvement')")

    # Source tracking
    related_experience: str | None = Field(default=None, description="Company/role this achievement is from")

    @model_validator(mode="after")
    def extract_metrics(self) -> Self:
        """Auto-extract metrics from result if not provided."""
        if not self.metrics:
            # Find percentage patterns
            percentages = re.findall(r"\d+(?:\.\d+)?%", self.result)
            # Find dollar amounts
            dollars = re.findall(r"\$[\d,]+(?:\.\d{2})?[KMB]?", self.result)
            # Find multipliers
            multipliers = re.findall(r"\d+[xX]", self.result)

            self.metrics = percentages + dollars + multipliers
        return self

    def to_bullet(self, max_length: int = 150) -> str:
        """Convert to resume bullet format.

        Args:
            max_length: Maximum character length for the bullet

        Returns:
            Condensed bullet point emphasizing action and result
        """
        bullet = f"{self.action} {self.result}"
        if len(bullet) > max_length:
            bullet = bullet[: max_length - 3] + "..."
        return bullet

    def to_markdown_section(self) -> str:
        """Convert to detailed Markdown format."""
        lines = []
        if self.title:
            lines.append(f"### {self.title}")
        lines.append(f"**Situation:** {self.situation}")
        lines.append(f"**Task:** {self.task}")
        lines.append(f"**Action:** {self.action}")
        lines.append(f"**Result:** {self.result}")
        if self.keywords:
            lines.append(f"**Keywords:** {', '.join(self.keywords)}")
        return "\n".join(lines)


class Achievements(GroundedModel):
    """Collection of STAR-formatted achievements.

    Maps to: master-resume/achievements.md
    """

    yaml_filename: ClassVar[str] = "achievements.md"

    entries: list[Achievement] = Field(default_factory=list)

    # Source tracking (not serialized)
    _source_file: Path | None = PrivateAttr(default=None)

    def to_markdown(self) -> str:
        """Export all achievements to Markdown format."""
        sections = ["# Achievements\n"]
        for i, achievement in enumerate(self.entries, 1):
            if not achievement.title:
                achievement.title = f"Achievement {i}"
            sections.append(achievement.to_markdown_section())
            sections.append("")  # Blank line between entries
        return "\n".join(sections)

    @classmethod
    def from_markdown(cls, content: str, source_file: Path | None = None) -> Self:
        """Parse achievements from Markdown format.

        Expected format:
        ### Achievement Title
        **Situation:** ...
        **Task:** ...
        **Action:** ...
        **Result:** ...
        **Keywords:** keyword1, keyword2

        Args:
            content: Markdown content
            source_file: Optional source file for tracking

        Returns:
            Achievements instance
        """
        achievements = []

        # Split by achievement headers
        sections = re.split(r"^###\s+", content, flags=re.MULTILINE)

        for section in sections[1:]:  # Skip content before first ###
            lines = section.strip().split("\n")
            if not lines:
                continue

            title = lines[0].strip()
            achievement_data: dict[str, str | list[str]] = {"title": title}

            # Parse STAR components
            text = "\n".join(lines[1:])

            for field in ["situation", "task", "action", "result"]:
                pattern = rf"\*\*{field.capitalize()}:\*\*\s*(.+?)(?=\*\*|\Z)"
                if match := re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                    achievement_data[field] = match.group(1).strip()

            # Parse keywords if present
            if keywords_match := re.search(r"\*\*Keywords:\*\*\s*(.+?)(?=\n|$)", text, re.IGNORECASE):
                keywords = [k.strip() for k in keywords_match.group(1).split(",")]
                achievement_data["keywords"] = keywords

            # Validate we have all required STAR fields
            required_fields = ["situation", "task", "action", "result"]
            missing_fields = [f for f in required_fields if f not in achievement_data]

            if missing_fields:
                logger.warning(
                    "Skipping achievement section '%s': missing STAR component(s): %s",
                    title,
                    ", ".join(missing_fields),
                )
            else:
                achievements.append(Achievement.model_validate(achievement_data))

        instance = cls(entries=achievements)
        instance._source_file = source_file
        return instance

    @classmethod
    def from_markdown_file(cls, file_path: Path) -> Self:
        """Load achievements from Markdown file."""
        content = file_path.read_text(encoding="utf-8")
        return cls.from_markdown(content, source_file=file_path)

    def to_markdown_file(self, file_path: Path) -> None:
        """Save achievements to Markdown file."""
        file_path.write_text(self.to_markdown(), encoding="utf-8")

    def get_by_keyword(self, keyword: str) -> list[Achievement]:
        """Find achievements with a specific keyword."""
        keyword_lower = keyword.lower()
        return [a for a in self.entries if any(keyword_lower in k.lower() for k in a.keywords)]

"""Tests for Achievement model."""

import pytest
from pydantic import ValidationError

from app.models.achievement import Achievement, Achievements


class TestAchievementValidation:
    """Tests for Achievement model validation."""

    def test_valid_achievement(self, sample_achievement_data):
        """Test achievement creates with valid data."""
        achievement = Achievement(**sample_achievement_data)
        assert achievement.title == "Platform Migration Success"
        assert achievement.situation == sample_achievement_data["situation"]

    def test_missing_required_situation(self, sample_achievement_data):
        """Test situation is required."""
        del sample_achievement_data["situation"]
        with pytest.raises(ValidationError, match="situation"):
            Achievement(**sample_achievement_data)

    def test_missing_required_task(self, sample_achievement_data):
        """Test task is required."""
        del sample_achievement_data["task"]
        with pytest.raises(ValidationError, match="task"):
            Achievement(**sample_achievement_data)

    def test_missing_required_action(self, sample_achievement_data):
        """Test action is required."""
        del sample_achievement_data["action"]
        with pytest.raises(ValidationError, match="action"):
            Achievement(**sample_achievement_data)

    def test_missing_required_result(self, sample_achievement_data):
        """Test result is required."""
        del sample_achievement_data["result"]
        with pytest.raises(ValidationError, match="result"):
            Achievement(**sample_achievement_data)

    def test_auto_extract_percentage_metrics(self):
        """Test metrics are auto-extracted from result."""
        achievement = Achievement(
            situation="Issue",
            task="Fix",
            action="Fixed",
            result="Improved performance by 50% and reduced latency by 30%",
        )
        assert "50%" in achievement.metrics
        assert "30%" in achievement.metrics

    def test_auto_extract_dollar_metrics(self):
        """Test dollar amounts are auto-extracted from result."""
        achievement = Achievement(
            situation="Issue",
            task="Fix",
            action="Fixed",
            result="Saved $50K monthly and reduced costs by $100,000",
        )
        assert "$50K" in achievement.metrics
        assert "$100,000" in achievement.metrics

    def test_auto_extract_multiplier_metrics(self):
        """Test multipliers are auto-extracted from result."""
        achievement = Achievement(
            situation="Issue",
            task="Fix",
            action="Fixed",
            result="Achieved 5x improvement in throughput",
        )
        assert "5x" in achievement.metrics

    def test_preserve_provided_metrics(self):
        """Test provided metrics are not overwritten."""
        achievement = Achievement(
            situation="Issue",
            task="Fix",
            action="Fixed",
            result="Improved by 50%",
            metrics=["custom metric"],
        )
        assert achievement.metrics == ["custom metric"]


class TestAchievementMethods:
    """Tests for Achievement helper methods."""

    def test_to_bullet(self, sample_achievement_data):
        """Test converting to resume bullet format."""
        achievement = Achievement(**sample_achievement_data)
        bullet = achievement.to_bullet()

        assert "Designed event-driven architecture" in bullet
        assert "Reduced customer complaints" in bullet

    def test_to_bullet_truncation(self):
        """Test bullet is truncated to max length."""
        achievement = Achievement(
            situation="S",
            task="T",
            action="A very long action description that goes on and on",
            result="A very long result description that also goes on and on",
        )
        bullet = achievement.to_bullet(max_length=50)
        assert len(bullet) == 50
        assert bullet.endswith("...")

    def test_to_markdown_section(self, sample_achievement_data):
        """Test converting to Markdown section."""
        achievement = Achievement(**sample_achievement_data)
        md = achievement.to_markdown_section()

        assert "### Platform Migration Success" in md
        assert "**Situation:**" in md
        assert "**Task:**" in md
        assert "**Action:**" in md
        assert "**Result:**" in md
        assert "**Keywords:**" in md


class TestAchievements:
    """Tests for Achievements collection model."""

    def test_empty_achievements(self):
        """Test empty achievements collection."""
        achievements = Achievements()
        assert achievements.entries == []

    def test_to_markdown(self, sample_achievement_data):
        """Test exporting to Markdown format."""
        achievements = Achievements(entries=[Achievement(**sample_achievement_data)])
        md = achievements.to_markdown()

        assert "# Achievements" in md
        assert "### Platform Migration Success" in md

    def test_from_markdown(self, sample_achievements_markdown):
        """Test parsing from Markdown format."""
        achievements = Achievements.from_markdown(sample_achievements_markdown)

        assert len(achievements.entries) == 2
        assert achievements.entries[0].title == "Platform Migration Success"
        assert achievements.entries[1].title == "Cost Optimization"
        assert "Architecture" in achievements.entries[0].keywords

    def test_markdown_roundtrip(self, sample_achievement_data, temp_directory):
        """Test achievements survive Markdown round-trip."""
        original = Achievements(entries=[Achievement(**sample_achievement_data)])

        md_path = temp_directory / "achievements.md"
        original.to_markdown_file(md_path)

        loaded = Achievements.from_markdown_file(md_path)

        assert len(loaded.entries) == 1
        assert loaded.entries[0].title == sample_achievement_data["title"]
        assert loaded.entries[0].situation == sample_achievement_data["situation"]

    def test_get_by_keyword(self, sample_achievements_markdown):
        """Test filtering achievements by keyword."""
        achievements = Achievements.from_markdown(sample_achievements_markdown)

        arch_results = achievements.get_by_keyword("Architecture")
        assert len(arch_results) == 1
        assert arch_results[0].title == "Platform Migration Success"

        aws_results = achievements.get_by_keyword("AWS")
        assert len(aws_results) == 1
        assert aws_results[0].title == "Cost Optimization"

    def test_get_by_keyword_case_insensitive(self, sample_achievements_markdown):
        """Test keyword search is case insensitive."""
        achievements = Achievements.from_markdown(sample_achievements_markdown)
        results = achievements.get_by_keyword("leadership")
        assert len(results) == 1

    def test_source_tracking(self, sample_achievements_markdown, temp_directory):
        """Test source file is tracked."""
        md_path = temp_directory / "achievements.md"
        md_path.write_text(sample_achievements_markdown)

        loaded = Achievements.from_markdown_file(md_path)
        # Note: Achievements uses _source_file directly since it has different serialization
        assert loaded._source_file == md_path

    def test_from_markdown_skips_incomplete_entries(self, caplog):
        """Test incomplete STAR entries are skipped with warning."""
        import logging

        incomplete_md = """# Achievements

### Incomplete Entry
**Situation:** Only situation provided
**Task:** Only task provided
"""
        with caplog.at_level(logging.WARNING):
            achievements = Achievements.from_markdown(incomplete_md)

        # Entry should be skipped
        assert len(achievements.entries) == 0

        # Warning should be logged
        assert "Skipping achievement section" in caplog.text
        assert "Incomplete Entry" in caplog.text
        assert "action" in caplog.text.lower()
        assert "result" in caplog.text.lower()

    def test_from_markdown_mixed_complete_incomplete(self, caplog):
        """Test parsing with mix of complete and incomplete entries."""
        import logging

        mixed_md = """# Achievements

### Complete Entry
**Situation:** Context here
**Task:** Responsibility here
**Action:** Steps taken
**Result:** Outcome achieved

### Missing Result
**Situation:** Context
**Task:** Task
**Action:** Action
"""
        with caplog.at_level(logging.WARNING):
            achievements = Achievements.from_markdown(mixed_md)

        # Only complete entry should be parsed
        assert len(achievements.entries) == 1
        assert achievements.entries[0].title == "Complete Entry"

        # Warning about incomplete entry
        assert "Missing Result" in caplog.text

"""Fixtures for model tests."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest


@pytest.fixture
def sample_profile_data() -> dict:
    """Valid profile data."""
    return {
        "name": "Jane Developer",
        "email": "jane@example.com",
        "phone": "+1 (555) 123-4567",
        "location": "San Francisco, CA",
        "linkedin": "linkedin.com/in/janedeveloper",
        "github": "github.com/janedeveloper",
        "summary": "Senior software engineer with 10 years experience.",
        "target_roles": ["Staff Engineer", "Tech Lead"],
    }


@pytest.fixture
def sample_experience_entry() -> dict:
    """Valid experience entry data."""
    return {
        "title": "Senior Software Engineer",
        "company": "Tech Corp",
        "start_date": "2020-01-15",
        "end_date": None,
        "is_current": True,
        "location": "San Francisco, CA",
        "bullets": [
            "Led team of 5 engineers to deliver microservices platform",
            "Reduced deployment time by 60% through CI/CD automation",
        ],
        "keywords": ["Python", "Kubernetes", "CI/CD"],
    }


@pytest.fixture
def sample_degree_data() -> dict:
    """Valid degree data."""
    return {
        "degree": "BS Computer Science",
        "institution": "State University",
        "location": "Boston, MA",
        "graduation_date": "2015-05-15",
        "gpa": 3.8,
        "honors": ["Magna Cum Laude"],
    }


@pytest.fixture
def sample_certification_data() -> dict:
    """Valid certification data."""
    return {
        "name": "AWS Solutions Architect",
        "issuer": "Amazon Web Services",
        "date_obtained": "2022-06-01",
        "credential_id": "ABC123",
    }


@pytest.fixture
def sample_skills_data() -> dict:
    """Valid skills data."""
    return {
        "languages": ["Python", "TypeScript", "Go"],
        "frameworks": ["FastAPI", "React", "Django"],
        "tools": ["Docker", "Kubernetes", "Git"],
        "databases": ["PostgreSQL", "Redis"],
        "cloud": ["AWS", "GCP"],
        "soft_skills": ["Leadership", "Communication"],
        "methodologies": ["Agile", "Scrum"],
    }


@pytest.fixture
def sample_achievement_data() -> dict:
    """Valid STAR achievement data."""
    return {
        "title": "Platform Migration Success",
        "situation": "Legacy monolith was causing 30% of customer complaints",
        "task": "Lead migration to microservices architecture",
        "action": "Designed event-driven architecture and led phased migration",
        "result": "Reduced customer complaints by 80% and improved uptime to 99.9%",
        "keywords": ["Architecture", "Leadership", "Migration"],
    }


@pytest.fixture
def temp_directory():
    """Temporary directory for file tests."""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_achievements_markdown() -> str:
    """Sample achievements in Markdown format."""
    return """# Achievements

### Platform Migration Success
**Situation:** Legacy monolith was causing 30% of customer complaints
**Task:** Lead migration to microservices architecture
**Action:** Designed event-driven architecture and led phased migration
**Result:** Reduced customer complaints by 80% and improved uptime to 99.9%
**Keywords:** Architecture, Leadership, Migration

### Cost Optimization
**Situation:** Cloud spending was 40% over budget
**Task:** Reduce cloud costs without impacting performance
**Action:** Implemented auto-scaling and reserved instances
**Result:** Reduced cloud costs by $50K monthly, a 35% savings
**Keywords:** Cost Optimization, AWS, Infrastructure
"""

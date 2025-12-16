"""Configuration management for GroundedCV."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Note: Claude Agent SDK uses Claude CLI configuration for authentication.
    # No API key configuration is needed here. Set up via `claude login` or
    # environment variables for Bedrock/Vertex.

    # Application
    app_name: str = "GroundedCV"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Models
    model_fast: str = "claude-3-5-haiku-20241022"
    model_balanced: str = "claude-sonnet-4-5-20250929"
    model_reasoning: str = "claude-opus-4-5-20251101"

    # Agent Configuration
    max_tokens: int = 4096
    max_iterations: int = 10
    quality_threshold: float = 0.8
    agent_pool_size: int = 5
    ab_variant_count: int = 3

    # Cache Configuration
    market_research_cache_days: int = 180  # 6 months
    company_research_cache_days: int = 180  # 6 months
    ai_company_cache_days: int = 90  # 3 months

    # Paths
    data_dir: Path = Path("../data")
    templates_dir: Path = Path("../data/templates")

    @property
    def master_resume_dir(self) -> Path:
        return self.data_dir / "master-resume"

    @property
    def market_research_dir(self) -> Path:
        return self.data_dir / "market-research"

    @property
    def company_research_dir(self) -> Path:
        return self.data_dir / "company-research"

    @property
    def base_resumes_dir(self) -> Path:
        return self.data_dir / "base-resumes"

    @property
    def tailored_dir(self) -> Path:
        return self.data_dir / "tailored"

    def get_model(self, complexity: Literal["fast", "balanced", "reasoning"]) -> str:
        """Get the appropriate model for task complexity."""
        model_map = {
            "fast": self.model_fast,
            "balanced": self.model_balanced,
            "reasoning": self.model_reasoning,
        }
        return model_map[complexity]


# Global settings instance
settings = Settings()

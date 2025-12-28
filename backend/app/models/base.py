"""Base model with YAML/Markdown serialization for GroundedCV models."""

from pathlib import Path
from typing import ClassVar, TypeVar

import yaml
from pydantic import BaseModel, ConfigDict, PrivateAttr

T = TypeVar("T", bound="GroundedModel")


class GroundedModel(BaseModel):
    """Base model with YAML serialization and source tracking.

    All Master Resume models inherit from this to support:
    - YAML serialization/deserialization
    - Source file tracking for anti-hallucination
    - Consistent configuration across models
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_default=True,
        extra="forbid",  # Strict - reject unknown fields
        populate_by_name=True,  # Allow alias usage
    )

    # Source tracking for anti-hallucination (not serialized to YAML)
    _source_file: Path | None = PrivateAttr(default=None)

    # Class variable for YAML file name mapping
    yaml_filename: ClassVar[str] = ""

    def to_yaml(self) -> str:
        """Export model to YAML string.

        Returns:
            YAML-formatted string representation
        """
        return yaml.dump(
            self.model_dump(mode="json", exclude_none=True),
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

    @classmethod
    def from_yaml(cls: type[T], yaml_content: str, source_file: Path | None = None) -> T:
        """Import model from YAML string.

        Args:
            yaml_content: YAML string to parse
            source_file: Optional source file path for tracking

        Returns:
            Validated model instance

        Raises:
            ValueError: If YAML content is empty
            ValidationError: If content doesn't match model schema
        """
        data = yaml.safe_load(yaml_content)
        if data is None:
            source_context = f" from '{source_file}'" if source_file else ""
            raise ValueError(f"Cannot load {cls.__name__}{source_context}: YAML content is empty")
        instance = cls.model_validate(data)
        instance._source_file = source_file
        return instance

    @classmethod
    def from_yaml_file(cls: type[T], file_path: Path) -> T:
        """Load model from YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            Validated model instance with source tracking

        Raises:
            FileNotFoundError: If file does not exist
            PermissionError: If file cannot be read
            UnicodeDecodeError: If file encoding is invalid
            ValueError: If file is empty
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Cannot load {cls.__name__}: file not found at '{file_path}'") from e
        except PermissionError as e:
            raise PermissionError(f"Cannot load {cls.__name__}: permission denied reading '{file_path}'") from e
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                e.encoding, e.object, e.start, e.end, f"Cannot load {cls.__name__}: invalid encoding in '{file_path}'"
            ) from e
        return cls.from_yaml(content, source_file=file_path)

    def to_yaml_file(self, file_path: Path) -> None:
        """Save model to YAML file.

        Args:
            file_path: Destination path for YAML file

        Raises:
            PermissionError: If file cannot be written
            OSError: If write fails (disk full, etc.)
        """
        try:
            file_path.write_text(self.to_yaml(), encoding="utf-8")
        except PermissionError as e:
            raise PermissionError(
                f"Cannot save {self.__class__.__name__}: permission denied writing '{file_path}'"
            ) from e
        except OSError as e:
            raise OSError(f"Cannot save {self.__class__.__name__} to '{file_path}': {e.strerror}") from e

    def get_source_file(self) -> Path | None:
        """Get the source file path for anti-hallucination tracking."""
        return self._source_file

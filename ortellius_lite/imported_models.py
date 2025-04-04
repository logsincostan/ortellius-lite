"""Models defined in other projects that are not yet importable via pip."""

from collections.abc import Set as AbstractSet

from pydantic import BaseModel, field_serializer, field_validator

from .typing import is_list, is_set


class AnalysisResult(BaseModel):
    """Serializable result of an analysis."""

    read: set[int]
    write: set[int]

    @field_serializer("read", "write")
    def serialize_read(self, value: list[int]) -> list[str]:
        """Serialize hexadecimally."""
        return [f"{addr:08x}" for addr in sorted(value)]

    @field_validator("read", "write", mode="before")
    @classmethod
    def validate_from_hex(cls, value: object) -> AbstractSet[int]:
        """Unserialize from hex."""
        if is_set(value, int):
            return value

        if is_list(value, str):
            return {int(v, 16) for v in value}

        msg = "Unexpected type."
        raise ValueError(msg)

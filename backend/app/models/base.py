"""Shared model mixin."""

from typing import Any


class DictMixin:
    """Adds ``to_dict`` that returns every mapped column."""

    def to_dict(self) -> dict[str, Any]:
        """Return the row as a plain dictionary."""
        columns = self.__table__.columns  # type: ignore[attr-defined]
        return {c.key: getattr(self, c.key) for c in columns}

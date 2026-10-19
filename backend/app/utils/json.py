"""JSON provider that serialises Decimal, datetime and timedelta values."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from flask.json.provider import DefaultJSONProvider


class AppJSONProvider(DefaultJSONProvider):
    """Flask JSON provider with ISO timestamps and float decimals."""

    def default(self, o: Any) -> Any:
        """Convert unsupported types to JSON-friendly values."""
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, timedelta):
            return o.total_seconds()
        return super().default(o)

"""Authorization decorators."""

from collections.abc import Callable, Iterable
from functools import wraps
from typing import Any

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def role_required(roles: Iterable[str]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Require a valid JWT whose ``role`` claim is in ``roles``."""
    allowed = set(roles)

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            verify_jwt_in_request()
            if get_jwt().get("role") not in allowed:
                return jsonify(error="insufficient role"), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator

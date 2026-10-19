"""Authentication endpoints."""

from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ..models import User
from ..schemas import LoginSchema, RegisterSchema

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _claims(user: User) -> dict[str, Any]:
    """Return the extra JWT claims for ``user``."""
    return {"role": user.role, "username": user.username}


@bp.post("/register")
def register() -> Any:
    """Create a clinician or nurse account."""
    data = RegisterSchema().load(request.get_json(silent=True) or {})
    taken = db.session.scalar(
        db.select(User).where((User.email == data["email"]) | (User.username == data["username"]))
    )
    if taken:
        return jsonify(error="username or email already exists"), 409
    user = User(
        username=data["username"],
        email=data["email"],
        full_name=data["full_name"],
        role=data["role"],
        password_hash=generate_password_hash(data["password"]),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@bp.post("/login")
def login() -> Any:
    """Exchange credentials for access and refresh tokens."""
    data = LoginSchema().load(request.get_json(silent=True) or {})
    user = db.session.scalar(db.select(User).filter_by(email=data["email"]))
    if not user or not user.is_active:
        return jsonify(error="invalid credentials"), 401
    if not check_password_hash(user.password_hash, data["password"]):
        return jsonify(error="invalid credentials"), 401
    return jsonify(
        access_token=create_access_token(identity=str(user.id), additional_claims=_claims(user)),
        refresh_token=create_refresh_token(identity=str(user.id), additional_claims=_claims(user)),
        user=user.to_dict(),
    )


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh() -> Any:
    """Issue a new access token from a refresh token."""
    user = db.session.get(User, int(get_jwt_identity()))
    if not user or not user.is_active:
        return jsonify(error="user inactive"), 401
    token = create_access_token(identity=str(user.id), additional_claims=_claims(user))
    return jsonify(access_token=token)


@bp.get("/me")
@jwt_required()
def me() -> Any:
    """Return the current user."""
    user = db.get_or_404(User, int(get_jwt_identity()))
    return jsonify(user.to_dict())

"""Authentication endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from marshmallow import ValidationError

from app.extensions import db
from app.models.user import User
from app.schemas.auth import RegisterSchema, LoginSchema

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    """Register a new user."""
    schema = RegisterSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    if User.query.filter(
        (User.email == data["email"]) | (User.username == data["username"])
    ).first():
        return jsonify({"message": "User with email or username already exists"}), 409

    user = User(
        username=data["username"],
        email=data["email"],
        full_name=data.get("full_name"),
        role=data.get("role", "clinician"),
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201


@auth_bp.post("/login")
def login():
    """Authenticate user and return JWT tokens."""
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if user is None or not user.check_password(data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(
        identity=str(user.id), additional_claims={"role": user.role}
    )
    refresh_token = create_refresh_token(identity=str(user.id))
    return (
        jsonify(
            access_token=access_token,
            refresh_token=refresh_token,
            user={"id": user.id, "role": user.role, "full_name": user.full_name},
        ),
        200,
    )


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using a valid refresh token."""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    """Return current authenticated user profile."""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"message": "User not found"}), 404
    return (
        jsonify(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
        ),
        200,
    )

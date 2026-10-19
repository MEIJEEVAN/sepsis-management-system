"""Flask application factory for the Sepsis Management System."""

from flask import Flask, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import DataError, IntegrityError

from .config import Config
from .extensions import cors, db, jwt, migrate
from .utils.json import AppJSONProvider


def create_app(config_class: type[Config] = Config) -> Flask:
    """Build and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json = AppJSONProvider(app)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    from .resources import register_blueprints

    register_blueprints(app)

    @app.errorhandler(ValidationError)
    def _validation(err: ValidationError):  # type: ignore[no-untyped-def]
        return jsonify(error="validation failed", details=err.messages), 422

    @app.errorhandler(IntegrityError)
    @app.errorhandler(DataError)
    def _database(err: Exception):  # type: ignore[no-untyped-def]
        db.session.rollback()
        detail = str(getattr(err, "orig", err)).splitlines()[0]
        return jsonify(error="database rejected the data", detail=detail), 400

    return app

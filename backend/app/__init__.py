"""Flask application factory."""

from flask import Flask

from app.config import Config
from app.extensions import db, migrate, jwt, cors


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

    # Register blueprints
    from app.resources.auth import auth_bp
    from app.resources.patients import patients_bp
    from app.resources.vitals import vitals_bp
    from app.resources.labs import labs_bp
    from app.resources.sepsis import sepsis_bp
    from app.resources.alerts import alerts_bp
    from app.resources.protocols import protocols_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(vitals_bp)
    app.register_blueprint(labs_bp)
    app.register_blueprint(sepsis_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(protocols_bp)

    return app

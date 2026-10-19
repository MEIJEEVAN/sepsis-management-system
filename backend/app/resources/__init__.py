"""API blueprints."""

from flask import Flask


def register_blueprints(app: Flask) -> None:
    """Register every API blueprint on ``app``."""
    from . import alerts, auth, labs, patients, protocols, sepsis, stream, vitals

    for module in (alerts, auth, labs, patients, protocols, sepsis, stream, vitals):
        app.register_blueprint(module.bp)

"""Create or reset the seeded admin user with a properly hashed password."""

import os

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User


def main() -> None:
    """Insert the admin user if missing, otherwise reset its password."""
    email = os.getenv("ADMIN_EMAIL", "admin@sepsis.local")
    password = os.getenv("ADMIN_PASSWORD", "admin12345")
    app = create_app()
    with app.app_context():
        user = db.session.scalar(db.select(User).filter_by(email=email))
        if user is None:
            user = User(username="admin", email=email, full_name="System Admin", role="admin")
            db.session.add(user)
        user.password_hash = generate_password_hash(password)
        db.session.commit()
        print(f"Admin ready: {email}")


if __name__ == "__main__":
    main()

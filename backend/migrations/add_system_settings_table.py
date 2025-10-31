"""Create system_settings table and seed default security settings."""

import os
import sys

from sqlalchemy import inspect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import SystemSetting, db

DEFAULT_TIMEOUT_MINUTES = 30
SETTING_KEY = "session_inactivity_timeout_minutes"


def migrate():
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        if "system_settings" not in tables:
            print("Creating system_settings table...")
            SystemSetting.__table__.create(db.engine)
            print("system_settings table created.")
        else:
            print("system_settings table already exists.")

        setting = SystemSetting.query.filter_by(key=SETTING_KEY).first()
        if not setting:
            print(
                f"Seeding default inactivity timeout setting ({DEFAULT_TIMEOUT_MINUTES} minutes)..."
            )
            setting = SystemSetting(
                key=SETTING_KEY,
                value=str(DEFAULT_TIMEOUT_MINUTES),
                category="security",
                description="Session inactivity timeout in minutes",
                is_sensitive=False,
            )
            db.session.add(setting)
            db.session.commit()
            print("Default inactivity timeout setting created.")
        else:
            print("Inactivity timeout setting already present. Ensuring metadata is populated...")
            updated = False

            if not setting.category:
                setting.category = "security"
                updated = True

            if not setting.description:
                setting.description = "Session inactivity timeout in minutes"
                updated = True

            if setting.value is None:
                setting.value = str(DEFAULT_TIMEOUT_MINUTES)
                updated = True

            if updated:
                db.session.commit()
                print("Updated existing inactivity timeout metadata.")
            else:
                print("No changes required for existing inactivity timeout setting.")

    print("Migration complete.")


if __name__ == "__main__":
    migrate()

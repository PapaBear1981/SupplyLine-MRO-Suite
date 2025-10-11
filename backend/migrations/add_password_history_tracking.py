"""Migration script to add password history tracking infrastructure."""

import logging
import os
import sys
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, MetaData, String, Table, inspect
from sqlalchemy.exc import SQLAlchemyError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_users_columns(inspector):
    """Ensure password tracking columns exist on the users table."""
    from models import db

    columns = {column['name'] for column in inspector.get_columns('users')}
    dialect = db.engine.dialect.name

    if 'force_password_change' not in columns:
        logger.info("Adding force_password_change column to users table")
        default_value = '0' if dialect == 'sqlite' else 'FALSE'
        with db.engine.connect() as conn:
            conn.execute(db.text(
                f"ALTER TABLE users ADD COLUMN force_password_change BOOLEAN DEFAULT {default_value}"
            ))
            conn.commit()

    if 'password_changed_at' not in columns:
        logger.info("Adding password_changed_at column to users table")
        column_type = 'DATETIME' if dialect == 'sqlite' else 'TIMESTAMP'
        with db.engine.connect() as conn:
            conn.execute(db.text(
                f"ALTER TABLE users ADD COLUMN password_changed_at {column_type}"
            ))
            conn.execute(db.text(
                "UPDATE users SET password_changed_at = CURRENT_TIMESTAMP WHERE password_changed_at IS NULL"
            ))
            conn.commit()


def ensure_password_history_table(inspector):
    """Create password_history table if it does not exist."""
    from models import db

    if 'password_history' in inspector.get_table_names():
        return

    logger.info("Creating password_history table")
    metadata = MetaData()
    metadata.bind = db.engine

    password_history_table = Table(
        'password_history',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        Column('password_hash', String, nullable=False),
        Column('created_at', DateTime, nullable=False, default=datetime.utcnow),
    )

    password_history_table.create(checkfirst=True)


def backfill_password_history():
    """Backfill password history entries for existing users."""
    from models import PasswordHistory, User, db

    users = User.query.all()
    inserted = 0
    for user in users:
        has_history = PasswordHistory.query.filter_by(user_id=user.id).first() is not None
        if has_history:
            continue

        password_changed_at = user.password_changed_at or user.created_at or datetime.utcnow()
        history = PasswordHistory(
            user_id=user.id,
            password_hash=user.password_hash,
            created_at=password_changed_at,
        )
        db.session.add(history)
        inserted += 1

    if inserted:
        logger.info("Inserted %s password history records", inserted)
        db.session.commit()
    else:
        logger.info("No password history records required for backfill")


def run_migration():
    """Run the password history migration."""
    from models import db

    inspector = inspect(db.engine)
    ensure_users_columns(inspector)
    ensure_password_history_table(inspector)
    backfill_password_history()


def main():
    try:
        # Import here to avoid circular dependencies
        from app import create_app
        from models import PasswordHistory, User, db

        app = create_app()

        with app.app_context():
            logger.info("Running password history migration")
            run_migration()
            logger.info("Password history migration completed successfully")
            return True

    except SQLAlchemyError as exc:
        logger.error("Database error during migration: %s", exc)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Unexpected error during migration: %s", exc)

    return False


if __name__ == '__main__':
    sys.exit(0 if main() else 1)

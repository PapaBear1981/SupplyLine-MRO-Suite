from app import create_app
from models import db
from sqlalchemy import text

def check_db():
    app = create_app()
    with app.app_context():
        try:
            # Check what tables exist
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
                tables = [row[0] for row in result]
                print(f"Tables in database: {tables}")

                # Check if specific tables exist
                for table in ['users', 'tools', 'checkouts', 'audit_logs', 'sessions']:
                    if table in tables:
                        print(f"✓ Table '{table}' exists")
                        # Count records
                        try:
                            count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                            count = count_result.scalar()
                            print(f"  - {count} records in {table}")
                        except Exception as e:
                            print(f"  - Error counting records in {table}: {e}")
                    else:
                        print(f"✗ Table '{table}' does not exist")

        except Exception as e:
            print(f"Database check failed: {e}")

if __name__ == "__main__":
    check_db()

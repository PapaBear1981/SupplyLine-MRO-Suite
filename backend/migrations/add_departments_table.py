"""
Migration to add departments table and seed with existing departments
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Department, User
from datetime import datetime


def migrate():
    """Create departments table and seed with existing departments from users"""
    app = create_app()
    
    with app.app_context():
        print("Creating departments table...")
        
        # Create the departments table
        db.create_all()
        
        # Get unique departments from existing users
        existing_departments = db.session.query(User.department).distinct().filter(
            User.department.isnot(None),
            User.department != ''
        ).all()
        
        print(f"Found {len(existing_departments)} unique departments in users table")
        
        # Create department records for each unique department
        created_count = 0
        for (dept_name,) in existing_departments:
            # Check if department already exists
            existing = Department.query.filter_by(name=dept_name).first()
            if not existing:
                department = Department(
                    name=dept_name,
                    description=f"{dept_name} Department",
                    is_active=True
                )
                db.session.add(department)
                created_count += 1
                print(f"  Created department: {dept_name}")
            else:
                print(f"  Department already exists: {dept_name}")
        
        # Add some common departments if they don't exist
        common_departments = [
            ('Maintenance', 'Maintenance and repair operations'),
            ('Materials', 'Materials management and inventory'),
            ('Engineering', 'Engineering and technical services'),
            ('Quality', 'Quality assurance and control'),
            ('Production', 'Production and manufacturing'),
            ('IT', 'Information technology and systems'),
            ('Safety', 'Safety and compliance'),
            ('Planning', 'Planning and scheduling'),
            ('Purchasing', 'Purchasing and procurement'),
            ('Logistics', 'Logistics and supply chain')
        ]
        
        for dept_name, dept_desc in common_departments:
            existing = Department.query.filter_by(name=dept_name).first()
            if not existing:
                department = Department(
                    name=dept_name,
                    description=dept_desc,
                    is_active=True
                )
                db.session.add(department)
                created_count += 1
                print(f"  Created common department: {dept_name}")
        
        db.session.commit()
        
        print(f"\nMigration complete!")
        print(f"  Total departments created: {created_count}")
        print(f"  Total departments in database: {Department.query.count()}")


if __name__ == '__main__':
    migrate()


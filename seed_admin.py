"""Seed an admin user for development.

Creates an admin account with full access.
Run after seed_roles.py:

    python seed_roles.py
    python seed_admin.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password


def seed_admin():
    """Create or update the default admin user."""
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing = db.query(User).filter(
            User.email == "admin@hygig.com"
        ).first()

        if existing:
            print(f"  ↻ Admin user already exists (id={existing.id})")
            # Ensure they have admin role
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            if admin_role and existing.role_id != admin_role.id:
                existing.role_id = admin_role.id
                db.commit()
                print(f"  ✓ Assigned admin role to existing user")
            return

        # Find admin role
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            print("❌ Admin role not found. Run seed_roles.py first.")
            return

        # Create admin user
        admin = User(
            username="admin",
            email="admin@hygig.com",
            password_hash=hash_password("password"),
            is_active=True,
            role_id=admin_role.id,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"  ✓ Admin user created (id={admin.id})")
        print(f"    Email:    admin@hygig.com")
        print(f"    Password: password")
        print(f"    Role:     admin")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding admin user...")
    seed_admin()
    print("\n✅ Done!")

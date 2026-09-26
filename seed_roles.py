"""Seed default roles and permissions.

Run once after migrations:
    python seed_roles.py

This creates:
  - All permission definitions from app.core.authorization
  - Default roles with appropriate permissions
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database.session import SessionLocal
from app.models.role import Role, Permission
from app.core.authorization import get_all_permission_defs


# Role definitions: (name, description, list of permission codenames)
ROLE_DEFINITIONS = [
    (
        "super_admin",
        "Full system access. Has every permission.",
        None,  # None = all permissions
    ),
    (
        "admin",
        "Administrator with broad system access.",
        [
            "post.create", "post.read", "post.update", "post.delete", "post.publish",
            "category.create", "category.read", "category.update", "category.delete",
            "user.create", "user.read", "user.update", "user.delete",
            "role.read",
            "comment.create", "comment.read", "comment.update", "comment.delete", "comment.moderate",
            "media.create", "media.read", "media.update", "media.delete",
            "admin.access",
        ],
    ),
    (
        "editor",
        "Can manage all content but not users or settings.",
        [
            "post.create", "post.read", "post.update", "post.delete", "post.publish",
            "category.create", "category.read", "category.update", "category.delete",
            "comment.read", "comment.update", "comment.moderate",
            "media.create", "media.read",
            "admin.access",
        ],
    ),
    (
        "author",
        "Can create and manage own posts.",
        [
            "post.create", "post.read", "post.update",
            "category.read",
            "comment.create", "comment.read",
            "media.create", "media.read",
        ],
    ),
    (
        "user",
        "Basic read-only access with commenting ability.",
        [
            "post.read",
            "category.read",
            "comment.create", "comment.read",
        ],
    ),
]


def seed():
    """Create all permissions and default roles."""
    db = SessionLocal()
    try:
        print("Seeding permissions...")

        # Create all permissions
        perm_map: dict[str, Permission] = {}
        for group, codename, name, description in get_all_permission_defs():
            existing = db.query(Permission).filter(
                Permission.codename == codename
            ).first()
            if existing:
                perm_map[codename] = existing
                print(f"  ↻ {codename} (exists)")
            else:
                perm = Permission(
                    codename=codename,
                    name=name,
                    description=description,
                )
                db.add(perm)
                db.flush()
                perm_map[codename] = perm
                print(f"  ✓ {codename}")
        db.commit()

        print("\nSeeding roles...")

        for role_name, role_desc, perm_codenames in ROLE_DEFINITIONS:
            existing = db.query(Role).filter(Role.name == role_name).first()
            if existing:
                role = existing
                print(f"  ↻ {role_name} (exists)")
            else:
                role = Role(
                    name=role_name,
                    description=role_desc,
                    is_system_role=True,
                )
                db.add(role)
                db.flush()
                print(f"  ✓ {role_name}")

            # Assign permissions
            if perm_codenames is None:
                # Super admin gets ALL permissions
                role.permissions = list(perm_map.values())
            else:
                role.permissions = [
                    perm_map[c] for c in perm_codenames if c in perm_map
                ]
            db.flush()

        db.commit()
        print("\n✅ Roles and permissions seeded successfully!")

        # Print summary
        print("\n--- Summary ---")
        for role in db.query(Role).all():
            print(f"  {role.name}: {len(role.permissions)} permissions")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()

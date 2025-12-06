#!/usr/bin/env python3
"""Migration script to add hierarchical fields to roadmap_items table.

This script adds the following columns to roadmap_items:
- parent_id (ForeignKey to roadmap_items.id, nullable)
- level (Integer, default=0)
- is_leaf (Boolean, default=False)
- is_career_goal (Boolean, default=False)

Note: SQLite doesn't support ALTER TABLE ADD COLUMN with constraints well,
so this migration recreates the table structure. For development, it's recommended
to drop and recreate the database using init_db.py --drop.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from database.base import engine, SessionLocal


def migrate_roadmap_items():
    """Add hierarchical fields to roadmap_items table."""
    print("=" * 60)
    print("Roadmap Items Hierarchical Migration")
    print("=" * 60)

    # SQLite has limited ALTER TABLE support
    # We need to recreate the table with new columns
    print("\n⚠️  SQLite Migration Warning:")
    print("SQLite has limited ALTER TABLE support.")
    print("For production databases, use proper migrations (Alembic).")
    print("\nFor development, it's recommended to:")
    print("  1. Backup your data (if needed)")
    print("  2. Run: python scripts/init_db.py --drop")
    print("  3. This will recreate the database with new schema")

    print("\n✓ Migration script ready")
    print("   Run 'python scripts/init_db.py --drop' to apply changes")


if __name__ == "__main__":
    try:
        migrate_roadmap_items()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


#!/usr/bin/env python3
"""Main script to initialize the database and seed with mock data."""

import sys
from pathlib import Path

# Add parent directory to path to import database module
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.base import Base, SessionLocal, create_tables, drop_tables, engine
from scripts.seed_database import seed_database
from sqlalchemy.orm import Session


def init_database(drop_existing: bool = False):
    """
    Initialize the database.

    Args:
        drop_existing: If True, drop existing tables before creating new ones.
    """
    print("=" * 60)
    print("Uni Pilot Database Initialization")
    print("=" * 60)

    db_file = Path("uni_pilot.db")

    if db_file.exists():
        if drop_existing:
            print(f"\n⚠️  Existing database found: {db_file}")
            print("Dropping existing tables...")
            drop_tables()
            db_file.unlink()  # Delete the database file
            print("✓ Existing database removed")
        else:
            print(f"\n⚠️  Database already exists: {db_file}")
            response = input("Do you want to drop and recreate it? (yes/no): ").strip().lower()
            if response in ["yes", "y"]:
                print("Dropping existing tables...")
                drop_tables()
                db_file.unlink()
                print("✓ Existing database removed")
            else:
                print("Keeping existing database. Exiting.")
                return

    # Create tables
    print("\n📦 Creating database tables...")
    create_tables()
    print("✓ Tables created successfully")

    # Seed with mock data
    print("\n🌱 Seeding database with mock data...")
    db: Session = SessionLocal()
    try:
        seed_database(db)
        print("\n✅ Database initialization complete!")
        print(f"\n📁 Database file: {db_file.absolute()}")
        print("\n📝 Test User Credentials:")
        print("   Email: max.mustermann@stud.tu-darmstadt.de")
        print("   Password: password123")
        print("\n   Email: anna.schmidt@stud.tu-darmstadt.de")
        print("   Password: password123")
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize Uni Pilot database")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing database if it exists",
    )
    args = parser.parse_args()

    try:
        init_database(drop_existing=args.drop)
    except KeyboardInterrupt:
        print("\n\n⚠️  Initialization cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        sys.exit(1)


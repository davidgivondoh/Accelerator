#!/usr/bin/env python3
"""
Database initialization script for the Growth Engine.

This script:
1. Creates all database tables
2. Optionally seeds initial data
3. Verifies connection to Neon PostgreSQL

Usage:
    python scripts/init_db.py
    python scripts/init_db.py --seed
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse

# Import database components directly to avoid ADK dependencies
from config.settings import settings
from src.data.database import Base, close_db, engine, get_session, init_db
from src.models import OpportunityType, SourceType


async def verify_connection() -> bool:
    """Verify database connection."""
    print("🔌 Verifying database connection...")
    
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def create_tables() -> bool:
    """Create all database tables."""
    print("\n📊 Creating database tables...")
    
    try:
        await init_db()
        print("✅ All tables created successfully!")
        
        # List created tables
        async with engine.connect() as conn:
            from sqlalchemy import text
            result = await conn.execute(text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            ))
            tables = [row[0] for row in result.fetchall()]
            print(f"   Created tables: {', '.join(tables)}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False


async def seed_sample_data() -> bool:
    """Seed sample data for testing."""
    print("\n🌱 Seeding sample data...")
    
    try:
        from src.data.models import OpportunityORM
        from src.models import OpportunityCreate
        
        async with get_session() as session:
            # Check if data already exists
            from sqlalchemy import select, func
            result = await session.execute(
                select(func.count()).select_from(OpportunityORM)
            )
            count = result.scalar()
            
            if count > 0:
                print(f"   Database already has {count} opportunities, skipping seed.")
                return True
            
            # Sample opportunities
            samples = [
                OpportunityORM(
                    title="Sample Fellowship - AI Research",
                    organization="Sample Foundation",
                    description="A sample fellowship opportunity for testing the Growth Engine.",
                    summary="Test fellowship for development purposes.",
                    opportunity_type="FELLOWSHIP",
                    url="https://example.com/sample-fellowship",
                    source="MANUAL",
                    location="Remote",
                    is_remote=True,
                    tags=["ai", "research", "fellowship"],
                ),
                OpportunityORM(
                    title="Sample Grant - Tech Innovation",
                    organization="Innovation Fund",
                    description="A sample grant opportunity for testing.",
                    summary="Test grant for development purposes.",
                    opportunity_type="GRANT",
                    url="https://example.com/sample-grant",
                    source="MANUAL",
                    compensation={"amount": 50000, "currency": "USD"},
                    tags=["technology", "innovation", "grant"],
                ),
            ]
            
            for sample in samples:
                session.add(sample)
            
            await session.commit()
            print(f"✅ Seeded {len(samples)} sample opportunities!")
        
        return True
    except Exception as e:
        print(f"❌ Failed to seed data: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main(seed: bool = False) -> int:
    """Main initialization routine."""
    print("=" * 60)
    print("🚀 Growth Engine - Database Initialization")
    print("=" * 60)
    
    # Show configuration
    print(f"\n📋 Configuration:")
    print(f"   Environment: {'Development' if settings.is_development else 'Production'}")
    db_url = settings.database_url.get_secret_value()
    # Mask password in URL for display
    masked_url = db_url.split("@")[-1] if "@" in db_url else "configured"
    print(f"   Database: ...@{masked_url}")
    
    # Verify connection
    if not await verify_connection():
        print("\n💡 Tip: Make sure your DATABASE_URL in .env is correct.")
        print("   For Neon: postgresql+asyncpg://user:pass@host/dbname?sslmode=require")
        return 1
    
    # Create tables
    if not await create_tables():
        return 1
    
    # Seed data if requested
    if seed:
        if not await seed_sample_data():
            return 1
    
    # Cleanup
    await close_db()
    
    print("\n" + "=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run 'python daily_run.py' to start the Growth Engine")
    print("  2. Or run individual agents with 'python -m src.agents.discovery'")
    
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize Growth Engine database")
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed sample data for testing",
    )
    args = parser.parse_args()
    
    exit_code = asyncio.run(main(seed=args.seed))
    sys.exit(exit_code)

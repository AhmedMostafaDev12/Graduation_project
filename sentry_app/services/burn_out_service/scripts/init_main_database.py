"""
Initialize Main Burnout System Database
========================================

This script creates all tables in the sentry_burnout_db PostgreSQL database:
- user_profiles
- user_behavioral_profiles
- user_constraints
- user_preferences
- burnout_analyses

Run once to set up the database schema.
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the shared Base and all models
from sentry_app.services.burn_out_service.user_profile.database_base import Base
from sentry_app.services.burn_out_service.user_profile.user_profile_models import (
    UserProfile,
    UserBehavioralProfile,
    UserConstraint,
    UserPreferences
)
from sentry_app.services.burn_out_service.user_profile.burnout_model import BurnoutAnalysis


def init_main_database():
    """Initialize all tables in the main burnout system database."""

    print("=" * 80)
    print("INITIALIZING SENTRY BURNOUT SYSTEM DATABASE")
    print("=" * 80)

    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("\nERROR: DATABASE_URL not found in .env file")
        print("   Please add: DATABASE_URL=postgresql://user:pass@localhost:5432/sentry_burnout_db")
        return

    print(f"\nDatabase: {database_url.split('@')[1] if '@' in database_url else database_url}")

    try:
        # Create engine
        print("\nConnecting to database...")
        engine = create_engine(database_url, echo=False)

        # Test connection
        with engine.connect() as conn:
            print("Connection successful!")

        # Create all tables
        print("\nCreating tables...")
        Base.metadata.create_all(engine)

        # List all created tables
        print("\nSUCCESS! Tables created:")
        print("\nUser Management Tables:")
        print("   - user_profiles - Basic user info, role, team, capabilities")
        print("   - user_behavioral_profiles - Learned patterns, baselines, stress triggers")
        print("   - user_constraints - Active deadlines, PTO blocks, restrictions")
        print("   - user_preferences - Notification settings, quiet hours, UI preferences")

        print("\nAnalysis Tables:")
        print("   - burnout_analyses - Daily burnout analysis history")

        print("\n" + "=" * 80)
        print("DATABASE READY!")
        print("=" * 80)

        print("\nTable Descriptions:")
        print("\n1. user_profiles")
        print("   - Stores: Name, email, job role, team info, work arrangement")
        print("   - Created: During onboarding")
        print("   - Updated: When user changes profile settings")

        print("\n2. user_behavioral_profiles")
        print("   - Stores: Learned patterns (avg tasks, hours, meetings), baseline burnout score")
        print("   - Created: Automatically after 7 days of data")
        print("   - Updated: Continuously by behavioral learning system")

        print("\n3. user_constraints")
        print("   - Stores: Active constraints (deadlines, on-call, PTO blocks)")
        print("   - Created: When user adds constraint or system detects one")
        print("   - Updated: When constraint is resolved or dates change")

        print("\n4. user_preferences")
        print("   - Stores: Notification settings, quiet hours, alert preferences")
        print("   - Created: During onboarding (with defaults)")
        print("   - Updated: When user changes preferences")

        print("\n5. burnout_analyses")
        print("   - Stores: Daily burnout scores, levels, insights, raw metrics")
        print("   - Created: Every time complete_daily_flow() runs")
        print("   - Updated: Never (historical record)")

        print("\n" + "=" * 80)
        print("Next Steps:")
        print("=" * 80)
        print("\n1. Database is ready - tables created successfully")
        print("2. Run example_usage.py to create demo user and test system")
        print("3. Populate vector database: python populate_strategies.py")
        print("4. Start using the system via integration_services.py")

        print("\nQuick Test:")
        print("   cd backend/app/services/burn_out_service")
        print("   python example_usage.py")

    except Exception as e:
        print(f"\nERROR: Failed to initialize database")
        print(f"   {type(e).__name__}: {str(e)}")
        print("\nTroubleshooting:")
        print("   1. Check DATABASE_URL is correct in .env")
        print("   2. Verify PostgreSQL is running")
        print("   3. Confirm database 'sentry_burnout_db' exists")
        print("   4. Check database user has CREATE TABLE permissions")
        print("   5. Try connecting with psql or pgAdmin first")

        import traceback
        print("\nFull Error Details:")
        traceback.print_exc()
        return


if __name__ == "__main__":
    try:
        init_main_database()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

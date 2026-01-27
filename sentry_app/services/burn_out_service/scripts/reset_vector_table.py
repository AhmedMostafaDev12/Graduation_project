"""
Reset Vector Database Table
============================

Drops and recreates the langchain_pg_embedding table with correct dimensions.
Run this when switching embedding models (e.g., from sentence-transformers to Voyage AI).

Usage:
    python reset_vector_table.py
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

VECTOR_DB_URL = os.getenv("VECTOR_DB_URL")
COLLECTION_NAME = "burnout_strategies"

def reset_vector_table():
    """Drop and recreate the vector embedding table."""

    print("=" * 80)
    print("RESET VECTOR DATABASE TABLE")
    print("=" * 80)

    if not VECTOR_DB_URL:
        print("\nERROR: VECTOR_DB_URL not found in .env file")
        return

    # Convert connection string format if needed
    connection_string = VECTOR_DB_URL
    if connection_string.startswith("postgresql://"):
        connection_string = connection_string.replace("postgresql://", "postgresql+psycopg://")

    print(f"\nDatabase: {VECTOR_DB_URL.split('@')[1] if '@' in VECTOR_DB_URL else VECTOR_DB_URL}")
    print(f"Collection: {COLLECTION_NAME}")

    try:
        engine = create_engine(connection_string)

        with engine.connect() as conn:
            print(f"\nDropping existing vector tables...")

            # Drop tables in correct order (embedding first due to foreign key)
            conn.execute(text("DROP TABLE IF EXISTS langchain_pg_embedding CASCADE"))
            print("   Dropped: langchain_pg_embedding")

            conn.execute(text("DROP TABLE IF EXISTS langchain_pg_collection CASCADE"))
            print("   Dropped: langchain_pg_collection")

            conn.commit()

            print(f"\n[OK] Vector tables have been dropped!")
            print("\nThe tables will be automatically recreated with correct dimensions")
            print("when you run populate_strategies.py")

            print("\nNext steps:")
            print("   1. Run: python populate_strategies.py")
            print("   2. This will recreate tables with Voyage AI embeddings (1024 dimensions)")
            print("\n" + "=" * 80)

    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nTroubleshooting:")
        print("   1. Check VECTOR_DB_URL is correct in .env")
        print("   2. Verify PostgreSQL is running")
        print("   3. Check database permissions")
        print("   4. Make sure no applications are using the tables")

if __name__ == "__main__":
    try:
        print("\nWARNING: This will delete all existing vector embeddings!")
        response = input("Are you sure you want to continue? (yes/no): ")

        if response.lower() in ['yes', 'y']:
            reset_vector_table()
        else:
            print("\nOperation cancelled.")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

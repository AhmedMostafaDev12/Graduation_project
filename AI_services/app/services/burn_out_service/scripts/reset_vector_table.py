"""
Reset Vector Database Table
============================

Drops the existing burnout_strategies collection and recreates it with correct dimensions.
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
    """Drop and recreate the vector collection table."""

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
            # Drop the langchain_pg_embedding table entries for this collection
            print(f"\nDropping existing '{COLLECTION_NAME}' collection...")

            # Delete from langchain_pg_embedding table
            result = conn.execute(
                text("""
                    DELETE FROM langchain_pg_embedding
                    WHERE collection_id = (
                        SELECT uuid FROM langchain_pg_collection
                        WHERE name = :collection_name
                    )
                """),
                {"collection_name": COLLECTION_NAME}
            )

            deleted_rows = result.rowcount
            print(f"   Deleted {deleted_rows} embedding entries")

            # Delete from langchain_pg_collection table
            result = conn.execute(
                text("DELETE FROM langchain_pg_collection WHERE name = :collection_name"),
                {"collection_name": COLLECTION_NAME}
            )

            conn.commit()

            print(f"\n[OK] Collection '{COLLECTION_NAME}' has been reset!")
            print("\nNext steps:")
            print("   1. Run: python populate_strategies.py")
            print("   2. This will recreate the collection with Voyage AI embeddings (1024 dimensions)")
            print("\n" + "=" * 80)

    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nTroubleshooting:")
        print("   1. Check VECTOR_DB_URL is correct in .env")
        print("   2. Verify PostgreSQL is running")
        print("   3. Check database permissions")

if __name__ == "__main__":
    try:
        reset_vector_table()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

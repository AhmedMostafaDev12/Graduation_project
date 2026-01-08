"""
Fix Vector Database Schema
===========================

This script fixes the PGVector database schema by dropping and recreating
the tables with the correct structure for the current version of langchain.

Run this if you encounter schema errors like:
  "column langchain_pg_embedding.id does not exist"

Author: Sentry AI Team
Date: 2025
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg
from psycopg import sql

# Load environment variables
load_dotenv()

VECTOR_DB_URL = os.getenv("VECTOR_DB_URL")


def fix_vector_database():
    """Drop and recreate vector database tables with correct schema."""

    print("=" * 80)
    print("FIXING VECTOR DATABASE SCHEMA")
    print("=" * 80)

    if not VECTOR_DB_URL:
        print("\n ERROR: VECTOR_DB_URL not found in .env file")
        print("  Please add: VECTOR_DB_URL=postgresql://user:pass@localhost:5432/sentry_vector_db")
        return

    print(f"\nDatabase: {VECTOR_DB_URL.split('@')[1] if '@' in VECTOR_DB_URL else 'localhost'}")

    try:
        # Connect to database
        print("\n[1/4] Connecting to database...")
        conn = psycopg.connect(VECTOR_DB_URL)
        conn.autocommit = True

        print(" Connected successfully")

        # Drop old tables
        print("\n[2/4] Dropping old tables...")
        with conn.cursor() as cur:
            # Drop tables if they exist
            cur.execute("DROP TABLE IF EXISTS langchain_pg_embedding CASCADE;")
            print("   Dropped langchain_pg_embedding")

            cur.execute("DROP TABLE IF EXISTS langchain_pg_collection CASCADE;")
            print("   Dropped langchain_pg_collection")

        # Create pgvector extension if not exists
        print("\n[3/4] Ensuring pgvector extension is enabled...")
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("   pgvector extension enabled")

        # Create new tables with correct schema
        print("\n[4/4] Creating new tables with correct schema...")
        with conn.cursor() as cur:
            # Create collection table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS langchain_pg_collection (
                    name VARCHAR,
                    cmetadata JSON,
                    uuid UUID PRIMARY KEY
                );
            """)
            print("   Created langchain_pg_collection table")

            # Create embedding table with correct schema for current langchain version
            # Note: LangChain expects 'id' (VARCHAR) as primary key, not 'uuid'
            cur.execute("""
                CREATE TABLE IF NOT EXISTS langchain_pg_embedding (
                    id VARCHAR PRIMARY KEY,
                    collection_id UUID REFERENCES langchain_pg_collection(uuid) ON DELETE CASCADE,
                    embedding VECTOR(768),
                    document TEXT,
                    cmetadata JSON,
                    custom_id VARCHAR
                );
            """)
            print("   Created langchain_pg_embedding table")

            # Create index for similarity search
            cur.execute("""
                CREATE INDEX IF NOT EXISTS langchain_pg_embedding_collection_id_idx
                ON langchain_pg_embedding (collection_id);
            """)
            print("   Created indexes")

        conn.close()

        print("\n" + "=" * 80)
        print(" VECTOR DATABASE SCHEMA FIXED SUCCESSFULLY!")
        print("=" * 80)

        print("\nNext steps:")
        print("1. Run populate_strategies.py to load burnout prevention strategies:")
        print("   python scripts/populate_strategies.py")
        print("\n2. Test the system:")
        print("   python test_complete_flow.py")

    except Exception as e:
        print(f"\n ERROR: {e}")
        import traceback
        traceback.print_exc()

        print("\nTroubleshooting:")
        print("1. Ensure PostgreSQL is running")
        print("2. Verify VECTOR_DB_URL is correct in .env")
        print("3. Ensure pgvector extension is installed:")
        print("   - Ubuntu/Debian: sudo apt install postgresql-16-pgvector")
        print("   - MacOS: brew install pgvector")
        print("   - Windows: Download from https://github.com/pgvector/pgvector/releases")


if __name__ == "__main__":
    try:
        fix_vector_database()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n Script failed: {e}")
        import traceback
        traceback.print_exc()

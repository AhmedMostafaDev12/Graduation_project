"""
Populate Vector Database with Evidence-Based Burnout Prevention Strategies
===========================================================================

This script loads burnout prevention strategies into the PGVector database
for use by the RAG recommendation system.

Run once to initialize the database with strategies.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_postgres.vectorstores import PGVector
from langchain_voyageai import VoyageAIEmbeddings
from langchain.schema import Document
import re

# Load environment variables
load_dotenv()

# Database configuration
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL")
COLLECTION_NAME = "burnout_strategies"

# Initialize embeddings with Voyage-3-large (same as rag_retrieval.py)
embeddings = VoyageAIEmbeddings(
    model="voyage-3-large",  # Free tier: 200M tokens/month, 1024 dimensions
    voyage_api_key=os.getenv("VOYAGE_API_KEY")
)


def parse_markdown_strategy(file_path: Path, category: str) -> dict:
    """Parse a markdown strategy file into structured format."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title (first # heading)
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else file_path.stem.replace('_', ' ').title()

    # Extract sections
    def extract_section(section_name: str) -> str:
        pattern = rf'^## {section_name}\s*\n(.*?)(?=^## |\Z)'
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        return match.group(1).strip() if match else ""

    overview = extract_section("Overview")
    when_to_use = extract_section("When to Use")
    requirements = extract_section("Requirements")
    evidence = extract_section("Research Evidence")
    implementation = extract_section("How to Implement")
    obstacles = extract_section("Common Obstacles & Solutions")
    doesnt_work = extract_section("When This Doesn't Work")
    citations = extract_section("Research Citations")

    # Extract tags and metadata from bottom
    tags_match = re.search(r'\*\*Tags:\*\*\s*(.+)', content)
    difficulty_match = re.search(r'\*\*Difficulty:\*\*\s*(\w+)', content)
    effort_match = re.search(r'\*\*Effort:\*\*\s*(\w+)', content)
    time_match = re.search(r'\*\*Time to implement:\*\*\s*(.+)', content)

    # Extract success rate and burnout reduction from "When to Use"
    effectiveness = "Medium"
    if when_to_use:
        success_match = re.search(r'Success Rate[:\s]+~?(\d+)%', when_to_use)
        reduction_match = re.search(r'Burnout Reduction[:\s]+(\d+)[–-](\d+)\s*points', when_to_use)
        if success_match and reduction_match:
            success_rate = success_match.group(1)
            reduction_avg = (int(reduction_match.group(1)) + int(reduction_match.group(2))) / 2
            if int(success_rate) >= 80 and reduction_avg >= 15:
                effectiveness = "High"
            elif int(success_rate) >= 60 and reduction_avg >= 10:
                effectiveness = "Medium"
            else:
                effectiveness = "Low"

    time_investment = time_match.group(1).strip() if time_match else "Varies"

    # Combine description
    description = overview
    if when_to_use:
        description += f"\n\nWHEN TO USE:\n{when_to_use}"
    if requirements:
        description += f"\n\nREQUIREMENTS:\n{requirements}"

    # Combine evidence
    full_evidence = evidence
    if citations:
        full_evidence += f"\n\nCITATIONS:\n{citations}"

    # Combine implementation
    full_implementation = implementation
    if obstacles:
        full_implementation += f"\n\nCOMMON OBSTACLES & SOLUTIONS:\n{obstacles}"

    # Contraindications
    contraindications = doesnt_work if doesnt_work else "None specified"

    return {
        'title': title,
        'category': category,
        'description': description,
        'evidence': full_evidence,
        'implementation': full_implementation,
        'contraindications': contraindications,
        'effectiveness': effectiveness,
        'time_investment': time_investment
    }


def load_strategies_from_guidebook() -> list:
    """Load all strategy markdown files from Guide_book folder."""
    guidebook_path = Path(__file__).parent.parent / "Guide_book"

    if not guidebook_path.exists():
        print(f"\n ERROR: Guide_book folder not found at {guidebook_path}")
        return []

    strategies = []

    # Map folder names to category names
    category_map = {
        'boundary_setting': 'boundary_setting',
        'breaks_recovery': 'breaks_recovery',
        'communication': 'communication',
        'meeting_management': 'meeting_management',
        'stress_management': 'stress_management',
        'time_management': 'time_management',
        'workload_reduction': 'workload_reduction'
    }

    # Iterate through category folders
    for category_folder, category_name in category_map.items():
        category_path = guidebook_path / category_folder
        if not category_path.exists():
            continue

        # Load all markdown files in the category
        for md_file in category_path.glob("*.md"):
            try:
                strategy = parse_markdown_strategy(md_file, category_name)
                strategies.append(strategy)
                print(f"   Loaded: {strategy['title']}")
            except Exception as e:
                print(f"   Warning: Failed to parse {md_file.name}: {e}")

    return strategies



def format_strategy_document(strategy: dict) -> Document:
    """Format strategy dict into Document for vector storage."""
    content = f"""
STRATEGY: {strategy['title']}

CATEGORY: {strategy['category'].replace('_', ' ').title()}

DESCRIPTION:
{strategy['description']}

EVIDENCE BASE:
{strategy['evidence']}

HOW TO IMPLEMENT:
{strategy['implementation']}

CONTRAINDICATIONS / WHEN NOT TO USE:
{strategy['contraindications']}

EFFECTIVENESS: {strategy['effectiveness']}

TIME INVESTMENT: {strategy['time_investment']}
""".strip()

    metadata = {
        "title": strategy['title'],
        "category": strategy['category'],
        "source": "evidence_based_burnout_strategies_v1"
    }

    return Document(page_content=content, metadata=metadata)


def populate_vector_database():
    """Populate vector database with burnout prevention strategies."""

    print("=" * 80)
    print("POPULATING VECTOR DATABASE WITH BURNOUT PREVENTION STRATEGIES")
    print("=" * 80)

    if not VECTOR_DB_URL:
        print("\n ERROR: VECTOR_DB_URL not found in .env file")
        print("   Please add: VECTOR_DB_URL=postgresql://user:pass@localhost:5432/burnout_recommendations")
        return

    # Load strategies from Guide_book folder
    print("\n Loading strategies from Guide_book folder...")
    STRATEGIES = load_strategies_from_guidebook()

    if not STRATEGIES:
        print("\n ERROR: No strategies found in Guide_book folder")
        return

    print(f"\n Total strategies to add: {len(STRATEGIES)}")
    print(f"  Database: {VECTOR_DB_URL.split('@')[1] if '@' in VECTOR_DB_URL else VECTOR_DB_URL}")
    print(f" Collection: {COLLECTION_NAME}")

    # Convert strategies to documents
    print("\n Converting strategies to documents...")
    documents = [format_strategy_document(s) for s in STRATEGIES]

    # Category breakdown
    categories = {}
    for s in STRATEGIES:
        cat = s['category']
        categories[cat] = categories.get(cat, 0) + 1

    print("\n Strategies by category:")
    for cat, count in sorted(categories.items()):
        print(f"   - {cat.replace('_', ' ').title()}: {count} strategies")

    # Create vector store and add documents
    print("\n Creating embeddings and storing in vector database...")
    print("   (This may take 1-2 minutes...)")

    try:
        # Convert connection string format if needed (postgresql:// → postgresql+psycopg://)
        connection_string = VECTOR_DB_URL
        if connection_string.startswith("postgresql://"):
            connection_string = connection_string.replace("postgresql://", "postgresql+psycopg://")

        # Use from_documents which creates collection if not exists
        print("   Creating vector store and adding documents...")
        vector_store = PGVector.from_documents(
            documents=documents,
            embedding=embeddings,
            collection_name=COLLECTION_NAME,
            connection=connection_string,
            use_jsonb=True,
            pre_delete_collection=True,  # Clear existing data if collection exists
        )

        print(f"   Added {len(documents)} documents to vector store")

        print("\n SUCCESS! Vector database populated with strategies!")
        print(f"\n Database Stats:")
        print(f"   - Total strategies: {len(documents)}")
        print(f"   - Embedding model: voyage-3-large (Voyage AI)")
        print(f"   - Vector dimensions: 1024")
        print(f"   - Collection: {COLLECTION_NAME}")

        # Test retrieval
        print("\n Testing retrieval...")
        test_query = "I'm feeling overwhelmed with too many meetings"
        results = vector_store.similarity_search(test_query, k=3)

        print(f"\n   Query: '{test_query}'")
        print(f"   Top 3 relevant strategies:")
        for i, doc in enumerate(results, 1):
            title = doc.metadata.get('title', 'Unknown')
            category = doc.metadata.get('category', 'unknown').replace('_', ' ').title()
            print(f"      {i}. {title} ({category})")

        print("\n" + "=" * 80)
        print(" VECTOR DATABASE READY FOR USE!")
        print("=" * 80)
        print("\nYour RAG recommendation system can now retrieve personalized strategies!")

    except Exception as e:
        print(f"\n ERROR: Failed to populate database")
        print(f"   {type(e).__name__}: {str(e)}")
        print("\nTroubleshooting:")
        print("   1. Check VECTOR_DB_URL is correct in .env")
        print("   2. Verify PostgreSQL is running")
        print("   3. Confirm vector extension is enabled: CREATE EXTENSION vector;")
        print("   4. Check database permissions")
        return


if __name__ == "__main__":
    try:
        populate_vector_database()
    except KeyboardInterrupt:
        print("\n\n  Interrupted by user")
    except Exception as e:
        print(f"\n\n Unexpected error: {e}")
        import traceback
        traceback.print_exc()

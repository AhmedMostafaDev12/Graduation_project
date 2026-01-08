"""
RAG Retrieval Service
=====================

Handles vector database operations and document retrieval.

Responsibilities:
- Vector store initialization and management
- Document embedding and storage
- MMR-based similarity search
- Strategy retrieval and formatting

Author: Sentry AI Team
Date: 2025
"""

import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

from langchain_voyageai import VoyageAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document

# Load environment variables from .env file
load_dotenv()


# ============================================================================
# RAG CONFIGURATION
# ============================================================================

@dataclass
class RAGConfig:
    """Configuration for RAG system"""
    # Database
    connection_string: str
    collection_name: str = "burnout_strategies"

    # Embeddings
    embedding_model: str = ""
    embedding_dimension: int = 768

    # Retrieval
    top_k: int = 5
    similarity_threshold: float = 0.7
    mmr_lambda: float = 0.5  # MMR diversity parameter: 0=max diversity, 1=max relevance
    mmr_fetch_k_multiplier: int = 3  # Fetch k*multiplier candidates for MMR

    @classmethod
    def from_env(cls) -> 'RAGConfig':
        """Create config from environment variables"""
        # Get VECTOR_DB_URL from .env (matches populate_strategies.py)
        vector_db_url = os.getenv("VECTOR_DB_URL")

        if not vector_db_url:
            raise ValueError("VECTOR_DB_URL not found in .env file")

        # Convert to psycopg format if needed
        if vector_db_url.startswith("postgresql://"):
            connection_string = vector_db_url.replace("postgresql://", "postgresql+psycopg://")
        else:
            connection_string = vector_db_url

        return cls(connection_string=connection_string)


# ============================================================================
# RAG RETRIEVAL SERVICE
# ============================================================================

class RAGRetrievalService:
    """
    Vector database retrieval service.

    Features:
    - PGVector integration (cloud-ready)
    - MMR-based diverse retrieval
    - Strategy storage and management
    - Semantic search with embeddings
    """

    def __init__(
        self,
        config: Optional[RAGConfig] = None
    ):
        """
        Initialize RAG retrieval service.

        Args:
            config: RAG configuration (defaults to env-based config using VECTOR_DB_URL)
        """
        self.config = config or RAGConfig.from_env()

        # Initialize embeddings with Voyage-3-large (free tier: 200M tokens/month)
        self.embeddings = VoyageAIEmbeddings(
            model="voyage-3-large",  # Free tier, best quality, 2048 dimensions
            voyage_api_key=os.getenv("VOYAGE_API_KEY")
        )

        # Initialize vector store
        self._init_vector_store()

    def _init_vector_store(self):
        """Initialize PGVector store (creates table if not exists)"""
        try:
            self.vector_store = PGVector(
                embeddings=self.embeddings,
                collection_name=self.config.collection_name,
                connection=self.config.connection_string,
                use_jsonb=True
            )
            print(f"[OK] Connected to vector store: {self.config.collection_name}")
        except Exception as e:
            print(f"[WARNING] Could not connect to vector store: {e}")
            print("    RAG retrieval will be disabled. Using LLM knowledge only.")
            self.vector_store = None

    # ========================================================================
    # RETRIEVAL QUERY BUILDING
    # ========================================================================

    def build_retrieval_query(self, context: Dict) -> str:
        """
        Build semantic query for vector retrieval from burnout context.

        Args:
            context: Extracted burnout context with metrics, issues, and patterns

        Returns:
            Formatted query string for semantic search
        """
        # Create rich query that captures the user's situation
        query_parts = [
            f"Burnout level: {context['burnout_level']}",
            f"Score: {context['burnout_score']} (deviation: {int(context['deviation']):+d} from baseline)",
        ]

        if context.get('primary_issues'):
            query_parts.append(f"Issues: {', '.join(context['primary_issues'])}")

        if context.get('stress_indicators'):
            query_parts.append(f"Stress: {', '.join(context['stress_indicators'])}")

        if context.get('stress_triggers'):
            query_parts.append(f"Triggers: {', '.join(context['stress_triggers'])}")

        if context.get('workload_trend', 'unknown') != 'unknown':
            query_parts.append(f"Trend: {context['workload_trend']}")

        query = "\n".join(query_parts)

        print(f"\n[QUERY] Retrieval query:\n{query}")

        return query

    # ========================================================================
    # STRATEGY RETRIEVAL (MMR)
    # ========================================================================

    def retrieve_strategies(
        self,
        query: str,
        top_k: Optional[int] = None
    ) -> List[Document]:
        """
        Retrieve relevant strategies using MMR for diversity.

        Args:
            query: Semantic search query
            top_k: Number of documents to retrieve (defaults to config)

        Returns:
            List of relevant Document objects
        """
        if not self.vector_store:
            print("[WARNING] Vector store not available")
            return []

        k = top_k or self.config.top_k

        try:
            # Perform MMR search for diverse, relevant results
            # MMR balances relevance with diversity to avoid redundant recommendations
            docs = self.vector_store.max_marginal_relevance_search(
                query,
                k=k,
                fetch_k=k * self.config.mmr_fetch_k_multiplier,
                lambda_mult=self.config.mmr_lambda
            )

            if not docs:
                print("[WARNING] No strategies found")
                return []

            print(f"[OK] Retrieved {len(docs)} diverse strategies using MMR")

            return docs

        except Exception as e:
            print(f"[WARNING] Error retrieving strategies: {e}")
            return []

    # ========================================================================
    # FORMATTING
    # ========================================================================

    def format_retrieved_strategies(self, docs: List[Document]) -> str:
        """
        Format retrieved strategies for LLM prompt.

        Args:
            docs: List of Document objects from retrieval

        Returns:
            Formatted string with all strategy information
        """
        if not docs:
            return "No pre-loaded strategies available. Using LLM knowledge only."

        formatted = []

        for i, doc in enumerate(docs, 1):
            strategy = f"""
Strategy {i}:
Title: {doc.metadata.get('title', 'Untitled')}
Category: {doc.metadata.get('category', 'General')}
Evidence: {doc.metadata.get('evidence_level', 'Unknown')}
Success Rate: {doc.metadata.get('success_rate', 'Unknown')}

Description:
{doc.page_content}

Implementation:
{doc.metadata.get('implementation', 'See description')}
"""
            formatted.append(strategy)

        return "\n".join(formatted)

    # ========================================================================
    # VECTOR STORE MANAGEMENT
    # ========================================================================

    def add_strategy(
        self,
        title: str,
        content: str,
        category: str,
        metadata: Optional[Dict] = None
    ):
        """
        Add a new strategy to vector store.

        Args:
            title: Strategy title
            content: Strategy description
            category: Strategy category
            metadata: Additional metadata (evidence_level, success_rate, etc.)
        """
        if not self.vector_store:
            print("[WARNING] Vector store not available")
            return

        doc = Document(
            page_content=content,
            metadata={
                "title": title,
                "category": category,
                **(metadata or {})
            }
        )

        self.vector_store.add_documents([doc])
        print(f"[OK] Added strategy: {title}")

    def add_strategies_bulk(self, strategies: List[Dict]):
        """
        Add multiple strategies at once.

        Args:
            strategies: List of strategy dicts with 'title', 'content', 'category', 'metadata'
        """
        if not self.vector_store:
            print("[WARNING] Vector store not available")
            return

        docs = [
            Document(
                page_content=s['content'],
                metadata={
                    "title": s['title'],
                    "category": s['category'],
                    **s.get('metadata', {})
                }
            )
            for s in strategies
        ]

        self.vector_store.add_documents(docs)
        print(f"[OK] Added {len(docs)} strategies to vector store")


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def retrieve_strategies_for_context(
    context: Dict,
    config: Optional[RAGConfig] = None
) -> Tuple[List[Document], str]:
    """
    Convenience function to retrieve and format strategies for a given context.

    Args:
        context: Burnout context dictionary
        config: Optional RAG config

    Returns:
        Tuple of (documents list, formatted string)
    """
    service = RAGRetrievalService(config=config)
    query = service.build_retrieval_query(context)
    docs = service.retrieve_strategies(query)
    formatted = service.format_retrieved_strategies(docs)

    return docs, formatted


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example of using the RAG retrieval service.
    """
    print("=" * 80)
    print("RAG RETRIEVAL SERVICE - EXAMPLE")
    print("=" * 80)

    # Example context
    example_context = {
        'burnout_score': 78,
        'burnout_level': 'YELLOW',
        'baseline_score': 42,
        'deviation': 36,
        'primary_issues': ['High task load', 'Too many meetings'],
        'stress_indicators': ['overwhelmed', 'exhaustion'],
        'stress_triggers': ['back_to_back_meetings', 'weekend_work'],
        'workload_trend': 'increasing'
    }

    try:
        # Initialize service
        service = RAGRetrievalService()

        # Build query
        query = service.build_retrieval_query(example_context)

        # Retrieve strategies
        docs = service.retrieve_strategies(query)

        # Format for display
        formatted = service.format_retrieved_strategies(docs)

        print("\n[RESULTS] RETRIEVED STRATEGIES:")
        print("=" * 80)
        print(formatted)

        print("\n" + "=" * 80)
        print("[OK] RAG Retrieval Service Working!")
        print("=" * 80)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

import os
import logging
from typing import Optional, List
from collections import OrderedDict

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredFileLoader
from langchain_voyageai import VoyageAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from langchain_core.documents import Document
import os

from app.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================================
# CONFIGURATION - Exported for other modules
# ==========================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
uploads_dir = os.path.join(current_dir, "uploads")

os.makedirs(uploads_dir, exist_ok=True)

# PgVector collection name
COLLECTION_NAME = "notebook_documents"

def get_loader(file_path: str):
    """Returns the appropriate document loader based on file extension"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return PyMuPDFLoader(file_path)
    else:
        return UnstructuredFileLoader(file_path)

# ==========================================================
# RAG DOCUMENT PROCESSING 
# ==========================================================

class DocumentProcessor:
    """Handles document processing and vector store management with PgVector"""

    def __init__(self):
        """
        Initialize the document processor with a single PgVector store.
        Uses Voyage-3 embeddings for best document search quality.
        """
        self.embeddings = VoyageAIEmbeddings(
            model="voyage-3-large",  # Free tier: 200M tokens/month, 2048 dimensions
            voyage_api_key=os.getenv("VOYAGE_API_KEY")
        )
        self.vector_store = self._initialize_pgvector_store()
        logger.info("DocumentProcessor initialized with PgVector + Voyage-3-large embeddings")

    def _initialize_pgvector_store(self) -> PGVector:
        """
        Initializes and returns the PgVector store.
        """
        return PGVector(
            collection_name=COLLECTION_NAME,
            connection=settings.VECTOR_DB_URL,
            embeddings=self.embeddings,
            distance_strategy="cosine" # or "euclidean", "inner_product"
        )
    
    def _get_db_session(self):
        """Creates a SQLAlchemy session to interact with the database."""
        engine = create_engine(settings.VECTOR_DB_URL)
        Session = sessionmaker(bind=engine)
        return Session()

    def process_file(self, file_path: str, doc_id: str) -> dict:
        """
        Process a file and create/update its entries in the PgVector store.
        
        Args:
            file_path: Path to the file
            doc_id: Unique identifier for the document
            
        Returns:
            Dict with processing status and metadata
        """
        session = self._get_db_session()
        try:
            # Delete existing entries for this doc_id before re-uploading/processing
            self.delete_document(doc_id) # Ensures idempotency

            logger.info(f"Processing new file: {file_path}")
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            loader = get_loader(file_path)
            documents = loader.load()

            if not documents:
                raise ValueError("File contains no readable content")

            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500, 
                chunk_overlap=200,
                separators=["\n\n", "\n", " ", ""],
                length_function=len
            )

            docs = text_splitter.split_documents(documents)

            # Add doc_id to metadata for filtering
            for doc in docs:
                doc.metadata['doc_id'] = doc_id
                if 'page' not in doc.metadata:
                    doc.metadata['page'] = 0 # Default page number

            logger.info(f"Created {len(docs)} chunks for doc_id: {doc_id}")

            # Add to PgVector
            self.vector_store.add_documents(docs)
            
            return {
                "doc_id": doc_id,
                "status": "created",
                "chunks": len(docs)
            }
            
        except Exception as e:
            logger.error(f"Error processing file {doc_id}: {str(e)}")
            return {
                "doc_id": doc_id,
                "status": "error",
                "error": str(e)
            }
        finally:
            session.close()
    
    def get_vector_store(self) -> PGVector:
        """
        Retrieve the PgVector store instance.
        """
        return self.vector_store

    def get_full_text(self, doc_id: str) -> str:
        """
        Get the full text of a document from the vector store.
        """
        session = self._get_db_session()
        try:
            results = session.execute(
                text(f"SELECT cmetadata, document FROM langchain_pg_embedding WHERE cmetadata->>'doc_id' = :doc_id"),
                {"doc_id": doc_id}
            ).fetchall()
            
            if not results:
                return ""
            
            full_text_chunks = [row.document for row in results if row.document]
            return "\n".join(full_text_chunks)
        except Exception as e:
            logger.error(f"Error getting full text for doc {doc_id}: {str(e)}")
            return ""
        finally:
            session.close()
    
    def search_document(
        self,
        doc_id: str,
        query: str,
        k: int = 5,
        page_filter: Optional[List[int]] = None,
        score_threshold: float = 0.0
    ) -> List[dict]:
        """
        Search within a document using PgVector.
        """
        try:
            # Do similarity search without filters to avoid jsonb_path_match issues
            # We'll filter results in Python instead
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": k * 3  # Get more results to filter
                }
            )

            docs = retriever.invoke(query)

            # Filter results in Python by doc_id
            filtered_docs = [
                doc for doc in docs
                if doc.metadata.get("doc_id") == doc_id
            ]

            # Apply page filter if specified
            if page_filter:
                filtered_docs = [
                    doc for doc in filtered_docs
                    if doc.metadata.get("page") in page_filter
                ]

            # Limit to k results
            filtered_docs = filtered_docs[:k]

            logger.info(f"Found {len(filtered_docs)} results for query in doc {doc_id} using PgVector")

            return [
                {
                    "content": doc.page_content,
                    "page": doc.metadata.get("page", "unknown"),
                    "source": doc.metadata.get("source", "unknown")
                }
                for doc in filtered_docs
            ]

        except Exception as e:
            logger.error(f"Error searching document {doc_id} with PgVector: {str(e)}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document and its entries from the PgVector store.
        """
        session = self._get_db_session()
        try:
            # Delete entries from langchain_pg_embedding table using SQL
            # PGVector doesn't have a direct high-level method for deleting by metadata,
            # so we use raw SQL.
            delete_query = text(
                f"DELETE FROM langchain_pg_embedding WHERE cmetadata->>'doc_id' = :doc_id AND collection_id = (SELECT id FROM langchain_pg_collection WHERE name = :collection_name)"
            )
            
            result = session.execute(delete_query, {"doc_id": doc_id, "collection_name": COLLECTION_NAME})
            session.commit()
            
            # Delete uploaded file and its metadata file
            for filename in os.listdir(uploads_dir):
                if filename.startswith(doc_id):
                    file_path = os.path.join(uploads_dir, filename)
                    os.remove(file_path)
                    logger.info(f"Deleted uploaded file for {doc_id}: {filename}")

            metadata_path = os.path.join(uploads_dir, f"{doc_id}.txt")
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
                logger.info(f"Deleted metadata file for {doc_id}")
            
            logger.info(f"Deleted {result.rowcount} entries for doc_id: {doc_id} from PgVector.")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {doc_id} from PgVector: {str(e)}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def clear_cache(self):
        """No-op for PgVector as it doesn't use an in-memory cache like Chroma"""
        logger.info("Clear cache called, but PgVector does not use in-memory cache.")
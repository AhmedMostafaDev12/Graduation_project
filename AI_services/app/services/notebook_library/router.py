"""
Notebook Library Router
=======================

Router for notebook library endpoints to be included in unified app.
Separates endpoints from the standalone FastAPI app.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from uuid import uuid4
import os
import logging

from Document import DocumentProcessor, uploads_dir
from LangGraph_tool import graph

logger = logging.getLogger(__name__)

# Initialize document processor
processor = DocumentProcessor()

# Notebooks data file
notebooks_file = os.path.join(os.path.dirname(__file__), "notebooks.json")

def load_notebooks():
    import json
    if not os.path.exists(notebooks_file):
        return {}
    with open(notebooks_file, "r") as f:
        return json.load(f)

def save_notebooks(data):
    import json
    with open(notebooks_file, "w") as f:
        json.dump(data, f, indent=4)

# Database dependency
def get_db():
    """Get database session."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import os

    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create router with prefix and tags
router = APIRouter(
    prefix="/notebooks",
    tags=["Notebook Library"]
)

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    checkpoint_id: Optional[str] = None

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("")
async def create_notebook(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Create a new notebook by uploading the first document."""
    notebook_id = str(uuid4())
    notebooks = load_notebooks()

    doc_id = str(uuid4())
    _, ext = os.path.splitext(file.filename)
    file_path = os.path.join(uploads_dir, f"{doc_id}{ext}")
    metadata_path = os.path.join(uploads_dir, f"{doc_id}.txt")

    try:
        # Save uploaded file
        content = await file.read()
        file_size = len(content)

        with open(file_path, "wb") as f:
            f.write(content)

        # Save original filename as metadata
        with open(metadata_path, "w", encoding="utf-8") as f:
            f.write(file.filename)

        # Record upload in database
        from sqlalchemy import Column, Integer, String, BigInteger, DateTime
        from sqlalchemy.dialects.postgresql import JSONB
        from sqlalchemy.ext.declarative import declarative_base
        from datetime import datetime

        Base = declarative_base()

        class Upload(Base):
            __tablename__ = "uploads"
            id = Column(Integer, primary_key=True)
            user_id = Column(Integer, nullable=False)
            filename = Column(String, nullable=False)
            file_path = Column(String, nullable=False)
            file_size_bytes = Column(BigInteger, nullable=False)
            mime_type = Column(String)
            upload_type = Column(String, nullable=False)
            processing_status = Column(String, default='processing')
            extraction_result = Column(JSONB)
            uploaded_at = Column(DateTime, default=datetime.utcnow)
            processed_at = Column(DateTime)

        upload_record = Upload(
            user_id=user_id,
            filename=file.filename,
            file_path=file_path,
            file_size_bytes=file_size,
            mime_type=file.content_type,
            upload_type='notebook',
            processing_status='processing'
        )
        db.add(upload_record)
        db.flush()
        upload_id = upload_record.id

        # Process document
        result = processor.process_file(file_path, doc_id)

        # Update upload status
        upload_record.processing_status = 'completed' if result.get("status") != "error" else 'failed'
        upload_record.processed_at = datetime.utcnow()
        upload_record.extraction_result = {
            "notebook_id": notebook_id,
            "doc_id": doc_id,
            "result": result
        }
        db.commit()

        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=f"Error processing file: {result.get('error')}")

        # Create notebook and add document
        notebooks[notebook_id] = {"doc_ids": [doc_id], "name": file.filename, "user_id": user_id}
        save_notebooks(notebooks)

        return {
            "notebook_id": notebook_id,
            "notebook_name": file.filename,
            "first_document": result,
            "upload_id": upload_id
        }

    except Exception as e:
        logger.error(f"Error creating notebook: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating notebook: {str(e)}")

@router.post("/{notebook_id}/documents")
async def upload_to_notebook(
    notebook_id: str,
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Upload a document to an existing notebook."""
    notebooks = load_notebooks()
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")

    doc_id = str(uuid4())
    _, ext = os.path.splitext(file.filename)
    file_path = os.path.join(uploads_dir, f"{doc_id}{ext}")
    metadata_path = os.path.join(uploads_dir, f"{doc_id}.txt")

    try:
        content = await file.read()
        file_size = len(content)

        with open(file_path, "wb") as f:
            f.write(content)

        with open(metadata_path, "w", encoding="utf-8") as f:
            f.write(file.filename)

        from sqlalchemy import Column, Integer, String, BigInteger, DateTime
        from sqlalchemy.dialects.postgresql import JSONB
        from sqlalchemy.ext.declarative import declarative_base
        from datetime import datetime

        Base = declarative_base()

        class Upload(Base):
            __tablename__ = "uploads"
            id = Column(Integer, primary_key=True)
            user_id = Column(Integer, nullable=False)
            filename = Column(String, nullable=False)
            file_path = Column(String, nullable=False)
            file_size_bytes = Column(BigInteger, nullable=False)
            mime_type = Column(String)
            upload_type = Column(String, nullable=False)
            processing_status = Column(String, default='processing')
            extraction_result = Column(JSONB)
            uploaded_at = Column(DateTime, default=datetime.utcnow)
            processed_at = Column(DateTime)

        upload_record = Upload(
            user_id=user_id,
            filename=file.filename,
            file_path=file_path,
            file_size_bytes=file_size,
            mime_type=file.content_type,
            upload_type='notebook',
            processing_status='processing'
        )
        db.add(upload_record)
        db.flush()
        upload_id = upload_record.id

        result = processor.process_file(file_path, doc_id)

        upload_record.processing_status = 'completed' if result.get("status") != "error" else 'failed'
        upload_record.processed_at = datetime.utcnow()
        upload_record.extraction_result = {
            "notebook_id": notebook_id,
            "doc_id": doc_id,
            "result": result
        }
        db.commit()

        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=f"Error processing file: {result.get('error')}")

        notebooks[notebook_id]["doc_ids"].append(doc_id)
        save_notebooks(notebooks)

        return {"notebook_id": notebook_id, "document": result, "upload_id": upload_id}

    except Exception as e:
        logger.error(f"Error uploading to notebook: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading to notebook: {str(e)}")

@router.get("")
async def list_notebooks():
    """List all notebooks."""
    notebooks = load_notebooks()
    return {"notebooks": [{"id": nid, "name": n.get("name", "Untitled")} for nid, n in notebooks.items()]}

@router.get("/{notebook_id}")
async def get_notebook(notebook_id: str):
    """Get details of a specific notebook."""
    notebooks = load_notebooks()
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")

    doc_details = []
    for doc_id in notebooks[notebook_id].get("doc_ids", []):
        metadata_path = os.path.join(uploads_dir, f"{doc_id}.txt")
        filename = "Unknown"
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                filename = f.read().strip()
        doc_details.append({"doc_id": doc_id, "filename": filename})

    return {"notebook_id": notebook_id, "name": notebooks[notebook_id].get("name", "Untitled"), "documents": doc_details}

@router.delete("/{notebook_id}/documents/{doc_id}")
async def delete_document_from_notebook(notebook_id: str, doc_id: str):
    """Delete a document from a notebook."""
    notebooks = load_notebooks()
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")

    if doc_id not in notebooks[notebook_id].get("doc_ids", []):
        raise HTTPException(status_code=404, detail="Document not found in this notebook")

    try:
        processor.delete_document(doc_id)
        notebooks[notebook_id]["doc_ids"].remove(doc_id)
        save_notebooks(notebooks)

        return {"status": "success", "message": f"Document {doc_id} deleted from notebook {notebook_id}"}
    except Exception as e:
        logger.error(f"Error deleting document from notebook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{notebook_id}/chat")
async def chat_with_notebook(notebook_id: str, request: ChatRequest):
    """Stream chat responses for a specific notebook."""
    notebooks = load_notebooks()
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")

    doc_ids = notebooks[notebook_id].get("doc_ids", [])
    if not doc_ids:
        raise HTTPException(status_code=400, detail="Notebook is empty")

    return StreamingResponse(
        stream_agent_response(
            request.message,
            notebook_id,
            request.checkpoint_id
        ),
        media_type="text/event-stream"
    )

async def stream_agent_response(
    message: str,
    notebook_id: str,
    checkpoint_id: Optional[str] = None
):
    """Stream agent responses using Server-Sent Events (SSE)."""
    from langchain_core.messages import HumanMessage

    is_new_conversation = checkpoint_id is None

    try:
        if is_new_conversation:
            checkpoint_id = str(uuid4())
            yield f'data: {{ "type": "checkpoint", "checkpoint_id": "{checkpoint_id}" }}\n\n'

        config = {"configurable": {"thread_id": checkpoint_id}}

        async for state in graph.astream(
            {
                "messages": [HumanMessage(content=message)],
                "notebook_id": notebook_id
            },
            config=config
        ):
            logger.info(f"State keys: {state.keys()}")
            if "agent" in state:
                messages = state["agent"].get("messages", [])
                logger.info(f"Messages count: {len(messages)}")
                if messages:
                    last_message = messages[-1]
                    logger.info(f"Last message type: {type(last_message)}, has content: {hasattr(last_message, 'content')}")
                    if hasattr(last_message, 'content'):
                        content = last_message.content
                        logger.info(f"Content length: {len(content)}")
                        content_escaped = content.replace('"', '\\"').replace("\n", "\\n")
                        yield f'data: {{ "type": "content", "content": "{content_escaped}" }}\n\n'

        yield f'data: {{ "type": "end" }}\n\n'

    except Exception as e:
        logger.error(f"Error in stream_agent_response: {str(e)}")
        error_msg = str(e).replace('"', '\"').replace("\n", "\\n")
        yield f'data: {{ "type": "error", "message": "{error_msg}" }}\n\n'
        yield f'data: {{ "type": "end" }}\n\n'

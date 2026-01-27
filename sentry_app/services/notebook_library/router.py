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
import sys

from sentry_app.services.notebook_library.Document import DocumentProcessor, uploads_dir
from sentry_app.services.notebook_library.LangGraph_tool import graph

# Add backend path for authentication imports
# path hack removed
# path hack removed)

from sentry_app.oauth2 import get_current_user
from sentry_app.models import User

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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new notebook by uploading the first document."""
    notebook_id = str(uuid4())
    notebooks = load_notebooks()
    user_id = current_user.id

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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document to an existing notebook."""
    notebooks = load_notebooks()
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")

    # Verify notebook ownership
    if notebooks[notebook_id].get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this notebook")

    user_id = current_user.id

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
async def list_notebooks(current_user: User = Depends(get_current_user)):
    """List all notebooks for the current user."""
    notebooks = load_notebooks()
    user_notebooks = [
        {"id": nid, "name": n.get("name", "Untitled")}
        for nid, n in notebooks.items()
        if n.get("user_id") == current_user.id
    ]
    return {"notebooks": user_notebooks}

@router.get("/{notebook_id}")
async def get_notebook(notebook_id: str, current_user: User = Depends(get_current_user)):
    """Get details of a specific notebook."""
    notebooks = load_notebooks()
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")

    # Verify notebook ownership
    if notebooks[notebook_id].get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this notebook")

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
async def delete_document_from_notebook(
    notebook_id: str,
    doc_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a document from a notebook."""
    notebooks = load_notebooks()
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")

    # Verify notebook ownership
    if notebooks[notebook_id].get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this notebook")

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
async def chat_with_notebook(
    notebook_id: str,
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Stream chat responses for a specific notebook."""
    notebooks = load_notebooks()
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")

    # Verify notebook ownership
    if notebooks[notebook_id].get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this notebook")

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
    """Stream agent responses word-by-word using Server-Sent Events (SSE)."""
    from langchain_core.messages import HumanMessage, SystemMessage
    from sentry_app.services.notebook_library.LangGraph_tool import (
        llm,
        search_notebook_tool,
        generate_summary_tool,
        generate_quiz_tool,
        extract_tasks_tool
    )

    is_new_conversation = checkpoint_id is None

    try:
        if is_new_conversation:
            checkpoint_id = str(uuid4())
            yield f'data: {{ "type": "checkpoint", "checkpoint_id": "{checkpoint_id}" }}\n\n'

        # Detect which tool to use (same logic as agent_node)
        user_message_lower = message.lower()
        tool_to_use = None
        tool_args = {"notebook_id": notebook_id}

        if any(word in user_message_lower for word in ["search", "find", "look for", "about", "what", "where"]):
            tool_to_use = search_notebook_tool
            tool_args["query"] = message
        elif any(word in user_message_lower for word in ["summarize", "summary", "overview", "main points"]):
            tool_to_use = generate_summary_tool
        elif any(word in user_message_lower for word in ["quiz", "questions", "test", "practice"]):
            # Special handling for quiz generation - inform user about dedicated endpoint
            yield f'data: {{ "type": "token", "content": "I can generate a quiz for you! " }}\n\n'
            yield f'data: {{ "type": "token", "content": "For the best experience with interactive quiz features, " }}\n\n'
            yield f'data: {{ "type": "token", "content": "please use the dedicated quiz endpoint:\\n\\n" }}\n\n'
            yield f'data: {{ "type": "token", "content": "POST /notebooks/{notebook_id}/generate-quiz\\n\\n" }}\n\n'
            yield f'data: {{ "type": "token", "content": "This will return structured JSON perfect for quiz UI components.\\n\\n" }}\n\n'
            yield f'data: {{ "type": "token", "content": "Example request body:\\n" }}\n\n'
            yield f'data: {{ "type": "token", "content": "{{ \\\\"num_questions\\\\": 5, \\\\"difficulty\\\\": \\\\"medium\\\\" }}" }}\n\n'
            yield f'data: {{ "type": "end" }}\n\n'
            return
        elif any(word in user_message_lower for word in ["task", "todo", "action", "extract tasks"]):
            tool_to_use = extract_tasks_tool

        # Execute tool if needed
        if tool_to_use:
            tool_result = tool_to_use.invoke(tool_args)

            system_message = SystemMessage(content=f"""You are an intelligent study assistant.

A tool has been executed with the following result:
{tool_result}

Based on this information, provide a helpful response to the user's question: "{message}"

Be clear, educational, and helpful.""")

            full_messages = [system_message, HumanMessage(content=message)]
        else:
            # No tool needed
            system_message = SystemMessage(content=f"""You are an intelligent study assistant helping users with their notebook.

**Current Notebook ID:** {notebook_id}

You can help users:
- Search for information in their notebook
- Summarize the notebook content
- Generate quiz questions
- Extract actionable tasks

Be clear, educational, and helpful in your responses.""")

            full_messages = [system_message, HumanMessage(content=message)]

        # Stream LLM response word by word
        async for chunk in llm.astream(full_messages):
            if hasattr(chunk, 'content') and chunk.content:
                # Escape special characters for JSON
                content_escaped = chunk.content.replace('\\', '\\\\').replace('"', '\\"').replace("\n", "\\n")
                yield f'data: {{ "type": "token", "content": "{content_escaped}" }}\n\n'

        yield f'data: {{ "type": "end" }}\n\n'

    except Exception as e:
        logger.error(f"Error in stream_agent_response: {str(e)}")
        error_msg = str(e).replace('"', '\\"').replace("\n", "\\n")
        yield f'data: {{ "type": "error", "message": "{error_msg}" }}\n\n'
        yield f'data: {{ "type": "end" }}\n\n'


# ============================================================================
# QUIZ GENERATION ENDPOINT
# ============================================================================

class QuizRequest(BaseModel):
    num_questions: int = 5
    difficulty: str = "medium"
    focus_topic: Optional[str] = None  # Specific topic/chapter to focus quiz on
    doc_id: Optional[str] = None  # Specific document ID to generate quiz from

@router.post("/{notebook_id}/generate-quiz")
async def generate_quiz(
    notebook_id: str,
    request: QuizRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a structured quiz in JSON format from notebook content.

    **Parameters:**
    - num_questions: Number of questions (1-10, default: 5)
    - difficulty: "easy", "medium", or "hard" (default: "medium")
    - focus_topic: Optional topic/chapter to focus on (e.g., "Chapter 3: Cloud Security")
    - doc_id: Optional specific document ID to generate quiz from (instead of all docs)

    Returns quiz in format suitable for frontend quiz components:
    {
        "quiz": {
            "title": "Quiz on [topic]",
            "difficulty": "medium",
            "total_questions": 5,
            "questions": [
                {
                    "id": 1,
                    "question": "Question text?",
                    "options": [
                        {"label": "A", "text": "Option A"},
                        {"label": "B", "text": "Option B"},
                        {"label": "C", "text": "Option C"},
                        {"label": "D", "text": "Option D"}
                    ],
                    "correct_answer": "A",
                    "explanation": "Explanation text"
                }
            ]
        }
    }
    """
    import json
    import re
    from sentry_app.services.notebook_library.LangGraph_tool import generate_quiz_tool, llm
    from langchain_core.messages import HumanMessage, SystemMessage

    notebooks = load_notebooks()
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")

    # Verify notebook ownership
    if notebooks[notebook_id].get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this notebook")

    doc_ids = notebooks[notebook_id].get("doc_ids", [])
    if not doc_ids:
        raise HTTPException(status_code=400, detail="Notebook is empty")

    try:
        # If doc_id is specified, validate it and use only that document
        if request.doc_id:
            if request.doc_id not in doc_ids:
                raise HTTPException(status_code=400, detail=f"Document {request.doc_id} not found in notebook")
            target_doc_ids = [request.doc_id]
        else:
            target_doc_ids = doc_ids

        # Get text content from target documents
        from sentry_app.services.notebook_library.LangGraph_tool import processor
        full_text = ""
        for doc_id in target_doc_ids:
            full_text += processor.get_full_text(doc_id) + "\n\n"

        if not full_text.strip():
            raise HTTPException(status_code=400, detail="No text content found in the specified document(s)")

        # Build the quiz generation prompt
        num_questions = max(1, min(10, request.num_questions))
        difficulty_descriptions = {
            "easy": "simple recall questions",
            "medium": "questions requiring understanding of concepts",
            "hard": "complex questions requiring analysis"
        }
        diff_desc = difficulty_descriptions.get(request.difficulty, difficulty_descriptions["medium"])

        # Add focus topic instruction if provided
        focus_instruction = ""
        if request.focus_topic:
            focus_instruction = f"\n\nIMPORTANT: Focus ALL questions specifically on this topic: '{request.focus_topic}'\nOnly ask questions directly related to this topic. Ignore other content."

        quiz_prompt = f"""Generate exactly {num_questions} multiple-choice quiz questions at {request.difficulty} difficulty ({diff_desc}) based on the content below.
{focus_instruction}

CONTENT FOR QUIZ:
{full_text}

CRITICAL: Return ONLY valid JSON in this EXACT format (no additional text):

{{
  "quiz": {{
    "title": "Quiz on {request.focus_topic if request.focus_topic else '[topic from content]'}",
    "difficulty": "{request.difficulty}",
    "total_questions": {num_questions},
    "questions": [
      {{
        "id": 1,
        "question": "Question text here?",
        "options": [
          {{"label": "A", "text": "First option"}},
          {{"label": "B", "text": "Second option"}},
          {{"label": "C", "text": "Third option"}},
          {{"label": "D", "text": "Fourth option"}}
        ],
        "correct_answer": "A",
        "explanation": "Brief explanation why this is correct"
      }}
    ]
  }}
}}

IMPORTANT:
1. Return ONLY the JSON object, no markdown, no explanations
2. Ensure all questions have exactly 4 options (A, B, C, D)
3. correct_answer must be one of: "A", "B", "C", or "D"
4. Make questions relevant to the actual content provided
5. {"Focus on: " + request.focus_topic if request.focus_topic else "Cover various topics from the content"}"""

        # Use LLM to generate the quiz
        system_message = SystemMessage(content="You are a quiz generation expert. Generate quizzes in valid JSON format only.")
        user_message = HumanMessage(content=quiz_prompt)

        response = await llm.ainvoke([system_message, user_message])
        response_text = response.content if hasattr(response, 'content') else str(response)

        logger.info(f"Quiz LLM response length: {len(response_text)}")

        # Clean the response (remove markdown code blocks if present)
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
        elif response_text.startswith("```"):
            response_text = re.sub(r'^```\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)

        # Parse the JSON response
        try:
            quiz_data = json.loads(response_text)
            return quiz_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse quiz JSON: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate valid quiz JSON. Please try again."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quiz generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")

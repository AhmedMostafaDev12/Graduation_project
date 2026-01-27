"""
AI Companion Router
===================

Router for AI companion endpoints to be included in unified app.
Separates endpoints from the standalone FastAPI app.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging
import os
import tempfile

from .companion_agent import companion_graph
from .companion_tools import save_emotional_entry

logger = logging.getLogger(__name__)

# Database dependency
def get_db():
    """Get database session."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

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
    prefix="/companion",
    tags=["AI Companion"]
)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ChatRequest(BaseModel):
    """Chat message request"""
    message: str
    user_id: int
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat message response"""
    response: str
    conversation_id: str
    sentiment: Optional[str] = None
    action_taken: Optional[str] = None

class DiaryRequest(BaseModel):
    """Diary entry request"""
    content: str
    user_id: int
    entry_date: Optional[str] = None

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint for text conversations.

    Capabilities:
    - Emotional support and diary processing
    - Task statistics and summaries
    - Burnout analysis queries
    - Task creation from natural language
    - General assistance
    """
    try:
        # Create initial state
        initial_state = {
            "messages": [{"role": "user", "content": request.message}],
            "user_id": request.user_id,
            "conversation_id": request.conversation_id or f"conv_{datetime.utcnow().timestamp()}",
            "db_session": db,
            "sentiment": "",
            "action_taken": "",
            "tool_calls": []
        }

        # Run the agent
        result = companion_graph.invoke(initial_state)

        # Extract response
        assistant_message = result["messages"][-1]["content"]

        return ChatResponse(
            response=assistant_message,
            conversation_id=result["conversation_id"],
            sentiment=result.get("sentiment"),
            action_taken=result.get("action_taken")
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.post("/chat/audio")
async def chat_audio(
    audio: UploadFile = File(...),
    user_id: int = Form(...),
    conversation_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Chat with audio input (transcribed using Vosk).

    Supports same capabilities as text chat.
    Audio is transcribed to text, then processed by the companion agent.
    """
    try:
        # Save audio to temp file
        temp_dir = tempfile.mkdtemp()
        audio_path = os.path.join(temp_dir, audio.filename)

        with open(audio_path, "wb") as f:
            content = await audio.read()
            f.write(content)

        # Transcribe audio using AssemblyAI (reuse from task extraction)
        import sys
        # path hack removed
        # path hack removed)

        from audio_processor import AudioProcessor

        audio_processor = AudioProcessor()
        transcript = audio_processor.transcribe_audio(audio_path)

        # Clean up audio file
        os.remove(audio_path)
        os.rmdir(temp_dir)

        # Process as text chat
        chat_request = ChatRequest(
            message=transcript,
            user_id=user_id,
            conversation_id=conversation_id
        )

        return await chat(chat_request, db)

    except Exception as e:
        logger.error(f"Audio chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Audio chat failed: {str(e)}")

@router.post("/diary")
async def save_diary(request: DiaryRequest, db: Session = Depends(get_db)):
    """
    Save diary entry and extract emotional insights.

    This endpoint:
    1. Saves the diary entry to qualitative_data table
    2. Analyzes sentiment using the companion AI
    3. Extracts key emotional themes
    4. Triggers burnout analysis if needed
    """
    try:
        # Parse entry date
        entry_date = datetime.utcnow()
        if request.entry_date:
            try:
                entry_date = datetime.fromisoformat(request.entry_date)
            except:
                pass

        # Save to qualitative data
        result = save_emotional_entry(
            user_id=request.user_id,
            content=request.content,
            entry_type="diary_entry",
            db=db
        )

        # Generate supportive response from companion
        chat_request = ChatRequest(
            message=f"I wrote in my diary: {request.content[:200]}... Please give me supportive feedback.",
            user_id=request.user_id
        )

        response = await chat(chat_request, db)

        return {
            "status": "success",
            "entry_saved": True,
            "sentiment": result.get("sentiment"),
            "themes": result.get("themes"),
            "companion_response": response.response,
            "entry_id": result.get("entry_id")
        }

    except Exception as e:
        logger.error(f"Diary save error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save diary: {str(e)}")

@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """
    Retrieve conversation history.

    Returns all messages in a conversation for context.
    """
    # TODO: Implement conversation storage/retrieval
    return {
        "conversation_id": conversation_id,
        "messages": [],
        "note": "Conversation history storage not yet implemented"
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-companion",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "capabilities": [
            "emotional_support",
            "task_statistics",
            "burnout_analysis",
            "task_creation",
            "general_assistance"
        ]
    }

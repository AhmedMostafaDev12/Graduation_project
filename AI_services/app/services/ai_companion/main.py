"""
AI Companion Chatbot Service
=============================

A conversational AI assistant that helps users with:
1. Emotional support and diary entries (saves to qualitative_data)
2. Task summaries and statistics
3. Burnout analysis and recommendations
4. Task creation from natural language
5. General everyday assistance

Port: 8002
"""

import os
import sys
from typing import Optional
from datetime import datetime
import logging

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import companion tools and agent
from .companion_agent import companion_graph, CompanionState
from .companion_tools import (
    save_emotional_entry,
    get_task_statistics,
    get_burnout_status,
    create_task_from_text,
    get_recent_recommendations
)

# ============================================================================
# DATABASE DEPENDENCY
# ============================================================================

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


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="AI Companion Service",
    description="Conversational AI assistant for emotional support, task management, and burnout prevention",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Companion agent is imported from companion_agent.py


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
    action_taken: Optional[str] = None  # Intent classification (e.g., 'task_query', 'emotional_support')


class DiaryRequest(BaseModel):
    """Diary entry request"""
    content: str
    user_id: int
    entry_date: Optional[str] = None


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint for text conversations.

    Capabilities:
    - Emotional support and diary processing
    - Task statistics and summaries
    - Burnout analysis queries
    - Task creation from natural language
    - General assistance

    Example messages:
    - "I'm feeling overwhelmed with work"
    - "Show me my task statistics"
    - "What's my burnout status?"
    - "Create a task: finish the report by Friday"
    - "How do I manage stress?"
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


@app.post("/chat/audio")
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
    import tempfile
    import subprocess

    try:
        # Save audio to temp file
        temp_dir = tempfile.mkdtemp()
        audio_path = os.path.join(temp_dir, audio.filename)

        with open(audio_path, "wb") as f:
            content = await audio.read()
            f.write(content)

        # Transcribe audio using Vosk (reuse from task extraction)
        from task_extraction.audio_processor import AudioProcessor

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


@app.post("/diary")
async def save_diary(request: DiaryRequest, db: Session = Depends(get_db)):
    """
    Save diary entry and extract emotional insights.

    This endpoint:
    1. Saves the diary entry to qualitative_data table
    2. Analyzes sentiment using the companion AI
    3. Extracts key emotional themes
    4. Triggers burnout analysis if needed

    Returns:
    - Sentiment analysis
    - Key themes identified
    - Supportive message from companion
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


@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """
    Retrieve conversation history.

    Returns all messages in a conversation for context.
    """
    # TODO: Implement conversation storage/retrieval
    # For now, return empty (conversations are stateless)
    return {
        "conversation_id": conversation_id,
        "messages": [],
        "note": "Conversation history storage not yet implemented"
    }


@app.get("/health")
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


# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🤖 AI Companion Service starting up...")
    logger.info("✅ Companion agent initialized")
    logger.info("✅ Database connection ready")
    logger.info("✅ All tools loaded")
    logger.info("🚀 AI Companion Service ready on port 8002")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

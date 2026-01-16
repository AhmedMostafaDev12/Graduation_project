"""
Unified Task Extraction Service
================================

This service provides a single endpoint to extract tasks from ANY input type
and save them directly to the database with valid JSON output.

Supported Inputs:
- Audio files (MP3, WAV, M4A, OGG) → Vosk transcription + task extraction
- Documents (PDF, DOCX, TXT, MD) → Unstructured parsing + task extraction
- Images (PNG, JPG, JPEG, BMP, TIFF) → Vision/OCR + task extraction
- Handwritten notes → OCR optimized for handwriting + task extraction
- Plain text → Direct task extraction

Features:
- Automatic file type detection
- Intelligent processor selection
- Database integration
- Valid JSON output
- Error handling and logging

Author: Sentry AI Team
Date: 2025
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator


# ============================================================================
# PYDANTIC MODELS FOR VALIDATION
# ============================================================================

class ExtractedTask(BaseModel):
    """
    Validated task model matching database schema.
    """
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: Optional[str] = Field(None, description="Task priority")
    deadline: Optional[str] = Field(None, description="Deadline in YYYY-MM-DD format")
    start_time: Optional[str] = Field(None, description="Start time in HH:MM format")
    end_time: Optional[str] = Field(None, description="End time in HH:MM format")
    assignee: Optional[str] = Field(None, max_length=100, description="Person assigned")
    category: Optional[str] = Field("general", description="Task category")
    estimated_hours: Optional[float] = Field(None, ge=0, description="Estimated hours")

    @validator('priority')
    def validate_priority(cls, v):
        """Validate priority values"""
        if v is None:
            return "MEDIUM"

        # Normalize priority
        v_upper = v.upper()
        valid_priorities = ["LOW", "MEDIUM", "HIGH", "URGENT", "CRITICAL"]

        # Map common variations
        priority_map = {
            "L": "LOW",
            "M": "MEDIUM",
            "H": "HIGH",
            "U": "URGENT",
            "C": "CRITICAL"
        }

        if v_upper in priority_map:
            return priority_map[v_upper]

        if v_upper in valid_priorities:
            return v_upper

        # Default to MEDIUM if invalid
        return "MEDIUM"

    @validator('category')
    def validate_category(cls, v):
        """Validate category values"""
        if v is None:
            return "general"

        v_lower = v.lower()
        valid_categories = ["assignment", "meeting", "exam", "project", "general"]

        if v_lower in valid_categories:
            return v_lower

        return "general"

    @validator('deadline')
    def validate_deadline(cls, v):
        """Validate deadline format"""
        if v is None or v == "null" or v == "":
            return None

        # Try to parse the date
        try:
            # If already in correct format
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except:
            # Try other common formats
            for fmt in ['%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y', '%m-%d-%Y', '%m/%d/%Y']:
                try:
                    dt = datetime.strptime(v, fmt)
                    return dt.strftime('%Y-%m-%d')
                except:
                    continue

            # If can't parse, return None
            return None


class TaskExtractionResult(BaseModel):
    """
    Result of task extraction with metadata.
    """
    success: bool
    tasks_extracted: int
    tasks_saved: int
    tasks: List[ExtractedTask]
    source_file: str
    source_type: str
    processor_used: str
    processing_time_seconds: float
    errors: List[str] = []
    warnings: List[str] = []


# ============================================================================
# UNIFIED TASK EXTRACTOR SERVICE
# ============================================================================

class UnifiedTaskExtractor:
    """
    Unified service to extract tasks from any input type.
    """

    def __init__(self, database_session: Optional[Session] = None):
        """
        Initialize the unified task extractor.

        Args:
            database_session: SQLAlchemy session for database operations
        """
        self.session = database_session
        self.errors = []
        self.warnings = []

    def extract_and_save_tasks(
        self,
        file_path: str,
        user_id: int,
        processor_type: Optional[str] = None,
        translate: bool = True,
        save_to_db: bool = True
    ) -> TaskExtractionResult:
        """
        Extract tasks from any file type and optionally save to database.

        Args:
            file_path: Path to input file
            user_id: User ID for database storage
            processor_type: Force specific processor (auto-detect if None)
            translate: Whether to translate non-English text
            save_to_db: Whether to save tasks to database

        Returns:
            TaskExtractionResult with extraction details and tasks
        """
        start_time = datetime.now()

        file_path_obj = Path(file_path)

        # Validate file exists
        if not file_path_obj.exists():
            return TaskExtractionResult(
                success=False,
                tasks_extracted=0,
                tasks_saved=0,
                tasks=[],
                source_file=str(file_path),
                source_type="unknown",
                processor_used="none",
                processing_time_seconds=0,
                errors=[f"File not found: {file_path}"]
            )

        # Detect file type and select processor
        source_type, processor = self._detect_file_type_and_processor(
            file_path_obj,
            processor_type
        )

        print(f"\n{'='*70}")
        print(f"UNIFIED TASK EXTRACTION")
        print(f"{'='*70}")
        print(f"File:       {file_path_obj.name}")
        print(f"Type:       {source_type}")
        print(f"Processor:  {processor}")
        print(f"User ID:    {user_id}")
        print(f"Translate:  {translate}")
        print(f"Save to DB: {save_to_db}")
        print(f"{'='*70}\n")

        # Extract tasks using appropriate processor
        try:
            raw_tasks = self._extract_tasks_with_processor(
                file_path_obj,
                processor,
                translate
            )

            print(f"\n[EXTRACT] Extracted {len(raw_tasks)} raw tasks")

        except Exception as e:
            return TaskExtractionResult(
                success=False,
                tasks_extracted=0,
                tasks_saved=0,
                tasks=[],
                source_file=str(file_path),
                source_type=source_type,
                processor_used=processor,
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                errors=[f"Extraction failed: {str(e)}"]
            )

        # Validate and clean tasks
        validated_tasks = self._validate_and_clean_tasks(raw_tasks)

        print(f"[VALIDATE] Validated {len(validated_tasks)} tasks")

        # Save to database if requested
        tasks_saved = 0
        if save_to_db and self.session:
            tasks_saved = self._save_tasks_to_database(validated_tasks, user_id)
            print(f"[DATABASE] Saved {tasks_saved} tasks to database")

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Create result
        result = TaskExtractionResult(
            success=len(validated_tasks) > 0,
            tasks_extracted=len(raw_tasks),
            tasks_saved=tasks_saved,
            tasks=validated_tasks,
            source_file=str(file_path),
            source_type=source_type,
            processor_used=processor,
            processing_time_seconds=processing_time,
            errors=self.errors,
            warnings=self.warnings
        )

        print(f"\n{'='*70}")
        print(f"EXTRACTION COMPLETE")
        print(f"{'='*70}")
        print(f"Success:        {result.success}")
        print(f"Tasks extracted: {result.tasks_extracted}")
        print(f"Tasks saved:     {result.tasks_saved}")
        print(f"Processing time: {result.processing_time_seconds:.2f}s")
        print(f"{'='*70}\n")

        return result

    def _detect_file_type_and_processor(
        self,
        file_path: Path,
        forced_processor: Optional[str]
    ) -> Tuple[str, str]:
        """
        Detect file type and select appropriate processor.

        Returns:
            Tuple of (source_type, processor_name)
        """
        ext = file_path.suffix.lower()

        # If processor is forced, use it
        if forced_processor:
            processors = {
                'audio': 'audio',
                'document': 'document',
                'vision': 'vision',
                'handwritten': 'handwritten',
                'text': 'text'
            }

            if forced_processor in processors:
                return (forced_processor, forced_processor)

        # Auto-detect based on extension
        if ext in ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.wma']:
            return ('audio', 'audio')

        elif ext in ['.pdf', '.docx', '.doc']:
            return ('document', 'document')

        elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']:
            # Default to vision, but could be handwritten
            return ('image', 'vision')

        elif ext in ['.txt', '.md']:
            return ('text', 'text')

        else:
            self.warnings.append(f"Unknown file type: {ext}, defaulting to text processor")
            return ('unknown', 'text')

    def _extract_tasks_with_processor(
        self,
        file_path: Path,
        processor: str,
        translate: bool
    ) -> List[dict]:
        """
        Extract tasks using the specified processor.
        """
        if processor == 'audio':
            from audio_processor import process_audio
            # process_audio returns (tasks, transcript, metadata) - we only need tasks
            tasks, _, _ = process_audio(str(file_path), translate=translate)
            return tasks if tasks else []

        elif processor == 'document':
            from document_processor import process_document
            tasks = process_document(str(file_path))
            return tasks if tasks else []

        elif processor == 'vision':
            from vision_extractor import extract_tasks_from_image
            tasks = extract_tasks_from_image(str(file_path))
            return tasks if tasks else []

        elif processor == 'handwritten':
            from handwritten_processor import process_handwritten_notes
            # Note: Handwritten processor uses Groq Vision API directly, no separate translation step
            tasks = process_handwritten_notes(str(file_path))
            return tasks if tasks else []

        elif processor == 'text':
            # Read text file and extract tasks
            from text_extractor import extract_task_from_text
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            tasks, _ = extract_task_from_text(text, translate=translate)
            return tasks if tasks else []

        else:
            raise ValueError(f"Unknown processor: {processor}")

    def _validate_and_clean_tasks(self, raw_tasks: List[dict]) -> List[ExtractedTask]:
        """
        Validate and clean extracted tasks.
        """
        validated_tasks = []

        for i, task in enumerate(raw_tasks):
            try:
                # Skip if task is not a dictionary
                if not isinstance(task, dict):
                    self.warnings.append(f"Skipping task {i+1}: Not a dictionary (got {type(task).__name__})")
                    continue

                # Skip if task has no title
                if not task.get('title'):
                    self.warnings.append(f"Skipping task {i+1}: No title found")
                    continue

                # Create validated task
                validated_task = ExtractedTask(
                    title=task.get('title', f'Task {i+1}'),
                    description=task.get('description'),
                    priority=task.get('priority'),
                    deadline=task.get('deadline'),
                    start_time=task.get('start_time'),
                    end_time=task.get('end_time'),
                    assignee=task.get('assignee'),
                    category=task.get('category', 'general'),
                    estimated_hours=task.get('estimated_hours')
                )

                validated_tasks.append(validated_task)

            except Exception as e:
                self.warnings.append(f"Failed to validate task {i+1}: {str(e)}")
                continue

        return validated_tasks

    def _save_tasks_to_database(
        self,
        tasks: List[ExtractedTask],
        user_id: int
    ) -> int:
        """
        Save tasks via Backend API (not direct database).

        This ensures:
        - Backend validation is applied
        - Burnout analysis is automatically triggered
        - Consistent task creation workflow

        Returns:
            Number of tasks saved
        """
        import sys
        import os
        from datetime import datetime as dt, date, time

        # Import shared service (replaces HTTP call)
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from shared_services import TaskService

        def parse_time_to_datetime(time_str: str, deadline_str: str = None) -> Optional[dt]:
            """
            Convert HH:MM time string to datetime object.
            If deadline provided, use that date; otherwise use today.
            """
            if not time_str:
                return None

            try:
                # Parse time string (HH:MM format)
                hour, minute = map(int, time_str.split(':'))

                # Determine the date to use
                if deadline_str:
                    try:
                        # Parse deadline (YYYY-MM-DD format)
                        deadline_date = dt.strptime(deadline_str, '%Y-%m-%d').date()
                    except:
                        deadline_date = date.today()
                else:
                    deadline_date = date.today()

                # Combine date and time
                return dt.combine(deadline_date, time(hour=hour, minute=minute))
            except Exception as e:
                print(f"Warning: Failed to parse time '{time_str}': {e}")
                return None

        tasks_saved = 0

        try:
            for task in tasks:
                # Parse deadline to datetime if it's a string
                due_date_obj = None
                if task.deadline:
                    try:
                        due_date_obj = dt.strptime(task.deadline, '%Y-%m-%d')
                    except:
                        pass

                # Convert time strings to datetime objects
                start_time_obj = parse_time_to_datetime(task.start_time, task.deadline)
                end_time_obj = parse_time_to_datetime(task.end_time, task.deadline)

                # Prepare task data for backend API
                task_data = {
                    "title": task.title,
                    "description": task.description or "",
                    "task_type": "task",
                    "status": "Todo",
                    "priority": task.priority or "MEDIUM",
                    "category": task.category or "general",
                    "due_date": due_date_obj,
                    "start_time": start_time_obj,
                    "end_time": end_time_obj,
                    "assigned_to": task.assignee,
                    "can_delegate": True,
                    "estimated_hours": task.estimated_hours,
                    "is_recurring": False,
                    "is_optional": False,
                    "source": "extracted"  # Mark as extracted task
                }

                # Use shared service instead of HTTP call
                try:
                    result = TaskService.create_task(user_id, task_data, self.session)
                    if result.get('id'):
                        tasks_saved += 1
                    else:
                        self.warnings.append(f"Failed to create task '{task.title}'")

                except Exception as e:
                    self.warnings.append(f"Error creating task '{task.title}': {str(e)}")

        except Exception as e:
            self.errors.append(f"Failed to save tasks: {str(e)}")
            return 0

        return tasks_saved

    def _save_tasks_directly_to_db(
        self,
        tasks: List[ExtractedTask],
        user_id: int
    ) -> int:
        """
        FALLBACK: Save tasks directly to database if backend is unavailable.

        This is only used when backend service is down.
        """
        if not self.session:
            self.errors.append("No database session for fallback save")
            return 0

        from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text
        from sqlalchemy.ext.declarative import declarative_base

        Base = declarative_base()

        class Task(Base):
            __tablename__ = 'tasks'
            id = Column(Integer, primary_key=True)
            title = Column(String, nullable=False)
            user_id = Column(Integer, nullable=False)
            description = Column(Text, default="")
            task_type = Column(String, default='task')
            status = Column(String, default='Todo')
            priority = Column(String)
            category = Column(String)
            due_date = Column(DateTime, nullable=True)
            assigned_to = Column(String)
            can_delegate = Column(Boolean, default=True)
            estimated_hours = Column(Float, nullable=True)
            source = Column(String, default='extracted')
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, default=datetime.utcnow)

        tasks_saved = 0

        try:
            for task in tasks:
                due_date = None
                if task.deadline:
                    try:
                        due_date = datetime.strptime(task.deadline, '%Y-%m-%d')
                    except:
                        pass

                db_task = Task(
                    title=task.title,
                    user_id=user_id,
                    description=task.description or "",
                    task_type='task',
                    status='Todo',
                    priority=task.priority or 'MEDIUM',
                    category=task.category or 'general',
                    due_date=due_date,
                    assigned_to=task.assignee,
                    can_delegate=True,
                    estimated_hours=task.estimated_hours,
                    source='extracted_fallback'
                )

                self.session.add(db_task)
                tasks_saved += 1

            self.session.commit()
            self.warnings.append(f"⚠️ Used fallback DB save - burnout analysis NOT triggered")

        except Exception as e:
            self.session.rollback()
            self.errors.append(f"Fallback database error: {str(e)}")
            return 0

        return tasks_saved

    def to_json(self, result: TaskExtractionResult) -> str:
        """
        Convert result to valid JSON string.
        """
        return result.json(indent=2)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def extract_tasks_from_file(
    file_path: str,
    user_id: int,
    database_session: Optional[Session] = None,
    save_to_db: bool = True,
    translate: bool = True
) -> dict:
    """
    Main entry point for task extraction.

    Args:
        file_path: Path to input file
        user_id: User ID
        database_session: Database session (optional)
        save_to_db: Whether to save to database
        translate: Whether to translate text

    Returns:
        Dictionary with extraction results (JSON-serializable)
    """
    extractor = UnifiedTaskExtractor(database_session)

    result = extractor.extract_and_save_tasks(
        file_path=file_path,
        user_id=user_id,
        save_to_db=save_to_db,
        translate=translate
    )

    # Return as dictionary (JSON-serializable)
    return json.loads(result.json())


def extract_tasks_to_json_file(
    file_path: str,
    user_id: int,
    output_file: str,
    database_session: Optional[Session] = None,
    save_to_db: bool = True
) -> str:
    """
    Extract tasks and save results to JSON file.

    Returns:
        Path to output JSON file
    """
    extractor = UnifiedTaskExtractor(database_session)

    result = extractor.extract_and_save_tasks(
        file_path=file_path,
        user_id=user_id,
        save_to_db=save_to_db
    )

    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result.json(indent=2))

    print(f"\n[SAVED] Results saved to: {output_file}")

    return output_file


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

USAGE_EXAMPLES = """
=============================================================================
UNIFIED TASK EXTRACTOR - USAGE EXAMPLES
=============================================================================

This service extracts tasks from ANY file type and saves them to the database.

BASIC USAGE:
------------

from unified_task_extractor import extract_tasks_from_file
from sqlalchemy.orm import Session

# Extract tasks from any file type
result = extract_tasks_from_file(
    file_path="meeting_recording.mp3",
    user_id=123,
    database_session=db_session,
    save_to_db=True
)

print(f"Extracted {result['tasks_extracted']} tasks")
print(f"Saved {result['tasks_saved']} tasks to database")


SPECIFIC FILE TYPES:
--------------------

# Audio file
result = extract_tasks_from_file("meeting.mp3", user_id=123, database_session=db)

# PDF document
result = extract_tasks_from_file("assignment.pdf", user_id=123, database_session=db)

# Handwritten notes
result = extract_tasks_from_file("notes.jpg", user_id=123, database_session=db)

# Plain text
result = extract_tasks_from_file("tasks.txt", user_id=123, database_session=db)


SAVE TO JSON FILE:
------------------

from unified_task_extractor import extract_tasks_to_json_file

output_file = extract_tasks_to_json_file(
    file_path="document.pdf",
    user_id=123,
    output_file="extracted_tasks.json",
    database_session=db,
    save_to_db=True
)


WITHOUT DATABASE:
-----------------

# Extract tasks without saving to database
result = extract_tasks_from_file(
    file_path="notes.txt",
    user_id=123,
    save_to_db=False
)

# Access extracted tasks
for task in result['tasks']:
    print(f"- {task['title']} (Priority: {task['priority']})")


RESULT STRUCTURE:
-----------------

{
  "success": true,
  "tasks_extracted": 5,
  "tasks_saved": 5,
  "tasks": [
    {
      "title": "Complete project proposal",
      "description": "Write and submit the Q1 project proposal",
      "priority": "HIGH",
      "deadline": "2025-01-15",
      "assignee": "John Doe",
      "category": "project",
      "estimated_hours": 8.0
    }
  ],
  "source_file": "meeting_notes.pdf",
  "source_type": "document",
  "processor_used": "document",
  "processing_time_seconds": 12.34,
  "errors": [],
  "warnings": []
}

=============================================================================
"""

if __name__ == "__main__":
    print(USAGE_EXAMPLES)

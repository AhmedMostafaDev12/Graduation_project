from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
import os


load_dotenv()

class Task(BaseModel):
    title: str = Field(description="Short task title (what needs to be done)")
    description: str = Field(description="Additional context, notes, or details about the task")
    assignee: Optional[str] = Field(description="Person assigned to this task", default=None)
    deadline: Optional[str] = Field(description="Due date or deadline in YYYY-MM-DD format. Extract from phrases like 'by Friday', 'due tomorrow', 'on Dec 15', etc.", default=None)
    start_time: Optional[str] = Field(description="Start time in HH:MM format (24-hour). Extract from phrases like 'from 5:00', 'starting at 3pm', 'at 9:30', etc.", default=None)
    end_time: Optional[str] = Field(description="End time in HH:MM format (24-hour). Extract from phrases like 'to 6:00', 'until 5pm', 'ending at 10:30', etc.", default=None)
    estimated_hours: Optional[float] = Field(description="Estimated duration in hours. Calculate from time ranges (e.g., '5:00 to 6:00' = 1 hour) or explicit durations", default=None)
    priority: Optional[str] = Field(description="URGENT, HIGH, MEDIUM, or LOW. Infer from words like 'urgent', 'ASAP', 'important', 'soon'", default=None)
    category: Optional[str] = Field(description="assignment, meeting, exam, project, or general. Infer from context", default="general")

class TaskList(BaseModel):
    tasks: List[Task]

# Use Groq API for text processing (fast and cloud-based)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
    model_kwargs={"response_format": {"type": "json_object"}}
)

llm_text = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.5
)  # For translation without JSON format

parser = PydanticOutputParser(pydantic_object=TaskList)
prompt = PromptTemplate(template="""You are an expert task extraction AI. Extract all actionable tasks from the text with precise temporal information.

Text: {text}

CRITICAL INSTRUCTIONS FOR TIME EXTRACTION:
1. **Start Time & End Time**: When the user mentions time ranges like "from 5:00 to 6:00", "3pm to 4pm", "at 9:30 until 10:00":
   - Extract start_time in 24-hour format (HH:MM)
   - Extract end_time in 24-hour format (HH:MM)
   - Convert PM times correctly (5:00 PM → 17:00, 6:00 PM → 18:00)

2. **Estimated Hours**: Calculate duration from time ranges:
   - "5:00 to 6:00" → 1 hour
   - "3pm to 5pm" → 2 hours
   - If explicit duration mentioned ("2 hour meeting"), use that

3. **Deadline/Due Date**: Extract dates in YYYY-MM-DD format from phrases like:
   - "by Friday" → calculate the date
   - "due tomorrow" → calculate tomorrow's date
   - "on January 15" → convert to YYYY-MM-DD
   - If only time mentioned (no date), set deadline to null

4. **Title vs Description**:
   - Title: What needs to be done (short, actionable)
   - Description: Only additional context NOT already in other fields (location, notes, etc.)
   - DO NOT put time/date information in description if it belongs in start_time/end_time/deadline

5. **Priority**: Infer from urgency words:
   - "urgent", "ASAP", "immediately" → URGENT
   - "important", "soon", "priority" → HIGH
   - Everything else → MEDIUM or LOW

6. **Category**: Infer from context:
   - Sports, games → could be "meeting" (if scheduled) or "general"
   - Work tasks → "assignment" or "project"
   - Exams, tests → "exam"
   - Meetings, calls → "meeting"

Return ONLY valid JSON in this exact format:
{{
  "tasks": [
    {{
      "title": "task title",
      "description": "additional notes (NOT times/dates)",
      "assignee": "person name or null",
      "deadline": "YYYY-MM-DD or null",
      "start_time": "HH:MM or null",
      "end_time": "HH:MM or null",
      "estimated_hours": float or null,
      "priority": "URGENT|HIGH|MEDIUM|LOW or null",
      "category": "assignment|meeting|exam|project|general"
    }}
  ]
}}

IMPORTANT: Return ONLY the JSON object, no additional text or explanations.""",
                        input_variables=["text"]
                        )

chain = prompt | llm | parser

def translate_and_enhance_text(text: str) -> str:
    """
    Translate text to English and enhance clarity using Ollama.

    Input: Text in any language
    Output: Enhanced English text
    """
    print("   Translating and enhancing text with Ollama...")

    # If text is very short, might not be worth translating
    if len(text.strip()) < 10:
        print("   Text too short to translate")
        return text

    try:
        translation_prompt = f"""Translate this text to English and enhance clarity. Preserve all information.

Text: {text}

English translation:"""

        response = llm_text.invoke(translation_prompt)

        # Extract content from AIMessage object
        enhanced_text = response.content if hasattr(response, 'content') else str(response)

        # Check if result is valid
        if enhanced_text and len(enhanced_text.strip()) > 0:
            print(f"   Translation/Enhancement complete: {len(enhanced_text)} characters")
            return enhanced_text.strip()
        else:
            print(f"   Empty translation result, using original text")
            return text

    except Exception as e:
        error_msg = str(e)
        print(f"   Translation failed: {error_msg}")

        # Check if it's a memory issue
        if "CUDA" in error_msg or "allocate" in error_msg or "memory" in error_msg.lower():
            print("   Tip: Ollama may be out of memory. Try:")
            print("     1. Restart Ollama: ollama serve")
            print("     2. Use a smaller model in .env: OLLAMA_TEXT_MODEL=llama3.2:1b")
            print("     3. Reduce GPU layers if using GPU")

        return text

def extract_task_from_text(text: str, translate: bool = True) -> tuple[List[dict], str]:
    """
    Extract tasks from text using LangChain + OLLAMA

    Input: Plain text (any language)
    Output: Tuple of (List of task dicts, enhanced text)
    """

    print("   Extracting tasks with LangChain + OLLAMA")

    # Check if text is empty or too short
    if not text or len(text.strip()) < 5:
        print("   Text too short to extract tasks")
        return [], text

    try:
        # Translate and enhance if needed
        processed_text = text
        if translate:
            processed_text = translate_and_enhance_text(text)
        else:
            processed_text = text

        # Run chain
        result = chain.invoke({"text": processed_text})

        # Convert to dict
        tasks = [task.dict() for task in result.tasks]

        print(f"   Extracted {len(tasks)} tasks")
        return tasks, processed_text

    except Exception as e:
        error_msg = str(e)
        print(f"   Task extraction error: {error_msg}")

        # Check for common issues
        if "CUDA" in error_msg or "allocate" in error_msg or "memory" in error_msg.lower():
            print("   Ollama out of memory. Try:")
            print("     - Restart Ollama")
            print("     - Use smaller model: OLLAMA_TEXT_MODEL=llama3.2:1b")
        elif "validation error" in error_msg.lower() or "parsing" in error_msg.lower():
            print("   LLM returned invalid JSON. The model may need:")
            print("     - More context in the text")
            print("     - A different model that's better at JSON")
            print("     - Text to actually contain tasks")

        return [], text if not translate else processed_text
from langchain_groq import ChatGroq
from langchain.schema.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from PIL import Image
import base64
from dotenv import load_dotenv
import os

load_dotenv()

# Use Groq Vision API for image/vision tasks (faster and cloud-based)
vision_llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
    max_tokens=2048
)

json_parser = JsonOutputParser()
def extract_tasks_from_image(image_path: str) -> list[dict]:
    """
    Extract tasks from image using LangChain + Ollama
    
    Input: Image path
    Output: List of task dicts
    
    Uses LangChain's multimodal capabilities
    """
    print(" Extracting tasks with LangChain + Ollama...")
    
    # Encode image to base64
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode()
    
    # Create prompt with enhanced time extraction instructions
    prompt = f"""You are an expert task extraction AI. Extract all actionable tasks from this image with precise temporal information.

The image could contain handwritten notes, whiteboard, screenshots, or typed text.

CRITICAL INSTRUCTIONS FOR TIME EXTRACTION:
1. **Start Time & End Time**: When you see time ranges like "from 5:00 to 6:00", "3pm to 4pm", "at 9:30 until 10:00":
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

IMPORTANT: Return ONLY the JSON object, no additional text or explanations."""

    try:
        # Create multimodal message with image
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                }
            ]
        )

        # Invoke LangChain ChatGroq with multimodal input
        response = vision_llm.invoke([message])

        # Parse JSON response
        result = json_parser.parse(response.content)
        tasks = result.get("tasks", [])

        print(f"    Extracted {len(tasks)} tasks")
        return tasks

    except Exception as e:
        print(f"    Error: {e}")
        return []

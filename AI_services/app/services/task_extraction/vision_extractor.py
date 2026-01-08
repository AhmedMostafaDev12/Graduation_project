from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from PIL import Image
import base64
from dotenv import load_dotenv
import os

load_dotenv()

# Use OLLAMA_VISION_MODEL for image/vision tasks
VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava")

vision_llm = Ollama(
    model=VISION_MODEL,
    format="json"
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
    
    # Create prompt
    prompt = f"""Extract all tasks from this image.
This could be handwritten notes, whiteboard, or typed text.

Return a JSON object with this structure:
{{
  "tasks": [
    {{
      "title": "task title",
      "description": "details",
      "assignee": "person or null",
      "deadline": "YYYY-MM-DD or null",
      "priority": "URGENT|HIGH|MEDIUM|LOW",
      "category": "assignment|meeting|exam|project|general"
    }}
  ]
}}

Return ONLY valid JSON."""

    try:
        # Invoke LangChain with multimodal input
        response = vision_llm.invoke(prompt, images=[image_data])
        
        # Parse JSON response
        result = json_parser.parse(response)
        tasks = result.get("tasks", [])
        
        print(f"    Extracted {len(tasks)} tasks")
        return tasks
        
    except Exception as e:
        print(f"    Error: {e}")
        return []

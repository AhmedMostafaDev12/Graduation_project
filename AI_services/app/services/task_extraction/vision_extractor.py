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
    model="llama-3.2-90b-vision-preview",
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

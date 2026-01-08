from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
import os


load_dotenv()

class Task(BaseModel):
    title: str = Field(description="Short task title")
    description: str = Field(description="Detailed description")
    assignee: Optional[str] = Field(description="Person assigned", default=None)
    deadline: Optional[str] = Field(description="Deadline in YYYY-MM-DD format", default=None)
    priority: Optional[str] = Field(description="URGENT, HIGH, MEDIUM, or LOW")
    category: Optional[str] = Field(description="assignment, meeting, exam, project, or general",default="general")

class TaskList(BaseModel):
    tasks: List[Task]

# Use OLLAMA_TEXT_MODEL for text processing
TEXT_MODEL = os.getenv("OLLAMA_TEXT_MODEL", "llama3.1:8b")

llm = Ollama(model=TEXT_MODEL, format="json")
llm_text = Ollama(model=TEXT_MODEL)  # For translation without JSON format

parser = PydanticOutputParser(pydantic_object=TaskList)
prompt = PromptTemplate(template="""Extract all actionable tasks from the following text.

Text: {text}

Instructions:
- Find all tasks, assignments, deadlines, and action items
- Return ONLY valid JSON in this exact format:
{{
  "tasks": [
    {{
      "title": "task title",
      "description": "detailed description",
      "assignee": "person name or null",
      "deadline": "YYYY-MM-DD or null",
      "priority": "URGENT, HIGH, MEDIUM, LOW, or null",
      "category": "assignment, meeting, exam, project, or general"
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

        enhanced_text = llm_text.invoke(translation_prompt)

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
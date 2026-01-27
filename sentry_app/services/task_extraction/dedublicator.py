from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model= "gemini-2.5-flash")

# JSON parser
parser = JsonOutputParser()

# Deduplication prompt
dedup_prompt = PromptTemplate(
    template="""You are given a list of tasks that may contain duplicates.
                Merge any duplicate or very similar tasks. Keep the most complete version.

                Tasks:
                {tasks}

                Return a JSON object with this structure:
            {{
                "tasks": [
                        {{
                            "title": "...",
                            "description": "...",
                            "assignee": "...",
                            "deadline": "...",
                            "priority": "...",
                            "category": "..."
                        }}
                        ]
            }}

        Return ONLY valid JSON.""",
    input_variables=["tasks"]
)

dedup_chain = dedup_prompt | llm | parser

def deduplicate_tasks(tasks: list[dict]) -> list[dict]:
    """
    Deduplicate tasks using LangChain + OLLAMA
    
    Input: List of tasks (may have duplicates)
    Output: List of unique tasks
    
    Uses LangChain chain for intelligent merging
    """
    if len(tasks) <= 1:
        return tasks
    
    try: 
        tasks_json = json.dumps(tasks, indent=2)

        result = dedup_chain.invoke({"tasks":tasks_json})
        unique_tasks = result.get("tasks", [])

        print(f"   ✅ After deduplication: {len(unique_tasks)} unique tasks")
        return unique_tasks
    
    except Exception as e:
        print(f"   ⚠️ Deduplication failed: {e}")
        return tasks
    
    
import os
import logging
from typing import TypedDict, Annotated, Optional, Literal
from uuid import uuid4
import json
import requests

from langgraph.graph import add_messages, StateGraph, END
from langchain_community.chat_models import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool

from dotenv import load_dotenv
from Document import DocumentProcessor, uploads_dir

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

processor = DocumentProcessor()
notebooks_file = os.path.join(os.path.dirname(__file__), "notebooks.json")

def load_notebooks():
    if not os.path.exists(notebooks_file):
        return {}
    with open(notebooks_file, "r") as f:
        return json.load(f)

# ==========================================================
# LangGraph TOOLS
# ==========================================================

@tool
def search_notebook_tool(notebook_id: str, query: str, pages: Optional[str] = None) -> str:
    """
    Search within a specific notebook using semantic similarity.
    """
    notebooks = load_notebooks()
    if notebook_id not in notebooks:
        return "Error: Notebook not found."

    doc_ids = notebooks[notebook_id].get("doc_ids", [])
    if not doc_ids:
        return "Notebook is empty."

    logger.info(f"Searching notebook {notebook_id} with {len(doc_ids)} documents. Doc IDs: {doc_ids}")

    all_results = []
    for idx, doc_id in enumerate(doc_ids):
        try:
            logger.info(f"Searching document {idx+1}/{len(doc_ids)}: {doc_id}")
            results = processor.search_document(doc_id=doc_id, query=query, k=3)
            logger.info(f"Document {doc_id} returned {len(results)} results")
            all_results.extend(results)
        except Exception as e:
            logger.error(f"Error searching in doc {doc_id}: {e}")

    logger.info(f"Total results from all documents: {len(all_results)}")

    if not all_results:
        return "No relevant information found in the notebook."

    formatted = [f"[Result {i+1} - Page {res.get('page', 'N/A')}]\n{res.get('content', '')}" for i, res in enumerate(all_results)]
    return "\n".join(formatted)

@tool
def generate_summary_tool(notebook_id: str, detail_level: str = "medium") -> str:
    """
    Generate a summary of the entire notebook.
    """
    notebooks = load_notebooks()
    if notebook_id not in notebooks:
        return "Error: Notebook not found."

    doc_ids = notebooks[notebook_id].get("doc_ids", [])
    if not doc_ids:
        return "Notebook is empty."

    full_text = ""
    for doc_id in doc_ids:
        full_text += processor.get_full_text(doc_id) + "\n\n"

    if not full_text.strip():
        return "No text content found in the notebook to summarize."

    detail_instructions = {
        "brief": "Create a brief 2-3 sentence summary highlighting only the main points.",
        "medium": "Create a comprehensive paragraph summary (5-7 sentences) covering the key concepts.",
        "detailed": "Create a detailed summary with main points organized in bullet form, including important details and examples."
    }
    instruction = detail_instructions.get(detail_level, detail_instructions["medium"])

    return f"""{instruction} based on the following content from the notebook:

CONTENT TO SUMMARIZE:
{full_text}

Provide a clear, well-structured summary."""

@tool
def generate_quiz_tool(notebook_id: str, num_questions: int = 5, difficulty: str = "medium") -> str:
    """
    Generate quiz questions from the entire notebook in JSON format.
    """
    notebooks = load_notebooks()
    if notebook_id not in notebooks:
        return json.dumps({"error": "Notebook not found."})

    doc_ids = notebooks[notebook_id].get("doc_ids", [])
    if not doc_ids:
        return json.dumps({"error": "Notebook is empty."})

    full_text = ""
    for doc_id in doc_ids:
        full_text += processor.get_full_text(doc_id) + "\n\n"

    if not full_text.strip():
        return json.dumps({"error": "No text content found in the notebook to create a quiz from."})

    num_questions = max(1, min(10, num_questions))
    difficulty_descriptions = {
        "easy": "simple recall questions",
        "medium": "questions requiring understanding of concepts",
        "hard": "complex questions requiring analysis"
    }
    diff_desc = difficulty_descriptions.get(difficulty, difficulty_descriptions["medium"])

    return f"""Generate exactly {num_questions} multiple-choice quiz questions at {difficulty} difficulty ({diff_desc}) based on the notebook's content.

CONTENT FOR QUIZ:
{full_text}

CRITICAL: Return ONLY valid JSON in this EXACT format (no additional text):

{{
  "quiz": {{
    "title": "Quiz on [topic from content]",
    "difficulty": "{difficulty}",
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
4. Make questions relevant to the actual content provided"""

@tool
def extract_tasks_tool(notebook_id: str) -> str:
    """
    Extract tasks from the entire notebook.
    """
    notebooks = load_notebooks()
    if notebook_id not in notebooks:
        return "Error: Notebook not found."

    doc_ids = notebooks[notebook_id].get("doc_ids", [])
    if not doc_ids:
        return "Notebook is empty."

    full_text = ""
    for doc_id in doc_ids:
        full_text += processor.get_full_text(doc_id) + "\n\n"
    
    if not full_text.strip():
        return "No text content found to extract tasks from."

    from ...services.task_extraction.text_extractor import extract_task_from_text
    tasks, _ = extract_task_from_text(full_text, translate=False)

    if not tasks:
        return "No tasks found in the notebook."

    formatted = [f"[Task {i+1}]\nTitle: {t.get('title', 'N/A')}\nDescription: {t.get('description', 'N/A')}" for i, t in enumerate(tasks)]
    return "\n".join(formatted)

@tool
def process_link_tool(url: str, notebook_id: str) -> str:
    """
    Process a web link and add it as a new document to the specified notebook.
    """
    notebooks = load_notebooks()
    if notebook_id not in notebooks:
        return "Error: Notebook not found."

    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        
        doc_id = str(uuid4())
        file_path = os.path.join(uploads_dir, f"{doc_id}.txt")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        result = processor.process_file(file_path, doc_id)
        if result.get("status") == "error":
            return f"Error processing link: {result.get('error')}"

        notebooks[notebook_id]["doc_ids"].append(doc_id)
        with open(notebooks_file, "w") as f:
            json.dump(notebooks, f, indent=4)
        
        return f"Successfully processed link. New document ID {doc_id} added to notebook {notebook_id}."
        
    except Exception as e:
        return f"Error processing link: {str(e)}"

# ==========================================================
# LANGGRAPH AGENT
# ==========================================================

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    notebook_id: str

tools = [search_notebook_tool, generate_summary_tool, generate_quiz_tool, extract_tasks_tool, process_link_tool]

# Use Groq instead of Ollama for better reliability (cloud-based)
# Ollama requires local installation and running service
try:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7
    )
    logger.info("Using Groq LLM for notebook chat")
except Exception as e:
    logger.warning(f"Failed to initialize Groq, falling back to Ollama: {e}")
    llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"), temperature=0.7)
    logger.info("Using Ollama LLM for notebook chat")

memory = MemorySaver()

async def agent_node(state: AgentState):
    messages = state["messages"]
    notebook_id = state["notebook_id"]

    # Get the last user message
    user_message = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_message = msg.content.lower()
            break

    # Simple keyword-based tool detection
    tool_to_use = None
    tool_args = {"notebook_id": notebook_id}

    if any(word in user_message for word in ["search", "find", "look for", "about", "what", "where"]):
        tool_to_use = "search_notebook_tool"
        tool_args["query"] = messages[-1].content if isinstance(messages[-1], HumanMessage) else ""
    elif any(word in user_message for word in ["summarize", "summary", "overview", "main points"]):
        tool_to_use = "generate_summary_tool"
    elif any(word in user_message for word in ["quiz", "questions", "test", "practice"]):
        tool_to_use = "generate_quiz_tool"
    elif any(word in user_message for word in ["task", "todo", "action", "extract tasks"]):
        tool_to_use = "extract_tasks_tool"

    # If a tool should be used, create a tool call response
    if tool_to_use:
        # Execute the tool immediately
        tool_map = {
            "search_notebook_tool": search_notebook_tool,
            "generate_summary_tool": generate_summary_tool,
            "generate_quiz_tool": generate_quiz_tool,
            "extract_tasks_tool": extract_tasks_tool,
            "process_link_tool": process_link_tool,
        }

        result = tool_map[tool_to_use].invoke(tool_args)

        # Create an AI response with the tool result
        user_question = messages[-1].content if isinstance(messages[-1], HumanMessage) else ''

        system_message = SystemMessage(content=f"""You are an intelligent study assistant.

A tool has been executed with the following result:
{result}

Based on this information, provide a helpful response to the user's question: "{user_question}"

Be clear, educational, and helpful.""")

        # Include both system message and user message for context
        full_messages = [system_message, HumanMessage(content=user_question)]

        try:
            # Use streaming for real-time word-by-word response
            response_content = ""
            async for chunk in llm.astream(full_messages):
                if hasattr(chunk, 'content'):
                    response_content += chunk.content

            logger.info(f"LLM response content length: {len(response_content)}")
        except Exception as e:
            logger.error(f"Error during LLM invocation: {str(e)}")
            response_content = f"I found some information: {result}"

        return {"messages": [AIMessage(content=response_content)]}
    else:
        # No tool needed, just respond normally
        system_message = SystemMessage(content=f"""You are an intelligent study assistant helping users with their notebook.

**Current Notebook ID:** {notebook_id}

You can help users:
- Search for information in their notebook
- Summarize the notebook content
- Generate quiz questions
- Extract actionable tasks
- Process web links

Be clear, educational, and helpful in your responses.""")

        full_messages = [system_message] + messages

        try:
            response = await llm.ainvoke(full_messages)
            response_content = response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Error during LLM invocation: {str(e)}")
            response_content = "I'm here to help with your notebook!"

        return {"messages": [response if isinstance(response, AIMessage) else AIMessage(content=response_content)]}

# Simplified graph without separate tool execution
graph_builder = StateGraph(AgentState)
graph_builder.add_node("agent", agent_node)
graph_builder.set_entry_point("agent")
graph_builder.set_finish_point("agent")
graph = graph_builder.compile(checkpointer=memory)

logger.info("LangGraph agent initialized successfully for notebooks.")
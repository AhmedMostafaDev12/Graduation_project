"""
AI Companion Agent
==================

LangGraph-based conversational agent that:
1. Provides emotional support and saves to qualitative_data
2. Answers questions about tasks, burnout status, recommendations
3. Creates tasks from natural language
4. Acts as general everyday assistant

Uses Ollama (llama3.1:8b) for natural language understanding.
"""

from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
import operator
import subprocess
import json

from .companion_tools import (
    save_emotional_entry,
    get_task_statistics,
    get_burnout_status,
    create_task_from_text
)


# ============================================================================
# STATE DEFINITION
# ============================================================================

class CompanionState(TypedDict):
    """State for companion conversation"""
    messages: List[Dict[str, str]]  # Removed operator.add to prevent duplicates
    user_id: int
    conversation_id: str
    db_session: Any
    sentiment: str
    action_taken: str
    tool_calls: Annotated[List[str], operator.add]  # Keep operator.add for tool_calls only


# ============================================================================
# AGENT NODE FUNCTIONS
# ============================================================================

def classify_intent(state: CompanionState) -> CompanionState:
    """
    Classify user intent and determine which tool(s) to use.

    Intent categories:
    - emotional_support: User sharing feelings, diary, emotions
    - task_query: Asking about tasks, statistics, summaries
    - burnout_query: Asking about burnout status, recommendations
    - task_creation: Wants to create a new task
    - general_chat: Everyday conversation, questions
    """
    last_message = state["messages"][-1]["content"]
    user_id = state["user_id"]

    prompt = f"""Analyze this user message and determine the intent.

User message: "{last_message}"

Classify as ONE of these intents:
1. emotional_support - User is sharing feelings, emotions, diary entry, mental health
2. task_query - User asking about their TASKS, task statistics, what's due, completed tasks
3. burnout_query - User asking about BURNOUT status, burnout statistics, burnout analysis, stress level, recommendations, mental health status
4. task_creation - User wants to create/add a new task
5. general_chat - General conversation, questions, everyday assistance

IMPORTANT:
- If message mentions "burnout" or "stress" or "mental health status" → burnout_query
- If message mentions "tasks" or "to-do" or "assignments" → task_query
- If message mentions "feel" or emotions → emotional_support

Examples:
- "tell me about my burnout statistics" → burnout_query
- "what's my stress level" → burnout_query
- "show me my tasks" → task_query
- "I'm feeling overwhelmed" → emotional_support

Respond in JSON format:
{{
  "intent": "intent_name",
  "needs_emotional_save": true/false,
  "reasoning": "brief explanation"
}}
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.1:8b", prompt],
            capture_output=True,
            text=True,
            encoding='utf-8',  # Fix Unicode errors with Arabic/special chars
            errors='replace',   # Replace invalid chars instead of crashing
            timeout=30          # Increase timeout for slow responses
        )

        response_text = result.stdout.strip()
        start = response_text.find('{')
        end = response_text.rfind('}') + 1

        if start != -1 and end != 0:
            json_str = response_text[start:end]
            classification = json.loads(json_str)

            state["action_taken"] = classification.get("intent", "general_chat")

            # If emotional content, save to database
            if classification.get("needs_emotional_save"):
                save_result = save_emotional_entry(
                    user_id=user_id,
                    content=last_message,
                    entry_type="conversation",
                    db=state["db_session"]
                )
                state["sentiment"] = save_result.get("sentiment", "neutral")

            return state

    except Exception as e:
        print(f"Intent classification error: {e}")
        state["action_taken"] = "general_chat"

    return state


def route_to_tool(state: CompanionState) -> str:
    """
    Route to appropriate tool based on intent.

    Returns next node name.
    """
    intent = state.get("action_taken", "general_chat")

    if intent == "task_query":
        return "task_tool"
    elif intent == "burnout_query":
        return "burnout_tool"
    elif intent == "task_creation":
        return "creation_tool"
    elif intent in ["emotional_support", "general_chat"]:
        return "respond"
    else:
        return "respond"


def task_tool_node(state: CompanionState) -> CompanionState:
    """Get task information and add to context"""
    user_id = state["user_id"]

    # Get task statistics from burnout analysis
    stats = get_task_statistics(user_id)

    # Simplified, concise context
    context = f"""[TASK STATS]
Active: {stats.get('total_tasks', 0)} | Overdue: {stats.get('overdue_tasks', 0)} | Due this week: {stats.get('due_this_week', 0)}
Completion: {stats.get('completion_rate', 0):.0%}
Work hours today: {stats.get('work_hours_today', 0):.1f}h | This week: {stats.get('work_hours_week', 0):.1f}h
Meetings today: {stats.get('meeting_hours_today', 0):.1f}h
"""

    state["messages"].append({
        "role": "system",
        "content": context
    })

    state["tool_calls"].append("task_statistics")

    return state


def burnout_tool_node(state: CompanionState) -> CompanionState:
    """Get burnout status (fast)"""
    user_id = state["user_id"]

    # Get burnout status - FAST (just retrieves existing analysis)
    burnout_data = get_burnout_status(user_id)

    # Extract insights if available
    insights = burnout_data.get('insights', {})

    # Get component breakdown
    components = burnout_data.get('component_breakdown', {})

    # Simplified, concise context for faster processing
    context = f"""[BURNOUT ANALYSIS]
Level: {burnout_data.get('burnout_level', 'UNKNOWN')} (Score: {burnout_data.get('burnout_score', 0)}/100)
Analyzed: {burnout_data.get('analyzed_at', 'N/A')}

Workload: {components.get('workload_score', 'N/A')} | Sentiment: {components.get('sentiment_adjustment', 'N/A')}

Issues: {', '.join(insights.get('primary_issues', [])[:3])}

Stress Signs: {', '.join(insights.get('stress_indicators', []))}

Burnout Signals: Emotional Exhaustion={insights.get('burnout_signals', {}).get('emotional_exhaustion')}, Overwhelm={insights.get('burnout_signals', {}).get('overwhelm')}

Top Concerns:
{chr(10).join(f"- {c}" for c in insights.get('key_concerns', [])[:2])}
"""

    state["messages"].append({
        "role": "system",
        "content": context
    })

    state["tool_calls"].append("burnout_status")

    return state


def creation_tool_node(state: CompanionState) -> CompanionState:
    """Create task from natural language"""
    user_id = state["user_id"]
    last_message = state["messages"][-1]["content"]

    # Extract task using extraction service
    result = create_task_from_text(user_id, last_message)

    if result.get("success"):
        context = f"""
[TASK CREATED]
Tasks created: {result.get('tasks_created', 0)}
Tasks: {json.dumps(result.get('tasks', []), indent=2)}
"""
    else:
        context = f"""
[TASK CREATION FAILED]
Error: {result.get('error')}
"""

    state["messages"].append({
        "role": "system",
        "content": context
    })

    state["tool_calls"].append("create_task")

    return state


def respond_node(state: CompanionState) -> CompanionState:
    """
    Generate final response using Ollama.

    Takes conversation history + tool results and generates helpful response.
    """
    # Build conversation context
    conversation = ""
    for msg in state["messages"]:
        role = msg["role"]
        content = msg["content"]

        if role == "user":
            conversation += f"User: {content}\n\n"
        elif role == "system":
            conversation += f"{content}\n\n"
        elif role == "assistant":
            conversation += f"Assistant: {content}\n\n"

    # Create response prompt (shortened for faster processing)
    prompt = f"""You are a supportive AI companion. Help the user based on this conversation:

{conversation}

Be warm, concise, and actionable. Use data provided above to give specific insights.

Response:"""

    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.1:8b", prompt],
            capture_output=True,
            text=True,
            encoding='utf-8',  # Fix Unicode errors with Arabic/special chars
            errors='replace',   # Replace invalid chars instead of crashing
            timeout=60  # Increased from 30 to 60 seconds
        )

        response = result.stdout.strip()

        # Remove any "Assistant:" prefix if model adds it
        if response.startswith("Assistant:"):
            response = response[10:].strip()

        state["messages"].append({
            "role": "assistant",
            "content": response
        })

    except Exception as e:
        error_response = "I'm here to help, but I'm having trouble processing right now. Could you try again?"
        state["messages"].append({
            "role": "assistant",
            "content": error_response
        })
        print(f"Response generation error: {e}")

    return state


# ============================================================================
# BUILD GRAPH
# ============================================================================

def create_companion_graph():
    """
    Create LangGraph workflow for companion agent.

    Flow:
    1. Classify intent
    2. Route to appropriate tool (or skip to respond)
    3. Execute tool to get data
    4. Generate natural language response
    """
    workflow = StateGraph(CompanionState)

    # Add nodes
    workflow.add_node("classify", classify_intent)
    workflow.add_node("task_tool", task_tool_node)
    workflow.add_node("burnout_tool", burnout_tool_node)
    workflow.add_node("creation_tool", creation_tool_node)
    workflow.add_node("respond", respond_node)

    # Set entry point
    workflow.set_entry_point("classify")

    # Add conditional routing from classify
    workflow.add_conditional_edges(
        "classify",
        route_to_tool,
        {
            "task_tool": "task_tool",
            "burnout_tool": "burnout_tool",
            "creation_tool": "creation_tool",
            "respond": "respond"
        }
    )

    # All tools route to respond
    workflow.add_edge("task_tool", "respond")
    workflow.add_edge("burnout_tool", "respond")
    workflow.add_edge("creation_tool", "respond")

    # Respond is the end
    workflow.add_edge("respond", END)

    return workflow.compile()


# ============================================================================
# EXPORT
# ============================================================================

companion_graph = create_companion_graph()

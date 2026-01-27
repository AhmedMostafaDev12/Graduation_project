"""
Recommendation Generator
========================

LLM-based recommendation generation using retrieved strategies and user profile.
Responsibilities:
- Build personalized LLM prompts
- Generate structured recommendations
- Parse and validate LLM output
- Handle fallback recommendations

Author: Sentry AI Team
Date: 2025
"""

import os
import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough

from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()


# ============================================================================
# OUTPUT MODELS
# ============================================================================

class RecommendationItem(BaseModel):
    """Single recommendation output"""
    title: str = Field(description="Short, action-oriented title")
    description: str = Field(description="Why this helps THIS specific user")
    action_steps: List[str] = Field(description="3-5 concrete steps to implement")
    expected_impact: str = Field(description="Expected outcome based on evidence")
    recommendation_type: str = Field(description="Category (e.g., time_blocking, delegation)")
    priority: str = Field(description="LOW, MEDIUM, HIGH, or CRITICAL")
    estimated_time_minutes: int = Field(description="Time to implement")
    evidence_source: Optional[str] = Field(default=None, description="Source of evidence")


class RecommendationEngineOutput(BaseModel):
    """Complete recommendation engine output
    الليل يا ليلي يعاتبني ويقول لي سلم على الليل 
    الحب لا تحلو نسائمه الا اذا غنى الهوى ليلى """
    recommendations: List[RecommendationItem]
    reasoning: str = Field(description="Why these specific recommendations were chosen")
    metadata: Dict = Field(default_factory=dict)


# ============================================================================
# GENERATOR CONFIGURATION
# ============================================================================

@dataclass
class GeneratorConfig:
    """Configuration for recommendation generator"""
    # LLM settings
    llm_model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.3
    max_output_tokens: int = 2048

    @classmethod
    def from_env(cls) -> 'GeneratorConfig':
        """Create config from environment variables"""
        return cls(
            llm_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
            max_output_tokens=int(os.getenv("LLM_MAX_TOKENS", "2048"))
        )


# ============================================================================
# RECOMMENDATION GENERATOR
# ============================================================================

class RecommendationGenerator:
    """
    LLM-based recommendation generator.

    Features:
    - Personalized prompt building
    - Structured output with validation
    - Context-aware recommendations
    - Fallback handling
    """

    def __init__(
        self,
        config: Optional[GeneratorConfig] = None,
        google_api_key: Optional[str] = None
    ):
        """
        Initialize recommendation generator.

        Args:
            config: Generator configuration (defaults to env-based config)
            google_api_key: Google API key (defaults to env variable)
        """
        self.config = config or GeneratorConfig.from_env()

        # Initialize LLM (Groq - cloud-based, fast inference)
        self.llm = ChatGroq(
            model=self.config.llm_model,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=self.config.temperature,
            max_tokens=self.config.max_output_tokens,
            model_kwargs={"response_format": {"type": "json_object"}}
        )

        # Initialize output parser
        self.output_parser = JsonOutputParser(pydantic_object=RecommendationEngineOutput)

    # ========================================================================
    # MAIN GENERATION
    # ========================================================================

    def generate_recommendations(
        self,
        user_profile_context: str,
        burnout_context: Dict,
        retrieved_strategies: str,
        num_recommendations: int = 3,
        calendar_events: Optional[List[Dict]] = None,
        task_list: Optional[List[Dict]] = None
    ) -> RecommendationEngineOutput:
        """
        Generate personalized recommendations using LLM.

        Args:
            user_profile_context: Formatted user profile string
            burnout_context: Extracted burnout context (from _extract_context)
            retrieved_strategies: Formatted strategies from RAG retrieval
            num_recommendations: Number of recommendations to generate
            calendar_events: Actual calendar events (for event-specific recommendations)
            task_list: Actual task list (for task-specific recommendations)

        Returns:
            RecommendationEngineOutput with recommendations
        """
        print(f"\n[GENERATE] Generating {num_recommendations} personalized recommendations...")

        # Build complete prompt
        prompt = self._build_llm_prompt(
            user_profile_context=user_profile_context,
            context=burnout_context,
            strategies=retrieved_strategies,
            num_recommendations=num_recommendations,
            calendar_events=calendar_events,
            task_list=task_list
        )

        # Generate recommendations
        output = self._generate_with_llm(prompt)

        print(f"[OK] Generated {len(output.recommendations)} recommendations")

        return output

    # ========================================================================
    # PROMPT BUILDING
    # ========================================================================

    def _build_llm_prompt(
        self,
        user_profile_context: str,
        context: Dict,
        strategies: str,
        num_recommendations: int,
        calendar_events: Optional[List[Dict]] = None,
        task_list: Optional[List[Dict]] = None
    ) -> str:
        """
        Build complete LLM prompt with all context.

        Note: user_profile_context already contains PREFERENCES and CONSTRAINTS
        from the CompleteProfileSchema.to_llm_context() method.
        The context dict contains burnout analysis data for dynamic content.
        """

        # Format burnout signals
        signals = context.get('burnout_signals', {})
        active_signals = [k for k, v in signals.items() if v]

        # Format calendar events section
        calendar_section = ""
        if calendar_events and len(calendar_events) > 0:
            calendar_section = "\nTODAY'S CALENDAR EVENTS:\n================================================\n"
            for i, event in enumerate(calendar_events, 1):
                start = event.get('start_time', 'Unknown')
                end = event.get('end_time', 'Unknown')
                title = event.get('title', 'Untitled')
                duration = event.get('duration_minutes', 0)

                # Build event line
                calendar_section += f"{i}. {start} - {end}: \"{title}\" ({duration} min)\n"

                # Add metadata
                metadata = []
                if event.get('is_optional'):
                    metadata.append("OPTIONAL - can decline")
                if event.get('is_recurring'):
                    metadata.append("Recurring")
                if event.get('attendees'):
                    metadata.append(f"Attendees: {len(event.get('attendees', []))} people")

                if metadata:
                    calendar_section += f"   → {' | '.join(metadata)}\n"

        # Format task list section
        task_section = ""
        if task_list and len(task_list) > 0:
            task_section = "\nCURRENT TASK LIST:\n================================================\n"
            for i, task in enumerate(task_list, 1):
                title = task.get('title', 'Untitled')
                status = task.get('status', 'Unknown')
                priority = task.get('priority', 'Unknown')
                due = task.get('due_date', 'No deadline')

                # Build task line
                task_section += f"{i}. \"{title}\"\n"
                task_section += f"   Status: {status} | Priority: {priority} | Due: {due}\n"

                # Add metadata
                metadata = []
                if task.get('can_delegate'):
                    metadata.append("CAN DELEGATE")
                if task.get('assigned_to'):
                    metadata.append(f"Currently assigned to: {task.get('assigned_to')}")
                if task.get('estimated_hours'):
                    metadata.append(f"Est. time: {task.get('estimated_hours')}h")

                if metadata:
                    task_section += f"   → {' | '.join(metadata)}\n"

        prompt = f"""
{user_profile_context}

CURRENT BURNOUT ANALYSIS:
================================================
Score: {context['burnout_score']} ({context['burnout_level']})
Baseline (healthy): {context['baseline_score']}
Deviation: {int(context['deviation']):+d} points {"[CRITICAL]" if abs(context['deviation']) > 30 else "[ELEVATED]" if abs(context['deviation']) > 15 else ""}

Status: {context['trend_direction']} trend, {context['days_in_level']} days in {context['burnout_level']}

PRIMARY ISSUES:
{chr(10).join('• ' + issue for issue in context.get('primary_issues', []))}

STRESS INDICATORS:
{chr(10).join('• ' + indicator for indicator in context.get('stress_indicators', []))}

{"BURNOUT SIGNALS DETECTED:" if active_signals else ""}
{chr(10).join('• ' + signal for signal in active_signals) if active_signals else ""}

{"KNOWN STRESS TRIGGERS:" if context.get('stress_triggers') else ""}
{chr(10).join('• ' + trigger for trigger in context.get('stress_triggers', [])) if context.get('stress_triggers') else ""}
{calendar_section}
{task_section}

ANALYSIS GUIDE - Connect Issues to Specific Events:
================================================
Based on the PRIMARY ISSUES and STRESS INDICATORS above, identify which specific calendar events or tasks are contributing to the burnout:

Example Analysis:
- If PRIMARY ISSUE is "Too many meetings" → Look at TODAY'S CALENDAR EVENTS and identify which meetings to cancel/delegate/reschedule
- If PRIMARY ISSUE is "Back-to-back meetings" → Look for consecutive meetings with < 5 min gap and suggest canceling the optional ones
- If PRIMARY ISSUE is "High task load" → Look at CURRENT TASK LIST for tasks that can be delegated (CAN DELEGATE flag) or postponed (low priority)
- If STRESS INDICATOR is "overwhelmed" → Look for High/Critical priority tasks due soon that can be delegated
- If STRESS TRIGGER is "back_to_back_meetings" → Identify the specific back-to-back meetings in the calendar

EVIDENCE-BASED STRATEGIES:
================================================
{strategies}

TASK:
================================================
Generate {num_recommendations} personalized, actionable recommendations to reduce this user's burnout.

**CRITICAL - EVENT-SPECIFIC RECOMMENDATIONS:**
You MUST analyze the actual calendar events and tasks listed above and make SPECIFIC recommendations.

Your recommendations should include BOTH:
A) **REMOVE/ADJUST**: Cancel/reschedule/delegate problematic events/tasks
B) **ADD**: Schedule refreshing activities (from Evidence-Based Strategies) into available time slots

DO NOT give generic advice like:
❌ "Reduce your meetings"
❌ "Delegate some tasks"
❌ "Take breaks"

INSTEAD, reference ACTUAL events, tasks, and TIME SLOTS:

REMOVE/ADJUST Examples:
✓ "Cancel your 3:30 PM 'Team Sync' meeting - it's optional and creates a back-to-back situation"
✓ "Delegate the 'Database Migration Script' task (Priority: High, Due: Tomorrow) to Alex from your team"
✓ "Move your '1:1 with Manager' from 4:30 PM to tomorrow morning"

ADD Examples (use Evidence-Based Strategies):
✓ "Block 11:30 AM - 12:00 PM for a 30-minute walk (between Sprint Planning and lunch)"
✓ "Schedule a 15-minute breathing exercise at 2:45 PM (before your afternoon meeting block)"
✓ "Add a 10-minute break at 3:25 PM (between Code Review and Team Sync)"
✓ "Reserve 4:30 PM - 5:30 PM tomorrow as focus time for deep work (instead of the 1:1 you moved)"

REQUIREMENTS FOR EACH RECOMMENDATION:
1. Must reference EXACT event/task title OR identify EXACT available time slots
2. Must include SPECIFIC times (e.g., "11:30 AM - 12:00 PM", "3:30 PM", "Due: Tomorrow")
3. Must provide SPECIFIC action (e.g., "Cancel X", "Delegate Y to Z", "Block 2:00-2:30 PM for walk")
4. Must explain WHY this specific change helps THIS user's specific situation
5. For ADD recommendations: Use strategies from Evidence-Based Strategies section (e.g., walks, meditation, breaks)

HOW TO ANALYZE:
- **REMOVE/ADJUST**: Look at TODAY'S CALENDAR EVENTS → identify optional meetings, back-to-back meetings, or tasks that can be delegated
- **ADD**: Look for GAPS in the calendar (time between meetings) where you can insert refreshing activities
  - Find gaps ≥ 15 minutes between meetings → suggest short breaks, breathing exercises
  - Find gaps ≥ 30 minutes → suggest walks, meditation, or focus time
  - Look at end of day (after last meeting) → suggest wind-down activities
- Match Evidence-Based Strategies (walks, meditation, breaks, etc.) to specific available time slots
- If you cancel a meeting, suggest what to do with that freed time (recovery activity or focus time)

CRITICAL REQUIREMENTS:
1. **Personalization (MUST RESPECT USER PROFILE)**:
   - Consider user's role, team size, and ability to delegate
   - **RESPECT ACTIVE CONSTRAINTS**: If user has constraints (deadlines, PTO blocks, delegation blocks),
     DO NOT suggest actions they cannot take during this period
   - **USE PREFERRED RECOMMENDATION TYPES**: Focus on types the user accepts/prefers
   - **AVOID DISMISSED TYPES**: Never suggest recommendation types the user has marked as "Avoids"
   - Match communication style (direct, supportive, data-driven, etc.)
   - Address THEIR specific issues and triggers from the analysis

2. **Actionability**:
   - Each recommendation must have 3-5 concrete, specific steps
   - Steps should be immediately implementable within their constraints
   - Include timing/scheduling details where relevant
   - Account for their typical workload and work hours

3. **Evidence-Based**:
   - Prioritize strategies from the evidence-based strategies above
   - Reference success rates and evidence levels when available
   - Explain WHY this will help THIS user specifically (connect to their situation)
   - Use evidence that aligns with their role and seniority level

4. **Prioritization**:
   - Higher priority for larger baseline deviations (>30 points = CRITICAL)
   - Address most severe issues first (from PRIMARY ISSUES section)
   - Consider urgency (days in current level, trend direction)
   - Factor in active burnout signals (emotional_exhaustion, overwhelm, etc.)

5. **Realism & Constraints**:
   - **CHECK CURRENT CONSTRAINTS**: If user cannot take PTO, don't suggest vacation
   - **CHECK DELEGATION ABILITY**: If user can't delegate or it's blocked, suggest alternatives
   - Account for current workload and team dynamics
   - Don't suggest what's impossible given their situation
   - Provide feasible alternatives for blocked actions

OUTPUT FORMAT:
Return a JSON object matching this schema:
{{
    "recommendations": [
        {{
            "title": "Brief, action-oriented title",
            "description": "Why this helps THIS user (reference their specific situation)",
            "action_steps": ["Step 1", "Step 2", "Step 3"],
            "expected_impact": "What they can expect (based on evidence)",
            "recommendation_type": "category (e.g., time_blocking, delegation, workload_reduction)",
            "priority": "LOW/MEDIUM/HIGH/CRITICAL",
            "estimated_time_minutes": 15,
            "evidence_source": "Reference to evidence or strategy used"
        }}
    ],
    "reasoning": "Brief explanation of why these specific recommendations were chosen for THIS user"
}}
"""

        return prompt

    # ========================================================================
    # LLM GENERATION
    # ========================================================================

    def _extract_json_from_text(self, text: str) -> dict:
        """
        Extract JSON from text that might be wrapped in markdown or have extra content.

        Args:
            text: Raw text that may contain JSON

        Returns:
            Parsed JSON dictionary
        """
        # Try to parse as-is first
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        # Try to remove markdown code blocks
        if '```' in text:
            # Find content between ``` markers
            parts = text.split('```')
            print(f"[DEBUG] Found {len(parts)} parts after splitting on ```")
            for i, part in enumerate(parts):
                # Skip the first part (before first ```) and look at content blocks
                if i > 0 and i % 2 == 1:  # Odd indices are inside code blocks
                    # Remove language identifier if present (e.g., "json\n")
                    content = re.sub(r'^[a-zA-Z]*\s*', '', part.strip())
                    print(f"[DEBUG] Trying to parse markdown block {i}, length: {len(content)}")
                    try:
                        result = json.loads(content)
                        print(f"[DEBUG] Successfully parsed JSON from markdown block!")
                        return result
                    except json.JSONDecodeError as e:
                        print(f"[DEBUG] Failed to parse markdown block {i}: {e}")
                        continue

        # Try to find JSON object by finding matching braces
        # Find the first { and try to parse from there
        start_idx = text.find('{')
        if start_idx != -1:
            # Try to find matching closing brace by counting braces
            brace_count = 0
            in_string = False
            escape_next = False

            for i in range(start_idx, len(text)):
                char = text[i]

                # Handle string escaping
                if escape_next:
                    escape_next = False
                    continue

                if char == '\\':
                    escape_next = True
                    continue

                # Track if we're inside a string
                if char == '"':
                    in_string = not in_string
                    continue

                # Only count braces outside of strings
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            # Found matching closing brace
                            potential_json = text[start_idx:i+1]
                            try:
                                return json.loads(potential_json)
                            except json.JSONDecodeError as e:
                                print(f"[DEBUG] JSON parse error: {e}")
                                print(f"[DEBUG] Attempted JSON: {potential_json[:300]}...")
                                break

        # If no JSON found, raise an error
        raise ValueError(f"Could not extract valid JSON from text: {text[:200]}...")

    def _generate_with_llm(self, prompt: str) -> RecommendationEngineOutput:
        """Generate recommendations using LLM"""
        try:
            print("[LLM] Generating recommendations with LLM...")

            # Create chain without output parser (we'll parse manually)
            chain = (
                {"prompt": RunnablePassthrough()}
                | PromptTemplate.from_template("{prompt}")
                | self.llm
            )

            # Generate
            response = chain.invoke(prompt)

            # Extract text content
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)

            print(f"[DEBUG] LLM Response (first 500 chars): {response_text[:500]}")

            # Extract and parse JSON
            result = self._extract_json_from_text(response_text)

            # Validate and return
            return RecommendationEngineOutput(**result)

        except Exception as e:
            print(f"[ERROR] Error generating recommendations: {e}")
            # Return fallback recommendations
            return self._get_fallback_recommendations()

    def _get_fallback_recommendations(self) -> RecommendationEngineOutput:
        """Fallback recommendations if LLM fails"""
        return RecommendationEngineOutput(
            recommendations=[
                RecommendationItem(
                    title="Take regular breaks",
                    description="Short breaks can reduce stress and improve focus",
                    action_steps=[
                        "Set a timer for every 60 minutes",
                        "Take a 5-minute break when timer goes off",
                        "Step away from your desk"
                    ],
                    expected_impact="Reduced stress and improved focus",
                    recommendation_type="breaks",
                    priority="MEDIUM",
                    estimated_time_minutes=5
                ),
                RecommendationItem(
                    title="Prioritize critical tasks",
                    description="Focus on high-impact work to reduce overwhelm",
                    action_steps=[
                        "List all pending tasks",
                        "Identify top 3 priorities for today",
                        "Defer or delegate remaining tasks"
                    ],
                    expected_impact="Reduced task overwhelm and increased effectiveness",
                    recommendation_type="prioritization",
                    priority="HIGH",
                    estimated_time_minutes=15
                ),
                RecommendationItem(
                    title="Set boundaries on meetings",
                    description="Reduce meeting load to create focus time",
                    action_steps=[
                        "Review calendar for next week",
                        "Decline optional meetings",
                        "Block 2-hour focus time blocks"
                    ],
                    expected_impact="More time for deep work and reduced context switching",
                    recommendation_type="time_management",
                    priority="MEDIUM",
                    estimated_time_minutes=10
                )
            ],
            reasoning="Fallback recommendations (LLM unavailable). These are general burnout prevention strategies.",
            metadata={"fallback": True}
        )


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def generate_recommendations_from_context(
    user_profile_context: str,
    burnout_context: Dict,
    retrieved_strategies: str,
    num_recommendations: int = 3,
    config: Optional[GeneratorConfig] = None
) -> RecommendationEngineOutput:
    """
    Convenience function to generate recommendations.

    Args:
        user_profile_context: Formatted user profile string
        burnout_context: Burnout context dictionary
        retrieved_strategies: Formatted strategies from RAG
        num_recommendations: Number of recommendations to generate
        config: Optional generator config

    Returns:
        RecommendationEngineOutput
    """
    generator = RecommendationGenerator(config=config)

    return generator.generate_recommendations(
        user_profile_context=user_profile_context,
        burnout_context=burnout_context,
        retrieved_strategies=retrieved_strategies,
        num_recommendations=num_recommendations
    )
# For usage examples, see: examples/complete_flow_example.py

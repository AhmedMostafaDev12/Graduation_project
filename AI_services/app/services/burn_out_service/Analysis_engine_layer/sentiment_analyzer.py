"""
Sentiment Analyzer - LLM-Powered Burnout Signal Detection
==========================================================

This module analyzes qualitative data (text) using Large Language Models (LLMs)
to detect stress, emotional exhaustion, and burnout signals.

Uses LangChain for:
- Google Gemini LLM support
- Structured output parsing with Pydantic
- Prompt templates
- Retry logic and error handling

Author: Sentry AI Team
Date: 2025
"""

from typing import List, Dict, Optional, Literal
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import json
import os
import sys
import io
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LangChain imports
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class QualitativeData:
    """
    Data class holding all text-based data from user activity.
    This data is analyzed by the LLM for sentiment and burnout signals.
    """
    meeting_transcripts: List[str] = field(default_factory=list)
    task_notes: List[str] = field(default_factory=list)
    user_check_ins: List[str] = field(default_factory=list)
    email_snippets: List[str] = field(default_factory=list)
    
    def has_data(self) -> bool:
        """Check if there's any text data to analyze"""
        return bool(
            self.meeting_transcripts or 
            self.task_notes or 
            self.user_check_ins or 
            self.email_snippets
        )
    
    def get_total_text_count(self) -> int:
        """Get total number of text items"""
        return (
            len(self.meeting_transcripts) + 
            len(self.task_notes) + 
            len(self.user_check_ins) + 
            len(self.email_snippets)
        )


class BurnoutSignals(BaseModel):
    """Specific burnout indicators detected in text"""
    emotional_exhaustion: bool = Field(
        description="Mentions of tiredness, drained, burned out, exhausted"
    )
    overwhelm: bool = Field(
        description="Feeling swamped, too much work, drowning in tasks"
    )
    sleep_concerns: bool = Field(
        description="Insomnia, can't sleep, tired all the time, sleep problems"
    )
    negative_outlook: bool = Field(
        description="Pessimism, hopelessness, 'what's the point', giving up"
    )
    health_concerns: bool = Field(
        description="Headaches, stress symptoms, anxiety, physical issues"
    )


class SentimentAnalysisResult(BaseModel):
    """
    Structured output from LLM sentiment analysis.
    Uses Pydantic for validation and type safety.
    """
    sentiment_score: float = Field(
        description="Overall sentiment score from -1.0 (very negative) to +1.0 (very positive)",
        ge=-1.0,
        le=1.0
    )
    
    stress_indicators: List[str] = Field(
        description="Specific phrases or words indicating stress",
        default_factory=list
    )
    
    burnout_signals: BurnoutSignals = Field(
        description="Specific burnout signals detected"
    )
    
    confidence: int = Field(
        description="Confidence level in the analysis (0-100)",
        ge=0,
        le=100
    )
    
    key_concerns: List[str] = Field(
        description="2-4 specific observations about user's mental state",
        default_factory=list
    )
    
    sentiment_adjustment: int = Field(
        description="Points to add to workload score (-20 to +20)",
        ge=-20,
        le=20
    )
    
    @field_validator('key_concerns')
    @classmethod
    def validate_concerns(cls, v):
        """Ensure we have 2-4 key concerns"""
        if len(v) > 4:
            return v[:4]
        return v
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "sentiment_score": self.sentiment_score,
            "stress_indicators": self.stress_indicators,
            "burnout_signals": self.burnout_signals.model_dump(),
            "confidence": self.confidence,
            "key_concerns": self.key_concerns,
            "sentiment_adjustment": self.sentiment_adjustment
        }


# ============================================================================
# LLM PROVIDER ENUM
# ============================================================================

class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OLLAMA = "ollama"


# ============================================================================
# SENTIMENT ANALYZER
# ============================================================================

class SentimentAnalyzer:
    """
    LLM-powered sentiment analyzer using LangChain.

    Supports Google Gemini LLM provider.

    Features:
    - Structured output with Pydantic validation
    - Automatic retry on failure
    - Comprehensive error handling
    - Configurable temperature and model
    """
    
    # System prompt for LLM
    SYSTEM_PROMPT = """You are a burnout detection expert and mental health analyst specializing in workplace wellness.

Your role is to analyze text data from users (meetings, tasks, messages) to identify:
- Overall emotional state and sentiment
- Signs of stress, anxiety, or emotional exhaustion
- Patterns indicating potential burnout
- Sleep or health concerns mentioned
- Changes in outlook or motivation

You provide objective, evidence-based analysis focused on helping users maintain mental wellbeing."""

    # Human prompt template
    HUMAN_PROMPT_TEMPLATE = """Analyze the following text data from a user collected over the last 7 days.

MEETING NOTES/TRANSCRIPTS:
{meeting_transcripts}

TASK DESCRIPTIONS/NOTES:
{task_notes}

USER CHECK-INS/MESSAGES:
{user_check_ins}

EMAIL SNIPPETS:
{email_snippets}

---

Perform a comprehensive sentiment and burnout risk analysis.

Provide your analysis in the following JSON format:

{{
  "sentiment_score": <float between -1.0 and 1.0>,
  "stress_indicators": [<list of specific phrases/words indicating stress>],
  "burnout_signals": {{
    "emotional_exhaustion": <true/false>,
    "overwhelm": <true/false>,
    "sleep_concerns": <true/false>,
    "negative_outlook": <true/false>,
    "health_concerns": <true/false>
  }},
  "confidence": <integer 0-100>,
  "key_concerns": [<2-4 specific observations>],
  "sentiment_adjustment": <integer -20 to +20>
}}

SCORING GUIDELINES:

1. sentiment_score:
   - -1.0 to -0.8: Very negative (severe stress/distress)
   - -0.79 to -0.5: Negative (clear stress indicators)
   - -0.49 to -0.2: Slightly negative (mild stress)
   - -0.19 to +0.19: Neutral
   - +0.2 to +1.0: Positive (healthy mindset)

2. stress_indicators:
   - Extract exact phrases showing stress (e.g., "feeling overwhelmed", "too much work")
   - Include frequency if mentioned multiple times

3. burnout_signals:
   - emotional_exhaustion: Look for "tired", "drained", "exhausted", "burned out"
   - overwhelm: Look for "too much", "drowning", "swamped", "can't keep up"
   - sleep_concerns: Look for "can't sleep", "insomnia", "tired all the time"
   - negative_outlook: Look for pessimism, hopelessness, cynicism
   - health_concerns: Look for headaches, anxiety, stress symptoms

4. confidence:
   - 90-100: Very clear signals, sufficient data
   - 70-89: Good indicators, moderate data
   - 50-69: Some signals, limited data
   - Below 50: Insufficient data for strong conclusion

5. key_concerns:
   - List 2-4 most important observations
   - Be specific and cite evidence from the text
   - Focus on actionable insights

6. sentiment_adjustment:
   - This adjusts the quantitative workload score
   - Negative sentiment = positive adjustment (makes burnout worse)
   - Guidelines:
     * Sentiment -0.8 to -1.0: +15 to +20 points
     * Sentiment -0.5 to -0.79: +10 to +14 points
     * Sentiment -0.2 to -0.49: +5 to +9 points
     * Sentiment -0.19 to +0.19: 0 to +4 points
     * Sentiment +0.2 to +1.0: -5 to 0 points

IMPORTANT: Return ONLY the JSON object, no additional text or formatting."""

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.OLLAMA,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.3,
        max_retries: int = 3
    ):
        """
        Initialize the Sentiment Analyzer.

        Args:
            provider: LLM provider to use (ollama/groq)
            api_key: GROQ_API_KEY from environment (for Groq)
            model_name: Specific model to use (defaults to llama-3.1-70b-versatile)
            temperature: LLM temperature (0.0-1.0, lower = more consistent)
            max_retries: Maximum retry attempts on failure
        """
        self.provider = provider
        self.temperature = temperature
        self.max_retries = max_retries

        # Initialize LLM based on provider
        self.llm = self._initialize_llm(provider, api_key, model_name)

        # Initialize prompt template
        self.prompt = self._create_prompt_template()

        # Initialize output parser
        self.output_parser = JsonOutputParser(pydantic_object=SentimentAnalysisResult)

        # Create the chain
        self.chain = self._create_chain()

    def _initialize_llm(
        self,
        provider: LLMProvider,
        api_key: Optional[str],
        model_name: Optional[str]
    ):
        """Initialize the LLM based on provider"""
        if provider == LLMProvider.OLLAMA:
            # Use Groq instead of Ollama (faster, cloud-based)
            import os
            default_model = "llama-3.1-70b-versatile"
            return ChatGroq(
                model=model_name or default_model,
                groq_api_key=api_key or os.getenv("GROQ_API_KEY"),
                temperature=self.temperature,
                max_tokens=2048,
                model_kwargs={"response_format": {"type": "json_object"}}
            )

        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """Create the prompt template"""
        system_message = SystemMessagePromptTemplate.from_template(self.SYSTEM_PROMPT)
        human_message = HumanMessagePromptTemplate.from_template(self.HUMAN_PROMPT_TEMPLATE)
        
        return ChatPromptTemplate.from_messages([system_message, human_message])
    
    def _create_chain(self):
        """Create the LangChain chain"""
        return (
            {"meeting_transcripts": lambda x: x["meeting_transcripts"],
             "task_notes": lambda x: x["task_notes"],
             "user_check_ins": lambda x: x["user_check_ins"],
             "email_snippets": lambda x: x["email_snippets"]}
            | self.prompt
            | self.llm
            | self.output_parser
        )
    
    def _format_text_list(self, items: List[str], default: str = "None") -> str:
        """Format list of text items for prompt"""
        if not items:
            return default
        return "\n".join(f"- {item}" for item in items)
    
    def analyze(self, data: QualitativeData) -> SentimentAnalysisResult:
        """
        Analyze qualitative data for sentiment and burnout signals.
        
        Args:
            data: QualitativeData object containing text from various sources
            
        Returns:
            SentimentAnalysisResult with complete analysis
            
        Raises:
            ValueError: If no data provided
            Exception: If LLM call fails after retries
        """
        # Validate input
        if not data.has_data():
            raise ValueError("No qualitative data provided for analysis")
        
        # Prepare input for chain
        chain_input = {
            "meeting_transcripts": self._format_text_list(data.meeting_transcripts),
            "task_notes": self._format_text_list(data.task_notes),
            "user_check_ins": self._format_text_list(data.user_check_ins),
            "email_snippets": self._format_text_list(data.email_snippets)
        }
        
        try:
            # Invoke the chain
            result = self.chain.invoke(chain_input)
            
            # Parse and validate result
            analysis = SentimentAnalysisResult(**result)
            
            return analysis
            
        except Exception as e:
            print(f"Error during sentiment analysis: {e}")
            
            # Return neutral/fallback result on error
            return self._get_fallback_result(data)
    
    def _get_fallback_result(self, data: QualitativeData) -> SentimentAnalysisResult:
        """
        Return a neutral fallback result if LLM fails.
        This ensures the system continues to function even if LLM is unavailable.
        """
        return SentimentAnalysisResult(
            sentiment_score=0.0,
            stress_indicators=[],
            burnout_signals=BurnoutSignals(
                emotional_exhaustion=False,
                overwhelm=False,
                sleep_concerns=False,
                negative_outlook=False,
                health_concerns=False
            ),
            confidence=0,
            key_concerns=["Unable to analyze sentiment - LLM service unavailable"],
            sentiment_adjustment=0
        )
    
    async def analyze_async(self, data: QualitativeData) -> SentimentAnalysisResult:
        """
        Async version of analyze for concurrent processing.
        
        Args:
            data: QualitativeData object containing text from various sources
            
        Returns:
            SentimentAnalysisResult with complete analysis
        """
        # Validate input
        if not data.has_data():
            raise ValueError("No qualitative data provided for analysis")
        
        # Prepare input for chain
        chain_input = {
            "meeting_transcripts": self._format_text_list(data.meeting_transcripts),
            "task_notes": self._format_text_list(data.task_notes),
            "user_check_ins": self._format_text_list(data.user_check_ins),
            "email_snippets": self._format_text_list(data.email_snippets)
        }
        
        try:
            # Invoke the chain asynchronously
            result = await self.chain.ainvoke(chain_input)
            
            # Parse and validate result
            analysis = SentimentAnalysisResult(**result)
            
            return analysis
            
        except Exception as e:
            print(f"Error during async sentiment analysis: {e}")
            return self._get_fallback_result(data)


# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of SentimentAnalyzer with different scenarios.

    NOTE: You need to set GOOGLE_API_KEY environment variable.
    """
    import asyncio

    # Configure stdout for UTF-8 encoding to handle emojis on Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 80)
    print("SENTIMENT ANALYZER - TEST SCENARIOS")
    print("=" * 80)

    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: GOOGLE_API_KEY not found in environment variables")
        print("Please set your API key to run the tests:")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        print("\nSkipping LLM tests, showing example output structure instead...")
        
        # Show example output structure
        example_result = SentimentAnalysisResult(
            sentiment_score=-0.65,
            stress_indicators=["overwhelmed", "exhausted", "too much work"],
            burnout_signals=BurnoutSignals(
                emotional_exhaustion=True,
                overwhelm=True,
                sleep_concerns=False,
                negative_outlook=False,
                health_concerns=True
            ),
            confidence=85,
            key_concerns=[
                "User mentions feeling overwhelmed 3 times",
                "Signs of emotional exhaustion in recent check-ins"
            ],
            sentiment_adjustment=15
        )
        
        print("\n📊 Example Output Structure:")
        print(json.dumps(example_result.to_dict(), indent=2))
        exit(0)
    
    # Initialize analyzer
    print("\n🔧 Initializing Sentiment Analyzer (Google Gemini)...")
    analyzer = SentimentAnalyzer(
        provider=LLMProvider.GOOGLE_GEMINI,
        temperature=0.3
    )
    print("✅ Analyzer ready!\n")
    
    # ========================================================================
    # SCENARIO 1: Positive/Healthy User
    # ========================================================================
    print("\n" + "=" * 80)
    print("📗 SCENARIO 1: Positive/Healthy User")
    print("=" * 80)
    
    positive_data = QualitativeData(
        meeting_transcripts=[
            "Great meeting today! Team is making excellent progress on the project.",
            "Productive discussion about the new features. Everyone is aligned."
        ],
        task_notes=[
            "Finished the report ahead of schedule",
            "Code review went smoothly",
            "Looking forward to implementing the new design"
        ],
        user_check_ins=[
            "Feeling good today, got a lot done",
            "Had a nice work-life balance this week"
        ]
    )
    
    print(f"📊 Analyzing {positive_data.get_total_text_count()} text items...")
    result = analyzer.analyze(positive_data)
    
    print(f"\n📈 Results:")
    print(f"  Sentiment Score: {result.sentiment_score:.2f}")
    print(f"  Confidence: {result.confidence}%")
    print(f"  Sentiment Adjustment: {result.sentiment_adjustment:+d} points")
    print(f"\n  Stress Indicators: {result.stress_indicators if result.stress_indicators else 'None detected'}")
    print(f"\n  Burnout Signals:")
    for signal, detected in result.burnout_signals.model_dump().items():
        status = "✓" if detected else "✗"
        print(f"    {status} {signal.replace('_', ' ').title()}")
    print(f"\n  Key Concerns:")
    for concern in result.key_concerns:
        print(f"    • {concern}")
    
    # ========================================================================
    # SCENARIO 2: Moderate Stress
    # ========================================================================
    print("\n" + "=" * 80)
    print("📙 SCENARIO 2: Moderate Stress")
    print("=" * 80)
    
    moderate_data = QualitativeData(
        meeting_transcripts=[
            "Meeting ran over time again. Feels like we're not making progress.",
            "Discussed the tight deadline. Team is concerned about capacity."
        ],
        task_notes=[
            "So many tasks piling up this week",
            "Need to finish this by Friday but also have 3 other priorities",
            "Feeling a bit overwhelmed with the workload"
        ],
        user_check_ins=[
            "Busy week ahead, lots on my plate",
            "Had to work late yesterday to catch up"
        ],
        email_snippets=[
            "Can you also handle this urgent request?",
            "Need this ASAP - client is waiting"
        ]
    )
    
    print(f"📊 Analyzing {moderate_data.get_total_text_count()} text items...")
    result = analyzer.analyze(moderate_data)
    
    print(f"\n📈 Results:")
    print(f"  Sentiment Score: {result.sentiment_score:.2f}")
    print(f"  Confidence: {result.confidence}%")
    print(f"  Sentiment Adjustment: {result.sentiment_adjustment:+d} points")
    print(f"\n  Stress Indicators: {', '.join(result.stress_indicators)}")
    print(f"\n  Burnout Signals:")
    for signal, detected in result.burnout_signals.model_dump().items():
        status = "✓" if detected else "✗"
        print(f"    {status} {signal.replace('_', ' ').title()}")
    print(f"\n  Key Concerns:")
    for concern in result.key_concerns:
        print(f"    • {concern}")
    
    # ========================================================================
    # SCENARIO 3: High Stress / Burnout Risk
    # ========================================================================
    print("\n" + "=" * 80)
    print("📕 SCENARIO 3: High Stress / Burnout Risk")
    print("=" * 80)
    
    high_stress_data = QualitativeData(
        meeting_transcripts=[
            "Another meeting that could have been an email. I'm exhausted.",
            "Difficult conversation with stakeholders. Feeling drained.",
            "Team is overloaded. Don't see how we'll meet these deadlines."
        ],
        task_notes=[
            "I can't keep up with all these tasks anymore",
            "Feeling completely overwhelmed and burned out",
            "Too much work, not enough time. Don't know where to start.",
            "Working on weekends just to stay afloat"
        ],
        user_check_ins=[
            "Feeling exhausted all the time lately",
            "Haven't been sleeping well, thinking about work all night",
            "Don't have energy for anything anymore",
            "Honestly questioning if this is worth it"
        ],
        email_snippets=[
            "Emergency: need this done tonight",
            "Why isn't this complete yet? Client is furious",
            "Can you work this weekend to finish?"
        ]
    )
    
    print(f"📊 Analyzing {high_stress_data.get_total_text_count()} text items...")
    result = analyzer.analyze(high_stress_data)
    
    print(f"\n📈 Results:")
    print(f"  Sentiment Score: {result.sentiment_score:.2f} ⚠️")
    print(f"  Confidence: {result.confidence}%")
    print(f"  Sentiment Adjustment: {result.sentiment_adjustment:+d} points ⚠️")
    print(f"\n  Stress Indicators: {', '.join(result.stress_indicators)}")
    print(f"\n  Burnout Signals:")
    for signal, detected in result.burnout_signals.model_dump().items():
        status = "⚠️ " if detected else "✗ "
        print(f"    {status} {signal.replace('_', ' ').title()}")
    print(f"\n  Key Concerns:")
    for concern in result.key_concerns:
        print(f"    🚨 {concern}")
    
    print("\n" + "=" * 80)
    print("Testing complete! ✅")
    print("=" * 80)
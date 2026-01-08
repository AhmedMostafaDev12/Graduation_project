"""
RAG-Based Recommendation Engine (Orchestrator)
===============================================

High-level orchestration of RAG retrieval and LLM generation.

This module coordinates:
1. RAG retrieval (via rag_retrieval.py)
2. LLM generation (via recommendation_generator.py)
3. Context extraction from burnout analysis
4. End-to-end recommendation flow

Architecture:
1. Extract context from burnout analysis
2. Retrieve relevant strategies from vector DB (RAG)
3. Generate personalized recommendations (LLM)

Author: Sentry AI Team
Date: 2025
"""

from typing import Dict, Optional

# Import RAG retrieval service
from .rag_retrieval import (
    RAGRetrievalService,
    RAGConfig
)

# Import recommendation generator
from .recommendation_generator import (
    RecommendationGenerator,
    RecommendationEngineOutput,
    GeneratorConfig
)


# ============================================================================
# RECOMMENDATION ENGINE (ORCHESTRATOR)
# ============================================================================

class RecommendationEngine:
    """
    High-level orchestrator for recommendation generation.

    Coordinates:
    - Context extraction from burnout analysis
    - RAG-based strategy retrieval
    - LLM-based recommendation generation

    Usage:
        engine = RecommendationEngine()
        output = engine.generate_recommendations(
            burnout_analysis=analysis_result,
            user_profile_context=profile_text,
            learned_patterns=patterns
        )
    """

    def __init__(
        self,
        rag_config: Optional[RAGConfig] = None,
        generator_config: Optional[GeneratorConfig] = None,
        ollama_model: Optional[str] = None
    ):
        """
        Initialize recommendation engine orchestrator.

        Args:
            rag_config: RAG retrieval configuration (uses VECTOR_DB_URL from .env)
            generator_config: LLM generator configuration
            ollama_model: Ollama model name (defaults to llama3.1:8b from env)
        """
        # Initialize RAG retrieval service (uses VECTOR_DB_URL from .env)
        self.rag_service = RAGRetrievalService(
            config=rag_config or RAGConfig.from_env()
        )

        # Initialize recommendation generator (uses Ollama)
        self.generator = RecommendationGenerator(
            config=generator_config,
            google_api_key=ollama_model  # Parameter name kept for compatibility, but uses Ollama
        )

    # ========================================================================
    # MAIN RECOMMENDATION GENERATION
    # ========================================================================

    def generate_recommendations(
        self,
        burnout_analysis: Dict,
        user_profile_context: str,
        learned_patterns: Optional[Dict] = None,
        num_recommendations: int = 3,
        calendar_events: Optional[list] = None,
        task_list: Optional[list] = None
    ) -> RecommendationEngineOutput:
        """
        Generate personalized recommendations using RAG + LLM.

        Args:
            burnout_analysis: Result from integration.analyze_user_burnout()
            user_profile_context: Formatted profile from result['user_profile']
                                 (already contains preferences and constraints)
            learned_patterns: Learned patterns from result['learned_patterns']
            num_recommendations: Number of recommendations to generate
            calendar_events: List of actual calendar events for event-specific recommendations
            task_list: List of actual tasks for task-specific recommendations

        Returns:
            RecommendationEngineOutput with recommendations
        """
        # Validate inputs
        if not burnout_analysis or not isinstance(burnout_analysis, dict):
            raise ValueError("burnout_analysis must be a non-empty dictionary")

        if not user_profile_context or not isinstance(user_profile_context, str):
            raise ValueError("user_profile_context must be a non-empty string")

        print(f"\n[START] Starting recommendation generation pipeline...")

        try:
            # Step 1: Extract context from burnout analysis
            print("\n[STEP 1] Extracting context...")
            context = self._extract_context(burnout_analysis, learned_patterns)

            # Step 2: Build retrieval query and retrieve strategies (RAG)
            print("\n[STEP 2] Retrieving strategies from vector database...")
            retrieval_query = self.rag_service.build_retrieval_query(context)
            retrieved_docs = self.rag_service.retrieve_strategies(retrieval_query)

            if not retrieved_docs:
                print("\n[WARNING] No strategies retrieved from vector database")
                print("          Make sure populate_strategies.py has been run")

            formatted_strategies = self.rag_service.format_retrieved_strategies(retrieved_docs)

            # Step 3: Generate recommendations (LLM)
            print("\n[STEP 3] Generating personalized recommendations...")
            output = self.generator.generate_recommendations(
                user_profile_context=user_profile_context,
                burnout_context=context,
                retrieved_strategies=formatted_strategies,
                num_recommendations=num_recommendations,
                calendar_events=calendar_events,
                task_list=task_list
            )

            print(f"\n[OK] Pipeline complete! Generated {len(output.recommendations)} recommendations")

            return output

        except Exception as e:
            print(f"\n[ERROR] Recommendation generation failed: {str(e)}")
            raise

    # ========================================================================
    # CONTEXT EXTRACTION
    # ========================================================================

    def _extract_context(
        self,
        burnout_analysis: Dict,
        learned_patterns: Optional[Dict]
    ) -> Dict:
        """
        Extract burnout analysis context for retrieval and generation.

        Note: User preferences and constraints are already in user_profile_context string.
        This method only extracts burnout-specific metrics and patterns.

        Args:
            burnout_analysis: Burnout analysis result
            learned_patterns: Learned behavioral patterns

        Returns:
            Context dictionary with burnout metrics and patterns
        """
        burnout = burnout_analysis.get('burnout', {})
        insights = burnout.get('insights', {})

        # Calculate baseline deviation with None handling
        current_score = burnout.get('final_score', 0)

        # Handle case where learned_patterns or baseline_score is None
        if learned_patterns and learned_patterns.get('baseline_score') is not None:
            baseline = learned_patterns.get('baseline_score')
        else:
            baseline = 40  # Default baseline if no learning data yet

        deviation = current_score - baseline if baseline is not None else 0

        # Handle missing or None values in insights
        primary_issues = insights.get('primary_issues') if insights.get('primary_issues') else []
        stress_indicators = insights.get('stress_indicators') if insights.get('stress_indicators') else []
        burnout_signals = insights.get('burnout_signals') if insights.get('burnout_signals') else {}

        # Handle missing or None values in patterns
        stress_triggers = []
        workload_trend = 'unknown'
        if learned_patterns:
            stress_triggers = learned_patterns.get('stress_triggers') if learned_patterns.get('stress_triggers') else []
            workload_trend = learned_patterns.get('workload_trend') if learned_patterns.get('workload_trend') else 'unknown'

        # Handle missing trend data
        trend_data = burnout.get('trend', {})
        trend_direction = trend_data.get('trend_direction') if trend_data and trend_data.get('trend_direction') else 'unknown'
        days_in_level = trend_data.get('days_in_current_level') if trend_data and trend_data.get('days_in_current_level') is not None else 0

        # Handle missing alert triggers
        alert_triggers = burnout.get('alert_triggers', {})
        alert_priority = alert_triggers.get('alert_priority') if alert_triggers and alert_triggers.get('alert_priority') else 'MEDIUM'

        context = {
            # Core metrics
            'burnout_score': current_score,
            'burnout_level': burnout.get('level', 'UNKNOWN'),
            'baseline_score': baseline,
            'deviation': deviation,

            # Issues
            'primary_issues': primary_issues,
            'stress_indicators': stress_indicators,
            'burnout_signals': burnout_signals,

            # Patterns
            'stress_triggers': stress_triggers,
            'workload_trend': workload_trend,

            # Trend
            'trend_direction': trend_direction,
            'days_in_level': days_in_level,

            # Alert priority
            'alert_priority': alert_priority
        }

        return context

    # ========================================================================
    # VECTOR STORE MANAGEMENT (DELEGATED TO RAG SERVICE)
    # ========================================================================

    def add_strategy(
        self,
        title: str,
        content: str,
        category: str,
        metadata: Optional[Dict] = None
    ):
        """Add a new strategy to vector store"""
        self.rag_service.add_strategy(title, content, category, metadata)

    def add_strategies_bulk(self, strategies: list):
        """Add multiple strategies at once"""
        self.rag_service.add_strategies_bulk(strategies)


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def generate_recommendations_from_analysis(
    analysis_result: Dict,
    rag_config: Optional[RAGConfig] = None,
    generator_config: Optional[GeneratorConfig] = None
) -> RecommendationEngineOutput:
    """
    Convenience function to generate recommendations from analysis result.

    Usage:
        result = integration.complete_daily_flow(user_id, metrics, qualitative)
        recommendations = generate_recommendations_from_analysis(result)

    Args:
        analysis_result: Result from integration.complete_daily_flow()
                        Must contain 'user_profile' (formatted string) and 'burnout' data
        rag_config: Optional RAG config
        generator_config: Optional generator config

    Returns:
        RecommendationEngineOutput
    """
    engine = RecommendationEngine(
        rag_config=rag_config,
        generator_config=generator_config
    )

    return engine.generate_recommendations(
        burnout_analysis=analysis_result,
        user_profile_context=analysis_result.get('user_profile', ''),
        learned_patterns=analysis_result.get('learned_patterns')
    )



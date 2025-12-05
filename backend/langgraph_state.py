"""
LangGraph State Model - Autonomous Agent State
Enables ReAct reasoning loop with self-correction and learning
"""

from typing import TypedDict, Optional, List, Dict, Any, Literal
from datetime import datetime
from models import (
    ResearchOutput,
    ContentStrategy,
    CreativeOutput,
    OrchestrationOutput,
    BusinessContext
)


class ThoughtAction(TypedDict):
    """Single thought-action-observation in ReAct loop"""
    step: int
    timestamp: datetime
    thought: str  # What should I do next?
    action: str  # Which tool to use (research, strategy, creative, evaluate, learn)
    action_input: Dict[str, Any]  # Parameters for the action
    observation: str  # Result of the action
    quality_score: float  # 0-1, quality of output


class CampaignState(TypedDict):
    """
    LangGraph state for autonomous campaign generation

    This replaces the fixed sequential pipeline with a dynamic reasoning loop:
    - Master reasoner decides next actions
    - Agents are tools that can be called multiple times
    - Quality evaluation triggers self-correction
    - Learning from past campaigns informs strategy
    """

    # Core inputs
    campaign_id: str
    business_url: str
    competitor_urls: Optional[List[str]]
    goal: str  # High-level goal (e.g., "Generate engaging 7-day social campaign")

    # ReAct loop tracking
    scratchpad: List[ThoughtAction]  # Full thought/action/observation history
    current_step: int
    max_iterations: int

    # Agent outputs (built incrementally)
    research: Optional[ResearchOutput]
    strategy: Optional[ContentStrategy]
    creative: Optional[CreativeOutput]
    orchestration: Optional[OrchestrationOutput]

    # Quality and learning
    quality_scores: Dict[str, float]  # {agent_name: score}
    quality_threshold: float  # Minimum quality to proceed (0.7 default)
    past_learnings: List[Dict[str, Any]]  # Retrieved from RedisVL

    # Control flow
    next_action: Optional[str]  # Next action decided by reasoner
    should_regenerate: bool  # True if quality below threshold
    regenerate_agent: Optional[str]  # Which agent to regenerate
    iterations: int  # Current iteration count

    # Status
    status: Literal[
        "reasoning",      # Master reasoner deciding next action
        "researching",    # Research agent running
        "strategizing",   # Strategy agent running
        "creating",       # Creative agent running
        "evaluating",     # Quality evaluation running
        "regenerating",   # Regenerating low-quality output
        "orchestrating",  # Final orchestration
        "learning",       # Storing learnings
        "completed",      # Successfully completed
        "failed"          # Failed with error
    ]
    error_message: Optional[str]

    # Metadata
    created_at: datetime
    completed_at: Optional[datetime]


# Initial state factory
def create_initial_state(
    campaign_id: str,
    business_url: str,
    competitor_urls: Optional[List[str]] = None,
    goal: str = "Generate engaging 7-day social media campaign",
    max_iterations: int = 15,
    quality_threshold: float = 0.7
) -> CampaignState:
    """Create initial campaign state for LangGraph"""
    return CampaignState(
        campaign_id=campaign_id,
        business_url=business_url,
        competitor_urls=competitor_urls,
        goal=goal,
        scratchpad=[],
        current_step=0,
        max_iterations=max_iterations,
        research=None,
        strategy=None,
        creative=None,
        orchestration=None,
        quality_scores={},
        quality_threshold=quality_threshold,
        past_learnings=[],
        next_action=None,
        should_regenerate=False,
        regenerate_agent=None,
        iterations=0,
        status="reasoning",
        error_message=None,
        created_at=datetime.now(),
        completed_at=None
    )

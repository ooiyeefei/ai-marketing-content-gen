"""
LangGraph Autonomous Orchestrator
Replaces fixed pipeline with ReAct reasoning loop
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

from langgraph.graph import StateGraph, END
from langgraph_state import CampaignState, ThoughtAction, create_initial_state

from services.gemini_service import get_gemini_service
from services.redis_service import get_redis_service
from agents.research_agent import get_research_agent
from agents.strategy_agent import get_strategy_agent
from agents.creative_agent import get_creative_agent
from agents.orchestration_agent import get_orchestration_agent

logger = logging.getLogger(__name__)


class AutonomousOrchestrator:
    """
    Autonomous multi-agent orchestrator using LangGraph

    Key Features:
    1. ReAct Loop: Reason → Act → Observe → Learn
    2. Dynamic Routing: Master reasoner decides next actions
    3. Quality Evaluation: Self-correction when quality is low
    4. Learning Integration: Uses past campaign insights from RedisVL
    5. Adaptive Strategy: Changes approach based on observations
    """

    def __init__(self):
        self.gemini = get_gemini_service()
        self.redis = get_redis_service()
        self.research_agent = get_research_agent()
        self.strategy_agent = get_strategy_agent()
        self.creative_agent = get_creative_agent()
        self.orchestration_agent = get_orchestration_agent()

        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()

        logger.info("✅ Autonomous orchestrator initialized with LangGraph")

    def _build_workflow(self) -> StateGraph:
        """Build LangGraph state machine with conditional routing"""
        workflow = StateGraph(CampaignState)

        # Add nodes
        workflow.add_node("master_reasoner", self.master_reasoner_node)
        workflow.add_node("retrieve_learnings", self.retrieve_learnings_node)
        workflow.add_node("research", self.research_tool_node)
        workflow.add_node("strategy", self.strategy_tool_node)
        workflow.add_node("creative", self.creative_tool_node)
        workflow.add_node("orchestrate", self.orchestrate_tool_node)
        workflow.add_node("evaluate_quality", self.evaluate_quality_node)
        workflow.add_node("store_learnings", self.store_learnings_node)

        # Set entry point
        workflow.set_entry_point("retrieve_learnings")

        # Add conditional edges (autonomous routing)
        workflow.add_edge("retrieve_learnings", "master_reasoner")
        workflow.add_conditional_edges(
            "master_reasoner",
            self.route_next_action,
            {
                "research": "research",
                "strategy": "strategy",
                "creative": "creative",
                "orchestrate": "orchestrate",
                "evaluate": "evaluate_quality",
                "learn": "store_learnings",
                "end": END
            }
        )

        # Tool nodes loop back to reasoner
        workflow.add_edge("research", "master_reasoner")
        workflow.add_edge("strategy", "master_reasoner")
        workflow.add_edge("creative", "master_reasoner")
        workflow.add_edge("orchestrate", "master_reasoner")

        # Quality evaluation can trigger regeneration
        workflow.add_conditional_edges(
            "evaluate_quality",
            self.route_after_evaluation,
            {
                "regenerate_strategy": "strategy",
                "regenerate_creative": "creative",
                "continue": "master_reasoner"
            }
        )

        # Store learnings and end
        workflow.add_edge("store_learnings", END)

        return workflow

    async def run(self, campaign_id: str, business_url: str, competitor_urls: Optional[list] = None) -> CampaignState:
        """
        Run autonomous campaign generation

        This replaces the old fixed pipeline with dynamic reasoning:
        - OLD: research → strategy → creative → orchestrate (always same steps)
        - NEW: reasoner decides which action to take next based on observations
        """
        logger.info(f"🤖 Starting autonomous campaign generation: {campaign_id}")

        try:
            # Create initial state
            initial_state = create_initial_state(
                campaign_id=campaign_id,
                business_url=business_url,
                competitor_urls=competitor_urls
            )

            # Run LangGraph workflow
            final_state = await self.app.ainvoke(initial_state)

            logger.info(f"✅ Autonomous campaign completed: {campaign_id}")
            return final_state

        except Exception as e:
            logger.error(f"❌ Autonomous campaign failed: {e}", exc_info=True)
            raise

    # ============================================
    # NODES: ReAct Loop Components
    # ============================================

    async def retrieve_learnings_node(self, state: CampaignState) -> Dict[str, Any]:
        """Retrieve relevant learnings from past campaigns before reasoning"""
        logger.info("📚 Retrieving past campaign learnings...")

        try:
            # Get research data to understand industry
            research = state.get("research")
            if research and research.business_context:
                industry = research.business_context.industry
                query_text = f"{research.business_context.business_name} {research.business_context.description}"
            else:
                # No research yet, use business URL as query
                industry = None
                query_text = state["business_url"]

            # Get embedding for query
            query_embedding = self.gemini.get_embedding(query_text)

            # Retrieve relevant learnings from RedisVL
            past_learnings = self.redis.retrieve_learnings(
                query_embedding=query_embedding,
                industry=industry,
                min_performance=0.5,  # Only use learnings from decent campaigns
                top_k=5
            )

            logger.info(f"✅ Retrieved {len(past_learnings)} past learnings")

            return {
                "past_learnings": past_learnings
            }

        except Exception as e:
            logger.warning(f"Failed to retrieve learnings: {e}")
            return {"past_learnings": []}

    async def master_reasoner_node(self, state: CampaignState) -> Dict[str, Any]:
        """
        Master reasoning node - the brain of the autonomous system

        Decides:
        1. What action to take next?
        2. Is current quality acceptable?
        3. Should we regenerate any outputs?
        4. Are we done?
        """
        logger.info(f"🧠 Master reasoner (iteration {state['iterations']})")

        # Check iteration limit
        if state["iterations"] >= state["max_iterations"]:
            logger.warning("⚠️  Max iterations reached, ending")
            return {
                "next_action": "end",
                "status": "completed",
                "completed_at": datetime.now()
            }

        # Build reasoning prompt with full context
        reasoning_prompt = self._build_reasoning_prompt(state)

        # Use Gemini to reason about next action
        system_prompt = """You are a master reasoning agent for social media campaign generation.
Your role is to analyze the current state and decide the NEXT SINGLE ACTION to take.

Available actions:
- research: Gather business context, products, competitors
- strategy: Generate 7-day content strategy
- creative: Generate captions and images for each day
- orchestrate: Publish to Sanity CMS
- evaluate: Check quality of outputs
- learn: Store learnings for future campaigns
- end: Complete the workflow

Rules:
1. Only choose actions where previous steps are complete
2. If quality_score < 0.7, recommend regeneration
3. Follow logical order but adapt based on observations
4. Keep track of what's been done vs what's needed

Respond with JSON:
{
    "thought": "What should I do next and why?",
    "action": "research|strategy|creative|orchestrate|evaluate|learn|end",
    "reasoning": "Why this action makes sense now",
    "confidence": 0.0-1.0
}"""

        try:
            response_text = self.gemini.generate(
                prompt=reasoning_prompt,
                system=system_prompt,
                temperature=0.3,  # Lower temperature for more consistent reasoning
                json_mode=True
            )

            # Parse JSON response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()

            decision = json.loads(response_text)

            logger.info(f"💭 Thought: {decision['thought']}")
            logger.info(f"🎯 Action: {decision['action']}")

            # Create thought-action record
            thought_action = ThoughtAction(
                step=state["iterations"] + 1,
                timestamp=datetime.now(),
                thought=decision["thought"],
                action=decision["action"],
                action_input={},
                observation="",  # Will be filled after action
                quality_score=decision.get("confidence", 0.8)
            )

            # Update state
            new_scratchpad = state["scratchpad"] + [thought_action]

            return {
                "scratchpad": new_scratchpad,
                "next_action": decision["action"],
                "current_step": state["iterations"] + 1,
                "iterations": state["iterations"] + 1,
                "status": "reasoning"
            }

        except Exception as e:
            logger.error(f"Reasoning error: {e}", exc_info=True)
            # Fallback to logical progression
            return self._fallback_reasoning(state)

    def _build_reasoning_prompt(self, state: CampaignState) -> str:
        """Build comprehensive reasoning prompt with full context"""

        prompt_parts = [
            f"Goal: {state['goal']}",
            f"Business URL: {state['business_url']}",
            f"Current Iteration: {state['iterations']}/{state['max_iterations']}",
            f"",
            "Current State:"
        ]

        # Add completion status
        prompt_parts.append(f"- Research: {'✅ Complete' if state.get('research') else '❌ Not done'}")
        prompt_parts.append(f"- Strategy: {'✅ Complete' if state.get('strategy') else '❌ Not done'}")
        prompt_parts.append(f"- Creative: {'✅ Complete' if state.get('creative') else '❌ Not done'}")
        prompt_parts.append(f"- Orchestration: {'✅ Complete' if state.get('orchestration') else '❌ Not done'}")

        # Add quality scores if any
        if state.get("quality_scores"):
            prompt_parts.append("\nQuality Scores:")
            for agent, score in state["quality_scores"].items():
                status = "✅ Good" if score >= state["quality_threshold"] else "⚠️  Needs improvement"
                prompt_parts.append(f"- {agent}: {score:.2f} {status}")

        # Add recent thoughts
        if state.get("scratchpad"):
            prompt_parts.append("\nRecent Actions:")
            for ta in state["scratchpad"][-3:]:  # Last 3 actions
                prompt_parts.append(f"- Step {ta['step']}: {ta['action']} - {ta['observation'][:100]}")

        # Add past learnings if any
        if state.get("past_learnings"):
            prompt_parts.append(f"\nPast Learnings: {len(state['past_learnings'])} relevant insights available")

        prompt_parts.append("\nWhat should be the next action?")

        return "\n".join(prompt_parts)

    def _fallback_reasoning(self, state: CampaignState) -> Dict[str, Any]:
        """Fallback to logical progression if reasoning fails"""
        logger.warning("Using fallback reasoning logic")

        if not state.get("research"):
            next_action = "research"
        elif not state.get("strategy"):
            next_action = "strategy"
        elif not state.get("creative"):
            next_action = "creative"
        elif not state.get("orchestration"):
            next_action = "orchestrate"
        else:
            next_action = "end"

        return {
            "next_action": next_action,
            "iterations": state["iterations"] + 1
        }

    # ============================================
    # TOOL NODES: Wrap existing agents
    # ============================================

    async def research_tool_node(self, state: CampaignState) -> Dict[str, Any]:
        """Research tool - wraps research agent"""
        logger.info("🔍 Executing research agent...")

        try:
            research = await self.research_agent.research(
                business_url=state["business_url"],
                competitor_urls=state.get("competitor_urls")
            )

            # Update scratchpad with observation
            last_thought = state["scratchpad"][-1]
            last_thought["observation"] = f"Research complete: Found {len(research.product_images)} product images, {research.business_context.business_name} in {research.business_context.industry}"

            logger.info("✅ Research complete")

            return {
                "research": research,
                "status": "researching",
                "scratchpad": state["scratchpad"][:-1] + [last_thought]
            }

        except Exception as e:
            logger.error(f"Research failed: {e}")
            return {
                "error_message": str(e),
                "status": "failed"
            }

    async def strategy_tool_node(self, state: CampaignState) -> Dict[str, Any]:
        """Strategy tool - wraps strategy agent"""
        logger.info("📋 Executing strategy agent...")

        if not state.get("research"):
            logger.warning("Cannot create strategy without research")
            return {"status": "reasoning"}

        try:
            strategy = await self.strategy_agent.create_strategy(
                research_output=state["research"],  # Fixed: use research_output
                campaign_id=state["campaign_id"]
            )

            # Update scratchpad
            last_thought = state["scratchpad"][-1]
            last_thought["observation"] = f"Strategy complete: Created {len(strategy.days)}-day content plan"

            logger.info("✅ Strategy complete")

            return {
                "strategy": strategy,
                "status": "strategizing",
                "scratchpad": state["scratchpad"][:-1] + [last_thought]
            }

        except Exception as e:
            logger.error(f"Strategy failed: {e}")
            return {
                "error_message": str(e),
                "status": "failed"
            }

    async def creative_tool_node(self, state: CampaignState) -> Dict[str, Any]:
        """Creative tool - wraps creative agent"""
        logger.info("🎨 Executing creative agent...")

        if not state.get("strategy") or not state.get("research"):
            logger.warning("Cannot create content without strategy and research")
            return {"status": "reasoning"}

        try:
            creative = await self.creative_agent.create_content(
                strategy=state["strategy"],
                product_images=state["research"].product_images,
                campaign_id=state["campaign_id"]
            )

            # Update scratchpad
            last_thought = state["scratchpad"][-1]
            last_thought["observation"] = f"Creative complete: Generated {creative.total_images_generated} images, {creative.total_videos_generated} videos"

            logger.info("✅ Creative complete")

            return {
                "creative": creative,
                "status": "creating",
                "scratchpad": state["scratchpad"][:-1] + [last_thought]
            }

        except Exception as e:
            logger.error(f"Creative failed: {e}")
            return {
                "error_message": str(e),
                "status": "failed"
            }

    async def orchestrate_tool_node(self, state: CampaignState) -> Dict[str, Any]:
        """Orchestrate tool - wraps orchestration agent"""
        logger.info("📤 Executing orchestration agent...")

        if not state.get("creative"):
            logger.warning("Cannot orchestrate without creative content")
            return {"status": "reasoning"}

        try:
            orchestration = await self.orchestration_agent.orchestrate(
                creative=state["creative"],
                campaign_id=state["campaign_id"]
            )

            # Update scratchpad
            last_thought = state["scratchpad"][-1]
            last_thought["observation"] = f"Orchestration complete: Published {len(orchestration.published_content_ids)} posts to Sanity"

            logger.info("✅ Orchestration complete")

            return {
                "orchestration": orchestration,
                "status": "orchestrating",
                "scratchpad": state["scratchpad"][:-1] + [last_thought]
            }

        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            return {
                "error_message": str(e),
                "status": "failed"
            }

    async def evaluate_quality_node(self, state: CampaignState) -> Dict[str, Any]:
        """Evaluate quality of generated content"""
        logger.info("🔍 Evaluating output quality...")

        quality_scores = {}

        # Evaluate strategy quality
        if state.get("strategy"):
            strategy_score = self._evaluate_strategy_quality(state["strategy"])
            quality_scores["strategy"] = strategy_score

        # Evaluate creative quality
        if state.get("creative"):
            creative_score = self._evaluate_creative_quality(state["creative"])
            quality_scores["creative"] = creative_score

        # Check if regeneration needed
        should_regenerate = False
        regenerate_agent = None

        for agent, score in quality_scores.items():
            if score < state["quality_threshold"]:
                should_regenerate = True
                regenerate_agent = agent
                logger.warning(f"⚠️  {agent} quality below threshold: {score:.2f} < {state['quality_threshold']}")
                break

        logger.info(f"Quality scores: {quality_scores}")

        return {
            "quality_scores": quality_scores,
            "should_regenerate": should_regenerate,
            "regenerate_agent": regenerate_agent,
            "status": "evaluating"
        }

    def _evaluate_strategy_quality(self, strategy) -> float:
        """Evaluate strategy quality (simple heuristics for now)"""
        score = 0.5  # Base score

        # Check if we have content for all days
        if len(strategy.days) == 7:
            score += 0.3

        # Check if days have good variety
        content_types = set(day.content_type for day in strategy.days)
        if len(content_types) > 1:
            score += 0.2

        return min(score, 1.0)

    def _evaluate_creative_quality(self, creative) -> float:
        """Evaluate creative quality"""
        score = 0.5  # Base score

        # Check if images were generated
        if creative.total_images_generated > 0:
            score += 0.3

        # Check if captions exist
        has_captions = all(day.caption for day in creative.days)
        if has_captions:
            score += 0.2

        return min(score, 1.0)

    async def store_learnings_node(self, state: CampaignState) -> Dict[str, Any]:
        """Store learnings from this campaign for future use"""
        logger.info("💾 Storing campaign learnings...")

        try:
            # Generate learning analysis with Gemini
            if state.get("research") and state.get("strategy") and state.get("creative"):

                analysis_prompt = f"""Analyze this social media campaign and extract key learnings for future campaigns:

Business: {state['research'].business_context.business_name}
Industry: {state['research'].business_context.industry}
Strategy: {len(state['strategy'].days)} days, themes: {', '.join([d.theme for d in state['strategy'].days[:3]])}
Content: {state['creative'].total_images_generated} images, {state['creative'].total_videos_generated} videos
Quality Scores: {state.get('quality_scores', {})}

What worked well? What could be improved? What insights can help future campaigns in this industry?
Respond in 2-3 sentences."""

                learning_text = self.gemini.generate(
                    prompt=analysis_prompt,
                    temperature=0.5
                )

                # Get embedding
                learning_embedding = self.gemini.get_embedding(learning_text)

                # Store in Redis
                self.redis.store_learning(
                    campaign_id=state["campaign_id"],
                    industry=state['research'].business_context.industry,
                    learning_text=learning_text,
                    embedding=learning_embedding,
                    performance_score=0.7,  # Default, will be updated with real metrics later
                    metadata={
                        "business_name": state['research'].business_context.business_name,
                        "days": len(state['strategy'].days),
                        "images": state['creative'].total_images_generated,
                        "videos": state['creative'].total_videos_generated
                    }
                )

                logger.info(f"✅ Learnings stored: {learning_text[:100]}...")
            else:
                logger.warning("⚠️  Incomplete campaign, skipping learning storage")

            return {
                "status": "completed",
                "completed_at": datetime.now()
            }

        except Exception as e:
            logger.error(f"Failed to store learnings: {e}")
            return {"status": "completed", "completed_at": datetime.now()}

    # ============================================
    # ROUTING FUNCTIONS: Conditional edges
    # ============================================

    def route_next_action(self, state: CampaignState) -> str:
        """Route to next node based on reasoner's decision"""
        next_action = state.get("next_action", "end")
        logger.info(f"🔀 Routing to: {next_action}")
        return next_action

    def route_after_evaluation(self, state: CampaignState) -> str:
        """Route after quality evaluation"""
        if state.get("should_regenerate"):
            agent = state.get("regenerate_agent")
            logger.info(f"🔄 Regenerating {agent} due to low quality")
            return f"regenerate_{agent}"
        else:
            logger.info("✅ Quality acceptable, continuing")
            return "continue"


# Global instance
_autonomous_orchestrator = None


def get_autonomous_orchestrator() -> AutonomousOrchestrator:
    """Get or create autonomous orchestrator instance"""
    global _autonomous_orchestrator
    if _autonomous_orchestrator is None:
        _autonomous_orchestrator = AutonomousOrchestrator()
    return _autonomous_orchestrator

"""
Main Orchestrator - Coordinates all 4 agents
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from models import (
    Campaign,
    CampaignProgress,
    ResearchOutput,
    ContentStrategy,
    CreativeOutput,
    OrchestrationOutput
)
from agents.research_agent import get_research_agent
from agents.strategy_agent import get_strategy_agent
from agents.creative_agent import get_creative_agent
from agents.orchestration_agent import get_orchestration_agent
from services.redis_service import get_redis_service

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Main orchestrator that coordinates all 4 agents

    Pipeline:
    1. Agent 1: Research (0-25%) - Autonomous business discovery
    2. Agent 2: Strategy (25-50%) - 7-day content strategy
    3. Agent 3: Creative (50-85%) - Caption & image generation
    4. Agent 4: Orchestration (85-100%) - Sanity publishing
    """

    def __init__(self):
        self.research_agent = get_research_agent()
        self.strategy_agent = get_strategy_agent()
        self.creative_agent = get_creative_agent()
        self.orchestration_agent = get_orchestration_agent()
        self.redis = get_redis_service()

    async def run(
        self,
        campaign: Campaign,
        business_url: str,
        competitor_urls: Optional[List[str]] = None
    ) -> Campaign:
        """
        Run complete campaign generation pipeline

        Args:
            campaign: Campaign object
            business_url: Business website URL
            competitor_urls: Optional competitor URLs

        Returns:
            Updated campaign with all outputs
        """
        campaign_id = campaign.campaign_id
        logger.info(f"🚀 Starting orchestration for campaign {campaign_id}")

        try:
            # Agent 1: Research (0-25%)
            logger.info(f"📍 Step 1/4: Research Agent")
            campaign.status = "researching"
            campaign.progress = CampaignProgress(
                current_step="research",
                step_number=1,
                total_steps=4,
                message="Analyzing business website and extracting insights...",
                percentage=0
            )
            await self._store_campaign(campaign)

            research_output = await self.research_agent.research(
                business_url=business_url,
                competitor_urls=competitor_urls
            )
            campaign.research = research_output
            campaign.progress.percentage = 25
            campaign.progress.message = "Research complete! Creating content strategy..."
            await self._store_campaign(campaign)

            logger.info(f"✅ Research complete: {research_output.business_context.business_name}")

            # Agent 2: Strategy (25-50%)
            logger.info(f"📍 Step 2/4: Strategy Agent")
            campaign.status = "strategizing"
            campaign.progress = CampaignProgress(
                current_step="strategy",
                step_number=2,
                total_steps=4,
                message="Generating 7-day content strategy...",
                percentage=25
            )
            await self._store_campaign(campaign)

            strategy_output = await self.strategy_agent.create_strategy(
                research_output=research_output,
                campaign_id=campaign_id
            )
            campaign.strategy = strategy_output
            campaign.progress.percentage = 50
            campaign.progress.message = "Strategy complete! Generating creative content..."
            await self._store_campaign(campaign)

            logger.info(f"✅ Strategy complete: 7-day plan created")

            # Agent 3: Creative (50-85%)
            logger.info(f"📍 Step 3/4: Creative Agent")
            campaign.status = "creating"
            campaign.progress = CampaignProgress(
                current_step="creative",
                step_number=3,
                total_steps=4,
                message="Generating captions and images...",
                percentage=50
            )
            await self._store_campaign(campaign)

            creative_output = await self.creative_agent.create_content(
                strategy=strategy_output,
                product_images=research_output.product_images,
                campaign_id=campaign_id
            )
            campaign.creative = creative_output
            campaign.progress.percentage = 85
            campaign.progress.message = "Creative content complete! Publishing to Sanity..."
            await self._store_campaign(campaign)

            logger.info(f"✅ Creative complete: {len(creative_output.days)} days generated")

            # Agent 4: Orchestration (85-100%)
            logger.info(f"📍 Step 4/4: Orchestration Agent")
            campaign.status = "publishing"
            campaign.progress = CampaignProgress(
                current_step="orchestration",
                step_number=4,
                total_steps=4,
                message="Publishing to Sanity CMS...",
                percentage=85
            )
            await self._store_campaign(campaign)

            orchestration_output = await self.orchestration_agent.orchestrate(
                creative_output=creative_output,
                strategy=strategy_output,
                business_url=business_url,
                campaign_id=campaign_id
            )
            campaign.orchestration = orchestration_output
            campaign.progress.percentage = 100
            campaign.progress.message = "Campaign complete!"
            campaign.status = "completed"
            campaign.completed_at = datetime.now()
            await self._store_campaign(campaign)

            logger.info(f"✅ Orchestration complete: Published to Sanity")
            logger.info(f"🎉 Campaign {campaign_id} completed successfully!")

            return campaign

        except Exception as e:
            logger.error(f"❌ Orchestration failed: {e}", exc_info=True)
            campaign.status = "failed"
            campaign.error_message = str(e)
            campaign.progress = CampaignProgress(
                current_step="error",
                step_number=0,
                total_steps=4,
                message=f"Error: {str(e)}",
                percentage=0
            )
            await self._store_campaign(campaign)
            raise

    async def _store_campaign(self, campaign: Campaign):
        """Store campaign state in Redis"""
        try:
            self.redis.set(
                f"campaign:{campaign.campaign_id}",
                campaign.dict(),
                ex=604800  # 7 days
            )
        except Exception as e:
            logger.error(f"Failed to store campaign: {e}")

    async def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Get campaign from Redis"""
        try:
            data = self.redis.get(f"campaign:{campaign_id}")
            if data:
                return Campaign(**data)
            else:
                return None
        except Exception as e:
            logger.error(f"Failed to get campaign: {e}")
            return None

    async def get_campaign_progress(self, campaign_id: str) -> Optional[CampaignProgress]:
        """Get campaign progress from Redis"""
        try:
            campaign = await self.get_campaign(campaign_id)
            if campaign:
                return campaign.progress
            else:
                return None
        except Exception as e:
            logger.error(f"Failed to get campaign progress: {e}")
            return None


# Global instance
_orchestrator = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator

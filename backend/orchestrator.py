"""
Campaign Orchestrator: Main entry point for the 3-agent pipeline.

Sequential workflow:
1. Agent 1: Research & Intelligence (0-25%)
2. Agent 2: Analytics & Feedback (25-50%)
3. Agent 3: Creative Generation (50-100%)
"""

import uuid
import logging
from typing import Optional, List
from datetime import datetime

from models import CampaignResponse, ResearchOutput, AnalyticsOutput, CreativeOutput
from agents.research_agent import ResearchAgent
from agents.strategy_agent import StrategyAgent
from agents.creative_agent import CreativeAgent
from services.agi_service import AGIService
from services.gemini_service import GeminiService
from services.minimax_service import MiniMaxService
from services.convex_service import ConvexService
from services.r2_service import R2Service
from services.social_service import SocialService

logger = logging.getLogger(__name__)


class CampaignOrchestrator:
    """
    Orchestrates the 3-agent marketing campaign pipeline.

    Architecture:
    - Agent 1 (Research): Extracts business context, discovers competitors, analyzes market
    - Agent 2 (Strategy): Fetches reviews, analyzes sentiment, fetches social performance
    - Agent 3 (Creative): Generates captions, images, and videos for 7-day campaign

    All agents coordinate through Convex for data storage and progress tracking.
    """

    def __init__(self):
        """Initialize all services and agents"""
        logger.info("Initializing Campaign Orchestrator...")

        # Initialize services
        self.agi_service = AGIService()
        self.gemini_service = GeminiService()
        self.minimax_service = MiniMaxService()
        self.convex_service = ConvexService()
        self.r2_service = R2Service()
        self.social_service = SocialService()

        # Initialize agents
        self.research_agent = ResearchAgent(
            agi_service=self.agi_service,
            gemini_service=self.gemini_service,
            convex_service=self.convex_service,
            r2_service=self.r2_service
        )

        self.strategy_agent = StrategyAgent(
            gemini_service=self.gemini_service,
            social_service=self.social_service,
            convex_service=self.convex_service,
            r2_service=self.r2_service,
            agi_service=self.agi_service
        )

        self.creative_agent = CreativeAgent(
            gemini_service=self.gemini_service,
            minimax_service=self.minimax_service,
            convex_service=self.convex_service,
            r2_service=self.r2_service
        )

        logger.info("Campaign Orchestrator initialized successfully")

    async def run_campaign(
        self,
        business_url: str,
        competitor_urls: Optional[List[str]] = None,
        facebook_page_id: Optional[str] = None,
        instagram_account_id: Optional[str] = None
    ) -> CampaignResponse:
        """
        Execute complete 3-agent campaign pipeline.

        Args:
            business_url: Target business website
            competitor_urls: Optional list of competitor URLs (if not provided, auto-discover)
            facebook_page_id: Optional Facebook Page ID for performance analytics
            instagram_account_id: Optional Instagram account ID for performance analytics

        Returns:
            CampaignResponse with all research, analytics, and creative outputs

        Raises:
            Exception: If any agent fails
        """
        # Generate unique campaign ID
        campaign_id = str(uuid.uuid4())

        logger.info(f"Starting campaign pipeline: {campaign_id}")
        logger.info(f"Target business: {business_url}")

        try:
            # ================================================================
            # SETUP: Create campaign in Convex
            # ================================================================

            await self.convex_service.create_campaign(campaign_id)

            logger.info("Campaign created, starting agent pipeline...")

            # ================================================================
            # AGENT 1: Research & Intelligence (0-25%)
            # ================================================================

            logger.info("=" * 80)
            logger.info("AGENT 1: Research & Intelligence")
            logger.info("=" * 80)

            research_output = await self.research_agent.run(
                campaign_id=campaign_id,
                business_url=business_url,
                competitor_urls=competitor_urls
            )

            logger.info(f"Agent 1 complete: {research_output.business_context.business_name}")
            logger.info(f"  - Competitors researched: {len(research_output.competitors)}")
            logger.info(f"  - Market insights: {len(research_output.market_insights.trending_topics)} trending topics")

            # Store research data to Convex
            await self.convex_service.store_research(research_output)
            logger.info(f"✓ Research data stored to Convex")

            # ================================================================
            # AGENT 2: Analytics & Feedback (25-50%)
            # ================================================================

            logger.info("=" * 80)
            logger.info("AGENT 2: Analytics & Feedback")
            logger.info("=" * 80)

            analytics_output = await self.strategy_agent.run(
                campaign_id=campaign_id,
                facebook_page_id=facebook_page_id,
                instagram_account_id=instagram_account_id
            )

            logger.info(f"Agent 2 complete: Sentiment & Performance analyzed")
            logger.info(f"  - Positive themes: {len(analytics_output.customer_sentiment.positive_themes)}")
            logger.info(f"  - Recommendations: {len(analytics_output.past_performance.recommendations) if analytics_output.past_performance else 0}")

            # ================================================================
            # AGENT 3: Creative Generation (50-100%)
            # ================================================================

            logger.info("=" * 80)
            logger.info("AGENT 3: Creative Generation")
            logger.info("=" * 80)

            # Run Agent 3: Creative Generation with real MiniMax image/video generation
            logger.info("Generating 7-day content...")
            creative_output = await self.creative_agent.run(campaign_id)

            logger.info(f"Agent 3 complete: {len(creative_output.days)} days of content generated")

            # ================================================================
            # FINALIZE: Return complete campaign response
            # ================================================================

            logger.info("=" * 80)
            logger.info("CAMPAIGN COMPLETE")
            logger.info("=" * 80)

            campaign_response = CampaignResponse(
                success=True,
                campaign_id=campaign_id,
                business_name=research_output.business_context.business_name,
                research_report=research_output,
                analytics_report=analytics_output,
                campaign_content=creative_output,
                sanity_url=None  # TODO: Implement Sanity CMS sync
            )

            logger.info(f"Campaign {campaign_id} completed successfully!")

            return campaign_response

        except Exception as e:
            # Handle agent failures
            logger.error(f"Campaign {campaign_id} failed: {e}", exc_info=True)

            # Update Convex with error status
            try:
                await self.convex_service.update_progress(
                    campaign_id,
                    status="failed",
                    progress=0,
                    current_agent=None,
                    message=f"Error: {str(e)}"
                )
            except Exception as convex_error:
                logger.error(f"Failed to update error status in Convex: {convex_error}")

            # Re-raise the exception
            raise


# Global singleton instance
_orchestrator_instance = None


def get_orchestrator() -> CampaignOrchestrator:
    """Get or create orchestrator singleton"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = CampaignOrchestrator()
    return _orchestrator_instance

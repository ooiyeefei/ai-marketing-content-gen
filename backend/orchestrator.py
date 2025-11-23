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
        self.convex_service = ConvexService()
        self.r2_service = R2Service()
        self.social_service = SocialService()

        # Initialize agents
        self.research_agent = ResearchAgent(
            agi_service=self.agi_service,
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

        self.creative_agent = CreativeAgent()

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

            await self.convex_service.update_progress(
                campaign_id,
                status="agent3_running",
                progress=51,
                current_agent="Creative Agent",
                message="Retrieving campaign data..."
            )

            # Retrieve all campaign data for Agent 3
            campaign_data = await self.convex_service.get_full_campaign_data(campaign_id)

            # TODO: Extract product images from research data
            # For now, pass empty list - Agent 3 will generate from scratch
            product_images = []

            # TODO: Generate content strategy from research + analytics
            # For MVP, we'll let Agent 3 create its own strategy
            # In production, this should be synthesized by Gemini HIGH thinking

            logger.info("Generating 7-day content...")

            # Note: Creative Agent has different interface - uses ContentStrategy
            # We need to create a content strategy from research + analytics data
            # For now, skip creative agent and mark as TODO

            await self.convex_service.update_progress(
                campaign_id,
                status="agent3_running",
                progress=75,
                current_agent="Creative Agent",
                message="Creating content strategy..."
            )

            # TODO: Implement content strategy generation
            # This requires Gemini HIGH thinking to synthesize:
            # - Research insights (business context, competitors, market gaps)
            # - Analytics insights (customer sentiment, performance patterns)
            # Into a 7-day content plan with themes, formats, CTAs

            # For MVP, create placeholder creative output
            from models import DayContent, LearningData

            days_content = []
            for i in range(1, 8):
                day_content = DayContent(
                    day=i,
                    theme=f"Day {i} Theme (TODO)",
                    caption=f"Caption for day {i} (TODO)",
                    hashtags=["#TODO"],
                    image_urls=[],
                    video_url=None,
                    cta="Call to action (TODO)",
                    recommended_post_time="12:00 PM"
                )
                days_content.append(day_content)

            creative_output = CreativeOutput(
                campaign_id=campaign_id,
                days=days_content,
                learning_data=LearningData(
                    what_worked=[],
                    what_to_improve=[],
                    next_iteration_strategy={}
                ),
                status="completed",
                timestamp=datetime.now()
            )

            await self.convex_service.update_progress(
                campaign_id,
                status="completed",
                progress=100,
                current_agent=None,
                message="Campaign complete!"
            )

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

import os
from typing import Optional, Dict, Any, List
from convex import ConvexClient
from models import (
    ResearchOutput,
    AnalyticsOutput,
    CreativeOutput,
    CampaignProgress
)
import logging

logger = logging.getLogger(__name__)


class ConvexService:
    """
    Convex database service for storing campaign data.

    Schema (define in Convex dashboard):
    - campaigns: {_id, campaign_id, status, progress, created_at, updated_at}
    - research: {_id, campaign_id, business_context, competitors, market_insights, research_images}
    - analytics: {_id, campaign_id, customer_sentiment, past_performance, market_trends, customer_photos}
    - content: {_id, campaign_id, days[], learning_data, status}
    """

    def __init__(self):
        convex_url = os.getenv("CONVEX_URL")
        if not convex_url:
            raise ValueError("CONVEX_URL environment variable not set")

        self.client = ConvexClient(convex_url)
        logger.info(f" Connected to Convex: {convex_url}")

    # ========================================================================
    # Campaign Progress Tracking
    # ========================================================================

    async def create_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Create new campaign record"""
        result = self.client.mutation(
            "campaigns:create",
            {
                "campaign_id": campaign_id,
                "status": "pending",
                "progress": 0,
                "current_agent": None,
                "message": "Campaign created"
            }
        )
        logger.info(f" Created campaign: {campaign_id}")
        return result

    async def update_progress(
        self,
        campaign_id: str,
        status: str,
        progress: int,
        current_agent: Optional[str] = None,
        message: str = ""
    ) -> Dict[str, Any]:
        """Update campaign progress"""
        result = self.client.mutation(
            "campaigns:updateProgress",
            {
                "campaign_id": campaign_id,
                "status": status,
                "progress": progress,
                "current_agent": current_agent,
                "message": message
            }
        )
        logger.info(f" Progress {campaign_id}: {progress}% - {message}")
        return result

    async def get_progress(self, campaign_id: str) -> Optional[CampaignProgress]:
        """Get current campaign progress"""
        result = self.client.query(
            "campaigns:getProgress",
            {"campaign_id": campaign_id}
        )

        if result:
            return CampaignProgress(**result)
        return None

    # ========================================================================
    # Agent 1: Research Data Storage
    # ========================================================================

    async def store_research(self, data: ResearchOutput) -> Dict[str, Any]:
        """Store Agent 1 research output"""
        result = self.client.mutation(
            "research:store",
            {
                "campaign_id": data.campaign_id,
                "business_context": data.business_context.model_dump(),
                "competitors": [c.model_dump() for c in data.competitors],
                "market_insights": data.market_insights.model_dump(),
                "research_images": [str(url) for url in data.research_images],
                "timestamp": data.timestamp.isoformat()
            }
        )
        logger.info(f" Stored research for campaign: {data.campaign_id}")
        return result

    async def get_research(self, campaign_id: str) -> Optional[ResearchOutput]:
        """Retrieve Agent 1 research output"""
        result = self.client.query(
            "research:get",
            {"campaign_id": campaign_id}
        )

        if result:
            return ResearchOutput(**result)
        return None

    # ========================================================================
    # Agent 2: Analytics Data Storage
    # ========================================================================

    async def store_analytics(self, data: AnalyticsOutput) -> Dict[str, Any]:
        """Store Agent 2 analytics output"""
        result = self.client.mutation(
            "analytics:store",
            {
                "campaign_id": data.campaign_id,
                "customer_sentiment": data.customer_sentiment.model_dump(),
                "past_performance": data.past_performance.model_dump() if data.past_performance else None,
                "market_trends": data.market_trends.model_dump(),
                "customer_photos": [str(url) for url in data.customer_photos],
                "timestamp": data.timestamp.isoformat()
            }
        )
        logger.info(f" Stored analytics for campaign: {data.campaign_id}")
        return result

    async def get_analytics(self, campaign_id: str) -> Optional[AnalyticsOutput]:
        """Retrieve Agent 2 analytics output"""
        result = self.client.query(
            "analytics:get",
            {"campaign_id": campaign_id}
        )

        if result:
            return AnalyticsOutput(**result)
        return None

    # ========================================================================
    # Agent 3: Content Data Storage
    # ========================================================================

    async def store_content(self, data: CreativeOutput) -> Dict[str, Any]:
        """Store Agent 3 creative output"""
        result = self.client.mutation(
            "content:store",
            {
                "campaign_id": data.campaign_id,
                "days": [day.model_dump() for day in data.days],
                "learning_data": data.learning_data.model_dump(),
                "status": data.status,
                "timestamp": data.timestamp.isoformat()
            }
        )
        logger.info(f" Stored content for campaign: {data.campaign_id}")
        return result

    async def get_content(self, campaign_id: str) -> Optional[CreativeOutput]:
        """Retrieve Agent 3 creative output"""
        result = self.client.query(
            "content:get",
            {"campaign_id": campaign_id}
        )

        if result:
            return CreativeOutput(**result)
        return None

    # ========================================================================
    # Retrieve Full Campaign Data (for Agent 3)
    # ========================================================================

    async def get_full_campaign_data(self, campaign_id: str) -> Dict[str, Any]:
        """
        Retrieve ALL campaign data for Agent 3 content generation.
        Returns: {research, analytics, progress}
        """
        research = await self.get_research(campaign_id)
        analytics = await self.get_analytics(campaign_id)
        progress = await self.get_progress(campaign_id)

        return {
            "research": research,
            "analytics": analytics,
            "progress": progress
        }

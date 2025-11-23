import logging
from typing import Dict, List, Any, Optional
from models import (
    BusinessContext,
    CompetitorInfo,
    MarketInsights,
    ResearchOutput
)
from services.agi_service import AGIService
from services.convex_service import ConvexService
from services.r2_service import R2Service
from datetime import datetime

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Agent 1: Intelligence & Research

    Responsibilities:
    - Extract business context from website (AGI API)
    - Discover competitors intelligently (AGI API)
    - Deep competitor research (AGI API)
    - Market trend analysis (AGI API)
    - Store all data in Convex + R2
    """

    def __init__(
        self,
        agi_service: AGIService,
        convex_service: ConvexService,
        r2_service: R2Service
    ):
        self.agi = agi_service
        self.convex = convex_service
        self.r2 = r2_service
        logger.info("✓ Research Agent initialized")

    async def run(
        self,
        campaign_id: str,
        business_url: str,
        competitor_urls: Optional[List[str]] = None
    ) -> ResearchOutput:
        """
        Execute complete research workflow.

        Steps:
        1. Extract business context (AGI API)
        2. Discover competitors (AGI API or user-provided)
        3. Research each competitor (AGI API)
        4. Analyze market trends (AGI API)
        5. Store all data in Convex + R2

        Args:
            campaign_id: Unique campaign identifier
            business_url: Target business website
            competitor_urls: Optional list of competitor URLs

        Returns:
            ResearchOutput with all intelligence data
        """
        logger.info(f"🔍 Agent 1 starting research for campaign: {campaign_id}")

        # Update progress: 0-25%
        await self.convex.update_progress(
            campaign_id,
            status="agent1_running",
            progress=5,
            current_agent="Research Agent",
            message="Extracting business context..."
        )

        # =====================================================================
        # Step 0: Extract Business Context
        # =====================================================================

        logger.info(f"📄 Step 0: Extracting business context from {business_url}")

        business_data = await self.agi.extract_business_context(business_url)

        business_context = BusinessContext(
            business_name=business_data.get("business_name", "Unknown"),
            industry=business_data.get("industry", "Unknown"),
            description=business_data.get("description", ""),
            location=business_data.get("location", {}),
            price_range=business_data.get("price_range"),
            specialties=business_data.get("specialties", []),
            brand_voice=business_data.get("brand_voice"),
            target_audience=business_data.get("target_audience"),
            website_url=business_url
        )

        logger.info(f"✓ Business: {business_context.business_name} ({business_context.industry})")

        await self.convex.update_progress(
            campaign_id,
            status="agent1_running",
            progress=10,
            current_agent="Research Agent",
            message=f"Analyzing {business_context.business_name}..."
        )

        # =====================================================================
        # Step 1: Intelligent Competitor Discovery
        # =====================================================================

        competitors_data = []

        if competitor_urls:
            # User provided competitor URLs
            logger.info(f"👥 Step 1: Researching {len(competitor_urls)} user-provided competitors")

            for idx, comp_url in enumerate(competitor_urls):
                await self.convex.update_progress(
                    campaign_id,
                    status="agent1_running",
                    progress=10 + (idx * 5),
                    current_agent="Research Agent",
                    message=f"Researching competitor {idx + 1}/{len(competitor_urls)}..."
                )

                comp_data = await self.agi.research_competitor(
                    comp_url,
                    f"Competitor {idx + 1}"
                )

                if comp_data:
                    competitors_data.append(comp_data)

        else:
            # Auto-discover competitors via AGI API
            logger.info(f"🔍 Step 1: Auto-discovering competitors for {business_context.business_name}")

            await self.convex.update_progress(
                campaign_id,
                status="agent1_running",
                progress=12,
                current_agent="Research Agent",
                message="Discovering competitors..."
            )

            discovered = await self.agi.discover_competitors(
                business_context.model_dump(),
                num_competitors=5
            )

            logger.info(f"✓ Discovered {len(discovered)} competitors")

            # Step 2: Deep research on each competitor
            for idx, comp_info in enumerate(discovered):
                comp_url = comp_info.get("website")
                comp_name = comp_info.get("name")

                if not comp_url:
                    continue

                await self.convex.update_progress(
                    campaign_id,
                    status="agent1_running",
                    progress=12 + (idx * 3),
                    current_agent="Research Agent",
                    message=f"Researching {comp_name}..."
                )

                comp_data = await self.agi.research_competitor(comp_url, comp_name)

                if comp_data:
                    # Merge discovery data with research data
                    comp_data.update({
                        "google_rating": comp_info.get("google_rating"),
                        "review_count": comp_info.get("review_count"),
                        "social_handles": comp_info.get("social_handles", {}),
                        "similarity_score": comp_info.get("similarity_score")
                    })
                    competitors_data.append(comp_data)

        # Convert to Pydantic models
        competitors = [
            CompetitorInfo(
                name=comp.get("competitor_name", comp.get("name", "Unknown")),
                website=comp.get("website"),
                location=comp.get("location", "Unknown"),
                google_rating=comp.get("google_rating"),
                review_count=comp.get("review_count"),
                social_handles=comp.get("social_handles", {}),
                pricing_strategy=comp.get("pricing_strategy"),
                brand_voice=comp.get("brand_voice"),
                top_content_themes=comp.get("top_content_themes", []),
                differentiators=comp.get("differentiators", []),
                similarity_score=comp.get("similarity_score")
            )
            for comp in competitors_data
        ]

        logger.info(f"✓ Researched {len(competitors)} competitors")

        await self.convex.update_progress(
            campaign_id,
            status="agent1_running",
            progress=20,
            current_agent="Research Agent",
            message="Analyzing market trends..."
        )

        # =====================================================================
        # Step 3: Market Trends Analysis
        # =====================================================================

        logger.info(f"📈 Step 3: Analyzing market trends")

        trends_data = await self.agi.analyze_market_trends(
            business_context.model_dump(),
            [comp.model_dump() for comp in competitors]
        )

        market_insights = MarketInsights(
            trending_topics=trends_data.get("trending_topics", []),
            market_gaps=trends_data.get("market_gaps", []),
            positioning_opportunities=trends_data.get("positioning_opportunities", []),
            content_strategy={}  # Will be populated by Agent 2
        )

        logger.info(f"✓ Market insights: {len(market_insights.trending_topics)} trending topics")

        # =====================================================================
        # Step 4: Store Research Data
        # =====================================================================

        await self.convex.update_progress(
            campaign_id,
            status="agent1_running",
            progress=23,
            current_agent="Research Agent",
            message="Storing research data..."
        )

        # Create output model
        research_output = ResearchOutput(
            campaign_id=campaign_id,
            business_context=business_context,
            competitors=competitors,
            market_insights=market_insights,
            research_images=[],  # TODO: Extract and upload competitor images
            timestamp=datetime.now()
        )

        # Store in Convex
        await self.convex.store_research(research_output)

        await self.convex.update_progress(
            campaign_id,
            status="agent1_complete",
            progress=25,
            current_agent=None,
            message="Research complete ✓"
        )

        logger.info(f"✅ Agent 1 complete for campaign: {campaign_id}")

        return research_output

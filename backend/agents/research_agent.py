import logging
from typing import Dict, List, Any, Optional
from models import (
    BusinessContext,
    CompetitorInfo,
    MarketInsights,
    ResearchOutput
)
from services.agi_service import AGIService
from services.gemini_service import GeminiService
from services.convex_service import ConvexService
from services.r2_service import R2Service
from datetime import datetime

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Agent 1: Intelligence & Research

    Responsibilities:
    - Extract business context from website (AGI API)
    - Generate demo competitor insights (Gemini for hackathon)
    - Store all data in Convex + R2
    """

    def __init__(
        self,
        agi_service: AGIService,
        gemini_service: GeminiService,
        convex_service: ConvexService,
        r2_service: R2Service
    ):
        self.agi = agi_service
        self.gemini = gemini_service
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

        # Upload screenshots to R2 if available
        screenshot_urls = []
        screenshots = business_data.get("screenshots", [])
        if screenshots:
            logger.info(f"📤 Uploading {len(screenshots)} screenshots to R2...")
            for idx, screenshot in enumerate(screenshots):
                try:
                    screenshot_bytes = screenshot.get("data")
                    screenshot_page = screenshot.get("page", f"screenshot_{idx}")

                    if screenshot_bytes:
                        # Upload to R2
                        object_key = self.r2.get_campaign_path(
                            campaign_id,
                            f"research/{screenshot_page}.jpg"
                        )
                        r2_url = await self.r2.upload_bytes(
                            screenshot_bytes,
                            object_key,
                            content_type="image/jpeg"
                        )
                        screenshot_urls.append(r2_url)
                        logger.info(f"✓ Uploaded screenshot {idx + 1}/{len(screenshots)} to R2")
                except Exception as e:
                    logger.warning(f"⚠ Failed to upload screenshot {idx}: {e}")

        # Store screenshot URLs in business data
        business_data["screenshot_urls"] = screenshot_urls

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

        # =====================================================================
        # DEMO MODE: Generate Competitor Insights with Gemini
        # =====================================================================
        # Reason: AGI sessions timeout during competitor discovery
        # Using Gemini to generate realistic demo data instead
        # This provides fast, realistic competitor insights for demo purposes
        # =====================================================================

        await self.convex.update_progress(
            campaign_id,
            status="agent1_running",
            progress=15,
            current_agent="Research Agent",
            message="Generating demo competitor insights with Gemini..."
        )

        logger.info(f"🤖 Generating demo competitor insights with Gemini")

        # Prepare business context for Gemini
        business_context_dict = {
            "business_name": business_context.business_name,
            "industry": business_context.industry,
            "description": business_context.description,
            "location": business_context.location,
            "specialties": business_context.specialties
        }

        # Generate insights with Gemini
        demo_data = await self.gemini.generate_demo_competitor_insights(business_context_dict)

        # Parse competitors
        competitors = []
        for comp_data in demo_data.get("competitors", []):
            competitors.append(CompetitorInfo(
                name=comp_data.get("name", "Competitor"),
                location=comp_data.get("location", "Unknown"),
                google_rating=comp_data.get("google_rating"),
                review_count=comp_data.get("review_count"),
                pricing_strategy=comp_data.get("pricing_strategy"),
                brand_voice=comp_data.get("brand_voice"),
                top_content_themes=comp_data.get("top_content_themes", []),
                differentiators=comp_data.get("differentiators", [])
            ))

        # Parse market insights
        market_data = demo_data.get("market_insights", {})
        market_insights = MarketInsights(
            trending_topics=market_data.get("trending_topics", []),
            market_gaps=market_data.get("market_gaps", []),
            positioning_opportunities=market_data.get("positioning_opportunities", []),
            content_strategy=market_data.get("content_strategy", {})
        )

        logger.info(f"✓ Generated {len(competitors)} demo competitors with Gemini")
        logger.info(f"✓ Generated market insights: {len(market_insights.trending_topics)} trending topics")

        # =====================================================================
        # Step 3.5: Extract and Upload Images to R2 (Multi-Source)
        # =====================================================================

        await self.convex.update_progress(
            campaign_id,
            status="agent1_running",
            progress=22,
            current_agent="Research Agent",
            message="Downloading images from website, Google Maps, social media..."
        )

        research_images = []
        import httpx

        # Extract images from business data (website, Google Maps, social media)
        business_images = business_data.get("images", {})

        for source, img_urls in business_images.items():
            logger.info(f"📸 Processing {len(img_urls)} images from {source}")

            for img_url in img_urls[:5]:  # Max 5 images per source
                if not img_url or not isinstance(img_url, str):
                    continue

                try:
                    # Download image
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        img_response = await client.get(img_url)
                        img_response.raise_for_status()
                        image_bytes = img_response.content

                    # Upload to R2
                    filename = f"{source}_{campaign_id}_{len(research_images)}.jpg"
                    r2_url = await self.r2.upload_image(
                        image_bytes=image_bytes,
                        filename=filename,
                        folder="research"
                    )

                    research_images.append(r2_url)
                    logger.info(f"✓ Uploaded {source} image: {filename} → {r2_url}")

                except Exception as e:
                    logger.warning(f"⚠ Failed to download/upload {source} image {img_url}: {e}")
                    continue

        # HACKATHON SKIP: Competitor images disabled (competitors_data is empty)
        # Original code extracted hero_images from competitor data
        # Skipped because competitor analysis is disabled

        logger.info(f"✓ Uploaded {len(research_images)} total images to R2 (website + Maps + social)")

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
            research_images=research_images,  # Now populated with real R2 URLs
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

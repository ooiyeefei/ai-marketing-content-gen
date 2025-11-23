import logging
from typing import Dict, List, Any, Optional
from models import (
    CustomerSentiment,
    PerformancePatterns,
    TrendData,
    AnalyticsOutput,
    ResearchOutput
)
from services.gemini_service import GeminiService
from services.social_service import SocialService
from services.convex_service import ConvexService
from services.r2_service import R2Service
from services.agi_service import AGIService
from datetime import datetime

logger = logging.getLogger(__name__)


class StrategyAgent:
    """
    Agent 2: Analytics & Feedback

    Responsibilities:
    - Fetch Google My Business reviews (with AGI fallback for unclaimed businesses)
    - Analyze customer sentiment with Gemini HIGH thinking
    - Fetch Facebook/Instagram performance (optional)
    - Analyze performance patterns with Gemini HIGH thinking
    - Fetch Google Trends data (optional)
    - Store all data in Convex + R2
    """

    def __init__(
        self,
        gemini_service: GeminiService,
        social_service: SocialService,
        convex_service: ConvexService,
        r2_service: R2Service,
        agi_service: AGIService  # Added for review scraping fallback
    ):
        self.gemini = gemini_service
        self.social = social_service
        self.convex = convex_service
        self.r2 = r2_service
        self.agi = agi_service
        logger.info("✓ Strategy Agent initialized")

    async def run(
        self,
        campaign_id: str,
        facebook_page_id: Optional[str] = None,
        instagram_account_id: Optional[str] = None
    ) -> AnalyticsOutput:
        """
        Execute complete analytics workflow.

        Steps:
        1. Retrieve research data from Agent 1
        2. Fetch Google My Business reviews
        3. Analyze customer sentiment (Gemini HIGH)
        4. Fetch Facebook/Instagram insights (optional)
        5. Analyze performance patterns (Gemini HIGH)
        6. Fetch Google Trends data
        7. Store all data in Convex + R2

        Args:
            campaign_id: Unique campaign identifier
            facebook_page_id: Optional Facebook Page ID
            instagram_account_id: Optional Instagram account ID

        Returns:
            AnalyticsOutput with sentiment and performance data
        """
        logger.info(f"📊 Agent 2 starting analytics for campaign: {campaign_id}")

        # Update progress: 25-50%
        await self.convex.update_progress(
            campaign_id,
            status="agent2_running",
            progress=26,
            current_agent="Strategy Agent",
            message="Retrieving research data..."
        )

        # =====================================================================
        # Step 0: Retrieve Research Data from Agent 1
        # =====================================================================

        research = await self.convex.get_research(campaign_id)

        if not research:
            raise ValueError(f"No research data found for campaign: {campaign_id}")

        business_name = research.business_context.business_name
        location = research.business_context.location

        logger.info(f"✓ Retrieved research for {business_name}")

        # =====================================================================
        # Step 1: Fetch Google My Business Reviews
        # =====================================================================

        await self.convex.update_progress(
            campaign_id,
            status="agent2_running",
            progress=30,
            current_agent="Strategy Agent",
            message="Fetching customer reviews..."
        )

        logger.info(f"📝 Step 1: Fetching Google reviews for {business_name}")

        gmb_data = await self.social.get_google_reviews(
            business_name,
            location,
            agi_service=self.agi  # Pass AGI for fallback scraping
        )

        reviews = gmb_data.get("reviews", [])
        customer_photos = gmb_data.get("customer_photos", [])
        review_source = gmb_data.get("source", "unknown")

        logger.info(f"✓ Fetched {len(reviews)} reviews via {review_source}")

        # =====================================================================
        # Step 2: Analyze Customer Sentiment (Gemini HIGH)
        # =====================================================================

        await self.convex.update_progress(
            campaign_id,
            status="agent2_running",
            progress=35,
            current_agent="Strategy Agent",
            message="Analyzing customer sentiment..."
        )

        logger.info(f"🤔 Step 2: Analyzing sentiment with Gemini HIGH thinking")

        if reviews:
            sentiment_data = await self.gemini.analyze_customer_sentiment(
                reviews,
                business_name
            )
        else:
            # No reviews available
            sentiment_data = {
                "positive_themes": [],
                "negative_themes": [],
                "popular_items": [],
                "quotable_reviews": [],
                "content_opportunities": []
            }

        customer_sentiment = CustomerSentiment(**sentiment_data)

        logger.info(f"✓ Sentiment: {len(customer_sentiment.positive_themes)} positive themes")

        # =====================================================================
        # Step 3: Fetch Facebook/Instagram Insights (Optional)
        # =====================================================================

        await self.convex.update_progress(
            campaign_id,
            status="agent2_running",
            progress=40,
            current_agent="Strategy Agent",
            message="Fetching social media performance..."
        )

        logger.info(f"📱 Step 3: Fetching social media insights")

        fb_insights = None
        ig_insights = None

        if facebook_page_id:
            fb_insights = await self.social.get_facebook_insights(facebook_page_id)

        if instagram_account_id:
            ig_insights = await self.social.get_instagram_insights(instagram_account_id)

        # Combine all posts for analysis
        all_posts = []

        if fb_insights:
            all_posts.extend(fb_insights.get("posts", []))

        if ig_insights:
            all_posts.extend(ig_insights.get("posts", []))

        logger.info(f"✓ Fetched {len(all_posts)} past posts")

        # =====================================================================
        # Step 4: Analyze Performance Patterns (Gemini HIGH)
        # =====================================================================

        await self.convex.update_progress(
            campaign_id,
            status="agent2_running",
            progress=43,
            current_agent="Strategy Agent",
            message="Analyzing performance patterns..."
        )

        logger.info(f"📈 Step 4: Analyzing performance with Gemini HIGH thinking")

        past_performance = None

        if all_posts:
            performance_data = await self.gemini.analyze_performance_patterns(
                all_posts,
                business_name
            )

            past_performance = PerformancePatterns(**performance_data)

            logger.info(f"✓ Performance: {len(past_performance.recommendations)} recommendations")

        # =====================================================================
        # Step 5: Fetch Google Trends Data
        # =====================================================================

        await self.convex.update_progress(
            campaign_id,
            status="agent2_running",
            progress=46,
            current_agent="Strategy Agent",
            message="Analyzing market trends..."
        )

        logger.info(f"🔍 Step 5: Fetching Google Trends data")

        # Build search keywords from business context
        keywords = [
            research.business_context.industry,
            *research.business_context.specialties[:3]
        ]

        trends_data = await self.social.get_location_trends(
            keywords,
            location
        )

        market_trends = TrendData(
            trending_searches=trends_data.get("trending_searches", []),
            related_queries=trends_data.get("related_queries", []),
            rising_topics=trends_data.get("rising_topics", [])
        )

        logger.info(f"✓ Trends: {len(market_trends.trending_searches)} trending searches")

        # =====================================================================
        # Step 6: Store Analytics Data
        # =====================================================================

        await self.convex.update_progress(
            campaign_id,
            status="agent2_running",
            progress=48,
            current_agent="Strategy Agent",
            message="Storing analytics data..."
        )

        # Create output model
        analytics_output = AnalyticsOutput(
            campaign_id=campaign_id,
            customer_sentiment=customer_sentiment,
            past_performance=past_performance,
            market_trends=market_trends,
            customer_photos=[],  # TODO: Upload customer photos to R2
            timestamp=datetime.now()
        )

        # Store in Convex
        await self.convex.store_analytics(analytics_output)

        await self.convex.update_progress(
            campaign_id,
            status="agent2_complete",
            progress=50,
            current_agent=None,
            message="Analytics complete ✓"
        )

        logger.info(f"✅ Agent 2 complete for campaign: {campaign_id}")

        return analytics_output

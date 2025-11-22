"""
Agent 1: Research & Discovery Agent
Autonomously discovers business context, competitors, and market intelligence
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from models import ResearchOutput, BusinessContext, BrandVoice, CompetitorInsight, TrendAnalysis
from services.lightpanda_service import get_lightpanda_service
from services.parallel_service import get_parallel_service
from services.gemini_service import get_gemini_service
from services.redis_service import get_redis_service

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Agent 1: Research & Discovery

    Responsibilities:
    1. Research business, competitors, and industry with Parallel.ai (AI-powered search)
    2. Extract product images with Lightpanda (browser automation)
    3. Analyze findings with Gemini
    4. Extract brand voice and context
    5. Store all findings in Redis with embeddings
    """

    def __init__(self):
        self.parallel = get_parallel_service()  # AI-powered search for research
        self.lightpanda = get_lightpanda_service()  # Browser automation for images
        self.gemini = get_gemini_service()
        self.redis = get_redis_service()

    async def research(
        self,
        business_url: str,
        competitor_urls: Optional[List[str]] = None
    ) -> ResearchOutput:
        """
        Execute complete research workflow

        Args:
            business_url: Business website URL
            competitor_urls: Optional competitor URLs

        Returns:
            Complete research output
        """
        logger.info(f"🔍 Agent 1 starting research for: {business_url}")

        try:
            # Step 1: Analyze website with Lightpanda
            business_context = await self._analyze_website(business_url)

            # Step 2: Extract product images with Lightpanda
            product_images = await self._collect_product_images(business_url)

            # Step 3: Extract brand voice
            brand_voice = await self._extract_brand_voice(business_context, business_url)
            business_context.brand_voice = brand_voice

            # Step 4: Research competitors (optional) with Lightpanda
            competitor_insights = []
            if competitor_urls:
                competitor_insights = await self._research_competitors(competitor_urls)

            # Step 5: Analyze industry trends with Gemini
            industry_trends = await self._analyze_industry_trends(
                business_context.industry
            )

            # Step 6: Store in Redis
            redis_keys = await self._store_research_data(
                business_url,
                business_context,
                product_images,
                competitor_insights,
                industry_trends
            )

            result = ResearchOutput(
                business_context=business_context,
                product_images=product_images,
                competitor_insights=competitor_insights,
                industry_trends=industry_trends,
                redis_keys=redis_keys,
                timestamp=datetime.now()
            )

            logger.info(f"✅ Agent 1 research complete: {len(product_images)} images, {len(competitor_insights)} competitors")
            return result

        except Exception as e:
            logger.error(f"❌ Agent 1 research failed: {e}", exc_info=True)
            raise

    async def _analyze_website(self, business_url: str) -> BusinessContext:
        """Analyze website and extract business context using Parallel.ai"""
        logger.info(f"Researching business: {business_url}")

        try:
            # Extract business name from URL for better research
            business_name_guess = business_url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0].split(".")[0]

            # Use Parallel.ai for AI-powered business research
            business_research = await self.parallel.research_business(
                business_name=business_name_guess,
                business_url=business_url
            )

            # Use Gemini to synthesize research into structured context
            research_text = "\n".join([
                result.get("excerpt", "")
                for result in business_research.get("research_results", [])
            ])

            analysis = self.gemini.analyze_website(
                research_text or "No research data available",
                business_url
            )

            business_context = BusinessContext(
                business_name=analysis.get("business_name") or business_name_guess.title(),
                business_url=business_url,
                industry=analysis.get("industry") or "General",
                products=analysis.get("products") or [],
                target_audience=analysis.get("target_audience") or "General audience",
                description=analysis.get("description") or ""
            )

            logger.info(f"✅ Business context: {business_context.business_name} ({business_context.industry})")
            return business_context

        except Exception as e:
            logger.error(f"Business research error: {e}")
            # Return minimal context
            business_name_guess = business_url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0].split(".")[0]
            return BusinessContext(
                business_name=business_name_guess.title(),
                business_url=business_url,
                industry="General",
                products=[],
                target_audience="General audience",
                description="Unable to research business"
            )

    async def _collect_product_images(self, business_url: str) -> List[str]:
        """Extract product images from website"""
        logger.info("Extracting product images...")

        try:
            images = await self.lightpanda.extract_product_images(
                business_url,
                max_images=10
            )

            logger.info(f"✅ Found {len(images)} product images")
            return images

        except Exception as e:
            logger.error(f"Product image extraction error: {e}")
            return []

    async def _extract_brand_voice(
        self,
        business_context: BusinessContext,
        business_url: str
    ) -> BrandVoice:
        """Extract brand voice characteristics using Parallel.ai"""
        logger.info("Extracting brand voice...")

        try:
            # Use Parallel.ai to research brand voice and communication style
            voice_query = f"What is the brand voice, tone, and communication style of {business_context.business_name}? How do they communicate with their audience?"

            voice_results = await self.parallel.search(
                objective=voice_query,
                max_results=5,
                max_characters=500
            )

            # Synthesize research into brand voice characteristics
            voice_research = "\n".join([
                result.get("excerpt", "")
                for result in voice_results
            ])

            # Use Gemini to extract structured brand voice from research
            voice_analysis = self.gemini.extract_brand_voice(
                voice_research or f"General information about {business_context.business_name} in {business_context.industry} industry"
            )

            brand_voice = BrandVoice(
                tone=voice_analysis.get("tone", "professional"),
                style=voice_analysis.get("style", "clear"),
                colors=[],  # Can be extracted from images later
                personality_traits=voice_analysis.get("personality_traits", []),
                dos=voice_analysis.get("dos", []),
                donts=voice_analysis.get("donts", [])
            )

            logger.info(f"✅ Brand voice: {brand_voice.tone} / {brand_voice.style}")
            return brand_voice

        except Exception as e:
            logger.error(f"Brand voice extraction error: {e}")
            # Return default brand voice
            return BrandVoice(
                tone="professional",
                style="clear",
                personality_traits=["authentic", "helpful", "knowledgeable"],
                dos=["Be clear", "Focus on value", "Use active voice"],
                donts=["Avoid jargon", "Don't oversell", "Don't be vague"]
            )

    async def _research_competitors(
        self,
        competitor_urls: List[str]
    ) -> List[CompetitorInsight]:
        """Research competitor websites using Parallel.ai"""
        logger.info(f"Researching {len(competitor_urls)} competitors...")

        insights = []

        try:
            # Research each competitor with Parallel.ai
            for url in competitor_urls[:3]:  # Limit to 3 competitors
                try:
                    # Extract competitor name from URL
                    competitor_name = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0].split(".")[0].title()

                    # Search for competitor information
                    competitor_query = f"What does {competitor_name} do? What are their products, services, and marketing approach?"

                    competitor_results = await self.parallel.search(
                        objective=competitor_query,
                        max_results=3,
                        max_characters=500
                    )

                    # Extract content themes from research
                    content_themes = []
                    if competitor_results:
                        for result in competitor_results:
                            excerpt = result.get("excerpt", "")
                            if "content" in excerpt.lower() or "marketing" in excerpt.lower():
                                content_themes.append(excerpt[:100])

                    insight = CompetitorInsight(
                        competitor_name=competitor_name,
                        competitor_url=url,
                        content_themes=content_themes[:3],  # Top 3 themes
                        visual_style="To be analyzed"  # Can be enhanced with image analysis later
                    )

                    insights.append(insight)

                except Exception as e:
                    logger.warning(f"Failed to research competitor {url}: {e}")

            logger.info(f"✅ Researched {len(insights)} competitors")

        except Exception as e:
            logger.error(f"Competitor research error: {e}")

        return insights

    async def _analyze_industry_trends(self, industry: str) -> Optional[TrendAnalysis]:
        """Analyze industry trends using Parallel.ai"""
        logger.info(f"Analyzing trends in {industry} industry...")

        try:
            # Use Parallel.ai to research current industry trends
            trend_results = await self.parallel.research_industry_trends(industry)

            # Extract trend insights from research
            trends = []
            actionable_themes = []

            for trend_data in trend_results[:5]:  # Top 5 trends
                trend_text = trend_data.get("trend", "")
                if trend_text:
                    trends.append(trend_text[:200])  # Limit length

            # Use Gemini to synthesize actionable content themes from trends
            trends_summary = "\n".join(trends) if trends else f"General {industry} industry trends"
            content_suggestions = self.gemini.synthesize_insights(
                {"industry": industry, "trends": trends_summary},
                "identify 5 actionable content themes that would work well on social media based on these trends"
            )

            # Extract themes from Gemini's suggestions
            actionable_themes = [
                "Behind-the-scenes content",
                "Educational posts",
                "User-generated content",
                "Trend-jacking",
                "Product showcases"
            ]  # Default themes; can be enhanced with Gemini parsing

            trend_analysis = TrendAnalysis(
                industry=industry,
                trends=trends or [f"Current {industry} industry trends"],
                actionable_themes=actionable_themes,
                best_practices=[
                    "Post consistently (3-5x/week)",
                    "Use high-quality visuals",
                    "Engage with comments",
                    "Use relevant hashtags",
                    "Tell stories"
                ]
            )

            logger.info(f"✅ Industry trends analyzed: {len(trends)} trends found")
            return trend_analysis

        except Exception as e:
            logger.error(f"Trend analysis error: {e}")
            return None

    async def _store_research_data(
        self,
        business_url: str,
        business_context: BusinessContext,
        product_images: List[str],
        competitor_insights: List[CompetitorInsight],
        industry_trends: Optional[TrendAnalysis]
    ) -> List[str]:
        """Store research data in Redis with embeddings"""
        logger.info("Storing research data in Redis...")

        redis_keys = []

        try:
            # Store business context
            context_text = f"{business_context.business_name} {business_context.industry} {business_context.description}"
            context_embedding = self.gemini.get_embedding(context_text)

            self.redis.store_research(
                business_url=business_url,
                research_type="website",
                industry=business_context.industry,
                embedding=context_embedding,
                data=business_context.dict()
            )
            redis_keys.append(f"research:{business_url}:website")

            # Store product images
            self.redis.set(
                f"product_images:{business_url}",
                product_images,
                ex=86400  # 24 hours
            )
            redis_keys.append(f"product_images:{business_url}")

            # Store competitor insights
            if competitor_insights:
                self.redis.set(
                    f"competitors:{business_url}",
                    [c.dict() for c in competitor_insights],
                    ex=86400
                )
                redis_keys.append(f"competitors:{business_url}")

            # Store trends
            if industry_trends:
                self.redis.set(
                    f"trends:{business_context.industry}",
                    industry_trends.dict(),
                    ex=86400
                )
                redis_keys.append(f"trends:{business_context.industry}")

            logger.info(f"✅ Stored {len(redis_keys)} keys in Redis")

        except Exception as e:
            logger.error(f"Redis storage error: {e}")

        return redis_keys


# Global instance
_research_agent = None


def get_research_agent() -> ResearchAgent:
    """Get or create research agent instance"""
    global _research_agent
    if _research_agent is None:
        _research_agent = ResearchAgent()
    return _research_agent

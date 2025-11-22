"""
Agent 2: Brand Strategy Agent
Creates data-driven 7-day content strategy based on research
"""

import logging
from typing import Optional
from datetime import datetime

from models import ContentStrategy, DayPlan, ResearchOutput
from services.gemini_service import get_gemini_service
from services.redis_service import get_redis_service

logger = logging.getLogger(__name__)


class StrategyAgent:
    """
    Agent 2: Brand Strategy

    Responsibilities:
    1. Retrieve similar past campaigns from Redis (vector search)
    2. Analyze what content performed best
    3. Incorporate competitor insights and trends
    4. Generate 7-day content calendar with Claude
    5. Validate and store strategy
    """

    def __init__(self):
        self.gemini = get_gemini_service()
        self.redis = get_redis_service()

    async def create_strategy(
        self,
        research_output: ResearchOutput,
        campaign_id: str
    ) -> ContentStrategy:
        """
        Create 7-day content strategy

        Args:
            research_output: Output from Research Agent
            campaign_id: Campaign ID

        Returns:
            7-day content strategy
        """
        logger.info(f"🎯 Agent 2 creating strategy for campaign {campaign_id}")

        try:
            business_context = research_output.business_context
            brand_voice = business_context.brand_voice

            # Step 1: Retrieve similar past campaigns
            similar_campaigns = await self._get_similar_campaigns(business_context)

            # Step 2: Prepare context for strategy generation
            strategy_context = {
                "business_context": business_context.dict(),
                "brand_voice": brand_voice.dict() if brand_voice else {},
                "competitor_insights": [c.dict() for c in research_output.competitor_insights],
                "industry_trends": research_output.industry_trends.dict() if research_output.industry_trends else None,
                "similar_campaigns": similar_campaigns
            }

            # Step 3: Generate strategy with Gemini
            strategy_data = self.gemini.generate_content_strategy(
                business_context=business_context.dict(),
                brand_voice=brand_voice.dict() if brand_voice else {},
                competitor_insights=[c.dict() for c in research_output.competitor_insights],
                industry_trends=research_output.industry_trends.dict() if research_output.industry_trends else None
            )

            # Step 4: Parse days
            days = []
            for day_data in strategy_data.get("days", []):
                day_plan = DayPlan(
                    day=day_data.get("day", 1),
                    theme=day_data.get("theme") or "",
                    content_type=day_data.get("content_type") or "image",
                    caption_direction=day_data.get("caption_direction") or "",
                    image_concept=day_data.get("image_concept") or "",
                    video_concept=day_data.get("video_concept"),
                    cta=day_data.get("cta") or "",
                    hashtags=day_data.get("hashtags") or [],
                    optimal_post_time=day_data.get("optimal_post_time") or "10:00"
                )
                days.append(day_plan)

            # Ensure we have 7 days
            while len(days) < 7:
                days.append(self._create_default_day(len(days) + 1, business_context.industry))

            strategy = ContentStrategy(
                business_url=business_context.business_url,
                campaign_id=campaign_id,
                created_at=datetime.now(),
                days=days
            )

            # Step 5: Store strategy in Redis
            await self._store_strategy(campaign_id, strategy)

            logger.info(f"✅ Agent 2 strategy complete: 7 days planned")
            return strategy

        except Exception as e:
            logger.error(f"❌ Agent 2 strategy generation failed: {e}", exc_info=True)
            # Return fallback strategy
            return self._create_fallback_strategy(campaign_id, research_output)

    async def _get_similar_campaigns(self, business_context) -> list:
        """Retrieve similar past campaigns from Redis vector search"""
        try:
            # Create query from business context
            query_text = f"{business_context.industry} {' '.join(business_context.products[:3])}"
            query_embedding = self.gemini.get_embedding(query_text)

            # Vector search for similar campaigns
            similar = self.redis.get_similar_campaigns(
                query_embedding=query_embedding,
                industry=business_context.industry,
                top_k=3
            )

            logger.info(f"Found {len(similar)} similar campaigns")
            return similar

        except Exception as e:
            logger.warning(f"Similar campaign search failed: {e}")
            return []

    async def _store_strategy(self, campaign_id: str, strategy: ContentStrategy):
        """Store strategy in Redis"""
        try:
            self.redis.set(
                f"strategy:{campaign_id}",
                strategy.dict(),
                ex=604800  # 7 days
            )
            logger.info(f"✅ Strategy stored in Redis")

        except Exception as e:
            logger.error(f"Failed to store strategy: {e}")

    def _create_default_day(self, day: int, industry: str) -> DayPlan:
        """Create a default day plan"""
        themes = {
            1: "Behind the scenes",
            2: "Product showcase",
            3: "Customer testimonial",
            4: "Educational content",
            5: "Team highlight",
            6: "User-generated content",
            7: "Weekly recap"
        }

        return DayPlan(
            day=day,
            theme=themes.get(day, "General content"),
            content_type="image",
            caption_direction=f"Share {themes.get(day, 'content').lower()} in an engaging way",
            image_concept=f"Professional {industry} image showing {themes.get(day, 'content').lower()}",
            cta="Learn more",
            hashtags=[f"#{industry.lower().replace(' ', '')}", "#business", "#socialmedia"],
            optimal_post_time="10:00"
        )

    def _create_fallback_strategy(
        self,
        campaign_id: str,
        research_output: ResearchOutput
    ) -> ContentStrategy:
        """Create fallback strategy if generation fails"""
        logger.warning("Using fallback strategy")

        business_context = research_output.business_context

        days = [
            self._create_default_day(i + 1, business_context.industry)
            for i in range(7)
        ]

        return ContentStrategy(
            business_url=business_context.business_url,
            campaign_id=campaign_id,
            created_at=datetime.now(),
            days=days
        )


# Global instance
_strategy_agent = None


def get_strategy_agent() -> StrategyAgent:
    """Get or create strategy agent instance"""
    global _strategy_agent
    if _strategy_agent is None:
        _strategy_agent = StrategyAgent()
    return _strategy_agent

"""
Agent 4: Orchestration & Publishing Agent
Publishes content to Sanity CMS and schedules social media posts
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from models import OrchestrationOutput, CreativeOutput, ContentStrategy
from services.sanity_service import get_sanity_service
from services.redis_service import get_redis_service

logger = logging.getLogger(__name__)


class OrchestrationAgent:
    """
    Agent 4: Orchestration & Publishing

    Responsibilities:
    1. Create campaign in Sanity CMS
    2. Publish all content pieces to Sanity
    3. Generate content calendar
    4. Schedule posts (via Postman API - optional)
    5. Provide dashboard URL for review
    """

    def __init__(self):
        self.sanity = get_sanity_service()
        self.redis = get_redis_service()

    async def orchestrate(
        self,
        creative_output: CreativeOutput,
        strategy: ContentStrategy,
        business_url: str,
        campaign_id: str
    ) -> OrchestrationOutput:
        """
        Orchestrate content publishing

        Args:
            creative_output: Creative content from Creative Agent
            strategy: Content strategy from Strategy Agent
            business_url: Business website URL
            campaign_id: Campaign ID

        Returns:
            Orchestration output with Sanity URLs and status
        """
        logger.info(f"📋 Agent 4 orchestrating campaign {campaign_id}")

        try:
            # Step 1: Create campaign in Sanity
            campaign_doc = self.sanity.create_campaign(
                campaign_id=campaign_id,
                business_url=business_url,
                created_at=datetime.now()
            )

            sanity_campaign_id = campaign_doc.get("_id", campaign_id)
            logger.info(f"✅ Created Sanity campaign: {sanity_campaign_id}")

            # Step 2: Publish all content pieces
            published_content = []
            for day_content in creative_output.days:
                content_doc = self.sanity.create_content(
                    campaign_id=sanity_campaign_id,
                    day=day_content.day,
                    caption=day_content.caption,
                    hashtags=day_content.hashtags,
                    image_url=day_content.image_url,
                    video_url=day_content.video_url,
                    scheduled_time=day_content.scheduled_time
                )

                published_content.append({
                    "day": day_content.day,
                    "sanity_id": content_doc.get("_id"),
                    "status": "scheduled"
                })

                logger.info(f"✅ Published Day {day_content.day} to Sanity")

            # Step 3: Generate content calendar summary
            calendar_summary = self._generate_calendar_summary(
                creative_output,
                strategy
            )

            # Step 4: Get Sanity Studio URL
            studio_url = self.sanity.get_studio_url(sanity_campaign_id)

            # Step 5: Store orchestration data in Redis
            await self._store_orchestration_data(
                campaign_id,
                sanity_campaign_id,
                published_content,
                calendar_summary
            )

            # Step 6: Schedule posts (optional - via Postman)
            scheduled_posts = await self._schedule_posts(
                creative_output,
                campaign_id
            )

            orchestration_output = OrchestrationOutput(
                campaign_id=campaign_id,
                sanity_campaign_id=sanity_campaign_id,
                sanity_studio_url=studio_url,
                published_content_ids=[c["sanity_id"] for c in published_content],
                calendar_summary=calendar_summary,
                status="completed",
                scheduled_posts=scheduled_posts,
                created_at=datetime.now()
            )

            logger.info(f"✅ Agent 4 orchestration complete: {len(published_content)} pieces published")
            return orchestration_output

        except Exception as e:
            logger.error(f"❌ Agent 4 orchestration failed: {e}", exc_info=True)
            raise

    def _generate_calendar_summary(
        self,
        creative_output: CreativeOutput,
        strategy: ContentStrategy
    ) -> Dict[str, Any]:
        """Generate content calendar summary"""
        calendar = {
            "total_days": len(creative_output.days),
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=6)).isoformat(),
            "content_breakdown": {
                "images": sum(1 for d in creative_output.days if d.content_type == "image"),
                "videos": sum(1 for d in creative_output.days if d.content_type == "video"),
                "carousels": sum(1 for d in creative_output.days if d.content_type == "carousel")
            },
            "themes": [
                {
                    "day": d.day,
                    "theme": d.theme,
                    "scheduled_time": d.scheduled_time
                }
                for d in creative_output.days
            ]
        }

        return calendar

    async def _schedule_posts(
        self,
        creative_output: CreativeOutput,
        campaign_id: str
    ) -> List[Dict[str, Any]]:
        """
        Schedule posts via Postman API (optional)

        Note: For hackathon, this is a placeholder.
        In production, would integrate with:
        - Postman API for social media scheduling
        - Platform-specific APIs (Instagram, Facebook, Twitter)
        """
        logger.info("📅 Scheduling posts...")

        scheduled = []

        try:
            # Calculate scheduled dates
            start_date = datetime.now()

            for day_content in creative_output.days:
                # Calculate post date (Day 1 = tomorrow, etc.)
                post_date = start_date + timedelta(days=day_content.day)
                post_datetime = post_date.replace(
                    hour=int(day_content.scheduled_time.split(":")[0]),
                    minute=int(day_content.scheduled_time.split(":")[1]),
                    second=0
                )

                scheduled_post = {
                    "day": day_content.day,
                    "scheduled_datetime": post_datetime.isoformat(),
                    "platform": "instagram",  # Default platform
                    "status": "scheduled",
                    "post_id": f"post_{campaign_id}_day{day_content.day}"
                }

                scheduled.append(scheduled_post)

            logger.info(f"✅ Scheduled {len(scheduled)} posts")

        except Exception as e:
            logger.warning(f"Post scheduling failed: {e}")

        return scheduled

    async def _store_orchestration_data(
        self,
        campaign_id: str,
        sanity_campaign_id: str,
        published_content: List[Dict],
        calendar_summary: Dict
    ):
        """Store orchestration data in Redis"""
        try:
            orchestration_data = {
                "sanity_campaign_id": sanity_campaign_id,
                "published_content": published_content,
                "calendar_summary": calendar_summary,
                "status": "completed",
                "completed_at": datetime.now().isoformat()
            }

            self.redis.set(
                f"orchestration:{campaign_id}",
                orchestration_data,
                ex=604800  # 7 days
            )

            logger.info(f"✅ Orchestration data stored in Redis")

        except Exception as e:
            logger.error(f"Failed to store orchestration data: {e}")

    async def get_campaign_status(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign status from Redis"""
        try:
            data = self.redis.get(f"orchestration:{campaign_id}")
            if data:
                return data
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to get campaign status: {e}")
            return None


# Global instance
_orchestration_agent = None


def get_orchestration_agent() -> OrchestrationAgent:
    """Get or create orchestration agent instance"""
    global _orchestration_agent
    if _orchestration_agent is None:
        _orchestration_agent = OrchestrationAgent()
    return _orchestration_agent

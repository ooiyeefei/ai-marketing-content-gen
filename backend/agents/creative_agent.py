"""
Agent 3: Creative Agent
Generates captions and images for each day
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from models import CreativeOutput, DayContent, ContentStrategy
from services.gemini_service import get_gemini_service
from services.vertex_service import get_vertex_service
from services.aws_service import get_aws_service
from services.redis_service import get_redis_service

logger = logging.getLogger(__name__)


class CreativeAgent:
    """
    Agent 3: Creative Generation

    Responsibilities:
    1. Generate engaging captions for each day
    2. Generate images with Imagen 3 (using product images as reference)
    3. Select best images from generated options
    4. Upload to S3
    5. Store in Redis
    """

    def __init__(self):
        self.gemini = get_gemini_service()
        self.vertex = get_vertex_service()
        self.aws = get_aws_service()
        self.redis = get_redis_service()

    async def create_content(
        self,
        strategy: ContentStrategy,
        product_images: List[str],
        campaign_id: str
    ) -> CreativeOutput:
        """
        Generate creative content for all 7 days

        Args:
            strategy: Content strategy from Strategy Agent
            product_images: Product images from Research Agent
            campaign_id: Campaign ID

        Returns:
            Creative output with captions and images for 7 days
        """
        logger.info(f"🎨 Agent 3 creating content for campaign {campaign_id}")

        try:
            days_content = []

            for day_plan in strategy.days:
                logger.info(f"Creating content for Day {day_plan.day}: {day_plan.theme}")

                # Step 1: Generate caption
                caption = await self._generate_caption(
                    day_plan,
                    strategy.days[0].theme if strategy.days else None  # brand_voice info
                )

                # Step 2: Generate images
                images = await self._generate_images(
                    day_plan,
                    product_images,
                    campaign_id,
                    day_plan.day
                )

                # Step 3: Select best image
                best_image = images[0] if images else None

                # Step 4: Generate video (optional) - using image-to-video
                video_url = None
                if day_plan.content_type == "video" and day_plan.video_concept:
                    video_url = await self._generate_video(
                        day_plan,
                        product_images,  # Pass product images for image-to-video
                        campaign_id,
                        day_plan.day
                    )

                # Step 5: Create day content
                day_content = DayContent(
                    day=day_plan.day,
                    theme=day_plan.theme,
                    content_type=day_plan.content_type,
                    caption=caption,
                    hashtags=day_plan.hashtags,
                    image_url=best_image,
                    video_url=video_url,
                    cta=day_plan.cta,
                    scheduled_time=day_plan.optimal_post_time
                )

                days_content.append(day_content)

                # Step 6: Store in Redis
                await self._store_day_content(campaign_id, day_content)

            creative_output = CreativeOutput(
                campaign_id=campaign_id,
                days=days_content,
                total_images_generated=len(strategy.days) * 2,  # 2 per day
                total_videos_generated=sum(1 for d in days_content if d.video_url),
                created_at=datetime.now()
            )

            logger.info(f"✅ Agent 3 content complete: {len(days_content)} days, {creative_output.total_images_generated} images")
            return creative_output

        except Exception as e:
            logger.error(f"❌ Agent 3 creative generation failed: {e}", exc_info=True)
            raise

    async def _generate_caption(
        self,
        day_plan,
        brand_context: Optional[str] = None
    ) -> str:
        """Generate engaging caption for a day"""
        logger.info(f"Generating caption for: {day_plan.theme}")

        try:
            caption_data = self.gemini.generate_caption(
                day_plan=day_plan.dict(),
                brand_voice={
                    "tone": "professional",
                    "style": "engaging"
                }  # TODO: Use actual brand voice
            )

            caption = caption_data.get("full_caption", "")

            logger.info(f"✅ Caption generated ({len(caption)} chars)")
            return caption

        except Exception as e:
            logger.error(f"Caption generation error: {e}")
            # Fallback caption
            return f"{day_plan.caption_direction}\n\n{day_plan.cta}\n\n{' '.join(day_plan.hashtags)}"

    async def _generate_images(
        self,
        day_plan,
        product_images: List[str],
        campaign_id: str,
        day: int
    ) -> List[str]:
        """Generate images for a day"""
        logger.info(f"Generating images for: {day_plan.theme}")

        try:
            # Create image prompt from concept
            image_prompt = day_plan.image_concept

            # Use product images as style references (first 3)
            reference_images = product_images[:3] if product_images else None

            # Generate 2 image options
            generated_images = await self.vertex.generate_image(
                prompt=image_prompt,
                reference_images=reference_images,
                aspect_ratio="1:1",
                num_images=2
            )

            # Upload to S3
            uploaded_urls = []
            for i, image_data in enumerate(generated_images):
                s3_url = self.aws.upload_image(
                    image_data=image_data,
                    campaign_id=campaign_id,
                    day=day,
                    image_type=f"option{i+1}"
                )
                uploaded_urls.append(s3_url)

            logger.info(f"✅ Generated {len(uploaded_urls)} images")
            return uploaded_urls

        except Exception as e:
            logger.error(f"Image generation error: {e}")
            # Return placeholder
            return ["https://placehold.co/600x600/4285F4/white?text=Image"]

    async def _generate_video(
        self,
        day_plan,
        product_images: List[str],
        campaign_id: str,
        day: int
    ) -> Optional[str]:
        """
        Generate video for a day using IMAGE-TO-VIDEO

        CRITICAL: Uses business product photos as input to ensure video
        looks exactly like the actual business products, not generic content.
        """
        logger.info(f"Generating video for: {day_plan.theme}")

        try:
            if not day_plan.video_concept:
                return None

            # Generate video with Veo 3.1 IMAGE-TO-VIDEO
            # Uses business product photos to create authentic product videos
            video_uri = await self.vertex.generate_video(
                prompt=day_plan.video_concept,
                product_images=product_images,  # Use actual business product photos
                duration_seconds=8,
                aspect_ratio="9:16"  # Instagram Reels format
            )

            if video_uri:
                # Upload to S3
                s3_url = self.aws.upload_video(
                    video_path=video_uri,
                    campaign_id=campaign_id,
                    day=day
                )
                logger.info(f"✅ Video generated and uploaded")
                return s3_url
            else:
                logger.info("⏭️  Video generation skipped")
                return None

        except Exception as e:
            logger.error(f"Video generation error: {e}")
            return None

    async def _store_day_content(self, campaign_id: str, day_content: DayContent):
        """Store day content in Redis"""
        try:
            self.redis.set(
                f"creative:{campaign_id}:day{day_content.day}",
                day_content.dict(),
                ex=604800  # 7 days
            )
            logger.info(f"✅ Day {day_content.day} content stored in Redis")

        except Exception as e:
            logger.error(f"Failed to store day content: {e}")


# Global instance
_creative_agent = None


def get_creative_agent() -> CreativeAgent:
    """Get or create creative agent instance"""
    global _creative_agent
    if _creative_agent is None:
        _creative_agent = CreativeAgent()
    return _creative_agent

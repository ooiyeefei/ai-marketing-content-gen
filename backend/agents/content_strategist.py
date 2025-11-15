import logging
from typing import Dict, List
import json
from google import genai
from google.genai import types as genai_types
from config import settings

logger = logging.getLogger(__name__)


class ContentStrategistAgent:
    """
    Agent 2: Creates 7-day content calendar with video concepts.
    Takes business profile from Agent 1 and generates strategic content plan.
    """

    def __init__(self):
        self.genai_client = genai.Client(
            vertexai=True,
            project=settings.project_id,
            location=settings.region
        )

    async def create_calendar(self, business_profile: Dict, days: int = 7) -> List[Dict]:
        """
        Generate N-day content calendar with posts for each day.

        Args:
            business_profile: Business context from Agent 1
            days: Number of days to generate (1-7)

        Returns list of N content plans with:
        - day (1-N)
        - platform (instagram, facebook, etc.)
        - concept (post idea)
        - video_prompts (list of exactly 3 prompts for video segments)
        - image_prompts (list of exactly 3 prompts for image generation)
        - caption_theme (theme for caption)
        - cta (call to action)
        """
        logger.info(f"Content Strategist Agent: Creating {days}-day calendar...")

        # Build context for strategy
        context = self._build_strategy_context(business_profile)

        # Generate calendar with Gemini
        calendar = await self._generate_calendar(context, business_profile, days)

        logger.info(f"Content Strategist Agent: Created {len(calendar)} posts")
        return calendar

    def _build_strategy_context(self, profile: Dict) -> str:
        """Build context string for calendar generation"""
        business_name = profile.get('business_name', 'the business')
        themes = profile.get('content_themes', [])
        review_themes = profile.get('from_maps', {}).get('review_themes', [])
        trending = profile.get('local_trends', {}).get('trending_topics', [])
        brand_voice = profile.get('brand_voice', 'professional')

        context = f"""Business: {business_name}
Brand Voice: {brand_voice}
Content Themes: {', '.join(themes)}
Customer Praise Points: {', '.join(review_themes)}
Local Trending Topics: {', '.join(trending)}"""

        return context

    async def _generate_calendar(self, context: str, profile: Dict, days: int = 7) -> List[Dict]:
        """Generate N-day content calendar using Gemini"""
        try:
            prompt = f"""You are a social media strategist creating a {days}-day content calendar.

Context:
{context}

Create {days} engaging social media posts (one per day) following these rules:

1. Each post must have EXACTLY 3 video prompts ({settings.video_duration_seconds} seconds each)
2. Each post must have EXACTLY 3 image prompts (for static images)
3. Video prompts should tell a story (scene 1 → scene 2 → scene 3)
4. Image prompts should capture key moments or product highlights
5. Incorporate local trends where relevant
6. Vary content across the week (don't repeat concepts)
7. Each prompt should be HIGHLY SPECIFIC and VISUAL

Return a JSON array with {days} objects, each with:
- day (1-{days})
- platform ("instagram")
- concept (brief post idea)
- video_prompts (array of EXACTLY 3 specific visual prompts for Veo video generation)
- image_prompts (array of EXACTLY 3 specific image prompts for Imagen generation)
- caption_theme (theme for caption, e.g., "heritage recipe story")
- cta (call to action)

Example video_prompts:
- "Close-up shot of hands pulling fresh noodles, steam rising, bright kitchen lighting"
- "Wide shot of chef tossing noodles in wok with flames, dynamic action"
- "Happy customer taking first bite, expression of delight, cozy restaurant ambiance"

Example image_prompts:
- "Professional photo of signature noodle dish, top-down view, garnished with herbs, on wooden table"
- "High-quality portrait of smiling chef in kitchen, natural lighting, authentic atmosphere"
- "Beautiful interior shot of restaurant dining area, warm ambiance, customers in background"

CRITICAL: All prompts must be:
- Highly visual and specific
- Sequential for videos (tell a story when combined)
- Include lighting, camera angle, action details
- EXACTLY 3 video prompts and EXACTLY 3 image prompts per post

Return ONLY valid JSON."""

            response = self.genai_client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.7,
                )
            )

            # Parse JSON response
            text = response.text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()

            calendar = json.loads(text)

            # Validate structure
            for i, post in enumerate(calendar, 1):
                if 'day' not in post:
                    post['day'] = i
                if 'platform' not in post:
                    post['platform'] = 'instagram'

                # Ensure video_prompts exists and has exactly 3 items
                if 'video_prompts' not in post or not post['video_prompts']:
                    post['video_prompts'] = [post.get('concept', 'business content')] * settings.max_videos_per_post
                if isinstance(post['video_prompts'], str):
                    post['video_prompts'] = [post['video_prompts']]

                # Enforce exactly 3 video prompts
                while len(post['video_prompts']) < settings.max_videos_per_post:
                    post['video_prompts'].append(post['video_prompts'][0])  # Duplicate first prompt if needed
                post['video_prompts'] = post['video_prompts'][:settings.max_videos_per_post]

                # Ensure image_prompts exists and has exactly 3 items
                if 'image_prompts' not in post or not post['image_prompts']:
                    post['image_prompts'] = [f"Professional photo of {post.get('concept', 'business content')}"] * settings.max_images_per_post
                if isinstance(post['image_prompts'], str):
                    post['image_prompts'] = [post['image_prompts']]

                # Enforce exactly 3 image prompts
                while len(post['image_prompts']) < settings.max_images_per_post:
                    post['image_prompts'].append(post['image_prompts'][0])  # Duplicate first prompt if needed
                post['image_prompts'] = post['image_prompts'][:settings.max_images_per_post]

            return calendar[:7]  # Ensure exactly 7 posts

        except Exception as e:
            logger.error(f"Error generating calendar: {e}")
            # Return fallback calendar
            return self._generate_fallback_calendar(profile)

    def _generate_fallback_calendar(self, profile: Dict) -> List[Dict]:
        """Fallback calendar if generation fails"""
        business_name = profile.get('business_name', 'our business')

        return [
            {
                'day': 1,
                'platform': 'instagram',
                'concept': 'Product showcase',
                'video_prompts': [
                    f"Close-up of signature product at {business_name}, warm lighting",
                    f"Medium shot of product being prepared, professional setting",
                    f"Wide shot of final product display, attractive presentation"
                ],
                'image_prompts': [
                    f"Professional photo of signature product at {business_name}, top-down view",
                    f"High-quality product shot with natural lighting",
                    f"Product detail close-up, artistic composition"
                ],
                'caption_theme': 'product highlight',
                'cta': 'Visit us today'
            },
            {
                'day': 2,
                'platform': 'instagram',
                'concept': 'Behind the scenes',
                'video_prompts': [
                    f"Team member working at {business_name}, candid shot",
                    f"Process in action, dynamic movement",
                    f"Team collaboration, authentic atmosphere"
                ],
                'image_prompts': [
                    f"Professional photo of workspace at {business_name}",
                    f"Team member portrait in working environment",
                    f"Process detail shot, documentary style"
                ],
                'caption_theme': 'behind-the-scenes',
                'cta': 'See more on our page'
            },
            {
                'day': 3,
                'platform': 'instagram',
                'concept': 'Customer testimonial',
                'video_prompts': [
                    f"Happy customer at {business_name}, smiling",
                    f"Customer enjoying product or service",
                    f"Customer interaction, genuine moment"
                ],
                'image_prompts': [
                    f"Professional photo of satisfied customer at {business_name}",
                    f"Customer experience moment, natural lighting",
                    f"Customer testimonial portrait, warm atmosphere"
                ],
                'caption_theme': 'customer story',
                'cta': 'Share your experience'
            },
            {
                'day': 4,
                'platform': 'instagram',
                'concept': 'Process video',
                'video_prompts': [
                    f"Step 1 of process at {business_name}, clear view",
                    f"Step 2 of process, action in progress",
                    f"Final step, completed result"
                ],
                'image_prompts': [
                    f"Professional photo of process step 1 at {business_name}",
                    f"Process step 2, detailed view",
                    f"Final result, polished presentation"
                ],
                'caption_theme': 'how we do it',
                'cta': 'Learn more'
            },
            {
                'day': 5,
                'platform': 'instagram',
                'concept': 'Team introduction',
                'video_prompts': [
                    f"Team member waving at camera at {business_name}",
                    f"Team member at work, natural environment",
                    f"Team member personality moment"
                ],
                'image_prompts': [
                    f"Professional portrait of team member at {business_name}",
                    f"Team member in action shot",
                    f"Team member casual portrait, friendly atmosphere"
                ],
                'caption_theme': 'meet the team',
                'cta': 'Follow us'
            },
            {
                'day': 6,
                'platform': 'instagram',
                'concept': 'Special offer',
                'video_prompts': [
                    f"Product with promotional text overlay at {business_name}",
                    f"Offer details highlighted, clear view",
                    f"Call to action moment, engaging"
                ],
                'image_prompts': [
                    f"Professional promotional image for {business_name}",
                    f"Special offer graphic, clean design",
                    f"Product with offer highlight, eye-catching"
                ],
                'caption_theme': 'special offer',
                'cta': 'Book now'
            },
            {
                'day': 7,
                'platform': 'instagram',
                'concept': 'Week recap',
                'video_prompts': [
                    f"Best moment 1 from week at {business_name}",
                    f"Best moment 2 from week, diverse content",
                    f"Best moment 3 from week, strong finish"
                ],
                'image_prompts': [
                    f"Professional photo collage of week's highlights at {business_name}",
                    f"Week's best moment, standout image",
                    f"Thank you message graphic, warm design"
                ],
                'caption_theme': 'weekly highlight',
                'cta': 'See you next week'
            }
        ]

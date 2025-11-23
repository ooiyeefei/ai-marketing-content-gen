import os
from google import genai
from google.genai import types
from typing import Dict, List, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Gemini 3.0 Pro service for AI analysis and content generation.

    Thinking Levels:
    - HIGH: Complex analysis, strategic insights, pattern recognition
    - LOW: High-throughput generation, template-based content
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-3-pro-preview"
        logger.info("✓ Gemini 3.0 Pro initialized")

    # ========================================================================
    # HIGH Thinking: Strategic Analysis
    # ========================================================================

    async def analyze_customer_sentiment(
        self,
        reviews: List[Dict[str, Any]],
        business_name: str
    ) -> Dict[str, Any]:
        """
        Analyze customer reviews with HIGH thinking.

        Returns:
        {
            "positive_themes": ["fresh ingredients", "authentic taste"],
            "negative_themes": ["slow service on weekends"],
            "popular_items": ["spicy tuna roll", "sake selection"],
            "quotable_reviews": ["The freshest sushi in SF!"],
            "content_opportunities": ["Showcase ingredient sourcing"]
        }
        """
        prompt = f"""Analyze these {len(reviews)} reviews for {business_name}.

Extract:
1. Common positive themes (what customers love)
2. Common negative themes (pain points to address)
3. Specific dishes/products mentioned frequently
4. Service quality indicators
5. Quotable customer praise for content
6. Content opportunities based on feedback

Provide actionable insights for content strategy.

Reviews:
{json.dumps(reviews, indent=2)}

Output as JSON with keys: positive_themes, negative_themes, popular_items,
quotable_reviews, content_opportunities"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="high"),
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)
            logger.info(f"✓ Sentiment analysis complete for {business_name}")
            return result

        except Exception as e:
            logger.error(f"✗ Gemini sentiment analysis failed: {e}")
            raise

    async def analyze_performance_patterns(
        self,
        posts: List[Dict[str, Any]],
        business_name: str
    ) -> Dict[str, Any]:
        """
        Analyze past social media performance with HIGH thinking.

        Returns:
        {
            "winning_patterns": {
                "content_types": ["video > carousel > photo"],
                "themes": ["behind-the-scenes kitchen"],
                "best_posting_times": ["7-9 PM weekdays"],
                "effective_hashtags": ["#SushiArt"]
            },
            "avoid_patterns": {
                "low_performers": ["generic food photos"],
                "reasons": ["lack of storytelling"]
            },
            "recommendations": ["Increase video content by 40%"]
        }
        """
        prompt = f"""Analyze these past {len(posts)} social media posts for {business_name}.

Identify:
1. What content types performed best? (photos/videos/carousels)
2. What themes drove highest engagement?
3. What posting times worked best?
4. What hashtags performed well?
5. What content flopped and why?
6. Patterns in successful vs unsuccessful posts

Provide specific recommendations for future content.

Post Performance Data:
{json.dumps(posts, indent=2)}

Output as JSON with keys: winning_patterns, avoid_patterns, recommendations"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="high"),
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)
            logger.info(f"✓ Performance analysis complete for {business_name}")
            return result

        except Exception as e:
            logger.error(f"✗ Gemini performance analysis failed: {e}")
            raise

    async def create_content_strategy(
        self,
        business_context: Dict[str, Any],
        market_insights: Dict[str, Any],
        customer_sentiment: Dict[str, Any],
        past_performance: Optional[Dict[str, Any]],
        market_trends: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Create 7-day content strategy with HIGH thinking.

        Returns:
        {
            "days": [
                {
                    "day": 1,
                    "theme": "Behind the Scenes: The Art of Sushi",
                    "content_type": "video",
                    "message": "Showcase ingredient sourcing",
                    "hashtags": ["#SushiArt", "#FreshDaily"],
                    "cta": "Book your omakase experience",
                    "rationale": "Addresses market gap + customer positive theme"
                }
            ]
        }
        """
        business_name = business_context.get("business_name")

        prompt = f"""You are creating a 7-day social media campaign for {business_name}.

Synthesize these insights into a content strategy:

COMPETITIVE INTELLIGENCE:
- Market gaps: {market_insights.get('market_gaps', [])}
- Positioning opportunities: {market_insights.get('positioning_opportunities', [])}
- Trending topics: {market_insights.get('trending_topics', [])}

CUSTOMER SENTIMENT & PAST PERFORMANCE:
- What customers love: {customer_sentiment.get('positive_themes', [])}
- Popular items: {customer_sentiment.get('popular_items', [])}
- What worked before: {past_performance.get('winning_patterns', {}) if past_performance else 'No past data'}
- What to avoid: {past_performance.get('avoid_patterns', {}) if past_performance else 'N/A'}

MARKET TRENDS:
- Trending searches: {market_trends.get('trending_searches', [])}
- Rising topics: {market_trends.get('rising_topics', [])}

Create a 7-day content plan with:
1. Daily theme (based on what works + market gaps)
2. Content type (photo/video based on performance data)
3. Key message (addressing customer interests + market gaps)
4. Hashtag strategy (trending + proven performers)
5. Call-to-action
6. Rationale for each day's choice

Output as JSON:
{{
  "days": [
    {{
      "day": 1,
      "theme": "...",
      "content_type": "video|photo|carousel",
      "message": "...",
      "hashtags": ["#...", "#..."],
      "cta": "...",
      "rationale": "..."
    }}
  ]
}}"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="high"),
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)
            logger.info(f"✓ Content strategy created for {business_name}")
            return result

        except Exception as e:
            logger.error(f"✗ Gemini content strategy failed: {e}")
            raise

    # ========================================================================
    # LOW Thinking: High-Throughput Content Generation
    # ========================================================================

    async def generate_caption(
        self,
        day_plan: Dict[str, Any],
        business_context: Dict[str, Any]
    ) -> str:
        """
        Generate Instagram caption with LOW thinking (fast).
        """
        business_name = business_context.get("business_name")
        brand_voice = business_context.get("brand_voice", "professional")

        prompt = f"""Write an Instagram caption for {business_name}.

Theme: {day_plan['theme']}
Key Message: {day_plan['message']}
Brand Voice: {brand_voice}

Format:
- Hook (attention-grabbing first line)
- Body (2-3 sentences, tell a story)
- Call-to-action: {day_plan['cta']}
- Hashtags: {', '.join(day_plan['hashtags'])}

Keep it {brand_voice} and engaging.
Max 150 words.

Output only the caption text (no JSON, no explanation)."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="low")
                )
            )

            caption = response.text.strip()
            logger.info(f"✓ Caption generated for Day {day_plan['day']}")
            return caption

        except Exception as e:
            logger.error(f"✗ Gemini caption generation failed: {e}")
            raise

    async def generate_image_prompt(
        self,
        day_plan: Dict[str, Any],
        business_context: Dict[str, Any],
        customer_favorites: List[str]
    ) -> str:
        """
        Generate MiniMax image prompt with LOW thinking (fast).
        """
        business_name = business_context.get("business_name")
        industry = business_context.get("industry")

        prompt = f"""Create a detailed image generation prompt for:

Day {day_plan['day']}: {day_plan['theme']}
Business: {business_name} ({industry})
Style: Professional, Instagram-ready, commercial photography
Key Message: {day_plan['message']}

Reference: Use these customer favorites for style inspiration:
{', '.join(customer_favorites)}

Output: A single concise prompt (max 200 chars).
No JSON, just the prompt text."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="low")
                )
            )

            image_prompt = response.text.strip()
            logger.info(f"✓ Image prompt generated for Day {day_plan['day']}")
            return image_prompt

        except Exception as e:
            logger.error(f"✗ Gemini image prompt generation failed: {e}")
            raise

    async def generate_video_motion_prompt(
        self,
        day_plan: Dict[str, Any],
        business_name: str
    ) -> str:
        """
        Generate MiniMax video motion prompt with LOW thinking (fast).
        """
        prompt = f"""Create a video motion prompt for:

Theme: {day_plan['theme']}
Business: {business_name}

The video will animate a static image.

Describe the desired motion/animation (subtle and professional):
- Camera movement (pan, zoom, tilt)
- Scene dynamics (steam rising, ingredients moving, etc.)
- Duration: 6 seconds

Output: A concise motion description (max 150 chars).
No JSON, just the motion prompt."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="low")
                )
            )

            motion_prompt = response.text.strip()
            logger.info(f"✓ Video motion prompt generated for Day {day_plan['day']}")
            return motion_prompt

        except Exception as e:
            logger.error(f"✗ Gemini video motion prompt failed: {e}")
            raise

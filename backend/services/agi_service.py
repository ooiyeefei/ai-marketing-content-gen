import os
import httpx
from typing import Dict, List, Any, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)


class AGIService:
    """
    AGI API service for intelligent web research.

    Capabilities:
    - Multi-step web navigation
    - Business context extraction
    - Intelligent competitor discovery
    - Deep competitor research
    - Market trend synthesis
    """

    def __init__(self):
        self.api_key = os.getenv("AGI_API_KEY")
        if not self.api_key:
            raise ValueError("AGI_API_KEY environment variable not set")

        self.base_url = "https://api.agi.tech/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logger.info(" AGI API initialized")

    async def extract_business_context(self, business_url: str) -> Dict[str, Any]:
        """
        Extract business information from website.

        Returns:
        {
            "business_name": "Ozumo",
            "industry": "restaurant",
            "cuisine": "Japanese",
            "location": {"city": "San Francisco", "state": "CA", "country": "USA"},
            "price_range": "premium",
            "specialties": ["sushi", "sake", "omakase"],
            "brand_voice": "elegant, traditional, authentic",
            "description": "..."
        }
        """
        task_prompt = f"""
        Navigate to {business_url} and extract comprehensive business information:

        1. Business name
        2. Type of business (restaurant, retail, service, etc.)
        3. Industry-specific details:
           - If restaurant: cuisine type, price range
           - If retail: product categories
           - If service: service types
        4. Physical location (city, state, country)
        5. Key products/services offered
        6. Brand messaging and tone (elegant, casual, professional, etc.)
        7. Target audience (if mentioned)
        8. Specialties or unique selling points

        Output as JSON with these keys: business_name, industry, description, location,
        price_range, specialties, brand_voice, target_audience
        """

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/tasks",
                    headers=self.headers,
                    json={
                        "task": task_prompt,
                        "url": business_url,
                        "output_format": "json"
                    }
                )
                response.raise_for_status()

                task_id = response.json()["task_id"]
                logger.info(f" AGI task created: {task_id}")

                # Poll for completion
                result = await self._poll_task(task_id, max_wait=300)

                return result

        except Exception as e:
            logger.error(f" AGI API error: {e}")
            raise

    async def discover_competitors(
        self,
        business_context: Dict[str, Any],
        num_competitors: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Intelligently discover competitors based on business context.

        Returns:
        [
            {
                "name": "Akiko's Restaurant",
                "website": "https://akikos.com",
                "location": "San Francisco, CA",
                "google_rating": 4.5,
                "review_count": 1234,
                "social_handles": {"instagram": "@akikossf"},
                "similarity_score": 0.9
            }
        ]
        """
        business_name = business_context.get("business_name")
        industry = business_context.get("industry")
        location = business_context.get("location", {})
        city = location.get("city")

        # Build search query based on industry
        if industry == "restaurant":
            cuisine = business_context.get("specialties", [""])[0]
            search_query = f"{cuisine} {industry} in {city}"
        else:
            search_query = f"{industry} in {city}"

        task_prompt = f"""
        Find the top {num_competitors} competitors for {business_name} in {city}.

        Search criteria:
        - Same industry: {industry}
        - Located in {city} or nearby areas
        - Similar price range: {business_context.get('price_range', 'any')}
        - Active online presence

        Research method:
        1. Search Google for '{search_query}'
        2. Visit Google Maps results
        3. For each competitor, extract:
           - Name
           - Website
           - Google rating
           - Review count
           - Social media handles (Instagram, Facebook)
           - Brief description

        Output as JSON array with these keys per competitor:
        name, website, location, google_rating, review_count, social_handles, description
        """

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/tasks",
                    headers=self.headers,
                    json={
                        "task": task_prompt,
                        "output_format": "json"
                    }
                )
                response.raise_for_status()

                task_id = response.json()["task_id"]
                logger.info(f" AGI competitor discovery task: {task_id}")

                # Poll for completion
                result = await self._poll_task(task_id, max_wait=600)

                return result.get("competitors", [])

        except Exception as e:
            logger.error(f" AGI competitor discovery failed: {e}")
            return []

    async def research_competitor(
        self,
        competitor_url: str,
        competitor_name: str
    ) -> Dict[str, Any]:
        """
        Deep research on a single competitor.

        Returns:
        {
            "competitor_name": "Akiko's Restaurant",
            "menu": [{"item": "Omakase", "price": "$150"}],
            "pricing_strategy": "premium",
            "brand_voice": "elegant, traditional",
            "top_content_themes": ["behind-the-scenes", "seasonal ingredients"],
            "differentiators": ["20+ years experience"],
            "hero_images": ["https://..."]
        }
        """
        task_prompt = f"""
        Deep research on competitor: {competitor_name} ({competitor_url})

        Extract:
        1. Menu items with prices (or product catalog)
        2. Special promotions or offers
        3. Brand messaging and tone
        4. Key differentiators mentioned on website
        5. If social media linked:
           - Navigate to Instagram/Facebook profile
           - Identify 5 most recent post themes
        6. Screenshot/save hero images or key visuals

        Output as JSON with these keys:
        competitor_name, menu, pricing_strategy, brand_voice, top_content_themes,
        differentiators, hero_images
        """

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/tasks",
                    headers=self.headers,
                    json={
                        "task": task_prompt,
                        "url": competitor_url,
                        "output_format": "json",
                        "capture_screenshots": True
                    }
                )
                response.raise_for_status()

                task_id = response.json()["task_id"]
                logger.info(f" AGI competitor research task: {task_id}")

                result = await self._poll_task(task_id, max_wait=600)

                return result

        except Exception as e:
            logger.error(f" AGI competitor research failed: {e}")
            return {}

    async def scrape_online_reviews(
        self,
        business_name: str,
        location: Dict[str, str],
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Scrape online reviews when GMB API unavailable (business not claimed).

        Fallback strategy for businesses without claimed Google My Business profile.

        Returns:
        {
            "reviews": [
                {"rating": 5, "text": "...", "date": "2025-01-15", "source": "Google Maps", "reviewer_name": "John D."}
            ],
            "customer_photos": ["https://maps.google.com/..."],
            "overall_rating": 4.5,
            "total_reviews": 234,
            "sources": ["Google Maps", "Yelp", "TripAdvisor"]
        }
        """
        city = location.get("city", "")
        state = location.get("state", "")

        task_prompt = f"""
        Find and scrape online reviews for: {business_name} in {city}, {state}

        **Research Strategy:**
        1. Search Google Maps for "{business_name} {city}"
        2. Navigate to the business listing
        3. Extract:
           - Overall rating
           - Total review count
           - Up to {limit} most recent reviews (rating, text, date, reviewer name)
           - Customer-uploaded photos (URLs)

        4. If available, also check:
           - Yelp: "{business_name} {city}"
           - TripAdvisor (if applicable)

        5. Aggregate data from all sources

        **Output Requirements:**
        - Deduplicate reviews (same text from multiple sources)
        - Sort by date (most recent first)
        - Include source attribution (Google Maps, Yelp, etc.)
        - Extract photo URLs

        Output as JSON with keys:
        reviews (array of {{rating, text, date, source, reviewer_name}}),
        customer_photos (array of URLs),
        overall_rating (float),
        total_reviews (int),
        sources (array of source names)
        """

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/tasks",
                    headers=self.headers,
                    json={
                        "task": task_prompt,
                        "output_format": "json",
                        "capture_screenshots": True
                    }
                )
                response.raise_for_status()

                task_id = response.json()["task_id"]
                logger.info(f" AGI review scraping task: {task_id}")

                result = await self._poll_task(task_id, max_wait=600)

                # Ensure required keys exist
                return {
                    "reviews": result.get("reviews", []),
                    "customer_photos": result.get("customer_photos", []),
                    "overall_rating": result.get("overall_rating", 0.0),
                    "total_reviews": result.get("total_reviews", 0),
                    "sources": result.get("sources", ["AGI Scraped"])
                }

        except Exception as e:
            logger.error(f" AGI review scraping failed: {e}")
            return {
                "reviews": [],
                "customer_photos": [],
                "overall_rating": 0.0,
                "total_reviews": 0,
                "sources": []
            }

    async def analyze_market_trends(
        self,
        business_context: Dict[str, Any],
        competitors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesize market insights from competitors.

        Returns:
        {
            "trending_topics": ["sustainable seafood", "omakase experiences"],
            "market_gaps": ["late-night fusion", "vegetarian options"],
            "positioning_opportunities": ["Emphasize sustainability"]
        }
        """
        business_name = business_context.get("business_name")
        industry = business_context.get("industry")
        location = business_context.get("location", {})
        city = location.get("city")

        competitor_summary = "\n".join([
            f"- {c.get('name')}: {c.get('description', 'N/A')}"
            for c in competitors[:5]
        ])

        task_prompt = f"""
        Analyze the competitive landscape for {business_name} in {city}.

        Business: {business_name}
        Industry: {industry}
        Competitors:
        {competitor_summary}

        Research and synthesize:
        1. What's trending in {industry} in {city}?
        2. What are top competitors doing well?
        3. What gaps exist that no competitor is filling?
        4. What unique positioning opportunities exist for {business_name}?

        Use web search to supplement competitor data if needed.

        Output as JSON with keys:
        trending_topics (array), market_gaps (array), positioning_opportunities (array)
        """

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/tasks",
                    headers=self.headers,
                    json={
                        "task": task_prompt,
                        "output_format": "json"
                    }
                )
                response.raise_for_status()

                task_id = response.json()["task_id"]
                logger.info(f" AGI market trends task: {task_id}")

                result = await self._poll_task(task_id, max_wait=600)

                return result

        except Exception as e:
            logger.error(f" AGI market trends failed: {e}")
            return {
                "trending_topics": [],
                "market_gaps": [],
                "positioning_opportunities": []
            }

    async def _poll_task(self, task_id: str, max_wait: int = 300) -> Dict[str, Any]:
        """
        Poll AGI task until completion.

        Args:
            task_id: AGI task ID
            max_wait: Maximum wait time in seconds

        Returns:
            Task result JSON
        """
        waited = 0

        async with httpx.AsyncClient() as client:
            while waited < max_wait:
                response = await client.get(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=self.headers
                )
                response.raise_for_status()

                status_data = response.json()
                status = status_data.get("status")

                if status == "completed":
                    logger.info(f" AGI task completed: {task_id}")
                    return status_data.get("result", {})

                elif status == "failed":
                    error = status_data.get("error", "Unknown error")
                    logger.error(f" AGI task failed: {error}")
                    raise Exception(f"AGI task failed: {error}")

                # Still processing
                await asyncio.sleep(10)
                waited += 10

        raise TimeoutError(f"AGI task {task_id} timed out after {max_wait}s")

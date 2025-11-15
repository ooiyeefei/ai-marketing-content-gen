import logging
from typing import Dict, Optional
import json
from google import genai
from google.genai import types as genai_types

from services.google_services import GoogleServicesClient
from services.photo_scraper import PhotoScraper
from models import BusinessInput
from config import settings

logger = logging.getLogger(__name__)


class BusinessAnalystAgent:
    """
    Agent 1: Analyzes business context from website URL and address.
    Gathers data from Google Search, Maps Places API, Trends API, and scrapes photos.
    """

    def __init__(self):
        self.google_services = GoogleServicesClient()
        self.photo_scraper = PhotoScraper()
        try:
            self.genai_client = genai.Client(
                vertexai=True,
                project=settings.project_id,
                location=settings.region
            )
        except Exception as e:
            self.genai_client = None
            logger.warning(f"Failed to initialize Gemini client: {e}")

    async def analyze(self, business_input: BusinessInput) -> Dict:
        """
        Main analysis method that orchestrates data gathering.

        Returns enriched business profile with:
        - Website analysis
        - Maps data (reviews, ratings)
        - Local trends
        """
        logger.info("Business Analyst Agent: Starting analysis...")

        profile = {
            'business_name': business_input.business_name or '',
            'industry': business_input.industry or '',
            'brand_voice': business_input.brand_voice or 'professional',
            'from_website': {},
            'from_maps': {},
            'local_trends': {},
            'content_themes': [],
            'photos': []  # Will be populated from multiple sources
        }

        # Step 1: Analyze website if provided
        if business_input.website_url:
            logger.info(f"Analyzing website: {business_input.website_url}")
            website_data = self.google_services.analyze_website_with_search(
                str(business_input.website_url)
            )

            # Parse analysis with Gemini
            parsed_data = await self._parse_website_analysis(website_data['analysis'])
            profile['from_website'] = parsed_data

            # Update business name if not provided
            if not profile['business_name'] and 'business_name' in parsed_data:
                profile['business_name'] = parsed_data['business_name']

            # Scrape photos from the website/social media URL
            logger.info(f"Scraping photos from: {business_input.website_url}")
            scraped_photos = await self.photo_scraper.scrape_photos_from_url(
                str(business_input.website_url),
                max_photos=10
            )
            if scraped_photos:
                profile['photos'].extend(scraped_photos)
                logger.info(f"Scraped {len(scraped_photos)} photos from website/social media")

        # Step 2: Get Maps data if address provided
        if business_input.business_address:
            logger.info(f"Fetching Maps data for: {business_input.business_address}")
            maps_data = self.google_services.get_place_details(
                business_input.business_address
            )

            if maps_data:
                profile['from_maps'] = maps_data

                # Extract review themes
                review_themes = await self._extract_review_themes(
                    maps_data.get('review_themes', [])
                )
                profile['from_maps']['review_themes'] = review_themes

                # Update business name if not set
                if not profile['business_name'] and maps_data.get('name'):
                    profile['business_name'] = maps_data['name']

                # Get local trends based on business type
                business_types = maps_data.get('business_types', [])
                keywords = self._extract_keywords_from_types(business_types)

                logger.info(f"Fetching local trends for keywords: {keywords}")
                trends = self.google_services.get_local_trends(
                    location=business_input.business_address,
                    keywords=keywords
                )
                profile['local_trends'] = {
                    'trending_topics': trends,
                    'keywords_used': keywords
                }

                # Fetch business photos from Google Maps
                logger.info("Fetching business photos from Google Maps...")
                place_id = self._extract_place_id_from_maps_data(business_input.business_address)
                if place_id:
                    maps_photos = self.google_services.get_place_photos(place_id)
                    if maps_photos:
                        # Add to existing photos array (may already have social media photos)
                        profile['photos'].extend(maps_photos)
                        logger.info(f"Retrieved {len(maps_photos)} photos from Google Maps")
                    else:
                        logger.info("No photos available from Google Maps")
                else:
                    logger.warning("Could not extract place_id for photo fetching")

        # Step 3: Synthesize content themes
        profile['content_themes'] = await self._generate_content_themes(profile)

        # Log total photos collected
        total_photos = len(profile.get('photos', []))
        logger.info(f"Business Analyst Agent: Analysis complete. Collected {total_photos} photos total")

        return profile

    async def _parse_website_analysis(self, analysis_text: str) -> Dict:
        """Parse website analysis text into structured data"""
        if not self.genai_client or not analysis_text:
            logger.warning("Cannot parse website analysis - client not initialized or no text")
            return {}

        try:
            prompt = f"""Parse this website analysis into JSON format:

{analysis_text}

Return ONLY a valid JSON object with these keys:
- business_name (string)
- description (string)
- key_offerings (list of strings)
- brand_voice (string)
- target_audience (string)
- unique_value (string)

Example:
{{"business_name": "The Hawker", "description": "...", ...}}"""

            response = self.genai_client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.1,
                )
            )

            # Extract JSON from response
            text = response.text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()

            return json.loads(text)

        except Exception as e:
            logger.error(f"Error parsing website analysis: {e}")
            return {}

    async def _extract_review_themes(self, reviews: list) -> list:
        """Extract common themes from customer reviews"""
        if not reviews or not self.genai_client:
            return []

        try:
            reviews_text = "\n".join(reviews[:10])

            prompt = f"""Analyze these customer reviews and extract 3-5 key positive themes:

{reviews_text}

Return a JSON array of theme strings, e.g.:
["authentic taste", "generous portions", "friendly service"]"""

            response = self.genai_client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.2,
                )
            )

            text = response.text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()

            return json.loads(text)

        except Exception as e:
            logger.error(f"Error extracting review themes: {e}")
            return []

    def _extract_keywords_from_types(self, business_types: list) -> list:
        """Convert business types to search keywords"""
        keyword_map = {
            'restaurant': ['food', 'dining', 'cuisine'],
            'cafe': ['coffee', 'breakfast', 'brunch'],
            'retail': ['shopping', 'products'],
            'service': ['services', 'professional']
        }

        keywords = []
        for btype in business_types:
            for key, values in keyword_map.items():
                if key in btype.lower():
                    keywords.extend(values)

        return list(set(keywords))[:5] if keywords else ['business', 'local']

    def _extract_place_id_from_maps_data(self, address: str) -> Optional[str]:
        """
        Extract place_id from Google Maps geocoding result.

        Args:
            address: Business address

        Returns:
            place_id string or None
        """
        if not self.google_services.gmaps:
            return None

        try:
            geocode_result = self.google_services.gmaps.geocode(address)
            if geocode_result and len(geocode_result) > 0:
                place_id = geocode_result[0].get('place_id')
                logger.debug(f"Extracted place_id: {place_id}")
                return place_id
        except Exception as e:
            logger.error(f"Error extracting place_id: {e}")

        return None

    async def _generate_content_themes(self, profile: Dict) -> list:
        """Generate content themes based on business profile"""
        if not self.genai_client:
            logger.warning("Gemini client not initialized, returning fallback themes")
            return [
                "product highlights",
                "customer stories",
                "behind-the-scenes",
                "tips and advice",
                "special offers"
            ]

        try:
            prompt = f"""Based on this business profile, suggest 5 content themes for social media:

Business: {profile.get('business_name', 'Unknown')}
Description: {profile.get('from_website', {}).get('description', 'N/A')}
Review Themes: {profile.get('from_maps', {}).get('review_themes', [])}
Trending Topics: {profile.get('local_trends', {}).get('trending_topics', [])}

Return a JSON array of 5 specific content theme strings suitable for social media posts.
Example: ["behind-the-scenes cooking", "customer testimonials", "signature dish highlights"]"""

            response = self.genai_client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.5,
                )
            )

            text = response.text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()

            return json.loads(text)

        except Exception as e:
            logger.error(f"Error generating content themes: {e}")
            return [
                "product highlights",
                "customer stories",
                "behind-the-scenes",
                "tips and advice",
                "special offers"
            ]

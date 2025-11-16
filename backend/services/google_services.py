import logging
from typing import Dict, List, Optional
import googlemaps
from pytrends.request import TrendReq
from google import genai
from google.genai import types as genai_types
from config import settings
import httpx
import base64

logger = logging.getLogger(__name__)


class GoogleServicesClient:
    """Wrapper for Google APIs (Maps, Trends, Gemini)"""

    def __init__(self):
        # Initialize Google Maps client
        if settings.google_maps_api_key:
            try:
                self.gmaps = googlemaps.Client(key=settings.google_maps_api_key)
                self.api_key = settings.google_maps_api_key
            except Exception as e:
                self.gmaps = None
                self.api_key = None
                logger.warning(f"Failed to initialize Google Maps client: {e}")
        else:
            self.gmaps = None
            self.api_key = None
            logger.warning("Google Maps API key not configured")

        # Initialize Trends client
        try:
            self.trends = TrendReq(hl='en-US', tz=360)
        except Exception as e:
            self.trends = None
            logger.warning(f"Failed to initialize Trends client: {e}")

        # Initialize Gemini client (Vertex AI mode)
        try:
            self.genai_client = genai.Client(
                vertexai=True,
                project=settings.project_id,
                location=settings.region
            )
        except Exception as e:
            self.genai_client = None
            logger.warning(f"Failed to initialize Gemini client: {e}")

    def get_place_details(self, address: str) -> Optional[Dict]:
        """Get business details from Google Maps Places API"""
        if not self.gmaps:
            logger.warning("Google Maps client not initialized, returning None")
            return None

        try:
            # Geocode address
            geocode_result = self.gmaps.geocode(address)
            if not geocode_result:
                logger.warning(f"No geocode results for address: {address}")
                return None

            location = geocode_result[0]['geometry']['location']
            place_id = geocode_result[0].get('place_id')

            if not place_id:
                logger.warning("No place_id found in geocode result")
                return None

            # Get place details
            place_details = self.gmaps.place(place_id, fields=[
                'name',
                'rating',
                'reviews',
                'types',
                'photos',
                'opening_hours',
                'formatted_phone_number',
                'website'
            ])

            result = place_details.get('result', {})

            # Extract review themes
            reviews = result.get('reviews', [])
            review_texts = [r.get('text', '') for r in reviews[:10]]

            return {
                'name': result.get('name'),
                'rating': result.get('rating'),
                'total_reviews': len(reviews),
                'review_themes': review_texts,
                'business_types': result.get('types', []),
                'location': location,
                'address': geocode_result[0]['formatted_address']
            }

        except Exception as e:
            logger.error(f"Error fetching place details: {e}")
            return None

    def get_local_trends(self, location: str, keywords: List[str]) -> List[str]:
        """Get trending topics in location"""
        if not self.trends:
            logger.warning("Trends client not initialized, returning empty list")
            return []

        try:
            # Build payload for trends
            self.trends.build_payload(
                kw_list=keywords if keywords else ['restaurant', 'food', 'dining'],
                timeframe='now 7-d',
                geo='US'  # Can be refined with location
            )

            # Get related queries
            related = self.trends.related_queries()

            trending_topics = []
            for keyword in related:
                if related[keyword] and 'top' in related[keyword]:
                    top_queries = related[keyword]['top']
                    if top_queries is not None:
                        trending_topics.extend(
                            top_queries['query'].head(5).tolist()
                        )

            return trending_topics[:10]

        except Exception as e:
            logger.error(f"Error fetching trends: {e}")
            return []

    def analyze_website_with_search(self, website_url: str) -> Dict:
        """Analyze website content using Gemini with Search Grounding"""
        if not self.genai_client:
            logger.warning("Gemini client not initialized, returning empty analysis")
            return {'analysis': '', 'raw_url': website_url}

        try:
            prompt = f"""Analyze this business website: {website_url}

Extract the following information:
1. Business description and unique value proposition
2. Key products or services offered
3. Brand voice and tone (casual, professional, playful)
4. Target audience
5. Main differentiators

Provide a structured JSON response."""

            response = self.genai_client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.3,
                )
            )

            return {
                'analysis': response.text,
                'raw_url': website_url
            }

        except Exception as e:
            logger.error(f"Error analyzing website: {e}")
            return {'analysis': '', 'raw_url': website_url}

    def get_place_photos(self, place_id: str) -> List[Dict]:
        """
        Fetch photos from Google Business Profile via Places API.

        Args:
            place_id: Google Places ID for the business

        Returns:
            List of photo metadata dicts with URLs, dimensions
        """
        if not self.gmaps or not self.api_key:
            logger.warning("Google Maps client not initialized, cannot fetch photos")
            return []

        try:
            # Get place details with photos field
            place_result = self.gmaps.place(
                place_id=place_id,
                fields=['photos', 'name']
            )

            photos = []
            result = place_result.get('result', {})

            if 'photos' not in result:
                logger.info(f"No photos available for place_id: {place_id}")
                return []

            # Fetch up to 5 photos (enough for variety, respects rate limits)
            photo_data_list = result['photos'][:5]
            logger.info(f"Found {len(photo_data_list)} photos for {result.get('name', 'business')}")

            for idx, photo_data in enumerate(photo_data_list, 1):
                photo_ref = photo_data.get('photo_reference')

                if not photo_ref:
                    logger.warning(f"Photo {idx} missing reference, skipping")
                    continue

                # Construct photo URL (1024px width for good quality)
                photo_url = (
                    f"https://maps.googleapis.com/maps/api/place/photo"
                    f"?maxwidth=1024"
                    f"&photo_reference={photo_ref}"
                    f"&key={self.api_key}"
                )

                photos.append({
                    'url': photo_url,
                    'width': photo_data.get('width', 1024),
                    'height': photo_data.get('height', 768),
                    'photo_reference': photo_ref,
                    'attributions': photo_data.get('html_attributions', [])
                })

                logger.debug(f"Added photo {idx}: {photo_data.get('width')}x{photo_data.get('height')}")

            return photos

        except Exception as e:
            logger.error(f"Error fetching place photos: {e}")
            return []

    async def download_and_encode_photo(self, photo_url: str) -> Optional[str]:
        """
        Download a photo from URL and convert to base64 for Imagen.

        Args:
            photo_url: Full URL to the photo

        Returns:
            Base64-encoded image string, or None if download fails
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.debug(f"Downloading photo: {photo_url}")
                response = await client.get(photo_url)

                if response.status_code != 200:
                    logger.error(f"Failed to download photo: HTTP {response.status_code}")
                    return None

                # Encode to base64
                encoded = base64.b64encode(response.content).decode('utf-8')
                logger.info(f"Successfully encoded photo ({len(response.content)} bytes)")
                return encoded

        except httpx.TimeoutException:
            logger.error("Photo download timed out after 30s")
            return None
        except Exception as e:
            logger.error(f"Error downloading/encoding photo: {e}")
            return None

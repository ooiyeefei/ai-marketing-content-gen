"""
Photo scraper for extracting business photos from Facebook, Instagram, and Google Maps.
Uses Gemini Grounding with multimodal capabilities to extract photo URLs.
"""

import logging
import httpx
import base64
from typing import List, Dict, Optional
from google import genai
from google.genai import types as genai_types
from config import settings

logger = logging.getLogger(__name__)


class PhotoScraper:
    """Scrape photos from social media and business pages"""

    def __init__(self):
        try:
            self.genai_client = genai.Client(
                vertexai=True,
                project=settings.project_id,
                location=settings.region
            )
        except Exception as e:
            self.genai_client = None
            logger.warning(f"Failed to initialize Gemini client: {e}")

    async def scrape_photos_from_url(self, url: str, max_photos: int = 10) -> List[Dict]:
        """
        Scrape photos from any business URL (Facebook, Instagram, Google Maps, website).
        Uses Gemini with Google Search Grounding to find and extract photo URLs.

        Args:
            url: URL to scrape photos from
            max_photos: Maximum number of photos to return

        Returns:
            List of photo dicts with 'url' key
        """
        if not self.genai_client:
            logger.warning("Gemini client not initialized, cannot scrape photos")
            return []

        try:
            # Determine the type of URL
            if 'facebook.com' in url:
                return await self._scrape_facebook_photos(url, max_photos)
            elif 'instagram.com' in url:
                return await self._scrape_instagram_photos(url, max_photos)
            elif 'google.com/maps' in url or 'goo.gl/maps' in url:
                return await self._scrape_google_maps_photos(url, max_photos)
            else:
                # Generic website photo scraping
                return await self._scrape_website_photos(url, max_photos)

        except Exception as e:
            logger.error(f"Error scraping photos from {url}: {e}")
            return []

    async def _scrape_facebook_photos(self, url: str, max_photos: int) -> List[Dict]:
        """
        Extract photo URLs from Facebook business pages using Gemini grounding.
        """
        logger.info(f"Scraping photos from Facebook: {url}")

        try:
            # Use Gemini with Google Search to find photos from the Facebook page
            prompt = f"""Find {max_photos} high-quality food/product photos from this Facebook business page: {url}

Extract direct image URLs that show:
- Products (food, items, merchandise)
- Business interior/exterior
- Product presentations
- Avoid profile pictures, covers, text-only posts

Return ONLY a JSON array of photo URLs (direct links to images), like:
["https://example.com/photo1.jpg", "https://example.com/photo2.jpg"]

Important: Return actual image URLs, not Facebook post URLs."""

            response = self.genai_client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.1,
                    tools=[{'google_search': {}}]  # Enable Google Search grounding
                )
            )

            # Parse response
            text = response.text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()

            import json
            photo_urls = json.loads(text)

            # Convert to photo dict format
            photos = [{'url': url, 'source': 'facebook'} for url in photo_urls[:max_photos]]
            logger.info(f"Found {len(photos)} Facebook photos")
            return photos

        except Exception as e:
            logger.error(f"Error scraping Facebook photos: {e}")
            # Fallback: try direct HTTP scraping
            return await self._fallback_scrape_photos(url, 'facebook', max_photos)

    async def _scrape_instagram_photos(self, url: str, max_photos: int) -> List[Dict]:
        """
        Extract photo URLs from Instagram profiles using Gemini grounding.
        """
        logger.info(f"Scraping photos from Instagram: {url}")

        try:
            prompt = f"""Find {max_photos} high-quality photos from this Instagram business profile: {url}

Extract direct image URLs from recent posts that show:
- Products, food, or merchandise
- High-quality professional shots
- Business content (not personal/casual posts)

Return ONLY a JSON array of direct image URLs:
["https://example.com/img1.jpg", "https://example.com/img2.jpg"]"""

            response = self.genai_client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.1,
                    tools=[{'google_search': {}}]
                )
            )

            text = response.text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()

            import json
            photo_urls = json.loads(text)

            photos = [{'url': url, 'source': 'instagram'} for url in photo_urls[:max_photos]]
            logger.info(f"Found {len(photos)} Instagram photos")
            return photos

        except Exception as e:
            logger.error(f"Error scraping Instagram photos: {e}")
            return await self._fallback_scrape_photos(url, 'instagram', max_photos)

    async def _scrape_google_maps_photos(self, url: str, max_photos: int) -> List[Dict]:
        """
        Extract photo URLs from Google Maps listing using Gemini grounding.
        """
        logger.info(f"Scraping photos from Google Maps: {url}")

        try:
            prompt = f"""Find {max_photos} business photos from this Google Maps listing: {url}

Extract direct image URLs showing:
- Business exterior/interior
- Products or food
- Professional business photos

Return ONLY a JSON array of image URLs:
["https://example.com/photo1.jpg", "https://example.com/photo2.jpg"]"""

            response = self.genai_client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.1,
                    tools=[{'google_search': {}}]
                )
            )

            text = response.text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()

            import json
            photo_urls = json.loads(text)

            photos = [{'url': url, 'source': 'google_maps'} for url in photo_urls[:max_photos]]
            logger.info(f"Found {len(photos)} Google Maps photos")
            return photos

        except Exception as e:
            logger.error(f"Error scraping Google Maps photos: {e}")
            return []

    async def _scrape_website_photos(self, url: str, max_photos: int) -> List[Dict]:
        """
        Extract photo URLs from regular business websites using Gemini grounding.
        """
        logger.info(f"Scraping photos from website: {url}")

        try:
            prompt = f"""Find {max_photos} product/business photos from this website: {url}

Extract direct image URLs showing:
- Products, food, or services
- High-resolution images
- Professional business content

Return ONLY a JSON array of direct image URLs:
["https://example.com/img1.jpg", "https://example.com/img2.jpg"]"""

            response = self.genai_client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.1,
                    tools=[{'google_search': {}}]
                )
            )

            text = response.text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()

            import json
            photo_urls = json.loads(text)

            photos = [{'url': url, 'source': 'website'} for url in photo_urls[:max_photos]]
            logger.info(f"Found {len(photos)} website photos")
            return photos

        except Exception as e:
            logger.error(f"Error scraping website photos: {e}")
            return []

    async def _fallback_scrape_photos(self, url: str, source: str, max_photos: int) -> List[Dict]:
        """
        Fallback method: try to fetch the page and extract images with simple pattern matching.
        """
        logger.info(f"Attempting fallback photo scraping from {source}: {url}")

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()
                html = response.text

            # Simple pattern matching for image URLs
            import re
            patterns = [
                r'https://[^"\s]+\.jpg',
                r'https://[^"\s]+\.jpeg',
                r'https://[^"\s]+\.png',
                r'https://[^"\s]+\.webp',
            ]

            photo_urls = []
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                photo_urls.extend(matches)

            # Deduplicate and filter
            photo_urls = list(set(photo_urls))

            # Filter out tiny images, icons, etc.
            filtered_urls = [
                url for url in photo_urls
                if not any(x in url.lower() for x in ['icon', 'logo', 'avatar', 'thumb', 'pixel'])
            ]

            photos = [{'url': url, 'source': source} for url in filtered_urls[:max_photos]]
            logger.info(f"Fallback: Found {len(photos)} photos from {source}")
            return photos

        except Exception as e:
            logger.error(f"Fallback scraping failed: {e}")
            return []

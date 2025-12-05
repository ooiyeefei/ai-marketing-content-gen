"""
Lightpanda Service with Playwright - Image extraction only
Using correct Lightpanda Cloud API with context managers
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class LightpandaService:
    """
    Lightpanda browser service using Playwright (correct API)
    Focused on: Product image extraction from websites
    """

    def __init__(self):
        self.token = os.getenv("LIGHTPANDA_TOKEN")
        self.region = os.getenv("LIGHTPANDA_REGION", "euwest")  # euwest or uswest

        if not self.token:
            logger.warning("⚠️  LIGHTPANDA_TOKEN not set - image extraction will be limited")
        else:
            logger.info("✅ Lightpanda service initialized (Playwright)")

    def _get_endpoint(self) -> str:
        """Get Lightpanda Cloud WebSocket endpoint"""
        return f"wss://{self.region}.cloud.lightpanda.io/ws?token={self.token}"

    async def extract_images(self, url: str, min_size: int = 200) -> List[str]:
        """
        Extract product images from a website using Lightpanda

        Args:
            url: Website URL
            min_size: Minimum image size (width/height)

        Returns:
            List of image URLs
        """
        if not self.token:
            logger.warning(f"⚠️  No Lightpanda token - skipping image extraction for {url}")
            return []

        start_time = time.time()

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                # Connect to Lightpanda Cloud browser
                logger.info("🔌 Connecting to Lightpanda Cloud...")
                browser = await p.chromium.connect_over_cdp(
                    endpoint_url=self._get_endpoint()
                )

                # Create context and page
                context = await browser.new_context()
                page = await context.new_page()

                # Navigate to URL
                logger.info(f"🌐 Loading {url}...")
                await page.goto(url, wait_until="networkidle", timeout=30000)

                logger.info(f"✅ Page loaded successfully")

                # Extract images
                logger.info(f"🖼️  Extracting images (min size: {min_size}x{min_size})")

                images = await page.evaluate(f"""() => {{
                    return Array.from(document.querySelectorAll('img'))
                        .map(img => ({{
                            src: img.src,
                            alt: img.alt || '',
                            width: img.naturalWidth || img.width,
                            height: img.naturalHeight || img.height
                        }}))
                        .filter(img => img.width >= {min_size} && img.height >= {min_size})
                        .map(img => img.src);
                }}""")

                # Filter out data URLs and invalid URLs
                valid_images = [
                    img for img in images
                    if img and not img.startswith('data:')
                    and (img.startswith('http://') or img.startswith('https://'))
                ]

                # Cleanup
                await context.close()
                await browser.close()

                duration = time.time() - start_time

                logger.info(f"✅ Extracted {len(valid_images)} images in {duration:.2f}s")
                logger.info(f"⚡ Lightpanda performance: 10x faster than Chrome")

                return valid_images

        except Exception as e:
            logger.error(f"❌ Error extracting images from {url}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return []

    async def scrape_url(
        self,
        url: str,
        wait_for_selector: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Scrape a URL using Lightpanda Cloud browser

        Args:
            url: URL to scrape
            wait_for_selector: Optional CSS selector to wait for

        Returns:
            Dict with title, content, and metadata
        """
        if not self.token:
            logger.warning("⚠️  No Lightpanda token available")
            return None

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                # Connect to Lightpanda Cloud browser
                browser = await p.chromium.connect_over_cdp(
                    endpoint_url=self._get_endpoint()
                )

                context = await browser.new_context()
                page = await context.new_page()

                # Navigate to URL
                logger.info(f"🌐 Navigating to {url}...")
                await page.goto(url, wait_until="networkidle", timeout=30000)

                # Optional: wait for specific selector
                if wait_for_selector:
                    await page.wait_for_selector(wait_for_selector, timeout=10000)

                # Extract content
                title = await page.title()

                # Get text content from body
                body_text = await page.evaluate("""
                    () => {
                        const body = document.body;
                        return body ? body.innerText : '';
                    }
                """)

                # Get meta description
                meta_description = await page.evaluate("""
                    () => {
                        const meta = document.querySelector('meta[name="description"]');
                        return meta ? meta.content : '';
                    }
                """)

                # Get headings for structure
                headings = await page.evaluate("""
                    () => {
                        const h1s = Array.from(document.querySelectorAll('h1')).map(h => h.innerText);
                        const h2s = Array.from(document.querySelectorAll('h2')).map(h => h.innerText);
                        return { h1: h1s, h2: h2s };
                    }
                """)

                await context.close()
                await browser.close()

                logger.info(f"✅ Scraped successfully")

                return {
                    "title": title,
                    "description": meta_description,
                    "body_text": body_text[:5000],  # Limit to 5000 chars
                    "headings": headings,
                    "url": url
                }

        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {e}")
            return None

    async def extract_product_images(
        self,
        business_url: str,
        max_images: int = 20
    ) -> List[str]:
        """
        Extract high-quality product images from business website

        Args:
            business_url: Business website URL
            max_images: Maximum number of images to extract

        Returns:
            List of product image URLs
        """
        logger.info(f"🔍 Extracting product images from {business_url}")

        # Extract images (min 300x300 for products)
        images = await self.extract_images(business_url, min_size=300)

        # Limit results
        product_images = images[:max_images]

        logger.info(f"✅ Found {len(product_images)} product images")
        return product_images


# Global instance
_lightpanda_service = None


def get_lightpanda_service() -> LightpandaService:
    """Get or create Lightpanda service instance"""
    global _lightpanda_service
    if _lightpanda_service is None:
        _lightpanda_service = LightpandaService()
    return _lightpanda_service

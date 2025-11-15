#!/usr/bin/env python3
"""
Test script for Google Business Photos integration.

This script demonstrates the photo fetching and usage flow:
1. Fetches photos from Google Maps Places API
2. Downloads and encodes a photo for use as reference
3. Shows how the reference image is applied to video/image generation
"""

import asyncio
import logging
from services.google_services import GoogleServicesClient
from agents.business_analyst import BusinessAnalystAgent
from models import BusinessInput

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_photo_fetching():
    """Test photo fetching from Google Places API"""
    logger.info("=" * 80)
    logger.info("TEST 1: Photo Fetching from Google Places API")
    logger.info("=" * 80)

    google_services = GoogleServicesClient()

    # Test address (replace with actual business)
    test_address = "1600 Amphitheatre Parkway, Mountain View, CA"

    # Step 1: Get place_id
    logger.info(f"\n1. Geocoding address: {test_address}")
    geocode_result = google_services.gmaps.geocode(test_address)

    if not geocode_result:
        logger.error("Failed to geocode address")
        return

    place_id = geocode_result[0].get('place_id')
    logger.info(f"   Place ID: {place_id}")

    # Step 2: Fetch photos
    logger.info(f"\n2. Fetching photos for place_id: {place_id}")
    photos = google_services.get_place_photos(place_id)

    if photos:
        logger.info(f"   ✓ Retrieved {len(photos)} photos")
        for i, photo in enumerate(photos, 1):
            logger.info(f"   Photo {i}:")
            logger.info(f"     - URL: {photo['url'][:80]}...")
            logger.info(f"     - Dimensions: {photo['width']}x{photo['height']}")
            logger.info(f"     - Reference: {photo['photo_reference'][:20]}...")
    else:
        logger.warning("   ⚠ No photos available for this location")

    return photos


async def test_photo_encoding(photos):
    """Test photo download and base64 encoding"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Photo Download and Base64 Encoding")
    logger.info("=" * 80)

    if not photos:
        logger.warning("No photos to encode, skipping test")
        return None

    google_services = GoogleServicesClient()

    # Test downloading and encoding first photo
    photo_url = photos[0]['url']
    logger.info(f"\n1. Downloading photo from URL:")
    logger.info(f"   {photo_url[:100]}...")

    encoded = await google_services.download_and_encode_photo(photo_url)

    if encoded:
        logger.info(f"   ✓ Successfully encoded photo")
        logger.info(f"   - Encoded length: {len(encoded)} characters")
        logger.info(f"   - First 100 chars: {encoded[:100]}...")
        logger.info(f"   - Approximate size: {len(encoded) * 3 / 4 / 1024:.2f} KB")
    else:
        logger.error("   ✗ Failed to encode photo")

    return encoded


async def test_business_analyst_integration():
    """Test Business Analyst agent with photo fetching"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Business Analyst Agent Integration")
    logger.info("=" * 80)

    agent = BusinessAnalystAgent()

    # Create test input
    business_input = BusinessInput(
        business_name="Googleplex",
        business_address="1600 Amphitheatre Parkway, Mountain View, CA",
        brand_voice="professional"
    )

    logger.info(f"\n1. Analyzing business: {business_input.business_name}")
    logger.info(f"   Address: {business_input.business_address}")

    # Run analysis
    profile = await agent.analyze(business_input)

    # Check for photos in profile
    photos = profile.get('photos', [])

    if photos:
        logger.info(f"\n2. ✓ Business profile includes {len(photos)} photos")
        logger.info(f"   Sample photo:")
        logger.info(f"     - URL: {photos[0]['url'][:80]}...")
        logger.info(f"     - Dimensions: {photos[0]['width']}x{photos[0]['height']}")
    else:
        logger.warning("\n2. ⚠ No photos in business profile")

    # Show full profile structure
    logger.info(f"\n3. Business profile structure:")
    logger.info(f"   - business_name: {profile.get('business_name')}")
    logger.info(f"   - from_maps: {bool(profile.get('from_maps'))}")
    logger.info(f"   - photos: {len(profile.get('photos', []))} items")
    logger.info(f"   - content_themes: {len(profile.get('content_themes', []))} themes")

    return profile


async def test_reference_image_config():
    """Demonstrate how reference image is used in video/image config"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Reference Image Configuration")
    logger.info("=" * 80)

    # Simulate encoded photo (shortened for demo)
    sample_encoded = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

    logger.info("\n1. Video generation config WITH reference image:")
    video_config_with_ref = {
        "numberOfVideos": 1,
        "resolution": "720p",
        "aspectRatio": "16:9",
        "referenceImages": [{
            "image": {"imageBytes": sample_encoded},
            "referenceType": "STYLE"
        }]
    }
    logger.info(f"   {video_config_with_ref}")

    logger.info("\n2. Video generation config WITHOUT reference image:")
    video_config_without_ref = {
        "numberOfVideos": 1,
        "resolution": "720p",
        "aspectRatio": "16:9"
    }
    logger.info(f"   {video_config_without_ref}")

    logger.info("\n3. Image generation config WITH reference image:")
    image_config_with_ref = {
        "numberOfImages": 1,
        "aspectRatio": "1:1",
        "referenceImages": [{
            "image": {"imageBytes": sample_encoded},
            "referenceType": "STYLE"
        }]
    }
    logger.info(f"   {image_config_with_ref}")

    logger.info("\n4. Reference types available:")
    logger.info("   - STYLE: Applies visual style from reference (colors, lighting, mood)")
    logger.info("   - SUBJECT: Includes specific objects/subjects from reference")
    logger.info("   Current implementation uses: STYLE")


async def run_all_tests():
    """Run all integration tests"""
    logger.info("\n" + "=" * 80)
    logger.info("GOOGLE BUSINESS PHOTOS INTEGRATION TEST SUITE")
    logger.info("=" * 80)

    try:
        # Test 1: Photo fetching
        photos = await test_photo_fetching()

        # Test 2: Photo encoding
        if photos:
            await test_photo_encoding(photos)

        # Test 3: Business Analyst integration
        await test_business_analyst_integration()

        # Test 4: Reference config demo
        await test_reference_image_config()

        logger.info("\n" + "=" * 80)
        logger.info("ALL TESTS COMPLETED")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Test suite failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(run_all_tests())

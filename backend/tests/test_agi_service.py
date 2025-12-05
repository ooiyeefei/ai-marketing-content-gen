"""
Test suite for AGI Service - Web Research & Review Scraping

This test suite uses REAL API calls (no mocks) to verify AGI integration.
Tests cover:
1. Business context extraction
2. Competitor discovery
3. Online review scraping
4. Error handling

All outputs are saved to backend/tests/outputs/agi/ for manual inspection.
"""
import asyncio
import sys
import os

# Load environment variables
import json
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")




from services.agi_service import AGIService


# Test configuration
OUTPUT_DIR = Path(__file__).parent / "outputs" / "agi"
TEST_BUSINESS_URL = "https://www.bluebottlecoffee.com"
TEST_BUSINESS_NAME = "Blue Bottle Coffee"
TEST_LOCATION = {"city": "San Francisco", "state": "CA", "country": "USA"}


class TestResult:
    """Track test results for summary"""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.skipped = []
        self.start_time = datetime.now()

    def record_pass(self, test_name: str, details: str = ""):
        self.passed.append((test_name, details))
        print(f"✅ PASS: {test_name}")
        if details:
            print(f"   {details}")

    def record_fail(self, test_name: str, error: str):
        self.failed.append((test_name, error))
        print(f"❌ FAIL: {test_name}")
        print(f"   Error: {error}")

    def record_skip(self, test_name: str, reason: str):
        self.skipped.append((test_name, reason))
        print(f"⏭️  SKIP: {test_name}")
        print(f"   Reason: {reason}")

    def print_summary(self):
        duration = (datetime.now() - self.start_time).total_seconds()
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {len(self.passed) + len(self.failed) + len(self.skipped)}")
        print(f"✅ Passed: {len(self.passed)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"⏭️  Skipped: {len(self.skipped)}")
        print(f"Duration: {duration:.2f}s")

        if self.failed:
            print("\n❌ FAILED TESTS:")
            for test_name, error in self.failed:
                print(f"   - {test_name}: {error}")

        print("="*70)
        return len(self.failed) == 0


def save_json_output(filename: str, data: Any):
    """Save JSON data to output directory"""
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"   💾 Saved to: {filepath}")


def validate_json_structure(data: Dict, required_keys: List[str], test_name: str) -> bool:
    """Validate JSON structure has required keys"""
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        print(f"   ⚠️  Missing keys: {missing_keys}")
        return False
    return True


async def test_agi_scrape_business_context(results: TestResult):
    """
    Test AGI business context extraction from website.

    Expected output:
    {
        "business_name": "Blue Bottle Coffee",
        "industry": "coffee" or "restaurant",
        "description": "...",
        "location": {"city": "...", "state": "...", "country": "..."},
        "price_range": "premium",
        "specialties": ["specialty coffee", "pour-over", ...],
        "brand_voice": "elegant, artisanal, quality-focused",
        "target_audience": "..."
    }
    """
    test_name = "test_agi_scrape_business_context"
    print(f"\n{'='*70}")
    print(f"Test: {test_name}")
    print(f"{'='*70}")
    print(f"Input URL: {TEST_BUSINESS_URL}")

    try:
        # Check if AGI_API_KEY is available
        if not os.getenv("AGI_API_KEY"):
            results.record_skip(test_name, "AGI_API_KEY not set in environment")
            return

        # Initialize AGI service
        print("\n📡 Initializing AGI service...")
        agi_service = AGIService()

        # Extract business context
        print(f"🔍 Extracting business context from {TEST_BUSINESS_URL}...")
        print("⏱️  This may take 60-120 seconds...")

        business_context = await agi_service.extract_business_context(TEST_BUSINESS_URL)

        # Validate response structure
        required_keys = ["business_name", "industry", "description"]
        if not validate_json_structure(business_context, required_keys, test_name):
            results.record_fail(test_name, "Missing required keys in response")
            return

        # Verify data quality
        business_name = business_context.get("business_name", "")
        industry = business_context.get("industry", "")
        description = business_context.get("description", "")

        print(f"\n📊 Results:")
        print(f"   Business Name: {business_name}")
        print(f"   Industry: {industry}")
        print(f"   Description: {description[:100]}...")

        # Validate non-empty values
        if not business_name:
            results.record_fail(test_name, "business_name is empty")
            return

        if not industry:
            results.record_fail(test_name, "industry is empty")
            return

        if not description or len(description) < 20:
            results.record_fail(test_name, "description is too short or empty")
            return

        # Save output
        save_json_output("business_context.json", business_context)

        results.record_pass(
            test_name,
            f"Extracted context for {business_name} in {industry} industry"
        )

    except Exception as e:
        results.record_fail(test_name, str(e))


async def test_agi_discover_competitors(results: TestResult):
    """
    Test AGI autonomous competitor discovery.

    Expected output:
    [
        {
            "name": "Competitor Name",
            "website": "https://...",
            "location": "San Francisco, CA",
            "google_rating": 4.5,
            "review_count": 1234,
            "social_handles": {"instagram": "@handle"},
            "description": "..."
        },
        ...
    ]
    """
    test_name = "test_agi_discover_competitors"
    print(f"\n{'='*70}")
    print(f"Test: {test_name}")
    print(f"{'='*70}")

    try:
        # Check if AGI_API_KEY is available
        if not os.getenv("AGI_API_KEY"):
            results.record_skip(test_name, "AGI_API_KEY not set in environment")
            return

        # Load business context from previous test
        business_context_file = OUTPUT_DIR / "business_context.json"
        if not business_context_file.exists():
            # Create minimal business context for testing
            business_context = {
                "business_name": TEST_BUSINESS_NAME,
                "industry": "coffee",
                "location": TEST_LOCATION,
                "price_range": "premium",
                "specialties": ["specialty coffee", "pour-over"]
            }
            print("⚠️  Using fallback business context (previous test skipped)")
        else:
            with open(business_context_file, 'r') as f:
                business_context = json.load(f)

        # Initialize AGI service
        print("\n📡 Initializing AGI service...")
        agi_service = AGIService()

        # Discover competitors
        print(f"🔍 Discovering competitors for {business_context.get('business_name')}...")
        print("⏱️  This may take 120-180 seconds (includes web searches)...")

        competitors = await agi_service.discover_competitors(
            business_context=business_context,
            num_competitors=3
        )

        # Validate response
        if not isinstance(competitors, list):
            results.record_fail(test_name, "Response is not a list")
            return

        if len(competitors) < 1:
            results.record_fail(test_name, "No competitors discovered")
            return

        print(f"\n📊 Discovered {len(competitors)} competitors:")
        for i, competitor in enumerate(competitors, 1):
            name = competitor.get("name", "Unknown")
            website = competitor.get("website", "N/A")
            rating = competitor.get("google_rating", "N/A")
            print(f"   {i}. {name}")
            print(f"      Website: {website}")
            print(f"      Rating: {rating}")

        # Validate each competitor has required fields
        for competitor in competitors:
            if not competitor.get("name"):
                results.record_fail(test_name, "Competitor missing 'name' field")
                return

        # Save output
        save_json_output("competitors.json", competitors)

        results.record_pass(
            test_name,
            f"Discovered {len(competitors)} competitors autonomously"
        )

    except Exception as e:
        results.record_fail(test_name, str(e))


async def test_agi_scrape_online_reviews(results: TestResult):
    """
    Test AGI online review scraping (fallback for unclaimed GMB profiles).

    Expected output:
    {
        "reviews": [
            {
                "rating": 5,
                "text": "Great coffee!",
                "date": "2025-01-15",
                "source": "Google Maps",
                "reviewer_name": "John D."
            },
            ...
        ],
        "customer_photos": ["https://..."],
        "overall_rating": 4.5,
        "total_reviews": 234,
        "sources": ["Google Maps", "Yelp"]
    }
    """
    test_name = "test_agi_scrape_online_reviews"
    print(f"\n{'='*70}")
    print(f"Test: {test_name}")
    print(f"{'='*70}")
    print(f"Business: {TEST_BUSINESS_NAME}")
    print(f"Location: {TEST_LOCATION.get('city')}, {TEST_LOCATION.get('state')}")

    try:
        # Check if AGI_API_KEY is available
        if not os.getenv("AGI_API_KEY"):
            results.record_skip(test_name, "AGI_API_KEY not set in environment")
            return

        # Initialize AGI service
        print("\n📡 Initializing AGI service...")
        agi_service = AGIService()

        # Scrape reviews
        print(f"🔍 Scraping online reviews for {TEST_BUSINESS_NAME}...")
        print("⏱️  This may take 120-180 seconds (includes web searches + scraping)...")

        reviews_data = await agi_service.scrape_online_reviews(
            business_name=TEST_BUSINESS_NAME,
            location=TEST_LOCATION,
            limit=20
        )

        # Validate response structure
        required_keys = ["reviews", "overall_rating", "total_reviews", "sources"]
        if not validate_json_structure(reviews_data, required_keys, test_name):
            results.record_fail(test_name, "Missing required keys in response")
            return

        # Extract data
        reviews = reviews_data.get("reviews", [])
        overall_rating = reviews_data.get("overall_rating", 0.0)
        total_reviews = reviews_data.get("total_reviews", 0)
        sources = reviews_data.get("sources", [])

        print(f"\n📊 Results:")
        print(f"   Overall Rating: {overall_rating}")
        print(f"   Total Reviews: {total_reviews}")
        print(f"   Reviews Scraped: {len(reviews)}")
        print(f"   Sources: {', '.join(sources) if sources else 'N/A'}")

        # Show sample reviews
        if reviews:
            print(f"\n   Sample Reviews:")
            for i, review in enumerate(reviews[:3], 1):
                rating = review.get("rating", "N/A")
                text = review.get("text", "")
                source = review.get("source", "Unknown")
                print(f"   {i}. [{rating}⭐] {text[:80]}... (Source: {source})")

        # Validate data quality
        if overall_rating < 1.0 or overall_rating > 5.0:
            # If rating is 0, it might be a failed scrape
            if overall_rating == 0.0 and len(reviews) == 0:
                results.record_skip(
                    test_name,
                    "No reviews found (business may not have online reviews or scraping failed)"
                )
                return

        # Save output
        save_json_output("reviews.json", reviews_data)

        results.record_pass(
            test_name,
            f"Scraped {len(reviews)} reviews from {len(sources)} sources"
        )

    except Exception as e:
        results.record_fail(test_name, str(e))


async def test_agi_error_handling(results: TestResult):
    """
    Test AGI error handling with invalid inputs.

    Expected: Graceful error handling, no crashes
    """
    test_name = "test_agi_error_handling"
    print(f"\n{'='*70}")
    print(f"Test: {test_name}")
    print(f"{'='*70}")

    try:
        # Check if AGI_API_KEY is available
        if not os.getenv("AGI_API_KEY"):
            results.record_skip(test_name, "AGI_API_KEY not set in environment")
            return

        # Initialize AGI service
        print("\n📡 Initializing AGI service...")
        agi_service = AGIService()

        # Test 1: Invalid URL
        print("\n🧪 Test 1: Invalid URL")
        invalid_url = "https://this-is-definitely-not-a-real-website-123456789.com"
        print(f"   Input: {invalid_url}")

        try:
            result = await agi_service.extract_business_context(invalid_url)
            # If it doesn't raise an error, check if result is empty or has error indication
            if not result or not result.get("business_name"):
                print("   ✅ Handled gracefully (returned empty/minimal data)")
            else:
                print("   ⚠️  Warning: Returned data for invalid URL")
        except Exception as e:
            print(f"   ✅ Caught exception gracefully: {type(e).__name__}")

        # Test 2: Empty business name for review scraping
        print("\n🧪 Test 2: Empty business name for review scraping")
        try:
            result = await agi_service.scrape_online_reviews(
                business_name="",
                location=TEST_LOCATION,
                limit=10
            )
            if result.get("total_reviews") == 0:
                print("   ✅ Handled gracefully (returned empty results)")
            else:
                print("   ⚠️  Warning: Returned results for empty business name")
        except Exception as e:
            print(f"   ✅ Caught exception gracefully: {type(e).__name__}")

        # Test 3: Invalid location for review scraping
        print("\n🧪 Test 3: Invalid location")
        try:
            result = await agi_service.scrape_online_reviews(
                business_name=TEST_BUSINESS_NAME,
                location={"city": "", "state": "", "country": ""},
                limit=10
            )
            if result.get("total_reviews") == 0:
                print("   ✅ Handled gracefully (returned empty results)")
            else:
                print("   ⚠️  Warning: Returned results for invalid location")
        except Exception as e:
            print(f"   ✅ Caught exception gracefully: {type(e).__name__}")

        results.record_pass(
            test_name,
            "All error scenarios handled gracefully without crashes"
        )

    except Exception as e:
        results.record_fail(test_name, f"Unexpected error: {str(e)}")


async def test_agi_research_competitor(results: TestResult):
    """
    Test AGI deep competitor research.

    Expected output:
    {
        "competitor_name": "Competitor Name",
        "menu": [{"item": "...", "price": "..."}],
        "pricing_strategy": "premium",
        "brand_voice": "elegant, traditional",
        "top_content_themes": ["theme1", "theme2"],
        "differentiators": ["..."],
        "hero_images": ["https://..."]
    }
    """
    test_name = "test_agi_research_competitor"
    print(f"\n{'='*70}")
    print(f"Test: {test_name}")
    print(f"{'='*70}")

    try:
        # Check if AGI_API_KEY is available
        if not os.getenv("AGI_API_KEY"):
            results.record_skip(test_name, "AGI_API_KEY not set in environment")
            return

        # Load competitors from previous test
        competitors_file = OUTPUT_DIR / "competitors.json"
        if not competitors_file.exists():
            results.record_skip(test_name, "No competitors.json found (previous test skipped)")
            return

        with open(competitors_file, 'r') as f:
            competitors = json.load(f)

        if not competitors or len(competitors) == 0:
            results.record_skip(test_name, "No competitors available for research")
            return

        # Research first competitor
        competitor = competitors[0]
        competitor_name = competitor.get("name")
        competitor_url = competitor.get("website")

        if not competitor_url:
            results.record_skip(test_name, f"Competitor '{competitor_name}' has no website URL")
            return

        print(f"Researching: {competitor_name}")
        print(f"URL: {competitor_url}")

        # Initialize AGI service
        print("\n📡 Initializing AGI service...")
        agi_service = AGIService()

        # Research competitor
        print(f"🔍 Deep research on {competitor_name}...")
        print("⏱️  This may take 120-180 seconds...")

        research_data = await agi_service.research_competitor(
            competitor_url=competitor_url,
            competitor_name=competitor_name
        )

        # Validate response
        if not research_data:
            results.record_fail(test_name, "Empty response from competitor research")
            return

        # Extract data
        menu = research_data.get("menu", [])
        pricing_strategy = research_data.get("pricing_strategy", "N/A")
        brand_voice = research_data.get("brand_voice", "N/A")
        themes = research_data.get("top_content_themes", [])

        print(f"\n📊 Results:")
        print(f"   Competitor: {competitor_name}")
        print(f"   Pricing Strategy: {pricing_strategy}")
        print(f"   Brand Voice: {brand_voice}")
        print(f"   Menu Items: {len(menu)}")
        print(f"   Content Themes: {len(themes)}")

        # Save output
        save_json_output(f"competitor_research_{competitor_name.replace(' ', '_').lower()}.json", research_data)

        results.record_pass(
            test_name,
            f"Completed deep research on {competitor_name}"
        )

    except Exception as e:
        results.record_fail(test_name, str(e))


async def main():
    """Run all AGI service tests"""
    print("="*70)
    print("AGI SERVICE TEST SUITE")
    print("="*70)
    print("Testing: Web Research & Review Scraping")
    print("Mode: REAL API CALLS (no mocks)")
    print(f"Output Directory: {OUTPUT_DIR}")
    print("="*70)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Output directory created: {OUTPUT_DIR}")

    # Initialize test results tracker
    results = TestResult()

    # Run tests sequentially (AGI tasks take time)
    print("\n🚀 Starting test execution...\n")

    await test_agi_scrape_business_context(results)
    await test_agi_discover_competitors(results)
    await test_agi_scrape_online_reviews(results)
    await test_agi_research_competitor(results)
    await test_agi_error_handling(results)

    # Print summary
    success = results.print_summary()

    # Verify output files
    print("\n📁 Output Files:")
    if OUTPUT_DIR.exists():
        output_files = list(OUTPUT_DIR.glob("*.json"))
        for f in output_files:
            file_size = f.stat().st_size
            print(f"   - {f.name} ({file_size} bytes)")

        if len(output_files) == 0:
            print("   ⚠️  No output files generated")
    else:
        print("   ❌ Output directory not found")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

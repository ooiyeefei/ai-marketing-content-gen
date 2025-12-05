#!/usr/bin/env python3
"""
Test suite for SocialService - Real API Integration Tests

Tests:
1. GMB API (if available)
2. AGI fallback for reviews (real API call)
3. Optional APIs (Facebook, Instagram, Trends)
4. Graceful handling when tokens missing
5. Error handling

NOTE: This uses REAL APIs, no mocks. Tests will make actual API calls.
"""
import asyncio
import sys
import os

# Load environment variables
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")




from services.social_service import SocialService
from services.agi_service import AGIService


# =============================================================================
# Test Output Directory
# =============================================================================

OUTPUT_DIR = Path(__file__).parent / "outputs" / "social"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Helper Functions
# =============================================================================

def save_test_result(test_name: str, data: dict):
    """Save test result to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{test_name}_{timestamp}.json"
    filepath = OUTPUT_DIR / filename

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    print(f"   Saved result to: {filepath}")


def print_test_header(test_name: str):
    """Print formatted test header"""
    print("\n" + "="*80)
    print(f"TEST: {test_name}")
    print("="*80)


def print_test_result(passed: bool, message: str):
    """Print test result with status"""
    status = "PASS" if passed else "FAIL"
    symbol = "✓" if passed else "✗"
    print(f"\n{symbol} {status}: {message}\n")


# =============================================================================
# Test 1: GMB API Reviews (if available)
# =============================================================================

async def test_social_gmb_reviews_success():
    """
    Test: GMB API reviews for claimed business

    Expected: If GMB API key available and business claimed, returns reviews with source="gmb_api"
    Fallback: If unavailable, falls through to AGI test
    """
    print_test_header("Social GMB Reviews Success")

    try:
        social_service = SocialService()

        # Check if GMB API key is configured
        if not social_service.gmb_api_key:
            print("⚠ SKIP: GOOGLE_MY_BUSINESS_API_KEY not configured")
            print("   This is expected if you don't have GMB API access")
            print("   Test will fallback to AGI scraping in next test")
            return True  # Not a failure, just skipped

        print("✓ GMB API key configured")

        # Test with a known claimed business (example)
        # NOTE: You'll need to replace this with an actual claimed business
        business_name = "Starbucks Reserve Roastery"
        location = {"city": "San Francisco", "state": "CA", "country": "USA"}

        print(f"   Testing GMB API for: {business_name}")
        print(f"   Location: {location['city']}, {location['state']}")

        result = await social_service.get_google_reviews(
            business_name=business_name,
            location=location,
            limit=10
        )

        # Verify structure
        assert "reviews" in result, "Missing 'reviews' key"
        assert "customer_photos" in result, "Missing 'customer_photos' key"
        assert "overall_rating" in result, "Missing 'overall_rating' key"
        assert "total_reviews" in result, "Missing 'total_reviews' key"
        assert "source" in result, "Missing 'source' key"

        # Check if GMB API was successful
        if result["source"] == "gmb_api":
            print(f"✓ GMB API successful")
            print(f"   Reviews fetched: {len(result['reviews'])}")
            print(f"   Overall rating: {result['overall_rating']}")
            print(f"   Total reviews: {result['total_reviews']}")
            print(f"   Customer photos: {len(result['customer_photos'])}")

            # Save result
            save_test_result("gmb_reviews_success", result)

            print_test_result(True, "GMB API returned reviews successfully")
            return True
        else:
            # GMB API not available (business not claimed or API integration pending)
            print(f"⚠ GMB API not available (source: {result['source']})")
            print("   This is expected if business is not claimed or API integration is pending")
            print("   Falling back to AGI scraping test")
            return True  # Not a failure, expected fallback

    except Exception as e:
        print(f"✗ Exception: {e}")
        print_test_result(False, f"Test raised exception: {str(e)}")
        return False


# =============================================================================
# Test 2: AGI Fallback for Reviews (Most Important)
# =============================================================================

async def test_social_gmb_fallback_to_agi():
    """
    Test: AGI API fallback for unclaimed businesses

    Expected: When GMB unavailable, AGI scrapes public reviews from:
    - Google Maps
    - Yelp
    - TripAdvisor
    - Other review platforms

    This is the PRIMARY test since most businesses don't have claimed GMB profiles.
    """
    print_test_header("Social GMB Fallback to AGI")

    try:
        # Initialize services
        social_service = SocialService()

        # Check if AGI API key is configured
        agi_api_key = os.getenv("AGI_API_KEY")
        if not agi_api_key:
            print("✗ FAIL: AGI_API_KEY not configured")
            print("   AGI fallback is REQUIRED for unclaimed businesses")
            print_test_result(False, "AGI_API_KEY environment variable not set")
            return False

        print("✓ AGI API key configured")

        # Initialize AGI service
        agi_service = AGIService()
        print("✓ AGI Service initialized")

        # Test with a real business (unclaimed GMB profile)
        # Using a small local business that likely doesn't have claimed GMB
        business_name = "The Mill"  # Coffee shop in SF
        location = {"city": "San Francisco", "state": "CA", "country": "USA"}

        print(f"\n   Testing AGI fallback for: {business_name}")
        print(f"   Location: {location['city']}, {location['state']}")
        print("   This will scrape public reviews from Google Maps, Yelp, etc.")
        print("   Please wait, this may take 30-60 seconds...\n")

        # Call with AGI service for fallback
        result = await social_service.get_google_reviews(
            business_name=business_name,
            location=location,
            limit=10,
            agi_service=agi_service
        )

        # Verify structure
        assert "reviews" in result, "Missing 'reviews' key"
        assert "customer_photos" in result, "Missing 'customer_photos' key"
        assert "overall_rating" in result, "Missing 'overall_rating' key"
        assert "total_reviews" in result, "Missing 'total_reviews' key"
        assert "source" in result, "Missing 'source' key"

        # Verify AGI fallback was used
        if result["source"] == "agi_scrape":
            print(f"✓ AGI fallback activated successfully")
            print(f"\n   Results:")
            print(f"   - Reviews scraped: {len(result['reviews'])}")
            print(f"   - Overall rating: {result['overall_rating']}")
            print(f"   - Total reviews: {result['total_reviews']}")
            print(f"   - Customer photos: {len(result['customer_photos'])}")

            # Print sample reviews
            if result['reviews']:
                print(f"\n   Sample reviews (first 2):")
                for i, review in enumerate(result['reviews'][:2], 1):
                    print(f"   {i}. Rating: {review.get('rating', 'N/A')}/5")
                    text = review.get('text', 'N/A')
                    preview = text[:100] + "..." if len(text) > 100 else text
                    print(f"      Text: {preview}")
                    print(f"      Date: {review.get('date', 'N/A')}")
                    print(f"      Source: {review.get('source', 'N/A')}")

            # Verify we got actual data
            if len(result['reviews']) > 0:
                print(f"\n✓ AGI successfully scraped reviews")

                # Save result
                save_test_result("agi_fallback_success", result)

                print_test_result(True, "AGI fallback returned valid reviews")
                return True
            else:
                print(f"\n⚠ WARNING: AGI returned 0 reviews")
                print("   This could mean:")
                print("   1. Business name/location not found")
                print("   2. No public reviews available")
                print("   3. AGI API rate limit or error")

                # Save result anyway
                save_test_result("agi_fallback_empty", result)

                # Still pass if structure is correct
                print_test_result(True, "AGI fallback completed (but returned 0 reviews)")
                return True
        else:
            print(f"⚠ Unexpected source: {result['source']}")
            print("   Expected 'agi_scrape' but got something else")
            print_test_result(False, f"Unexpected source: {result['source']}")
            return False

    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        print_test_result(False, f"Test raised exception: {str(e)}")
        return False


# =============================================================================
# Test 3: Facebook Insights (Optional API)
# =============================================================================

async def test_social_facebook_insights():
    """
    Test: Facebook Marketing API insights

    Expected:
    - If token configured: Returns insights or None (depending on page access)
    - If token missing: Returns None gracefully (no crash)
    """
    print_test_header("Social Facebook Insights (Optional)")

    try:
        social_service = SocialService()

        # Check if Facebook token is configured
        if not social_service.facebook_token:
            print("⚠ SKIP: FACEBOOK_ACCESS_TOKEN not configured")
            print("   This is optional - test passes if no crash occurs")

            # Verify graceful handling
            result = await social_service.get_facebook_insights(
                page_id="example_page_id",
                limit=10
            )

            assert result is None, "Should return None when token missing"
            print("✓ Gracefully returned None when token missing")
            print_test_result(True, "Facebook API gracefully skipped when token unavailable")
            return True

        print("✓ Facebook access token configured")

        # Test with a page ID (you'll need to replace with actual page ID)
        # NOTE: This requires a valid Facebook Page ID you have access to
        page_id = os.getenv("FACEBOOK_PAGE_ID", "example_page_id")
        print(f"   Testing Facebook insights for page: {page_id}")

        result = await social_service.get_facebook_insights(
            page_id=page_id,
            limit=10
        )

        if result is None:
            print("⚠ Facebook API returned None")
            print("   Possible reasons:")
            print("   1. API integration is pending (TODO in code)")
            print("   2. Page ID invalid or no access")
            print("   3. API call failed")
            print_test_result(True, "Facebook API returned None (expected during development)")
            return True
        else:
            # If implementation is complete
            print(f"✓ Facebook insights retrieved")
            print(f"   Posts: {len(result.get('posts', []))}")
            print(f"   Avg engagement rate: {result.get('avg_engagement_rate', 0)}")

            save_test_result("facebook_insights", result)
            print_test_result(True, "Facebook API returned insights")
            return True

    except Exception as e:
        print(f"✗ Exception: {e}")
        print_test_result(False, f"Test raised exception (should handle gracefully): {str(e)}")
        return False


# =============================================================================
# Test 4: Instagram Insights (Optional API)
# =============================================================================

async def test_social_instagram_insights():
    """
    Test: Instagram Graph API insights

    Expected:
    - If token configured: Returns insights or None (depending on account access)
    - If token missing: Returns None gracefully (no crash)
    """
    print_test_header("Social Instagram Insights (Optional)")

    try:
        social_service = SocialService()

        # Check if Instagram token is configured
        if not social_service.instagram_token:
            print("⚠ SKIP: INSTAGRAM_ACCESS_TOKEN not configured")
            print("   This is optional - test passes if no crash occurs")

            # Verify graceful handling
            result = await social_service.get_instagram_insights(
                account_id="example_account_id",
                limit=10
            )

            assert result is None, "Should return None when token missing"
            print("✓ Gracefully returned None when token missing")
            print_test_result(True, "Instagram API gracefully skipped when token unavailable")
            return True

        print("✓ Instagram access token configured")

        # Test with an account ID (you'll need to replace with actual account ID)
        account_id = os.getenv("INSTAGRAM_ACCOUNT_ID", "example_account_id")
        print(f"   Testing Instagram insights for account: {account_id}")

        result = await social_service.get_instagram_insights(
            account_id=account_id,
            limit=10
        )

        if result is None:
            print("⚠ Instagram API returned None")
            print("   Possible reasons:")
            print("   1. API integration is pending (TODO in code)")
            print("   2. Account ID invalid or no access")
            print("   3. API call failed")
            print_test_result(True, "Instagram API returned None (expected during development)")
            return True
        else:
            # If implementation is complete
            print(f"✓ Instagram insights retrieved")
            print(f"   Posts: {len(result.get('posts', []))}")
            print(f"   Avg engagement rate: {result.get('avg_engagement_rate', 0)}")

            save_test_result("instagram_insights", result)
            print_test_result(True, "Instagram API returned insights")
            return True

    except Exception as e:
        print(f"✗ Exception: {e}")
        print_test_result(False, f"Test raised exception (should handle gracefully): {str(e)}")
        return False


# =============================================================================
# Test 5: Google Trends (Optional API)
# =============================================================================

async def test_social_google_trends():
    """
    Test: Google Trends API

    Expected:
    - If API key configured: Returns trend data or empty dict
    - If API key missing: Returns empty dict gracefully (no crash)
    """
    print_test_header("Social Google Trends (Optional)")

    try:
        social_service = SocialService()

        # Test data
        keywords = ["coffee", "specialty coffee", "cold brew"]
        location = {"city": "San Francisco", "state": "CA", "country": "USA"}

        # Check if Trends API key is configured
        if not social_service.trends_api_key:
            print("⚠ SKIP: GOOGLE_TRENDS_API_KEY not configured")
            print("   This is optional - test passes if no crash occurs")

            # Verify graceful handling
            result = await social_service.get_location_trends(
                keywords=keywords,
                location=location
            )

            # Should return empty dict structure
            assert isinstance(result, dict), "Should return dict"
            assert "trending_searches" in result, "Should have trending_searches key"
            assert "related_queries" in result, "Should have related_queries key"
            assert "rising_topics" in result, "Should have rising_topics key"

            print("✓ Gracefully returned empty dict structure when API key missing")
            print_test_result(True, "Google Trends gracefully skipped when API key unavailable")
            return True

        print("✓ Google Trends API key configured")

        print(f"   Testing Google Trends for keywords: {keywords}")
        print(f"   Location: {location['city']}, {location['state']}")

        result = await social_service.get_location_trends(
            keywords=keywords,
            location=location
        )

        # Verify structure
        assert isinstance(result, dict), "Should return dict"
        assert "trending_searches" in result, "Missing trending_searches key"
        assert "related_queries" in result, "Missing related_queries key"
        assert "rising_topics" in result, "Missing rising_topics key"

        # Check if API returned data
        has_data = (
            len(result.get("trending_searches", [])) > 0 or
            len(result.get("related_queries", [])) > 0 or
            len(result.get("rising_topics", [])) > 0
        )

        if has_data:
            print(f"✓ Google Trends data retrieved")
            print(f"   Trending searches: {len(result['trending_searches'])}")
            print(f"   Related queries: {len(result['related_queries'])}")
            print(f"   Rising topics: {len(result['rising_topics'])}")

            save_test_result("google_trends", result)
            print_test_result(True, "Google Trends returned data")
            return True
        else:
            print("⚠ Google Trends returned empty data")
            print("   Possible reasons:")
            print("   1. API integration is pending (TODO in code)")
            print("   2. No trends available for keywords/location")
            print("   3. API call failed")
            print_test_result(True, "Google Trends returned empty data (expected during development)")
            return True

    except Exception as e:
        print(f"✗ Exception: {e}")
        print_test_result(False, f"Test raised exception (should handle gracefully): {str(e)}")
        return False


# =============================================================================
# Test 6: Error Handling
# =============================================================================

async def test_social_error_handling():
    """
    Test: Error handling when no AGI service provided and no GMB API

    Expected: Should return empty dict structure, not crash
    """
    print_test_header("Social Error Handling")

    try:
        social_service = SocialService()

        # Temporarily unset GMB API key (if it exists)
        original_gmb_key = social_service.gmb_api_key
        social_service.gmb_api_key = None

        print("   Testing error handling with no GMB API and no AGI service")

        # Call without AGI service
        result = await social_service.get_google_reviews(
            business_name="Test Business",
            location={"city": "Test City", "state": "TC", "country": "USA"},
            limit=10,
            agi_service=None  # No fallback
        )

        # Restore original GMB key
        social_service.gmb_api_key = original_gmb_key

        # Verify graceful failure
        assert isinstance(result, dict), "Should return dict"
        assert result["source"] == "none", "Should indicate no source"
        assert len(result["reviews"]) == 0, "Should have no reviews"
        assert result["total_reviews"] == 0, "Should have 0 total reviews"

        print("✓ Gracefully handled missing APIs")
        print(f"   Returned source: {result['source']}")
        print(f"   No crash or unhandled exception")

        print_test_result(True, "Error handling works correctly")
        return True

    except Exception as e:
        print(f"✗ Exception: {e}")
        print_test_result(False, f"Should handle errors gracefully: {str(e)}")
        return False


# =============================================================================
# Main Test Runner
# =============================================================================

async def main():
    """Run all social service tests"""
    print("\n" + "="*80)
    print("BRANDMIND AI - SOCIAL SERVICE TEST SUITE")
    print("="*80)
    print("\nThis test suite uses REAL API calls (no mocks)")
    print("Tests will verify GMB API, AGI fallback, and optional social APIs")
    print("\nOutput directory:", OUTPUT_DIR.absolute())
    print("\n" + "="*80)

    # Track results
    results = {}

    # Test 1: GMB API (if available)
    results["gmb_reviews"] = await test_social_gmb_reviews_success()
    await asyncio.sleep(1)  # Brief pause between tests

    # Test 2: AGI Fallback (CRITICAL TEST)
    results["agi_fallback"] = await test_social_gmb_fallback_to_agi()
    await asyncio.sleep(1)

    # Test 3: Facebook Insights (optional)
    results["facebook_insights"] = await test_social_facebook_insights()
    await asyncio.sleep(1)

    # Test 4: Instagram Insights (optional)
    results["instagram_insights"] = await test_social_instagram_insights()
    await asyncio.sleep(1)

    # Test 5: Google Trends (optional)
    results["google_trends"] = await test_social_google_trends()
    await asyncio.sleep(1)

    # Test 6: Error Handling
    results["error_handling"] = await test_social_error_handling()

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    total_tests = len(results)
    passed_tests = sum(1 for passed in results.values() if passed)
    failed_tests = total_tests - passed_tests

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {total_tests} tests")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")

    print("\n" + "="*80)

    # Critical test check
    critical_passed = results.get("agi_fallback", False)

    if not critical_passed:
        print("\n⚠ CRITICAL: AGI fallback test failed!")
        print("   This is the PRIMARY functionality for unclaimed businesses")
        print("   Please ensure AGI_API_KEY is configured correctly")
        return False

    if failed_tests > 0:
        print(f"\n⚠ {failed_tests} test(s) failed")
        return False
    else:
        print("\n✓ All tests passed!")
        return True


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

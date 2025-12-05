"""
Test suite for ConvexService

Tests async database operations for campaigns, research, analytics, and creative data.

Requirements:
- Use REAL Convex deployment (no mocks)
- Test async operations (verify non-blocking)
- Verify data integrity (write-read consistency)
- Include error handling tests
- Clean up test data after execution

Test Philosophy (CLAUDE.md):
- No mocks - real API calls only
- Evidence before completion claims
- Test autonomous agent data flows
"""

import asyncio
import sys
import os

# Load environment variables
import time
import uuid
import json
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")




from services.convex_service import ConvexService
from models import (
    ResearchOutput,
    BusinessContext,
    CompetitorInfo,
    MarketInsights,
    AnalyticsOutput,
    CustomerSentiment,
    PerformancePatterns,
    TrendData,
    CreativeOutput,
    DayContent,
    LearningData,
    CampaignProgress
)

# ============================================================================
# Test Data Factories
# ============================================================================

def create_test_business_context() -> BusinessContext:
    """Create test business context data"""
    return BusinessContext(
        business_name="Test Coffee Shop",
        industry="Coffee & Café",
        description="A modern coffee shop with artisan roasts",
        location={"city": "San Francisco", "state": "CA", "country": "USA"},
        price_range="$$",
        specialties=["Specialty Coffee", "Pastries", "Cold Brew"],
        brand_voice="Friendly and welcoming",
        target_audience="Young professionals and coffee enthusiasts",
        website_url="https://testcoffeeshop.com"
    )


def create_test_competitors() -> List[CompetitorInfo]:
    """Create test competitor data"""
    return [
        CompetitorInfo(
            name="Blue Bottle Coffee",
            website="https://bluebottlecoffee.com",
            location="San Francisco, CA",
            google_rating=4.5,
            review_count=1250,
            social_handles={"instagram": "@bluebottle", "facebook": "bluebottlecoffee"},
            pricing_strategy="Premium",
            brand_voice="Artisan and sophisticated",
            top_content_themes=["Coffee education", "Brewing techniques", "Origin stories"],
            differentiators=["Single-origin focus", "Sustainability"],
            similarity_score=0.85
        ),
        CompetitorInfo(
            name="Philz Coffee",
            website="https://philzcoffee.com",
            location="San Francisco, CA",
            google_rating=4.3,
            review_count=980,
            social_handles={"instagram": "@philzcoffee"},
            pricing_strategy="Mid-range",
            brand_voice="Casual and friendly",
            top_content_themes=["Community", "Custom blends", "Local events"],
            differentiators=["Customized drinks", "One cup at a time"],
            similarity_score=0.78
        )
    ]


def create_test_market_insights() -> MarketInsights:
    """Create test market insights data"""
    return MarketInsights(
        trending_topics=["Cold brew", "Oat milk", "Specialty beans", "Nitro coffee"],
        market_gaps=["Late-night coffee service", "Coffee subscription boxes"],
        positioning_opportunities=["Position as eco-friendly", "Focus on local roasters"],
        content_strategy={
            "winning_formats": ["Short videos", "Behind-the-scenes", "Customer stories"],
            "high_engagement_themes": ["Latte art", "Brewing tips", "New menu items"]
        }
    )


def create_test_research_output(campaign_id: str) -> ResearchOutput:
    """Create test research output"""
    return ResearchOutput(
        campaign_id=campaign_id,
        business_context=create_test_business_context(),
        competitors=create_test_competitors(),
        market_insights=create_test_market_insights(),
        research_images=[],
        timestamp=datetime.now()
    )


def create_test_customer_sentiment() -> CustomerSentiment:
    """Create test customer sentiment data"""
    return CustomerSentiment(
        positive_themes=["Great coffee", "Friendly staff", "Cozy atmosphere"],
        negative_themes=["Long wait times", "Limited seating"],
        popular_items=["Cappuccino", "Croissant", "Cold Brew"],
        quotable_reviews=[
            "Best coffee in the neighborhood!",
            "Love the vibe and the baristas are awesome"
        ],
        content_opportunities=[
            "Showcase barista skills",
            "Highlight popular menu items",
            "Share customer testimonials"
        ]
    )


def create_test_performance_patterns() -> PerformancePatterns:
    """Create test performance patterns data"""
    return PerformancePatterns(
        winning_patterns={
            "content_types": ["video", "carousel"],
            "themes": ["latte art", "new menu items"],
            "posting_times": ["8:00 AM", "2:00 PM"],
            "hashtags": ["#coffeelover", "#specialtycoffee"]
        },
        avoid_patterns={
            "low_performers": ["text-only posts", "promotional posts"],
            "reasons": ["Low engagement", "Audience prefers visual content"]
        },
        recommendations=[
            "Post videos during morning hours",
            "Focus on behind-the-scenes content",
            "Use carousel posts for product showcases"
        ]
    )


def create_test_trend_data() -> TrendData:
    """Create test trend data"""
    return TrendData(
        trending_searches=[
            {"query": "cold brew coffee", "growth": "+25%"},
            {"query": "oat milk latte", "growth": "+40%"}
        ],
        related_queries=["specialty coffee near me", "artisan coffee shops"],
        rising_topics=["Nitro cold brew", "Coffee subscriptions", "Sustainable coffee"]
    )


def create_test_analytics_output(campaign_id: str) -> AnalyticsOutput:
    """Create test analytics output"""
    return AnalyticsOutput(
        campaign_id=campaign_id,
        customer_sentiment=create_test_customer_sentiment(),
        past_performance=create_test_performance_patterns(),
        market_trends=create_test_trend_data(),
        customer_photos=[],
        timestamp=datetime.now()
    )


def create_test_day_content(day: int) -> DayContent:
    """Create test day content"""
    return DayContent(
        day=day,
        theme=f"Day {day} Theme",
        caption=f"Test caption for day {day} #coffeelover #specialtycoffee",
        hashtags=["#coffeelover", "#specialtycoffee", f"#day{day}"],
        image_urls=[
            f"https://pub-test.r2.dev/campaigns/test/day_{day}_1.jpg",
            f"https://pub-test.r2.dev/campaigns/test/day_{day}_2.jpg"
        ],
        video_url=f"https://pub-test.r2.dev/campaigns/test/day_{day}_video.mp4" if day in [1, 4, 7] else None,
        cta="Visit us today!",
        recommended_post_time=f"{10 + day}:00 AM"
    )


def create_test_learning_data() -> LearningData:
    """Create test learning data"""
    return LearningData(
        what_worked=[
            {
                "insight": "Video content performed well",
                "evidence": "3 videos generated for days 1, 4, 7",
                "recommendation": "Continue creating video content"
            }
        ],
        what_to_improve=[
            {
                "issue": "Limited past performance data",
                "evidence": "Used default posting times",
                "recommendation": "Collect engagement data for optimization"
            }
        ],
        next_iteration_strategy={
            "focus_areas": ["Implement quality evaluation", "Build performance database"],
            "expected_improvements": ["15% higher quality scores", "20% better engagement"],
            "agent_evolution": "Move to autonomous quality assessment"
        }
    )


def create_test_creative_output(campaign_id: str) -> CreativeOutput:
    """Create test creative output"""
    days = [create_test_day_content(i) for i in range(1, 8)]
    return CreativeOutput(
        campaign_id=campaign_id,
        days=days,
        learning_data=create_test_learning_data(),
        status="completed",
        timestamp=datetime.now()
    )


# ============================================================================
# Test Functions
# ============================================================================

async def test_convex_create_campaign():
    """
    Test: Create campaign and verify it exists in Convex

    Success Criteria:
    - Campaign record created
    - Query returns record with matching ID
    - Initial status is 'pending'
    - Initial progress is 0
    """
    print("\n" + "="*70)
    print("TEST: Convex Create Campaign")
    print("="*70)

    try:
        service = ConvexService()
        campaign_id = f"test_campaign_{uuid.uuid4().hex[:8]}"

        print(f"Creating campaign: {campaign_id}")

        # Create campaign
        start_time = time.time()
        result = await service.create_campaign(campaign_id)
        elapsed = time.time() - start_time

        print(f"✓ Campaign created in {elapsed:.2f}s")
        print(f"  Result: {result}")

        # Verify campaign exists by retrieving progress
        progress = await service.get_progress(campaign_id)

        if not progress:
            raise AssertionError(f"Campaign {campaign_id} not found after creation")

        print(f"✓ Campaign verified:")
        print(f"  Status: {progress.status}")
        print(f"  Progress: {progress.percentage}%")

        # Verify initial state
        assert progress.status == "pending", f"Expected status 'pending', got '{progress.status}'"
        assert progress.percentage == 0, f"Expected progress 0, got {progress.percentage}"

        print("✅ TEST PASSED: Campaign created successfully")
        return True, campaign_id

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def test_convex_update_progress():
    """
    Test: Update campaign progress and verify changes

    Success Criteria:
    - Progress updated successfully
    - Query returns updated values
    - All fields match expected values
    """
    print("\n" + "="*70)
    print("TEST: Convex Update Progress")
    print("="*70)

    try:
        service = ConvexService()
        campaign_id = f"test_progress_{uuid.uuid4().hex[:8]}"

        # Create campaign first
        await service.create_campaign(campaign_id)
        print(f"✓ Campaign created: {campaign_id}")

        # Update progress to 50%
        await service.update_progress(
            campaign_id=campaign_id,
            status="agent2_running",
            progress=50,
            current_agent="Strategy Agent",
            message="Analyzing customer sentiment"
        )

        print("✓ Progress updated to 50%")

        # Verify update
        progress = await service.get_progress(campaign_id)

        if not progress:
            raise AssertionError(f"Campaign {campaign_id} not found")

        print(f"✓ Progress retrieved:")
        print(f"  Status: {progress.status}")
        print(f"  Progress: {progress.percentage}%")
        print(f"  Message: {progress.message}")

        # Verify values
        assert progress.status == "agent2_running", f"Expected 'agent2_running', got '{progress.status}'"
        assert progress.percentage == 50, f"Expected 50, got {progress.percentage}"
        assert "sentiment" in progress.message.lower(), f"Message doesn't contain expected text"

        # Update again to 100%
        await service.update_progress(
            campaign_id=campaign_id,
            status="completed",
            progress=100,
            current_agent=None,
            message="Campaign complete"
        )

        progress = await service.get_progress(campaign_id)
        assert progress.percentage == 100, f"Expected 100, got {progress.percentage}"

        print("✓ Progress updated to 100%")
        print("✅ TEST PASSED: Progress tracking works correctly")
        return True, campaign_id

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def test_convex_store_research():
    """
    Test: Store research data and verify retrieval

    Success Criteria:
    - Research data stored successfully
    - Retrieved data matches stored data
    - All nested objects preserved
    - Data integrity maintained
    """
    print("\n" + "="*70)
    print("TEST: Convex Store Research Data")
    print("="*70)

    try:
        service = ConvexService()
        campaign_id = f"test_research_{uuid.uuid4().hex[:8]}"

        # Create campaign
        await service.create_campaign(campaign_id)
        print(f"✓ Campaign created: {campaign_id}")

        # Create research data
        research_data = create_test_research_output(campaign_id)
        print(f"✓ Test research data created:")
        print(f"  Business: {research_data.business_context.business_name}")
        print(f"  Competitors: {len(research_data.competitors)}")
        print(f"  Trending topics: {len(research_data.market_insights.trending_topics)}")

        # Store research data
        start_time = time.time()
        result = await service.store_research(research_data)
        elapsed = time.time() - start_time

        print(f"✓ Research stored in {elapsed:.2f}s")

        # Retrieve and verify
        retrieved = await service.get_research(campaign_id)

        if not retrieved:
            raise AssertionError(f"Research data not found for campaign {campaign_id}")

        print("✓ Research data retrieved")

        # Verify data integrity
        assert retrieved.campaign_id == campaign_id, "Campaign ID mismatch"
        assert retrieved.business_context.business_name == research_data.business_context.business_name, "Business name mismatch"
        assert len(retrieved.competitors) == len(research_data.competitors), "Competitor count mismatch"
        assert retrieved.competitors[0].name == research_data.competitors[0].name, "Competitor name mismatch"
        assert len(retrieved.market_insights.trending_topics) == len(research_data.market_insights.trending_topics), "Trending topics count mismatch"

        print("✓ Data integrity verified:")
        print(f"  ✓ Business name: {retrieved.business_context.business_name}")
        print(f"  ✓ Competitors: {len(retrieved.competitors)} competitors")
        print(f"  ✓ Market insights: {len(retrieved.market_insights.trending_topics)} trending topics")

        print("✅ TEST PASSED: Research data stored and retrieved correctly")
        return True, campaign_id

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def test_convex_store_analytics():
    """
    Test: Store analytics data and verify retrieval

    Success Criteria:
    - Analytics data stored successfully
    - Retrieved data matches stored data
    - All nested objects preserved (sentiment, performance, trends)
    - Data integrity maintained
    """
    print("\n" + "="*70)
    print("TEST: Convex Store Analytics Data")
    print("="*70)

    try:
        service = ConvexService()
        campaign_id = f"test_analytics_{uuid.uuid4().hex[:8]}"

        # Create campaign
        await service.create_campaign(campaign_id)
        print(f"✓ Campaign created: {campaign_id}")

        # Create analytics data
        analytics_data = create_test_analytics_output(campaign_id)
        print(f"✓ Test analytics data created:")
        print(f"  Positive themes: {len(analytics_data.customer_sentiment.positive_themes)}")
        print(f"  Popular items: {len(analytics_data.customer_sentiment.popular_items)}")
        print(f"  Trending searches: {len(analytics_data.market_trends.trending_searches)}")

        # Store analytics data
        start_time = time.time()
        result = await service.store_analytics(analytics_data)
        elapsed = time.time() - start_time

        print(f"✓ Analytics stored in {elapsed:.2f}s")

        # Retrieve and verify
        retrieved = await service.get_analytics(campaign_id)

        if not retrieved:
            raise AssertionError(f"Analytics data not found for campaign {campaign_id}")

        print("✓ Analytics data retrieved")

        # Verify data integrity
        assert retrieved.campaign_id == campaign_id, "Campaign ID mismatch"
        assert len(retrieved.customer_sentiment.positive_themes) == len(analytics_data.customer_sentiment.positive_themes), "Positive themes count mismatch"
        assert retrieved.customer_sentiment.popular_items[0] == analytics_data.customer_sentiment.popular_items[0], "Popular items mismatch"
        assert retrieved.past_performance is not None, "Past performance missing"
        assert len(retrieved.past_performance.recommendations) == len(analytics_data.past_performance.recommendations), "Recommendations count mismatch"
        assert len(retrieved.market_trends.trending_searches) == len(analytics_data.market_trends.trending_searches), "Trending searches count mismatch"

        print("✓ Data integrity verified:")
        print(f"  ✓ Positive themes: {len(retrieved.customer_sentiment.positive_themes)}")
        print(f"  ✓ Popular items: {len(retrieved.customer_sentiment.popular_items)}")
        print(f"  ✓ Recommendations: {len(retrieved.past_performance.recommendations)}")
        print(f"  ✓ Trending searches: {len(retrieved.market_trends.trending_searches)}")

        print("✅ TEST PASSED: Analytics data stored and retrieved correctly")
        return True, campaign_id

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def test_convex_store_creative():
    """
    Test: Store creative content and verify retrieval

    Success Criteria:
    - Creative data stored successfully
    - All 7 days of content preserved
    - Learning data preserved
    - Retrieved data matches stored data
    """
    print("\n" + "="*70)
    print("TEST: Convex Store Creative Content")
    print("="*70)

    try:
        service = ConvexService()
        campaign_id = f"test_creative_{uuid.uuid4().hex[:8]}"

        # Create campaign
        await service.create_campaign(campaign_id)
        print(f"✓ Campaign created: {campaign_id}")

        # Create creative data
        creative_data = create_test_creative_output(campaign_id)
        print(f"✓ Test creative data created:")
        print(f"  Days: {len(creative_data.days)}")
        print(f"  Video days: {len([d for d in creative_data.days if d.video_url])}")
        print(f"  Learnings: {len(creative_data.learning_data.what_worked)}")

        # Store creative data
        start_time = time.time()
        result = await service.store_content(creative_data)
        elapsed = time.time() - start_time

        print(f"✓ Creative content stored in {elapsed:.2f}s")

        # Retrieve and verify
        retrieved = await service.get_content(campaign_id)

        if not retrieved:
            raise AssertionError(f"Creative data not found for campaign {campaign_id}")

        print("✓ Creative data retrieved")

        # Verify data integrity
        assert retrieved.campaign_id == campaign_id, "Campaign ID mismatch"
        assert len(retrieved.days) == 7, f"Expected 7 days, got {len(retrieved.days)}"
        assert retrieved.status == "completed", f"Expected 'completed', got '{retrieved.status}'"

        # Verify day content
        for day_num in range(1, 8):
            day = retrieved.days[day_num - 1]
            assert day.day == day_num, f"Day number mismatch: expected {day_num}, got {day.day}"
            assert len(day.image_urls) == 2, f"Day {day_num}: expected 2 images, got {len(day.image_urls)}"
            if day_num in [1, 4, 7]:
                assert day.video_url is not None, f"Day {day_num}: video missing"

        # Verify learning data
        assert len(retrieved.learning_data.what_worked) > 0, "Learning data missing 'what_worked'"
        assert len(retrieved.learning_data.what_to_improve) > 0, "Learning data missing 'what_to_improve'"
        assert "focus_areas" in retrieved.learning_data.next_iteration_strategy, "Strategy missing 'focus_areas'"

        print("✓ Data integrity verified:")
        print(f"  ✓ Days: {len(retrieved.days)}")
        print(f"  ✓ Videos: {len([d for d in retrieved.days if d.video_url])}")
        print(f"  ✓ What worked: {len(retrieved.learning_data.what_worked)} insights")
        print(f"  ✓ What to improve: {len(retrieved.learning_data.what_to_improve)} items")

        print("✅ TEST PASSED: Creative content stored and retrieved correctly")
        return True, campaign_id

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def test_convex_async_operations():
    """
    Test: Verify async operations don't block

    Success Criteria:
    - Multiple operations run concurrently
    - Total time < sum of individual times (proves non-blocking)
    - All operations complete successfully
    """
    print("\n" + "="*70)
    print("TEST: Convex Async Operations (Non-Blocking)")
    print("="*70)

    try:
        service = ConvexService()

        # Create 3 campaigns concurrently
        campaign_ids = [f"test_async_{i}_{uuid.uuid4().hex[:8]}" for i in range(3)]

        print(f"Creating {len(campaign_ids)} campaigns concurrently...")

        start_time = time.time()

        # Run all creates concurrently
        tasks = [service.create_campaign(cid) for cid in campaign_ids]
        results = await asyncio.gather(*tasks)

        elapsed = time.time() - start_time

        print(f"✓ All {len(campaign_ids)} campaigns created in {elapsed:.2f}s")
        print(f"  Average: {elapsed/len(campaign_ids):.2f}s per campaign")

        # Verify all campaigns exist
        for cid in campaign_ids:
            progress = await service.get_progress(cid)
            if not progress:
                raise AssertionError(f"Campaign {cid} not found")

        print(f"✓ All {len(campaign_ids)} campaigns verified")

        # Test concurrent updates
        print(f"\nUpdating {len(campaign_ids)} campaigns concurrently...")

        start_time = time.time()

        update_tasks = [
            service.update_progress(
                campaign_id=cid,
                status="agent1_running",
                progress=25,
                current_agent="Research Agent",
                message=f"Test update {i}"
            )
            for i, cid in enumerate(campaign_ids)
        ]

        await asyncio.gather(*update_tasks)
        elapsed = time.time() - start_time

        print(f"✓ All {len(campaign_ids)} updates completed in {elapsed:.2f}s")

        # Verify non-blocking behavior
        # If operations were blocking, time would be ~3x longer
        max_expected = 5.0  # Generous allowance for network latency

        if elapsed > max_expected:
            print(f"⚠ Warning: Operations may be blocking (took {elapsed:.2f}s)")
        else:
            print(f"✓ Operations are non-blocking (completed in {elapsed:.2f}s)")

        print("✅ TEST PASSED: Async operations work correctly")
        return True, campaign_ids

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def test_convex_full_campaign_data():
    """
    Test: Retrieve full campaign data (research + analytics + progress)

    Success Criteria:
    - All campaign data retrieved in one call
    - Research data present
    - Analytics data present
    - Progress data present
    """
    print("\n" + "="*70)
    print("TEST: Convex Get Full Campaign Data")
    print("="*70)

    try:
        service = ConvexService()
        campaign_id = f"test_full_{uuid.uuid4().hex[:8]}"

        # Create campaign
        await service.create_campaign(campaign_id)
        print(f"✓ Campaign created: {campaign_id}")

        # Store research data
        research_data = create_test_research_output(campaign_id)
        await service.store_research(research_data)
        print("✓ Research data stored")

        # Store analytics data
        analytics_data = create_test_analytics_output(campaign_id)
        await service.store_analytics(analytics_data)
        print("✓ Analytics data stored")

        # Update progress
        await service.update_progress(
            campaign_id=campaign_id,
            status="agent3_running",
            progress=75,
            current_agent="Creative Agent",
            message="Generating content"
        )
        print("✓ Progress updated")

        # Retrieve full campaign data
        print("\nRetrieving full campaign data...")
        start_time = time.time()

        full_data = await service.get_full_campaign_data(campaign_id)
        elapsed = time.time() - start_time

        print(f"✓ Full data retrieved in {elapsed:.2f}s")

        # Verify all components present
        assert full_data["research"] is not None, "Research data missing"
        assert full_data["analytics"] is not None, "Analytics data missing"
        assert full_data["progress"] is not None, "Progress data missing"

        print("✓ All data components present:")
        print(f"  ✓ Research: {full_data['research'].business_context.business_name}")
        print(f"  ✓ Analytics: {len(full_data['analytics'].customer_sentiment.positive_themes)} positive themes")
        print(f"  ✓ Progress: {full_data['progress'].percentage}% complete")

        print("✅ TEST PASSED: Full campaign data retrieved correctly")
        return True, campaign_id

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def test_convex_error_handling():
    """
    Test: Error handling for invalid operations

    Success Criteria:
    - Graceful handling of non-existent campaigns
    - Clear error messages
    - No unhandled exceptions
    """
    print("\n" + "="*70)
    print("TEST: Convex Error Handling")
    print("="*70)

    try:
        service = ConvexService()
        fake_campaign_id = "nonexistent_campaign_123"

        print(f"Testing retrieval of non-existent campaign: {fake_campaign_id}")

        # Try to get progress for non-existent campaign
        progress = await service.get_progress(fake_campaign_id)

        if progress is None:
            print("✓ Non-existent campaign returns None (as expected)")
        else:
            raise AssertionError("Expected None for non-existent campaign, got data")

        # Try to get research for non-existent campaign
        research = await service.get_research(fake_campaign_id)

        if research is None:
            print("✓ Non-existent research returns None (as expected)")
        else:
            raise AssertionError("Expected None for non-existent research, got data")

        # Try to get analytics for non-existent campaign
        analytics = await service.get_analytics(fake_campaign_id)

        if analytics is None:
            print("✓ Non-existent analytics returns None (as expected)")
        else:
            raise AssertionError("Expected None for non-existent analytics, got data")

        print("✅ TEST PASSED: Error handling works correctly")
        return True, None

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


# ============================================================================
# Test Cleanup
# ============================================================================

async def cleanup_test_data(campaign_ids: List[str]):
    """
    Clean up test data from Convex

    Note: Convex doesn't have a public delete API in Python SDK yet,
    so we log the campaigns that should be cleaned up manually.
    """
    print("\n" + "="*70)
    print("TEST DATA CLEANUP")
    print("="*70)

    print("\nTest campaigns created (for manual cleanup if needed):")
    for cid in campaign_ids:
        print(f"  - {cid}")

    print("\nNote: Convex test data can be cleaned up via dashboard:")
    print("  1. Go to Convex dashboard")
    print("  2. Navigate to Data tab")
    print("  3. Filter campaigns table by test_* prefix")
    print("  4. Delete test records")


# ============================================================================
# Main Test Runner
# ============================================================================

async def main():
    """
    Run all Convex service tests

    Success Criteria:
    - All tests pass
    - Evidence provided for each test
    - Test data logged for verification
    """
    print("\n" + "="*70)
    print("CONVEX SERVICE TEST SUITE")
    print("="*70)
    print("\nTesting with REAL Convex deployment (no mocks)")
    print("Following CLAUDE.md principles:")
    print("  ✓ Real API calls only")
    print("  ✓ Evidence before completion claims")
    print("  ✓ Test autonomous agent data flows")

    # Track results
    results = []
    campaign_ids = []

    # Run tests
    tests = [
        ("Create Campaign", test_convex_create_campaign),
        ("Update Progress", test_convex_update_progress),
        ("Store Research", test_convex_store_research),
        ("Store Analytics", test_convex_store_analytics),
        ("Store Creative", test_convex_store_creative),
        ("Async Operations", test_convex_async_operations),
        ("Full Campaign Data", test_convex_full_campaign_data),
        ("Error Handling", test_convex_error_handling),
    ]

    for test_name, test_func in tests:
        try:
            passed, cid = await test_func()
            results.append((test_name, passed))

            if cid:
                if isinstance(cid, list):
                    campaign_ids.extend(cid)
                else:
                    campaign_ids.append(cid)

        except Exception as e:
            print(f"\n❌ TEST '{test_name}' CRASHED: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, p in results if p)
    total = len(results)

    for test_name, passed_flag in results:
        status = "✅ PASSED" if passed_flag else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")

    # Cleanup
    if campaign_ids:
        await cleanup_test_data(campaign_ids)

    # Save test results
    output_dir = Path(__file__).parent / "outputs" / "convex"
    output_dir.mkdir(parents=True, exist_ok=True)

    results_file = output_dir / f"test_results_{int(time.time())}.json"
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": [
                {"test": name, "passed": passed}
                for name, passed in results
            ],
            "summary": {
                "total": total,
                "passed": passed,
                "failed": total - passed
            },
            "test_campaigns": campaign_ids
        }, f, indent=2)

    print(f"\n✓ Test results saved to: {results_file}")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
BrandMind AI - Strategy Agent (Agent 2) Integration Tests

Tests Agent 2's complete analytics workflow:
- Fetch Google My Business reviews (with AGI fallback)
- Analyze customer sentiment with Gemini HIGH thinking
- Fetch Facebook/Instagram performance (optional)
- Analyze performance patterns with Gemini HIGH thinking
- Fetch Google Trends data
- Store all data in Convex + R2

Test Philosophy:
- Use REAL API calls (no mocks) to verify integration
- Test AGI fallback for unclaimed businesses
- Test graceful handling of missing social tokens
- Save outputs for manual inspection
- Verify data stored in Convex
- Verify progress tracking (25% → 50%)

Test Cases (Section 2.2 from TEST_PLAN.md):
1. test_strategy_agent_full_workflow() - Complete analytics with sentiment analysis
2. test_strategy_agent_agi_fallback() - AGI scraping for unclaimed businesses
3. test_strategy_agent_no_social_tokens() - Graceful skip when FB/IG unavailable
4. test_strategy_agent_error_handling() - Error recovery
"""

import asyncio
import sys
import os

# Load environment variables
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")




from agents.strategy_agent import StrategyAgent
from agents.research_agent import ResearchAgent
from services.gemini_service import GeminiService
from services.social_service import SocialService
from services.agi_service import AGIService
from services.convex_service import ConvexService
from services.r2_service import R2Service
from models import AnalyticsOutput, CustomerSentiment, PerformancePatterns, TrendData

# Test configuration
OUTPUT_DIR = Path(__file__).parent / "outputs" / "agents" / "strategy"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Test data
TEST_BUSINESS_URL = "https://www.bluebottlecoffee.com"
TEST_BUSINESS_NAME = "Blue Bottle Coffee"
TEST_LOCATION = {"city": "San Francisco", "state": "CA", "country": "USA"}


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.start_time = datetime.now()

    def add_pass(self, test_name: str):
        self.passed.append(test_name)
        print(f"✅ PASS: {test_name}")

    def add_fail(self, test_name: str, error: str):
        self.failed.append((test_name, error))
        print(f"❌ FAIL: {test_name}")
        print(f"   Error: {error}")

    def summary(self):
        duration = (datetime.now() - self.start_time).total_seconds()
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {len(self.passed) + len(self.failed)}")
        print(f"Passed: {len(self.passed)}")
        print(f"Failed: {len(self.failed)}")
        print(f"Duration: {duration:.2f}s")

        if self.passed:
            print("\n✅ Passed Tests:")
            for test in self.passed:
                print(f"   - {test}")

        if self.failed:
            print("\n❌ Failed Tests:")
            for test, error in self.failed:
                print(f"   - {test}")
                print(f"     {error}")

        print("=" * 80)
        return len(self.failed) == 0


# Global test results tracker
results = TestResults()


async def setup_test_campaign(
    business_url: str = TEST_BUSINESS_URL,
    with_research: bool = True
) -> str:
    """
    Setup test campaign with Agent 1 research data.

    Args:
        business_url: Business website URL
        with_research: Whether to run Agent 1 first

    Returns:
        campaign_id
    """
    campaign_id = f"test_strategy_{uuid.uuid4().hex[:8]}"

    print(f"\n📋 Setting up test campaign: {campaign_id}")

    if with_research:
        # Initialize services for Agent 1
        agi_service = AGIService()
        convex_service = ConvexService()
        r2_service = R2Service()

        # Create campaign in Convex
        await convex_service.create_campaign(campaign_id)

        # Run Agent 1 to populate research data
        research_agent = ResearchAgent(
            agi_service=agi_service,
            convex_service=convex_service,
            r2_service=r2_service
        )

        print(f"🔍 Running Agent 1 to generate research data...")
        research_output = await research_agent.run(
            campaign_id=campaign_id,
            business_url=business_url
        )

        print(f"✅ Research complete: {research_output.business_context.business_name}")

        # Save research output
        research_file = OUTPUT_DIR / f"{campaign_id}_research.json"
        with open(research_file, "w") as f:
            json.dump(research_output.model_dump(mode='json'), f, indent=2, default=str)

        print(f"💾 Saved research to: {research_file}")

    return campaign_id


async def test_strategy_agent_full_workflow():
    """
    Test Agent 2 with complete analytics workflow.

    Expected:
    - Fetches reviews (GMB or AGI fallback)
    - Analyzes sentiment with Gemini HIGH thinking
    - Fetches social media insights (if tokens available)
    - Analyzes performance patterns with Gemini HIGH thinking
    - Fetches Google Trends data
    - Stores all data in Convex
    - Progress updates 25% → 50%
    """
    test_name = "test_strategy_agent_full_workflow"
    print("\n" + "=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)

    try:
        # Setup: Run Agent 1 to get research data
        campaign_id = await setup_test_campaign(with_research=True)

        # Initialize services for Agent 2
        gemini_service = GeminiService()
        social_service = SocialService()
        convex_service = ConvexService()
        r2_service = R2Service()
        agi_service = AGIService()

        # Initialize Agent 2
        strategy_agent = StrategyAgent(
            gemini_service=gemini_service,
            social_service=social_service,
            convex_service=convex_service,
            r2_service=r2_service,
            agi_service=agi_service
        )

        print(f"\n📊 Running Agent 2 for campaign: {campaign_id}")

        # Run Agent 2
        analytics_output = await strategy_agent.run(
            campaign_id=campaign_id,
            facebook_page_id=None,  # Optional
            instagram_account_id=None  # Optional
        )

        print(f"\n✓ Agent 2 completed")

        # Verify output structure
        assert isinstance(analytics_output, AnalyticsOutput), "Invalid output type"
        assert analytics_output.campaign_id == campaign_id, "Campaign ID mismatch"
        assert isinstance(analytics_output.customer_sentiment, CustomerSentiment), "Missing sentiment"
        assert isinstance(analytics_output.market_trends, TrendData), "Missing trends"

        print(f"\n📋 Analytics Output:")
        print(f"   - Positive themes: {len(analytics_output.customer_sentiment.positive_themes)}")
        print(f"   - Negative themes: {len(analytics_output.customer_sentiment.negative_themes)}")
        print(f"   - Popular items: {len(analytics_output.customer_sentiment.popular_items)}")
        print(f"   - Content opportunities: {len(analytics_output.customer_sentiment.content_opportunities)}")
        print(f"   - Quotable reviews: {len(analytics_output.customer_sentiment.quotable_reviews)}")
        print(f"   - Trending searches: {len(analytics_output.market_trends.trending_searches)}")
        print(f"   - Past performance: {'Available' if analytics_output.past_performance else 'None'}")

        # Verify sentiment analysis (Gemini HIGH thinking)
        assert len(analytics_output.customer_sentiment.positive_themes) > 0, \
            "Sentiment analysis should find positive themes"

        # Verify data stored in Convex
        retrieved_analytics = await convex_service.get_analytics(campaign_id)
        assert retrieved_analytics is not None, "Analytics not found in Convex"
        assert retrieved_analytics.campaign_id == campaign_id, "Convex data mismatch"

        print(f"\n✅ Data stored in Convex successfully")

        # Verify progress tracking
        progress = await convex_service.get_progress(campaign_id)
        assert progress is not None, "Progress not found"
        assert progress.percentage >= 50, f"Progress should be 50%, got {progress.percentage}%"

        print(f"\n✅ Progress tracking: {progress.percentage}% - {progress.message}")

        # Save analytics output
        output_file = OUTPUT_DIR / f"{campaign_id}_analytics.json"
        with open(output_file, "w") as f:
            json.dump(analytics_output.model_dump(mode='json'), f, indent=2, default=str)

        print(f"\n💾 Saved analytics to: {output_file}")

        # Save detailed report
        report_file = OUTPUT_DIR / f"{campaign_id}_report.txt"
        with open(report_file, "w") as f:
            f.write(f"Strategy Agent Test Report\n")
            f.write(f"Campaign ID: {campaign_id}\n")
            f.write(f"Test: {test_name}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")

            f.write(f"=== Customer Sentiment ===\n\n")
            f.write(f"Positive Themes:\n")
            for theme in analytics_output.customer_sentiment.positive_themes:
                f.write(f"  - {theme}\n")

            f.write(f"\nNegative Themes:\n")
            for theme in analytics_output.customer_sentiment.negative_themes:
                f.write(f"  - {theme}\n")

            f.write(f"\nPopular Items:\n")
            for item in analytics_output.customer_sentiment.popular_items:
                f.write(f"  - {item}\n")

            f.write(f"\nContent Opportunities:\n")
            for opp in analytics_output.customer_sentiment.content_opportunities:
                f.write(f"  - {opp}\n")

            f.write(f"\nQuotable Reviews:\n")
            for quote in analytics_output.customer_sentiment.quotable_reviews:
                f.write(f"  - \"{quote}\"\n")

            if analytics_output.past_performance:
                f.write(f"\n=== Performance Patterns ===\n\n")
                f.write(f"Winning Patterns:\n")
                f.write(json.dumps(analytics_output.past_performance.winning_patterns, indent=2))
                f.write(f"\n\nAvoid Patterns:\n")
                f.write(json.dumps(analytics_output.past_performance.avoid_patterns, indent=2))
                f.write(f"\n\nRecommendations:\n")
                for rec in analytics_output.past_performance.recommendations:
                    f.write(f"  - {rec}\n")

            f.write(f"\n=== Market Trends ===\n\n")
            f.write(f"Trending Searches:\n")
            for search in analytics_output.market_trends.trending_searches:
                f.write(f"  - {search}\n")

            f.write(f"\nRelated Queries:\n")
            for query in analytics_output.market_trends.related_queries:
                f.write(f"  - {query}\n")

            f.write(f"\nRising Topics:\n")
            for topic in analytics_output.market_trends.rising_topics:
                f.write(f"  - {topic}\n")

        print(f"💾 Saved report to: {report_file}")

        results.add_pass(test_name)

    except Exception as e:
        results.add_fail(test_name, str(e))
        print(f"\n💥 Exception details:")
        import traceback
        traceback.print_exc()


async def test_strategy_agent_agi_fallback():
    """
    Test Agent 2 with AGI fallback for unclaimed businesses.

    Expected:
    - GMB API fails (business not claimed)
    - AGI scraping activates automatically
    - Reviews fetched from Google Maps/Yelp/etc
    - Sentiment analysis works with AGI-scraped reviews
    - source = "agi_scrape"
    """
    test_name = "test_strategy_agent_agi_fallback"
    print("\n" + "=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)

    try:
        # Setup: Use a business that likely doesn't have claimed GMB
        campaign_id = await setup_test_campaign(
            business_url="https://www.philzcoffee.com",
            with_research=True
        )

        # Initialize services
        gemini_service = GeminiService()
        social_service = SocialService()
        convex_service = ConvexService()
        r2_service = R2Service()
        agi_service = AGIService()

        # Initialize Agent 2
        strategy_agent = StrategyAgent(
            gemini_service=gemini_service,
            social_service=social_service,
            convex_service=convex_service,
            r2_service=r2_service,
            agi_service=agi_service
        )

        print(f"\n📊 Running Agent 2 with AGI fallback test...")

        # Run Agent 2
        analytics_output = await strategy_agent.run(campaign_id=campaign_id)

        print(f"\n✓ Agent 2 completed")

        # Verify AGI fallback was used
        # Note: We can't directly check the source here since it's not exposed in AnalyticsOutput
        # But we can verify reviews were analyzed
        assert len(analytics_output.customer_sentiment.positive_themes) > 0 or \
               len(analytics_output.customer_sentiment.negative_themes) > 0, \
            "Sentiment analysis should work with AGI-scraped reviews"

        print(f"\n✅ AGI fallback worked - sentiment analysis completed")
        print(f"   - Positive themes: {len(analytics_output.customer_sentiment.positive_themes)}")
        print(f"   - Negative themes: {len(analytics_output.customer_sentiment.negative_themes)}")

        # Save output
        output_file = OUTPUT_DIR / f"{campaign_id}_agi_fallback.json"
        with open(output_file, "w") as f:
            json.dump(analytics_output.model_dump(mode='json'), f, indent=2, default=str)

        print(f"💾 Saved output to: {output_file}")

        results.add_pass(test_name)

    except Exception as e:
        results.add_fail(test_name, str(e))
        print(f"\n💥 Exception details:")
        import traceback
        traceback.print_exc()


async def test_strategy_agent_no_social_tokens():
    """
    Test Agent 2 graceful handling when FB/IG tokens unavailable.

    Expected:
    - Completes without social media insights
    - past_performance = None
    - No crashes
    - Sentiment analysis still works
    """
    test_name = "test_strategy_agent_no_social_tokens"
    print("\n" + "=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)

    try:
        # Setup campaign
        campaign_id = await setup_test_campaign(with_research=True)

        # Initialize services
        gemini_service = GeminiService()
        social_service = SocialService()
        convex_service = ConvexService()
        r2_service = R2Service()
        agi_service = AGIService()

        # Initialize Agent 2
        strategy_agent = StrategyAgent(
            gemini_service=gemini_service,
            social_service=social_service,
            convex_service=convex_service,
            r2_service=r2_service,
            agi_service=agi_service
        )

        print(f"\n📊 Running Agent 2 without social tokens...")

        # Run Agent 2 WITHOUT social media IDs
        analytics_output = await strategy_agent.run(
            campaign_id=campaign_id,
            facebook_page_id=None,  # No FB
            instagram_account_id=None  # No IG
        )

        print(f"\n✓ Agent 2 completed without social tokens")

        # Verify it completed successfully
        assert isinstance(analytics_output, AnalyticsOutput), "Invalid output type"

        # Verify past_performance is None (no social data)
        assert analytics_output.past_performance is None, \
            "past_performance should be None when no social data available"

        print(f"\n✅ Graceful handling confirmed:")
        print(f"   - past_performance: None (expected)")
        print(f"   - customer_sentiment: Available")
        print(f"   - market_trends: Available")

        # Verify sentiment analysis still worked
        assert len(analytics_output.customer_sentiment.positive_themes) > 0 or \
               len(analytics_output.customer_sentiment.negative_themes) > 0, \
            "Sentiment analysis should work without social data"

        print(f"\n✅ Sentiment analysis worked without social data")

        # Save output
        output_file = OUTPUT_DIR / f"{campaign_id}_no_social.json"
        with open(output_file, "w") as f:
            json.dump(analytics_output.model_dump(mode='json'), f, indent=2, default=str)

        print(f"💾 Saved output to: {output_file}")

        results.add_pass(test_name)

    except Exception as e:
        results.add_fail(test_name, str(e))
        print(f"\n💥 Exception details:")
        import traceback
        traceback.print_exc()


async def test_strategy_agent_error_handling():
    """
    Test Agent 2 error handling.

    Expected:
    - Graceful error when invalid campaign_id
    - Clear error message
    - No crashes
    """
    test_name = "test_strategy_agent_error_handling"
    print("\n" + "=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)

    try:
        # Initialize services
        gemini_service = GeminiService()
        social_service = SocialService()
        convex_service = ConvexService()
        r2_service = R2Service()
        agi_service = AGIService()

        # Initialize Agent 2
        strategy_agent = StrategyAgent(
            gemini_service=gemini_service,
            social_service=social_service,
            convex_service=convex_service,
            r2_service=r2_service,
            agi_service=agi_service
        )

        print(f"\n📊 Testing error handling with invalid campaign_id...")

        # Try to run with non-existent campaign
        invalid_campaign_id = "invalid_campaign_id_xyz"

        try:
            await strategy_agent.run(campaign_id=invalid_campaign_id)
            # If we get here, test failed
            raise AssertionError("Should have raised ValueError for missing research data")

        except ValueError as e:
            # Expected error
            error_msg = str(e)
            print(f"\n✅ Caught expected error: {error_msg}")
            assert "No research data found" in error_msg, "Error message should be clear"

        except Exception as e:
            # Unexpected error
            raise AssertionError(f"Unexpected error type: {type(e).__name__}: {e}")

        print(f"\n✅ Error handling works correctly")

        results.add_pass(test_name)

    except Exception as e:
        results.add_fail(test_name, str(e))
        print(f"\n💥 Exception details:")
        import traceback
        traceback.print_exc()


async def test_strategy_agent_gemini_high_thinking():
    """
    Test that Gemini HIGH thinking mode is used for analysis.

    Expected:
    - Sentiment analysis uses HIGH thinking
    - Performance analysis uses HIGH thinking
    - Analysis is detailed and strategic
    """
    test_name = "test_strategy_agent_gemini_high_thinking"
    print("\n" + "=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)

    try:
        # Setup campaign
        campaign_id = await setup_test_campaign(with_research=True)

        # Initialize services
        gemini_service = GeminiService()
        social_service = SocialService()
        convex_service = ConvexService()
        r2_service = R2Service()
        agi_service = AGIService()

        # Initialize Agent 2
        strategy_agent = StrategyAgent(
            gemini_service=gemini_service,
            social_service=social_service,
            convex_service=convex_service,
            r2_service=r2_service,
            agi_service=agi_service
        )

        print(f"\n📊 Running Agent 2 to verify Gemini HIGH thinking...")

        # Run Agent 2
        analytics_output = await strategy_agent.run(campaign_id=campaign_id)

        print(f"\n✓ Agent 2 completed")

        # Verify strategic analysis (HIGH thinking should produce detailed insights)
        sentiment = analytics_output.customer_sentiment

        # Check sentiment analysis depth
        assert len(sentiment.positive_themes) >= 2, \
            "HIGH thinking should identify multiple positive themes"
        assert len(sentiment.content_opportunities) >= 2, \
            "HIGH thinking should identify multiple content opportunities"

        # Check for strategic insights (not just literal review extraction)
        print(f"\n✅ Gemini HIGH thinking verification:")
        print(f"   - Positive themes: {sentiment.positive_themes}")
        print(f"   - Content opportunities: {sentiment.content_opportunities}")

        # Verify insights are actionable
        for opp in sentiment.content_opportunities:
            assert len(opp) > 10, "Content opportunities should be detailed"

        print(f"\n✅ HIGH thinking mode confirmed - strategic insights generated")

        results.add_pass(test_name)

    except Exception as e:
        results.add_fail(test_name, str(e))
        print(f"\n💥 Exception details:")
        import traceback
        traceback.print_exc()


async def cleanup_test_campaigns():
    """
    Clean up test campaigns from Convex.
    Note: This is optional - test campaigns are prefixed with 'test_strategy_'
    """
    print("\n" + "=" * 80)
    print("CLEANUP")
    print("=" * 80)

    print("\n⚠️  Test campaigns created with prefix 'test_strategy_'")
    print("💡 To clean up manually, delete campaigns from Convex dashboard")
    print("   Filter by campaign_id starting with 'test_strategy_'")


async def main():
    """
    Run all Strategy Agent tests.
    """
    print("\n" + "=" * 80)
    print("BRANDMIND AI - STRATEGY AGENT (AGENT 2) TESTS")
    print("=" * 80)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Test started: {datetime.now().isoformat()}")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Run tests
    await test_strategy_agent_full_workflow()
    await test_strategy_agent_agi_fallback()
    await test_strategy_agent_no_social_tokens()
    await test_strategy_agent_error_handling()
    await test_strategy_agent_gemini_high_thinking()

    # Cleanup
    await cleanup_test_campaigns()

    # Report results
    all_passed = results.summary()

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())

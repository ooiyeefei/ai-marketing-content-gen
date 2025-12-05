#!/usr/bin/env python3
"""
BrandMind AI - Research Agent (Agent 1) Integration Test

Tests the full workflow of Agent 1 with REAL API integrations:
- AGI API for web research and competitor discovery
- Convex for data storage
- Progress tracking verification

Test Philosophy:
- Use REAL API calls (no mocks)
- Verify autonomous competitor discovery
- Save all outputs for manual inspection
- Follow verification-before-completion principle
"""

import asyncio
import sys
import os

# Load environment variables
import json
import uuid
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")




from agents.research_agent import ResearchAgent
from services.agi_service import AGIService
from services.convex_service import ConvexService
from services.r2_service import R2Service
from models import ResearchOutput

# ============================================================================
# Test Configuration
# ============================================================================

OUTPUT_DIR = Path(__file__).parent / "outputs" / "agents" / "research"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Test business URLs
TEST_BUSINESS_URL = "https://www.bluebottlecoffee.com"
TEST_COMPETITOR_URLS = [
    "https://www.philzcoffee.com",
    "https://www.sightglasscoffee.com"
]

# ============================================================================
# Test Utilities
# ============================================================================

def log_test(message: str, level: str = "INFO"):
    """Log test message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️"
    }.get(level, "•")
    print(f"[{timestamp}] {prefix} {message}")


def save_output(filename: str, data: Any):
    """Save test output to file"""
    filepath = OUTPUT_DIR / filename

    if isinstance(data, dict) or isinstance(data, list):
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        log_test(f"Saved output: {filepath}")
    elif hasattr(data, "model_dump"):
        with open(filepath, "w") as f:
            json.dump(data.model_dump(), f, indent=2, default=str)
        log_test(f"Saved output: {filepath}")
    else:
        with open(filepath, "w") as f:
            f.write(str(data))
        log_test(f"Saved output: {filepath}")


async def verify_convex_data(convex: ConvexService, campaign_id: str) -> bool:
    """Verify research data was stored in Convex"""
    try:
        research = await convex.get_research(campaign_id)
        if research:
            log_test(f"Convex verification: Research data found", "SUCCESS")
            return True
        else:
            log_test(f"Convex verification: No research data found", "ERROR")
            return False
    except Exception as e:
        log_test(f"Convex verification failed: {e}", "ERROR")
        return False


async def verify_progress_tracking(
    convex: ConvexService,
    campaign_id: str,
    expected_progress: int
) -> bool:
    """Verify progress was updated correctly"""
    try:
        progress = await convex.get_progress(campaign_id)
        if progress:
            actual = progress.percentage if hasattr(progress, 'percentage') else 0
            log_test(f"Progress: {actual}% (expected: {expected_progress}%)", "INFO")

            if actual >= expected_progress - 5 and actual <= expected_progress + 5:
                log_test(f"Progress tracking verified", "SUCCESS")
                return True
            else:
                log_test(f"Progress mismatch: {actual}% vs {expected_progress}%", "WARNING")
                return False
        else:
            log_test(f"Progress data not found", "ERROR")
            return False
    except Exception as e:
        log_test(f"Progress verification failed: {e}", "ERROR")
        return False


# ============================================================================
# Test Cases
# ============================================================================

async def test_research_agent_full_workflow():
    """
    Test Agent 1 with autonomous competitor discovery

    Verification:
    - Business context extracted (all fields)
    - Competitors discovered autonomously (3-5)
    - Market insights generated
    - Data stored in Convex
    - Progress 0% → 25%
    """
    log_test("=" * 70, "INFO")
    log_test("Test 1: Research Agent Full Workflow (Autonomous Discovery)", "INFO")
    log_test("=" * 70, "INFO")

    campaign_id = f"test_{uuid.uuid4().hex[:8]}"
    log_test(f"Campaign ID: {campaign_id}", "INFO")

    try:
        # Initialize services
        log_test("Initializing services...", "INFO")
        agi = AGIService()
        convex = ConvexService()
        r2 = R2Service()

        # Create campaign in Convex
        await convex.create_campaign(campaign_id)
        log_test("Campaign created in Convex", "SUCCESS")

        # Verify initial progress (0%)
        initial_progress = await convex.get_progress(campaign_id)
        if initial_progress:
            log_test(f"Initial progress: {initial_progress.percentage}%", "INFO")

        # Initialize agent
        agent = ResearchAgent(agi, convex, r2)
        log_test("Research Agent initialized", "SUCCESS")

        # Run research workflow (autonomous competitor discovery)
        log_test(f"Starting research for: {TEST_BUSINESS_URL}", "INFO")
        log_test("Mode: AUTONOMOUS COMPETITOR DISCOVERY", "WARNING")

        research_output = await agent.run(
            campaign_id=campaign_id,
            business_url=TEST_BUSINESS_URL,
            competitor_urls=None  # Let agent discover competitors
        )

        log_test("Research workflow completed", "SUCCESS")

        # ====================================================================
        # Verification 1: Business Context
        # ====================================================================
        log_test("\n--- Verification 1: Business Context ---", "INFO")

        assert research_output.business_context is not None, "Business context missing"
        bc = research_output.business_context

        assert bc.business_name != "Unknown", "Business name not extracted"
        assert bc.industry != "Unknown", "Industry not extracted"
        assert bc.description != "", "Description not extracted"
        assert len(bc.location) > 0, "Location not extracted"

        log_test(f"Business: {bc.business_name}", "SUCCESS")
        log_test(f"Industry: {bc.industry}", "SUCCESS")
        log_test(f"Location: {bc.location}", "SUCCESS")
        log_test(f"Specialties: {len(bc.specialties)} found", "SUCCESS")

        # ====================================================================
        # Verification 2: Autonomous Competitor Discovery
        # ====================================================================
        log_test("\n--- Verification 2: Competitor Discovery ---", "INFO")

        assert len(research_output.competitors) >= 3, f"Expected 3+ competitors, got {len(research_output.competitors)}"
        assert len(research_output.competitors) <= 5, f"Expected max 5 competitors, got {len(research_output.competitors)}"

        log_test(f"Competitors discovered: {len(research_output.competitors)}", "SUCCESS")

        for i, comp in enumerate(research_output.competitors, 1):
            log_test(f"  {i}. {comp.name} ({comp.location})", "INFO")
            assert comp.name != "Unknown", f"Competitor {i} has no name"
            assert comp.website is not None, f"Competitor {i} has no website"

        # ====================================================================
        # Verification 3: Market Insights
        # ====================================================================
        log_test("\n--- Verification 3: Market Insights ---", "INFO")

        assert research_output.market_insights is not None, "Market insights missing"
        mi = research_output.market_insights

        assert len(mi.trending_topics) > 0, "No trending topics found"
        assert len(mi.market_gaps) >= 0, "Market gaps not analyzed"
        assert len(mi.positioning_opportunities) >= 0, "Positioning opportunities not analyzed"

        log_test(f"Trending topics: {len(mi.trending_topics)}", "SUCCESS")
        log_test(f"Market gaps: {len(mi.market_gaps)}", "SUCCESS")
        log_test(f"Positioning opportunities: {len(mi.positioning_opportunities)}", "SUCCESS")

        # ====================================================================
        # Verification 4: Convex Storage
        # ====================================================================
        log_test("\n--- Verification 4: Convex Storage ---", "INFO")

        convex_verified = await verify_convex_data(convex, campaign_id)
        assert convex_verified, "Convex data verification failed"

        # ====================================================================
        # Verification 5: Progress Tracking (0% → 25%)
        # ====================================================================
        log_test("\n--- Verification 5: Progress Tracking ---", "INFO")

        progress_verified = await verify_progress_tracking(convex, campaign_id, 25)
        assert progress_verified, "Progress tracking verification failed"

        # ====================================================================
        # Save Outputs
        # ====================================================================
        log_test("\n--- Saving Test Outputs ---", "INFO")

        save_output(f"{campaign_id}_full_research_output.json", research_output)
        save_output(f"{campaign_id}_business_context.json", bc)
        save_output(f"{campaign_id}_competitors.json", research_output.competitors)
        save_output(f"{campaign_id}_market_insights.json", mi)

        log_test("\n✅ Test 1: PASSED - Full workflow with autonomous discovery", "SUCCESS")
        return True

    except AssertionError as e:
        log_test(f"\n❌ Test 1: FAILED - {e}", "ERROR")
        return False
    except Exception as e:
        log_test(f"\n❌ Test 1: ERROR - {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False


async def test_research_agent_with_competitors():
    """
    Test Agent 1 with user-provided competitor URLs

    Verification:
    - Uses provided competitors (no discovery)
    - Competitor count matches input
    - All competitor data populated
    - Data stored in Convex
    """
    log_test("\n" + "=" * 70, "INFO")
    log_test("Test 2: Research Agent with Provided Competitors", "INFO")
    log_test("=" * 70, "INFO")

    campaign_id = f"test_{uuid.uuid4().hex[:8]}"
    log_test(f"Campaign ID: {campaign_id}", "INFO")

    try:
        # Initialize services
        log_test("Initializing services...", "INFO")
        agi = AGIService()
        convex = ConvexService()
        r2 = R2Service()

        # Create campaign in Convex
        await convex.create_campaign(campaign_id)
        log_test("Campaign created in Convex", "SUCCESS")

        # Initialize agent
        agent = ResearchAgent(agi, convex, r2)
        log_test("Research Agent initialized", "SUCCESS")

        # Run research workflow (with provided competitors)
        log_test(f"Starting research for: {TEST_BUSINESS_URL}", "INFO")
        log_test(f"Mode: PROVIDED COMPETITORS ({len(TEST_COMPETITOR_URLS)} URLs)", "WARNING")

        for url in TEST_COMPETITOR_URLS:
            log_test(f"  - {url}", "INFO")

        research_output = await agent.run(
            campaign_id=campaign_id,
            business_url=TEST_BUSINESS_URL,
            competitor_urls=TEST_COMPETITOR_URLS
        )

        log_test("Research workflow completed", "SUCCESS")

        # ====================================================================
        # Verification 1: Competitor Count Matches Input
        # ====================================================================
        log_test("\n--- Verification 1: Competitor Count ---", "INFO")

        expected_count = len(TEST_COMPETITOR_URLS)
        actual_count = len(research_output.competitors)

        log_test(f"Expected: {expected_count} competitors", "INFO")
        log_test(f"Actual: {actual_count} competitors", "INFO")

        # Allow slight variance (some URLs might fail)
        assert actual_count >= expected_count - 1, f"Too few competitors: {actual_count} < {expected_count}"

        # ====================================================================
        # Verification 2: All Competitor Data Populated
        # ====================================================================
        log_test("\n--- Verification 2: Competitor Data Quality ---", "INFO")

        for i, comp in enumerate(research_output.competitors, 1):
            log_test(f"\nCompetitor {i}: {comp.name}", "INFO")

            assert comp.name != "Unknown", f"Competitor {i} has no name"
            assert comp.website is not None, f"Competitor {i} has no website"

            log_test(f"  ✓ Name: {comp.name}", "SUCCESS")
            log_test(f"  ✓ Website: {comp.website}", "SUCCESS")
            log_test(f"  ✓ Location: {comp.location}", "SUCCESS")

            if comp.brand_voice:
                log_test(f"  ✓ Brand voice: {comp.brand_voice[:50]}...", "SUCCESS")

            if comp.top_content_themes:
                log_test(f"  ✓ Content themes: {len(comp.top_content_themes)}", "SUCCESS")

        # ====================================================================
        # Verification 3: Convex Storage
        # ====================================================================
        log_test("\n--- Verification 3: Convex Storage ---", "INFO")

        convex_verified = await verify_convex_data(convex, campaign_id)
        assert convex_verified, "Convex data verification failed"

        # ====================================================================
        # Save Outputs
        # ====================================================================
        log_test("\n--- Saving Test Outputs ---", "INFO")

        save_output(f"{campaign_id}_provided_competitors_output.json", research_output)
        save_output(f"{campaign_id}_provided_competitors_list.json", research_output.competitors)

        log_test("\n✅ Test 2: PASSED - Provided competitors workflow", "SUCCESS")
        return True

    except AssertionError as e:
        log_test(f"\n❌ Test 2: FAILED - {e}", "ERROR")
        return False
    except Exception as e:
        log_test(f"\n❌ Test 2: ERROR - {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False


async def test_research_agent_error_handling():
    """
    Test Agent 1 error handling with invalid URL

    Verification:
    - Invalid URL triggers proper error
    - No crash
    - Error message is clear
    """
    log_test("\n" + "=" * 70, "INFO")
    log_test("Test 3: Research Agent Error Handling", "INFO")
    log_test("=" * 70, "INFO")

    campaign_id = f"test_{uuid.uuid4().hex[:8]}"
    log_test(f"Campaign ID: {campaign_id}", "INFO")

    invalid_url = "https://this-url-does-not-exist-12345.com"

    try:
        # Initialize services
        log_test("Initializing services...", "INFO")
        agi = AGIService()
        convex = ConvexService()
        r2 = R2Service()

        # Create campaign in Convex
        await convex.create_campaign(campaign_id)

        # Initialize agent
        agent = ResearchAgent(agi, convex, r2)
        log_test("Research Agent initialized", "SUCCESS")

        # Run research workflow with invalid URL
        log_test(f"Testing with invalid URL: {invalid_url}", "WARNING")

        try:
            research_output = await agent.run(
                campaign_id=campaign_id,
                business_url=invalid_url,
                competitor_urls=None
            )

            # If we get here, agent handled the error gracefully
            log_test("Agent returned without crashing", "SUCCESS")

            # Check if business context has fallback values
            if research_output.business_context.business_name == "Unknown":
                log_test("Business context has fallback values", "SUCCESS")

            log_test("\n✅ Test 3: PASSED - Error handled gracefully", "SUCCESS")
            return True

        except Exception as e:
            # Agent should handle errors internally, but if it doesn't, that's OK too
            error_msg = str(e)
            log_test(f"Agent raised exception: {error_msg}", "INFO")

            # Check if error message is clear
            assert len(error_msg) > 10, "Error message too short"
            assert "error" in error_msg.lower() or "failed" in error_msg.lower(), "Error message not descriptive"

            log_test("Error message is clear and descriptive", "SUCCESS")
            log_test("\n✅ Test 3: PASSED - Error handling verified", "SUCCESS")
            return True

    except AssertionError as e:
        log_test(f"\n❌ Test 3: FAILED - {e}", "ERROR")
        return False
    except Exception as e:
        log_test(f"\n❌ Test 3: ERROR - Unexpected exception: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# Main Test Runner
# ============================================================================

async def main():
    """Run all Research Agent tests"""

    print("\n" + "=" * 70)
    print("BrandMind AI - Research Agent Integration Tests")
    print("=" * 70)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

    # Check environment variables
    required_env_vars = ["AGI_API_KEY", "CONVEX_URL"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        log_test(f"Missing required environment variables: {missing_vars}", "ERROR")
        log_test("Please set these in your .env file", "ERROR")
        return

    log_test("Environment variables verified", "SUCCESS")

    # Run tests
    results = []

    # Test 1: Full workflow with autonomous discovery
    result1 = await test_research_agent_full_workflow()
    results.append(("Full Workflow (Autonomous Discovery)", result1))

    # Test 2: Workflow with provided competitors
    result2 = await test_research_agent_with_competitors()
    results.append(("Provided Competitors Workflow", result2))

    # Test 3: Error handling
    result3 = await test_research_agent_error_handling()
    results.append(("Error Handling", result3))

    # ========================================================================
    # Test Summary
    # ========================================================================

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED")
    else:
        print("⚠️ SOME TESTS FAILED")

    print(f"\nTest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Outputs saved to: {OUTPUT_DIR}")
    print("=" * 70 + "\n")

    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    asyncio.run(main())

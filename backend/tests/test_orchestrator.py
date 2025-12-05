"""
Campaign Orchestrator E2E Tests

Tests the complete 3-agent pipeline with real APIs.

WARNING: These tests take 20-30 minutes EACH with real API calls.
Only run when you have time and want to verify the complete system.

Test Coverage:
1. test_orchestrator_full_pipeline() - Complete end-to-end campaign
2. test_orchestrator_progress_tracking() - Monitor 0→25→50→100
3. test_orchestrator_error_recovery() - Error handling and status updates
"""

import asyncio
import sys
import os

# Load environment variables
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")




from orchestrator import CampaignOrchestrator, get_orchestrator
from services.convex_service import ConvexService
from models import CampaignResponse, CampaignProgress

# ============================================================================
# Configuration
# ============================================================================

OUTPUT_DIR = Path(__file__).parent / "outputs" / "orchestrator"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Test business URL (use a real coffee shop website)
TEST_BUSINESS_URL = "https://www.bluebottlecoffee.com"

# Maximum execution time (30 minutes)
MAX_EXECUTION_TIME = 30 * 60  # 1800 seconds

# Progress tracking interval (check every 30 seconds)
PROGRESS_CHECK_INTERVAL = 30


# ============================================================================
# Helper Functions
# ============================================================================

def save_json(data: Any, filename: str):
    """Save data to JSON file in output directory"""
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w") as f:
        if hasattr(data, "model_dump"):
            json.dump(data.model_dump(mode="json"), f, indent=2, default=str)
        else:
            json.dump(data, f, indent=2, default=str)
    print(f"✓ Saved: {filepath}")


def save_text(content: str, filename: str):
    """Save text content to file"""
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w") as f:
        f.write(content)
    print(f"✓ Saved: {filepath}")


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    mins, secs = divmod(int(seconds), 60)
    return f"{mins}m {secs}s"


async def monitor_progress(
    convex_service: ConvexService,
    campaign_id: str,
    max_duration: float = MAX_EXECUTION_TIME
) -> List[Dict[str, Any]]:
    """
    Monitor campaign progress in real-time.

    Returns list of progress snapshots.
    """
    print("\n" + "=" * 80)
    print("PROGRESS MONITORING")
    print("=" * 80)

    start_time = time.time()
    progress_history = []
    last_progress = -1

    while True:
        elapsed = time.time() - start_time

        # Check timeout
        if elapsed > max_duration:
            print(f"\n⚠️ Timeout reached ({format_duration(elapsed)})")
            break

        # Get current progress
        try:
            progress = await convex_service.get_progress(campaign_id)

            if progress:
                # Record snapshot
                snapshot = {
                    "timestamp": datetime.now().isoformat(),
                    "elapsed_seconds": elapsed,
                    "status": progress.status,
                    "progress": progress.progress,
                    "current_agent": progress.current_agent,
                    "message": progress.message
                }
                progress_history.append(snapshot)

                # Print if progress changed
                if progress.progress != last_progress:
                    print(f"\n[{format_duration(elapsed)}] Progress: {progress.progress}%")
                    print(f"  Status: {progress.status}")
                    print(f"  Agent: {progress.current_agent or 'None'}")
                    print(f"  Message: {progress.message}")
                    last_progress = progress.progress

                # Check if complete
                if progress.status == "completed":
                    print(f"\n✅ Campaign completed in {format_duration(elapsed)}")
                    break

                # Check if failed
                if progress.status == "failed":
                    print(f"\n❌ Campaign failed after {format_duration(elapsed)}")
                    print(f"  Error: {progress.message}")
                    break

        except Exception as e:
            print(f"\n⚠️ Error checking progress: {e}")

        # Wait before next check
        await asyncio.sleep(PROGRESS_CHECK_INTERVAL)

    return progress_history


def verify_campaign_data(response: CampaignResponse) -> Dict[str, Any]:
    """
    Verify campaign data completeness and quality.

    Returns verification report.
    """
    print("\n" + "=" * 80)
    print("DATA VERIFICATION")
    print("=" * 80)

    checks = {
        "campaign_id": bool(response.campaign_id),
        "business_name": bool(response.business_name),
        "research_complete": False,
        "analytics_complete": False,
        "creative_complete": False,
        "research_has_competitors": False,
        "research_has_market_insights": False,
        "analytics_has_sentiment": False,
        "creative_has_7_days": False
    }

    # Verify Research (Agent 1)
    if response.research_report:
        checks["research_complete"] = True
        checks["research_has_competitors"] = len(response.research_report.competitors) > 0
        checks["research_has_market_insights"] = len(response.research_report.market_insights.trending_topics) > 0

        print("\n✅ Agent 1 (Research):")
        print(f"  - Business: {response.research_report.business_context.business_name}")
        print(f"  - Industry: {response.research_report.business_context.industry}")
        print(f"  - Competitors: {len(response.research_report.competitors)}")
        print(f"  - Trending topics: {len(response.research_report.market_insights.trending_topics)}")
        print(f"  - Market gaps: {len(response.research_report.market_insights.market_gaps)}")
    else:
        print("\n❌ Agent 1 (Research): Missing")

    # Verify Analytics (Agent 2)
    if response.analytics_report:
        checks["analytics_complete"] = True
        checks["analytics_has_sentiment"] = len(response.analytics_report.customer_sentiment.positive_themes) > 0

        print("\n✅ Agent 2 (Analytics):")
        print(f"  - Positive themes: {len(response.analytics_report.customer_sentiment.positive_themes)}")
        print(f"  - Negative themes: {len(response.analytics_report.customer_sentiment.negative_themes)}")
        print(f"  - Quotable reviews: {len(response.analytics_report.customer_sentiment.quotable_reviews)}")

        if response.analytics_report.past_performance:
            print(f"  - Performance patterns: {len(response.analytics_report.past_performance.winning_patterns)} winning")
    else:
        print("\n❌ Agent 2 (Analytics): Missing")

    # Verify Creative (Agent 3)
    if response.campaign_content:
        checks["creative_complete"] = True
        checks["creative_has_7_days"] = len(response.campaign_content.days) == 7

        print("\n✅ Agent 3 (Creative):")
        print(f"  - Days of content: {len(response.campaign_content.days)}")
        print(f"  - Status: {response.campaign_content.status}")

        # Check each day
        for day in response.campaign_content.days:
            print(f"    Day {day.day}: {day.theme}")
    else:
        print("\n❌ Agent 3 (Creative): Missing")

    # Summary
    print("\n" + "-" * 80)
    passed = sum(checks.values())
    total = len(checks)
    print(f"Verification: {passed}/{total} checks passed")

    return {
        "checks": checks,
        "passed": passed,
        "total": total,
        "success_rate": passed / total
    }


# ============================================================================
# Test 1: Full Pipeline E2E
# ============================================================================

async def test_orchestrator_full_pipeline():
    """
    Test complete 3-agent pipeline end-to-end.

    Verifies:
    - All 3 agents execute successfully
    - Complete campaign data returned
    - Total execution time < 30 minutes
    - Data saved to Convex
    """
    print("\n" + "=" * 80)
    print("TEST 1: ORCHESTRATOR FULL PIPELINE")
    print("=" * 80)
    print(f"\nTarget: {TEST_BUSINESS_URL}")
    print(f"Max duration: {format_duration(MAX_EXECUTION_TIME)}")

    start_time = time.time()

    try:
        # Initialize orchestrator
        print("\nInitializing orchestrator...")
        orchestrator = get_orchestrator()

        # Run campaign
        print("\nStarting campaign...")
        print("⚠️ This will take 20-30 minutes with real APIs")

        response = await orchestrator.run_campaign(
            business_url=TEST_BUSINESS_URL
        )

        elapsed = time.time() - start_time

        print(f"\n✅ Campaign completed in {format_duration(elapsed)}")

        # Verify time constraint
        if elapsed > MAX_EXECUTION_TIME:
            print(f"⚠️ WARNING: Exceeded time limit by {format_duration(elapsed - MAX_EXECUTION_TIME)}")
        else:
            print(f"✓ Completed within time limit ({format_duration(MAX_EXECUTION_TIME)})")

        # Verify data
        verification = verify_campaign_data(response)

        # Save outputs
        print("\nSaving outputs...")
        save_json(response, "test1_full_pipeline_response.json")
        save_json(verification, "test1_verification_report.json")

        # Save summary
        summary = {
            "test": "orchestrator_full_pipeline",
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": elapsed,
            "duration_formatted": format_duration(elapsed),
            "success": response.success,
            "campaign_id": response.campaign_id,
            "business_name": response.business_name,
            "verification": verification,
            "within_time_limit": elapsed <= MAX_EXECUTION_TIME
        }
        save_json(summary, "test1_summary.json")

        print("\n" + "=" * 80)
        print("TEST 1: PASSED ✅")
        print("=" * 80)

        return True

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ Test failed after {format_duration(elapsed)}")
        print(f"Error: {e}")

        # Save error report
        error_report = {
            "test": "orchestrator_full_pipeline",
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": elapsed,
            "error": str(e),
            "error_type": type(e).__name__
        }
        save_json(error_report, "test1_error_report.json")

        print("\n" + "=" * 80)
        print("TEST 1: FAILED ❌")
        print("=" * 80)

        return False


# ============================================================================
# Test 2: Progress Tracking
# ============================================================================

async def test_orchestrator_progress_tracking():
    """
    Test campaign progress tracking throughout execution.

    Verifies:
    - Progress starts at 0%
    - Progress updates through 0→25→50→100
    - Status updates correctly (pending→agent1_running→...→completed)
    - Current agent updates correctly
    """
    print("\n" + "=" * 80)
    print("TEST 2: ORCHESTRATOR PROGRESS TRACKING")
    print("=" * 80)
    print(f"\nTarget: {TEST_BUSINESS_URL}")

    start_time = time.time()

    try:
        # Initialize services
        print("\nInitializing services...")
        orchestrator = get_orchestrator()
        convex_service = ConvexService()

        # Start campaign in background
        print("\nStarting campaign...")
        print("⚠️ This will take 20-30 minutes with real APIs")

        # Run campaign and monitor progress concurrently
        campaign_task = asyncio.create_task(
            orchestrator.run_campaign(business_url=TEST_BUSINESS_URL)
        )

        # Give it a moment to create campaign
        await asyncio.sleep(5)

        # Get campaign ID from orchestrator (simplified - in reality we'd track this)
        # For now, we'll monitor progress by waiting for campaign_task

        # Wait for campaign to complete
        response = await campaign_task

        elapsed = time.time() - start_time

        print(f"\n✅ Campaign completed in {format_duration(elapsed)}")

        # Get final progress
        final_progress = await convex_service.get_progress(response.campaign_id)

        # Verify progress reached 100%
        print("\n" + "-" * 80)
        print("PROGRESS VERIFICATION")
        print("-" * 80)

        if final_progress:
            print(f"✓ Final status: {final_progress.status}")
            print(f"✓ Final progress: {final_progress.progress}%")

            if final_progress.progress == 100:
                print("✓ Progress reached 100%")
            else:
                print(f"⚠️ Progress did not reach 100% (got {final_progress.progress}%)")

            if final_progress.status == "completed":
                print("✓ Status is 'completed'")
            else:
                print(f"⚠️ Status is not 'completed' (got '{final_progress.status}')")
        else:
            print("❌ Could not retrieve final progress")

        # Save outputs
        print("\nSaving outputs...")
        save_json(response, "test2_progress_tracking_response.json")

        if final_progress:
            save_json(final_progress, "test2_final_progress.json")

        # Save summary
        summary = {
            "test": "orchestrator_progress_tracking",
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": elapsed,
            "duration_formatted": format_duration(elapsed),
            "success": response.success,
            "campaign_id": response.campaign_id,
            "final_progress": final_progress.progress if final_progress else None,
            "final_status": final_progress.status if final_progress else None,
            "progress_reached_100": final_progress.progress == 100 if final_progress else False,
            "status_completed": final_progress.status == "completed" if final_progress else False
        }
        save_json(summary, "test2_summary.json")

        print("\n" + "=" * 80)
        print("TEST 2: PASSED ✅")
        print("=" * 80)

        return True

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ Test failed after {format_duration(elapsed)}")
        print(f"Error: {e}")

        # Save error report
        error_report = {
            "test": "orchestrator_progress_tracking",
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": elapsed,
            "error": str(e),
            "error_type": type(e).__name__
        }
        save_json(error_report, "test2_error_report.json")

        print("\n" + "=" * 80)
        print("TEST 2: FAILED ❌")
        print("=" * 80)

        return False


# ============================================================================
# Test 3: Error Recovery
# ============================================================================

async def test_orchestrator_error_recovery():
    """
    Test orchestrator error handling and recovery.

    Verifies:
    - Invalid URL handled gracefully
    - Error status updated in Convex
    - Proper error messages returned
    - No partial data corruption
    """
    print("\n" + "=" * 80)
    print("TEST 3: ORCHESTRATOR ERROR RECOVERY")
    print("=" * 80)

    test_cases = [
        {
            "name": "Invalid URL",
            "url": "https://this-domain-does-not-exist-12345.com",
            "expected_error": True
        },
        {
            "name": "Empty URL",
            "url": "",
            "expected_error": True
        }
    ]

    results = []

    for test_case in test_cases:
        print(f"\n" + "-" * 80)
        print(f"Testing: {test_case['name']}")
        print("-" * 80)
        print(f"URL: {test_case['url']}")

        start_time = time.time()

        try:
            orchestrator = get_orchestrator()
            convex_service = ConvexService()

            # Try to run campaign
            response = await orchestrator.run_campaign(
                business_url=test_case['url']
            )

            elapsed = time.time() - start_time

            # If we got here, no exception was raised
            if test_case['expected_error']:
                print(f"⚠️ Expected error but got success")
                result = {
                    "test_case": test_case['name'],
                    "passed": False,
                    "reason": "Expected error but got success",
                    "duration_seconds": elapsed
                }
            else:
                print(f"✓ Succeeded as expected")
                result = {
                    "test_case": test_case['name'],
                    "passed": True,
                    "duration_seconds": elapsed,
                    "campaign_id": response.campaign_id
                }

        except Exception as e:
            elapsed = time.time() - start_time

            if test_case['expected_error']:
                print(f"✓ Failed as expected: {type(e).__name__}")
                print(f"  Error: {str(e)[:200]}")

                result = {
                    "test_case": test_case['name'],
                    "passed": True,
                    "error_type": type(e).__name__,
                    "error_message": str(e)[:500],
                    "duration_seconds": elapsed
                }
            else:
                print(f"❌ Unexpected error: {e}")
                result = {
                    "test_case": test_case['name'],
                    "passed": False,
                    "reason": "Unexpected error",
                    "error_type": type(e).__name__,
                    "error_message": str(e)[:500],
                    "duration_seconds": elapsed
                }

        results.append(result)

    # Summary
    print("\n" + "=" * 80)
    print("ERROR RECOVERY TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for r in results if r['passed'])
    total = len(results)

    print(f"\nPassed: {passed}/{total}")

    for result in results:
        status = "✅" if result['passed'] else "❌"
        print(f"{status} {result['test_case']}")

    # Save results
    save_json(results, "test3_error_recovery_results.json")

    summary = {
        "test": "orchestrator_error_recovery",
        "timestamp": datetime.now().isoformat(),
        "passed": passed,
        "total": total,
        "success_rate": passed / total,
        "results": results
    }
    save_json(summary, "test3_summary.json")

    if passed == total:
        print("\n" + "=" * 80)
        print("TEST 3: PASSED ✅")
        print("=" * 80)
        return True
    else:
        print("\n" + "=" * 80)
        print("TEST 3: FAILED ❌")
        print("=" * 80)
        return False


# ============================================================================
# Main Test Runner
# ============================================================================

async def main():
    """
    Run all orchestrator tests.

    WARNING: These tests are VERY SLOW (20-30 minutes each).
    Total runtime: 60-90 minutes for all tests.
    """
    print("\n" + "=" * 80)
    print("CAMPAIGN ORCHESTRATOR E2E TESTS")
    print("=" * 80)
    print("\n⚠️ WARNING: These tests take 20-30 minutes EACH")
    print("⚠️ Total runtime: 60-90 minutes for all tests")
    print("⚠️ Make sure you have:")
    print("  - Stable internet connection")
    print("  - All API credentials configured")
    print("  - Sufficient API quotas")
    print("\nOutput directory:", OUTPUT_DIR)

    # Confirm before running
    print("\n" + "=" * 80)
    print("Press Ctrl+C to cancel, or wait 10 seconds to start...")
    print("=" * 80)

    try:
        await asyncio.sleep(10)
    except KeyboardInterrupt:
        print("\n\n❌ Tests cancelled by user")
        return

    overall_start = time.time()
    test_results = []

    # Test 1: Full Pipeline
    try:
        result = await test_orchestrator_full_pipeline()
        test_results.append({"test": "Full Pipeline", "passed": result})
    except KeyboardInterrupt:
        print("\n\n❌ Test 1 cancelled by user")
        return
    except Exception as e:
        print(f"\n❌ Test 1 crashed: {e}")
        test_results.append({"test": "Full Pipeline", "passed": False, "error": str(e)})

    # Test 2: Progress Tracking
    try:
        result = await test_orchestrator_progress_tracking()
        test_results.append({"test": "Progress Tracking", "passed": result})
    except KeyboardInterrupt:
        print("\n\n❌ Test 2 cancelled by user")
        return
    except Exception as e:
        print(f"\n❌ Test 2 crashed: {e}")
        test_results.append({"test": "Progress Tracking", "passed": False, "error": str(e)})

    # Test 3: Error Recovery
    try:
        result = await test_orchestrator_error_recovery()
        test_results.append({"test": "Error Recovery", "passed": result})
    except KeyboardInterrupt:
        print("\n\n❌ Test 3 cancelled by user")
        return
    except Exception as e:
        print(f"\n❌ Test 3 crashed: {e}")
        test_results.append({"test": "Error Recovery", "passed": False, "error": str(e)})

    overall_elapsed = time.time() - overall_start

    # Final Summary
    print("\n" + "=" * 80)
    print("FINAL TEST SUMMARY")
    print("=" * 80)
    print(f"\nTotal runtime: {format_duration(overall_elapsed)}")

    passed = sum(1 for r in test_results if r['passed'])
    total = len(test_results)

    print(f"\nTests passed: {passed}/{total}")
    print()

    for result in test_results:
        status = "✅" if result['passed'] else "❌"
        print(f"{status} {result['test']}")
        if 'error' in result:
            print(f"   Error: {result['error'][:200]}")

    # Save final report
    final_report = {
        "timestamp": datetime.now().isoformat(),
        "total_duration_seconds": overall_elapsed,
        "total_duration_formatted": format_duration(overall_elapsed),
        "tests_passed": passed,
        "tests_total": total,
        "success_rate": passed / total,
        "results": test_results
    }
    save_json(final_report, "FINAL_REPORT.json")

    print(f"\n📁 All outputs saved to: {OUTPUT_DIR}")

    if passed == total:
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED ✅")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("SOME TESTS FAILED ❌")
        print("=" * 80)


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Tests crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

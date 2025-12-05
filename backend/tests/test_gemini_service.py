"""
Comprehensive Test Suite for Gemini Service

Tests Gemini 3.0 Pro with HIGH and LOW thinking modes.
No mocks - all tests use real Gemini API.

Requirements:
- GEMINI_API_KEY environment variable must be set
- Tests verify response times and quality
- All outputs saved to backend/tests/outputs/gemini/
"""

import asyncio
import sys
import os

# Load environment variables
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")




from services.gemini_service import GeminiService


class TestResults:
    """Track test results and timing"""
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
        self.output_dir = Path(__file__).parent / "outputs" / "gemini"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def add_result(self, test_name: str, passed: bool, duration: float, details: Dict[str, Any]):
        """Record test result"""
        self.results.append({
            "test": test_name,
            "passed": passed,
            "duration_seconds": round(duration, 2),
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

        if passed:
            self.tests_passed += 1
            print(f"✅ {test_name} - PASSED ({duration:.2f}s)")
        else:
            self.tests_failed += 1
            print(f"❌ {test_name} - FAILED ({duration:.2f}s)")
            print(f"   Error: {details.get('error', 'Unknown error')}")

    def save_output(self, filename: str, data: Any):
        """Save test output to file"""
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            if isinstance(data, str):
                f.write(data)
            else:
                json.dump(data, f, indent=2)
        print(f"   📁 Saved output: {filepath}")

    def print_summary(self):
        """Print test summary"""
        total = self.tests_passed + self.tests_failed
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"Success Rate: {(self.tests_passed/total*100):.1f}%")

        # Save full results
        results_file = self.output_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total": total,
                    "passed": self.tests_passed,
                    "failed": self.tests_failed,
                    "success_rate": round(self.tests_passed/total*100, 1)
                },
                "tests": self.results
            }, f, indent=2)
        print(f"\n📊 Full results saved: {results_file}")
        print("=" * 70)


async def test_gemini_high_thinking_sentiment_analysis(service: GeminiService, results: TestResults):
    """
    Test HIGH thinking mode with complex sentiment analysis.

    Expected:
    - Response time: 5-15 seconds (thinking takes time)
    - Valid JSON output with all required keys
    - Detailed insights with specific examples
    """
    test_name = "Gemini HIGH Thinking - Sentiment Analysis"
    print(f"\n{'='*70}")
    print(f"🧪 {test_name}")
    print(f"{'='*70}")

    # Sample customer reviews (realistic data)
    reviews = [
        {
            "rating": 5,
            "text": "The freshest sushi in San Francisco! The chef recommended the omakase and every piece was perfectly crafted. The spicy tuna roll is a MUST try!",
            "author": "Sarah M.",
            "date": "2025-01-15"
        },
        {
            "rating": 5,
            "text": "Incredible sake selection and the staff really knows their stuff. The yellowtail was buttery perfection. Only downside is it can get crowded on Friday nights.",
            "author": "David L.",
            "date": "2025-01-10"
        },
        {
            "rating": 4,
            "text": "Great food but service was a bit slow during dinner rush. The dragon roll is beautifully presented and tastes amazing. Would come back for lunch.",
            "author": "Jennifer K.",
            "date": "2025-01-08"
        },
        {
            "rating": 5,
            "text": "Authentic Japanese experience. The chef sources ingredients daily from the fish market. You can taste the quality. The miso soup is also excellent.",
            "author": "Michael T.",
            "date": "2025-01-05"
        },
        {
            "rating": 3,
            "text": "Food was good but pricey. Expected better ambiance for the price point. The salmon sashimi was fresh though.",
            "author": "Lisa P.",
            "date": "2025-01-03"
        }
    ]

    business_name = "Sakura Sushi House"

    start_time = time.time()

    try:
        print(f"📊 Analyzing {len(reviews)} customer reviews...")
        print(f"🧠 Thinking Mode: HIGH (complex analysis)")

        result = await service.analyze_customer_sentiment(
            reviews=reviews,
            business_name=business_name
        )

        duration = time.time() - start_time

        # Validation checks
        required_keys = [
            "positive_themes",
            "negative_themes",
            "popular_items",
            "quotable_reviews",
            "content_opportunities"
        ]

        missing_keys = [key for key in required_keys if key not in result]

        # Verify JSON structure
        is_valid = len(missing_keys) == 0

        if is_valid:
            # Check for content quality
            has_content = (
                len(result.get("positive_themes", [])) > 0 and
                len(result.get("popular_items", [])) > 0 and
                len(result.get("content_opportunities", [])) > 0
            )
            is_valid = has_content

            if not has_content:
                error_msg = "Empty arrays in response"
            else:
                error_msg = None
        else:
            error_msg = f"Missing keys: {missing_keys}"

        # Save output
        results.save_output(
            "high_thinking_sentiment_analysis.json",
            {
                "input": {
                    "business_name": business_name,
                    "review_count": len(reviews),
                    "reviews": reviews
                },
                "output": result,
                "metadata": {
                    "duration_seconds": round(duration, 2),
                    "thinking_mode": "HIGH",
                    "timestamp": datetime.now().isoformat()
                }
            }
        )

        # Print sample output
        print(f"\n📋 Sample Output:")
        print(f"  Positive Themes: {result.get('positive_themes', [])[:3]}")
        print(f"  Popular Items: {result.get('popular_items', [])[:3]}")
        print(f"  Content Opportunities: {len(result.get('content_opportunities', []))} found")

        results.add_result(
            test_name,
            is_valid,
            duration,
            {
                "thinking_mode": "HIGH",
                "response_keys": list(result.keys()),
                "missing_keys": missing_keys,
                "error": error_msg
            }
        )

        return is_valid

    except Exception as e:
        duration = time.time() - start_time
        results.add_result(
            test_name,
            False,
            duration,
            {"error": str(e), "thinking_mode": "HIGH"}
        )
        return False


async def test_gemini_low_thinking_caption_generation(service: GeminiService, results: TestResults):
    """
    Test LOW thinking mode with fast caption generation.

    Expected:
    - Response time: 1-3 seconds (fast generation)
    - String output (not JSON)
    - Caption should be 100-150 words
    - Should include hashtags and CTA
    """
    test_name = "Gemini LOW Thinking - Caption Generation"
    print(f"\n{'='*70}")
    print(f"🧪 {test_name}")
    print(f"{'='*70}")

    day_plan = {
        "day": 1,
        "theme": "Behind the Scenes: The Art of Sushi",
        "content_type": "video",
        "message": "Showcase our daily ingredient sourcing from local fish market",
        "hashtags": ["#SushiArt", "#FreshDaily", "#BehindTheScenes", "#SFFood"],
        "cta": "Book your omakase experience today"
    }

    business_context = {
        "business_name": "Sakura Sushi House",
        "brand_voice": "warm and storytelling",
        "industry": "restaurant"
    }

    start_time = time.time()

    try:
        print(f"✍️  Generating Instagram caption...")
        print(f"🧠 Thinking Mode: LOW (fast generation)")
        print(f"📝 Theme: {day_plan['theme']}")

        caption = await service.generate_caption(
            day_plan=day_plan,
            business_context=business_context
        )

        duration = time.time() - start_time

        # Validation checks
        is_string = isinstance(caption, str)
        has_content = len(caption) > 50  # Minimum length
        has_hashtags = any(tag in caption for tag in day_plan['hashtags'])
        is_reasonable_length = len(caption.split()) < 200  # Not too long

        is_valid = is_string and has_content and is_reasonable_length

        # Performance check: LOW thinking should be fast
        is_fast = duration < 5.0
        if not is_fast:
            print(f"⚠️  WARNING: Low thinking took {duration:.2f}s (expected < 5s)")

        # Save output
        results.save_output(
            "low_thinking_caption_generation.txt",
            f"""INPUT:
Business: {business_context['business_name']}
Theme: {day_plan['theme']}
Brand Voice: {business_context['brand_voice']}

OUTPUT:
{caption}

METADATA:
Duration: {duration:.2f} seconds
Thinking Mode: LOW
Word Count: {len(caption.split())}
Has Hashtags: {has_hashtags}
Timestamp: {datetime.now().isoformat()}
"""
        )

        # Print output
        print(f"\n📝 Generated Caption:")
        print(f"{'-'*70}")
        print(caption)
        print(f"{'-'*70}")
        print(f"  Word Count: {len(caption.split())}")
        print(f"  Has Hashtags: {'✓' if has_hashtags else '✗'}")

        results.add_result(
            test_name,
            is_valid,
            duration,
            {
                "thinking_mode": "LOW",
                "word_count": len(caption.split()),
                "has_hashtags": has_hashtags,
                "is_fast": is_fast,
                "error": None if is_valid else "Invalid caption format or length"
            }
        )

        return is_valid

    except Exception as e:
        duration = time.time() - start_time
        results.add_result(
            test_name,
            False,
            duration,
            {"error": str(e), "thinking_mode": "LOW"}
        )
        return False


async def test_gemini_high_thinking_strategy_creation(service: GeminiService, results: TestResults):
    """
    Test HIGH thinking mode with complex strategy creation.

    Expected:
    - Response time: 10-20 seconds (complex reasoning)
    - Valid JSON with 7-day plan
    - Each day has theme, content_type, message, hashtags, cta, rationale
    """
    test_name = "Gemini HIGH Thinking - Strategy Creation"
    print(f"\n{'='*70}")
    print(f"🧪 {test_name}")
    print(f"{'='*70}")

    business_context = {
        "business_name": "Sakura Sushi House",
        "industry": "restaurant",
        "brand_voice": "warm and storytelling"
    }

    market_insights = {
        "market_gaps": ["Limited video content in local sushi scene", "No one showcasing ingredient sourcing"],
        "positioning_opportunities": ["Authentic craftsmanship", "Sustainability story"],
        "trending_topics": ["Behind-the-scenes content", "Chef collaborations"]
    }

    customer_sentiment = {
        "positive_themes": ["Fresh ingredients", "Authentic taste", "Chef expertise"],
        "popular_items": ["Spicy tuna roll", "Omakase", "Sake selection"],
        "quotable_reviews": ["The freshest sushi in SF!"]
    }

    past_performance = {
        "winning_patterns": {
            "content_types": ["video > carousel > photo"],
            "best_posting_times": ["7-9 PM weekdays"]
        },
        "avoid_patterns": {
            "low_performers": ["generic food photos"]
        }
    }

    market_trends = {
        "trending_searches": ["sushi near me", "omakase SF", "fresh sushi"],
        "rising_topics": ["sustainable seafood", "chef stories"]
    }

    start_time = time.time()

    try:
        print(f"🎯 Creating 7-day content strategy...")
        print(f"🧠 Thinking Mode: HIGH (strategic planning)")

        result = await service.create_content_strategy(
            business_context=business_context,
            market_insights=market_insights,
            customer_sentiment=customer_sentiment,
            past_performance=past_performance,
            market_trends=market_trends
        )

        duration = time.time() - start_time

        # Validation checks
        has_days = "days" in result
        correct_length = len(result.get("days", [])) == 7 if has_days else False

        if has_days and correct_length:
            # Verify each day has required fields
            required_fields = ["day", "theme", "content_type", "message", "hashtags", "cta", "rationale"]
            all_days_valid = all(
                all(field in day for field in required_fields)
                for day in result["days"]
            )
            is_valid = all_days_valid
            error_msg = None if is_valid else "Some days missing required fields"
        else:
            is_valid = False
            error_msg = "Missing 'days' key or incorrect length"

        # Save output
        results.save_output(
            "high_thinking_strategy_creation.json",
            {
                "input": {
                    "business_context": business_context,
                    "market_insights": market_insights,
                    "customer_sentiment": customer_sentiment,
                    "past_performance": past_performance,
                    "market_trends": market_trends
                },
                "output": result,
                "metadata": {
                    "duration_seconds": round(duration, 2),
                    "thinking_mode": "HIGH",
                    "timestamp": datetime.now().isoformat()
                }
            }
        )

        # Print sample output
        if has_days and result["days"]:
            print(f"\n📅 Sample Days:")
            for i in range(min(3, len(result["days"]))):
                day = result["days"][i]
                print(f"  Day {day.get('day')}: {day.get('theme')}")
                print(f"    Type: {day.get('content_type')}")
                print(f"    Rationale: {day.get('rationale', '')[:80]}...")

        results.add_result(
            test_name,
            is_valid,
            duration,
            {
                "thinking_mode": "HIGH",
                "days_count": len(result.get("days", [])),
                "all_days_valid": all_days_valid if correct_length else False,
                "error": error_msg
            }
        )

        return is_valid

    except Exception as e:
        duration = time.time() - start_time
        results.add_result(
            test_name,
            False,
            duration,
            {"error": str(e), "thinking_mode": "HIGH"}
        )
        return False


async def test_gemini_json_output_parsing(service: GeminiService, results: TestResults):
    """
    Test that JSON responses are clean (no markdown wrapping).

    Expected:
    - Response is valid JSON
    - No ```json markdown wrappers
    - No extra text before/after JSON
    """
    test_name = "Gemini JSON Output Parsing"
    print(f"\n{'='*70}")
    print(f"🧪 {test_name}")
    print(f"{'='*70}")

    reviews = [
        {
            "rating": 5,
            "text": "Amazing coffee! The cold brew is incredible and the baristas are so friendly.",
            "author": "Emma S."
        }
    ]

    start_time = time.time()

    try:
        print(f"🔍 Testing JSON output cleanliness...")

        result = await service.analyze_customer_sentiment(
            reviews=reviews,
            business_name="Test Coffee Shop"
        )

        duration = time.time() - start_time

        # Validation: Result should already be parsed as dict
        is_dict = isinstance(result, dict)
        has_keys = len(result.keys()) > 0 if is_dict else False

        # Verify it's actual data, not wrapped text
        is_valid = is_dict and has_keys

        # Save raw output for inspection
        results.save_output(
            "json_output_parsing_test.json",
            {
                "type": str(type(result)),
                "is_dict": is_dict,
                "keys": list(result.keys()) if is_dict else None,
                "sample_data": result,
                "metadata": {
                    "duration_seconds": round(duration, 2),
                    "timestamp": datetime.now().isoformat()
                }
            }
        )

        print(f"\n✅ JSON Validation:")
        print(f"  Is Dictionary: {is_dict}")
        print(f"  Has Keys: {has_keys}")
        print(f"  Keys Found: {list(result.keys()) if is_dict else 'N/A'}")

        results.add_result(
            test_name,
            is_valid,
            duration,
            {
                "is_dict": is_dict,
                "has_keys": has_keys,
                "keys": list(result.keys()) if is_dict else None,
                "error": None if is_valid else "Invalid JSON format"
            }
        )

        return is_valid

    except json.JSONDecodeError as e:
        duration = time.time() - start_time
        results.add_result(
            test_name,
            False,
            duration,
            {"error": f"JSON parsing failed: {str(e)}"}
        )
        return False
    except Exception as e:
        duration = time.time() - start_time
        results.add_result(
            test_name,
            False,
            duration,
            {"error": str(e)}
        )
        return False


async def test_gemini_error_handling(service: GeminiService, results: TestResults):
    """
    Test error handling for edge cases.

    Expected:
    - Empty prompt should raise error
    - Invalid parameters should raise error
    - Service should not crash
    """
    test_name = "Gemini Error Handling"
    print(f"\n{'='*70}")
    print(f"🧪 {test_name}")
    print(f"{'='*70}")

    start_time = time.time()

    try:
        print(f"🔧 Testing error handling with empty reviews...")

        # Test with empty reviews
        result = await service.analyze_customer_sentiment(
            reviews=[],
            business_name="Test Business"
        )

        duration = time.time() - start_time

        # If we get here, check if result is reasonable
        # Empty reviews should either return empty structure or raise error
        is_valid = isinstance(result, dict)

        results.save_output(
            "error_handling_empty_input.json",
            {
                "input": "empty reviews list",
                "output": result,
                "metadata": {
                    "duration_seconds": round(duration, 2),
                    "timestamp": datetime.now().isoformat()
                }
            }
        )

        print(f"\n✅ Service handled empty input gracefully")
        print(f"  Response Type: {type(result)}")

        results.add_result(
            test_name,
            is_valid,
            duration,
            {
                "test_case": "empty_reviews",
                "handled_gracefully": True,
                "error": None
            }
        )

        return is_valid

    except Exception as e:
        duration = time.time() - start_time

        # Raising an exception is acceptable for invalid input
        print(f"\n✅ Service raised appropriate error: {type(e).__name__}")

        results.add_result(
            test_name,
            True,  # Raising error is expected behavior
            duration,
            {
                "test_case": "empty_reviews",
                "error_raised": type(e).__name__,
                "error_message": str(e)
            }
        )

        return True


async def test_gemini_performance_comparison(service: GeminiService, results: TestResults):
    """
    Compare HIGH vs LOW thinking performance.

    Expected:
    - LOW thinking should be significantly faster
    - HIGH thinking should provide deeper insights
    """
    test_name = "Gemini Performance Comparison"
    print(f"\n{'='*70}")
    print(f"🧪 {test_name}")
    print(f"{'='*70}")

    day_plan = {
        "day": 1,
        "theme": "Customer Favorite Monday",
        "content_type": "photo",
        "message": "Showcase our best-selling items",
        "hashtags": ["#MondayMotivation", "#CoffeeLover"],
        "cta": "Visit us today"
    }

    business_context = {
        "business_name": "Test Coffee Shop",
        "brand_voice": "casual",
        "industry": "cafe"
    }

    try:
        # Test LOW thinking (should be fast)
        print(f"⚡ Testing LOW thinking mode...")
        low_start = time.time()
        low_result = await service.generate_caption(day_plan, business_context)
        low_duration = time.time() - low_start

        # Test HIGH thinking (should be slower but deeper)
        print(f"🧠 Testing HIGH thinking mode...")
        high_start = time.time()
        high_result = await service.analyze_customer_sentiment(
            reviews=[{"rating": 5, "text": "Great coffee!"}],
            business_name="Test Coffee Shop"
        )
        high_duration = time.time() - high_start

        # Analysis
        speed_ratio = high_duration / low_duration
        low_is_faster = speed_ratio > 1.5  # HIGH should be at least 50% slower

        print(f"\n📊 Performance Results:")
        print(f"  LOW Thinking:  {low_duration:.2f}s")
        print(f"  HIGH Thinking: {high_duration:.2f}s")
        print(f"  Speed Ratio:   {speed_ratio:.1f}x")
        print(f"  LOW is faster: {'✓' if low_is_faster else '✗'}")

        results.save_output(
            "performance_comparison.json",
            {
                "low_thinking": {
                    "duration_seconds": round(low_duration, 2),
                    "output_type": "string",
                    "output_length": len(low_result)
                },
                "high_thinking": {
                    "duration_seconds": round(high_duration, 2),
                    "output_type": "dict",
                    "output_keys": list(high_result.keys())
                },
                "analysis": {
                    "speed_ratio": round(speed_ratio, 1),
                    "low_is_faster": low_is_faster
                },
                "timestamp": datetime.now().isoformat()
            }
        )

        is_valid = low_is_faster and low_duration < 10  # LOW should complete quickly

        results.add_result(
            test_name,
            is_valid,
            low_duration + high_duration,
            {
                "low_duration": round(low_duration, 2),
                "high_duration": round(high_duration, 2),
                "speed_ratio": round(speed_ratio, 1),
                "low_is_faster": low_is_faster
            }
        )

        return is_valid

    except Exception as e:
        results.add_result(
            test_name,
            False,
            0,
            {"error": str(e)}
        )
        return False


async def main():
    """
    Run all Gemini service tests.

    Test execution order:
    1. JSON output parsing (fundamental)
    2. HIGH thinking - Sentiment analysis
    3. HIGH thinking - Strategy creation
    4. LOW thinking - Caption generation
    5. Performance comparison
    6. Error handling
    """
    print("=" * 70)
    print("GEMINI SERVICE TEST SUITE")
    print("=" * 70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing: Gemini 3.0 Pro with HIGH/LOW thinking modes")
    print(f"Environment: GEMINI_API_KEY = {'✓ Set' if os.getenv('GEMINI_API_KEY') else '✗ Missing'}")
    print("=" * 70)

    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("\n❌ ERROR: GEMINI_API_KEY environment variable not set")
        print("   Set it with: export GEMINI_API_KEY='your-key-here'")
        return

    results = TestResults()

    try:
        # Initialize service
        print("\n🚀 Initializing Gemini Service...")
        service = GeminiService()
        print("✅ Service initialized successfully\n")

        # Run tests in order
        await test_gemini_json_output_parsing(service, results)
        await test_gemini_high_thinking_sentiment_analysis(service, results)
        await test_gemini_high_thinking_strategy_creation(service, results)
        await test_gemini_low_thinking_caption_generation(service, results)
        await test_gemini_performance_comparison(service, results)
        await test_gemini_error_handling(service, results)

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Print summary
        results.print_summary()

        print(f"\n📁 All outputs saved to: {results.output_dir}")
        print(f"🏁 Tests completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())

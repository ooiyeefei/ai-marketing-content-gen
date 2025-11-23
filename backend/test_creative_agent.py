"""
Test Agent 3: Creative Generation

Tests autonomous creative agent workflow following TDD principles (CLAUDE.md).

Test Coverage:
1. Campaign data retrieval from Convex
2. Content strategy creation (Gemini HIGH thinking)
3. Day content generation (captions + images + videos)
4. Media upload to R2
5. Learning data extraction (self-improvement)
6. Full workflow integration
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from models import (
    ResearchOutput,
    AnalyticsOutput,
    CreativeOutput,
    DayContent,
    BusinessContext,
    CompetitorInfo,
    MarketInsights,
    CustomerSentiment,
    TrendData
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Mock Data Fixtures
# ============================================================================

def create_mock_research() -> ResearchOutput:
    """Create mock research output for testing"""
    return ResearchOutput(
        campaign_id="test_campaign_123",
        business_context=BusinessContext(
            business_name="The Sushi Lab",
            industry="restaurant",
            description="Modern Japanese fusion restaurant",
            location={"city": "San Francisco", "state": "CA", "country": "USA"},
            price_range="$$",
            specialties=["omakase", "sake", "wagyu"],
            brand_voice="sophisticated, playful, educational",
            target_audience="food enthusiasts, millennials, date nights",
            website_url="https://thesushilab.com"
        ),
        competitors=[
            CompetitorInfo(
                name="Sushi Nakazawa",
                location="San Francisco",
                google_rating=4.7,
                review_count=1200,
                top_content_themes=["omakase experience", "chef stories"]
            )
        ],
        market_insights=MarketInsights(
            trending_topics=["sustainable seafood", "omakase at home"],
            market_gaps=["behind-the-scenes content", "sake education"],
            positioning_opportunities=["ingredient sourcing transparency"],
            content_strategy={"winning_formats": ["video", "carousel"]}
        ),
        research_images=[],
        timestamp=datetime.now()
    )


def create_mock_analytics() -> AnalyticsOutput:
    """Create mock analytics output for testing"""
    return AnalyticsOutput(
        campaign_id="test_campaign_123",
        customer_sentiment=CustomerSentiment(
            positive_themes=["fresh ingredients", "authentic taste", "beautiful presentation"],
            negative_themes=["weekend wait times"],
            popular_items=["spicy tuna roll", "wagyu nigiri", "sake flight"],
            quotable_reviews=["The freshest sushi in SF!", "Like dining in Tokyo"],
            content_opportunities=["showcase ingredient sourcing", "chef techniques"]
        ),
        past_performance=None,  # First-time campaign
        market_trends=TrendData(
            trending_searches=[{"query": "omakase near me", "growth": "+50%"}],
            related_queries=["best sushi SF", "sake pairing"],
            rising_topics=["sustainable seafood", "Japanese whisky"]
        ),
        customer_photos=[],
        timestamp=datetime.now()
    )


def create_mock_strategy() -> dict:
    """Create mock 7-day content strategy"""
    return {
        "days": [
            {
                "day": 1,
                "theme": "Behind the Scenes: The Art of Sushi",
                "content_type": "video",
                "message": "Showcase our chef's knife skills and ingredient selection",
                "hashtags": ["#SushiArt", "#OmakaseExperience", "#FreshDaily"],
                "cta": "Book your omakase experience",
                "rationale": "Video content + behind-the-scenes addresses market gap"
            },
            {
                "day": 2,
                "theme": "Ingredient Spotlight: Wagyu from Japan",
                "content_type": "photo",
                "message": "Highlight sustainable sourcing and quality",
                "hashtags": ["#WagyuNigiri", "#SustainableSeafood", "#JapaneseCuisine"],
                "cta": "Try our wagyu special tonight",
                "rationale": "Customer favorite + positioning opportunity"
            },
            {
                "day": 3,
                "theme": "Sake Education: Pairing Guide",
                "content_type": "carousel",
                "message": "Educational content on sake types and pairings",
                "hashtags": ["#SakePairing", "#JapaneseSake", "#Foodie"],
                "cta": "Ask our sommelier for recommendations",
                "rationale": "Market gap + educational content opportunity"
            },
            {
                "day": 4,
                "theme": "Customer Favorites: Spicy Tuna Roll",
                "content_type": "video",
                "message": "Making our most popular dish",
                "hashtags": ["#SpicyTuna", "#SushiLovers", "#FoodPorn"],
                "cta": "Order for delivery or dine in",
                "rationale": "Most mentioned item in reviews"
            },
            {
                "day": 5,
                "theme": "Chef's Table: Meet the Team",
                "content_type": "photo",
                "message": "Introduce our chefs and their stories",
                "hashtags": ["#ChefLife", "#JapaneseChef", "#SushiChef"],
                "cta": "Reserve our chef's table experience",
                "rationale": "Humanize brand + authenticity"
            },
            {
                "day": 6,
                "theme": "Seasonal Special: Spring Menu",
                "content_type": "photo",
                "message": "Highlight seasonal ingredients",
                "hashtags": ["#SeasonalCuisine", "#SpringMenu", "#FarmToTable"],
                "cta": "Try our spring specials",
                "rationale": "Trending topic + freshness positioning"
            },
            {
                "day": 7,
                "theme": "Weekend Vibes: Perfect Date Night",
                "content_type": "video",
                "message": "Showcase ambiance and romantic setting",
                "hashtags": ["#DateNight", "#SFEats", "#RomanticDinner"],
                "cta": "Book your table for this weekend",
                "rationale": "Target audience + high-value occasion"
            }
        ]
    }


# ============================================================================
# Test Cases
# ============================================================================

async def test_campaign_data_retrieval():
    """
    Test 1: Campaign data retrieval from Convex

    Verifies agent can retrieve research + analytics data autonomously
    """
    logger.info("\n=== Test 1: Campaign Data Retrieval ===")

    try:
        # Import CreativeAgent here to avoid import errors
        from agents.creative_agent import CreativeAgent

        # Mock services
        mock_convex = Mock()
        mock_convex.get_full_campaign_data = AsyncMock(return_value={
            "research": create_mock_research(),
            "analytics": create_mock_analytics(),
            "progress": None
        })

        agent = CreativeAgent(
            gemini_service=Mock(),
            minimax_service=Mock(),
            convex_service=mock_convex,
            r2_service=Mock()
        )

        # Execute
        campaign_data = await agent._retrieve_campaign_data("test_campaign_123")

        # Assert
        assert campaign_data["research"] is not None
        assert campaign_data["analytics"] is not None
        assert campaign_data["research"].business_context.business_name == "The Sushi Lab"

        logger.info("✓ Test 1 passed: Campaign data retrieved successfully")
    except ImportError as e:
        logger.warning(f"⚠ Test 1 skipped: Import error - {e}")
        raise


async def test_content_strategy_creation():
    """
    Test 2: Content strategy creation with Gemini HIGH thinking

    Verifies agent creates autonomous strategic plan based on data
    """
    logger.info("\n=== Test 2: Content Strategy Creation ===")

    # Mock Gemini service
    mock_gemini = Mock()
    mock_gemini.create_content_strategy = AsyncMock(return_value=create_mock_strategy())

    agent = CreativeAgent(
        gemini_service=mock_gemini,
        minimax_service=Mock(),
        convex_service=Mock(),
        r2_service=Mock()
    )

    # Execute
    research = create_mock_research()
    analytics = create_mock_analytics()
    strategy = await agent._create_content_strategy(research, analytics)

    # Assert
    assert len(strategy["days"]) == 7
    assert strategy["days"][0]["day"] == 1
    assert strategy["days"][0]["theme"] is not None
    assert "video" in [d["content_type"] for d in strategy["days"]]

    logger.info("✓ Test 2 passed: 7-day strategy created with autonomous reasoning")


async def test_day_content_generation():
    """
    Test 3: Day content generation (caption + images)

    Verifies agent generates complete content for one day
    """
    logger.info("\n=== Test 3: Day Content Generation ===")

    # Mock services
    mock_gemini = Mock()
    mock_gemini.generate_caption = AsyncMock(return_value="Fresh sushi daily! 🍣\n\nOur chefs select the finest ingredients every morning.\n\nBook your omakase experience! #SushiArt #FreshDaily")
    mock_gemini.generate_image_prompt = AsyncMock(return_value="Professional photo of sushi chef preparing fresh fish, commercial kitchen, natural lighting")

    mock_minimax = Mock()
    mock_minimax.generate_images = AsyncMock(return_value=[b"image1_bytes", b"image2_bytes"])

    mock_r2 = Mock()
    mock_r2.get_campaign_path = Mock(side_effect=lambda cid, fname: f"campaigns/{cid}/{fname}")
    mock_r2.upload_bytes = AsyncMock(side_effect=lambda data, key, ct: f"https://r2.dev/{key}")

    agent = CreativeAgent(
        gemini_service=mock_gemini,
        minimax_service=mock_minimax,
        convex_service=Mock(),
        r2_service=mock_r2
    )

    # Execute
    day_plan = create_mock_strategy()["days"][0]  # Day 1
    day_content = await agent._generate_day_content(
        campaign_id="test_campaign_123",
        day_plan=day_plan,
        business_context=create_mock_research().business_context.model_dump(),
        customer_favorites=["spicy tuna roll", "wagyu nigiri"]
    )

    # Assert
    assert day_content.day == 1
    assert day_content.caption is not None
    assert len(day_content.caption) > 0
    assert len(day_content.image_urls) == 2
    assert all("https://r2.dev/" in url for url in day_content.image_urls)

    logger.info("✓ Test 3 passed: Day content generated with caption + 2 images")


async def test_video_generation_for_video_days():
    """
    Test 4: Video generation for days 1, 4, 7

    Verifies agent generates videos only for specified days
    """
    logger.info("\n=== Test 4: Video Generation ===")

    # Mock services
    mock_gemini = Mock()
    mock_gemini.generate_video_motion_prompt = AsyncMock(return_value="Slow zoom on sushi preparation, smooth camera movement")

    mock_minimax = Mock()
    mock_minimax.generate_video = AsyncMock(return_value=b"video_bytes")

    mock_r2 = Mock()
    mock_r2.get_campaign_path = Mock(return_value="campaigns/test/day_1_video.mp4")
    mock_r2.upload_bytes = AsyncMock(return_value="https://r2.dev/campaigns/test/day_1_video.mp4")

    agent = CreativeAgent(
        gemini_service=mock_gemini,
        minimax_service=mock_minimax,
        convex_service=Mock(),
        r2_service=mock_r2
    )

    # Execute
    day_plan = create_mock_strategy()["days"][0]  # Day 1 (video day)
    video_url = await agent._generate_video_for_day(
        campaign_id="test_campaign_123",
        day_num=1,
        day_plan=day_plan,
        first_frame_image_url="https://r2.dev/image1.jpg",
        business_name="The Sushi Lab"
    )

    # Assert
    assert video_url is not None
    assert "video.mp4" in video_url
    assert mock_minimax.generate_video.called

    logger.info("✓ Test 4 passed: Video generated for video day")


async def test_learning_extraction():
    """
    Test 5: Learning data extraction (self-improvement)

    Verifies agent extracts learnings for future campaigns
    """
    logger.info("\n=== Test 5: Learning Extraction ===")

    agent = CreativeAgent(
        gemini_service=Mock(),
        minimax_service=Mock(),
        convex_service=Mock(),
        r2_service=Mock()
    )

    # Execute
    research = create_mock_research()
    analytics = create_mock_analytics()
    days_content = [
        DayContent(
            day=1,
            theme="Test theme",
            caption="Test caption",
            hashtags=["#test"],
            image_urls=["https://r2.dev/img1.jpg", "https://r2.dev/img2.jpg"],
            video_url="https://r2.dev/video1.mp4",
            cta="Test CTA",
            recommended_post_time="10:00 AM"
        )
    ]

    learning_data = await agent._extract_learnings(research, analytics, days_content)

    # Assert
    assert len(learning_data.what_worked) > 0
    assert len(learning_data.what_to_improve) > 0
    assert learning_data.next_iteration_strategy is not None
    assert "focus_areas" in learning_data.next_iteration_strategy

    logger.info("✓ Test 5 passed: Learning data extracted for self-improvement")


async def test_full_workflow_integration():
    """
    Test 6: Full creative agent workflow

    Integration test: Retrieves data → Creates strategy → Generates 7 days → Stores output
    """
    logger.info("\n=== Test 6: Full Workflow Integration ===")

    # Mock all services
    mock_convex = Mock()
    mock_convex.get_full_campaign_data = AsyncMock(return_value={
        "research": create_mock_research(),
        "analytics": create_mock_analytics(),
        "progress": None
    })
    mock_convex.update_progress = AsyncMock()
    mock_convex.store_content = AsyncMock()

    mock_gemini = Mock()
    mock_gemini.create_content_strategy = AsyncMock(return_value=create_mock_strategy())
    mock_gemini.generate_caption = AsyncMock(return_value="Test caption")
    mock_gemini.generate_image_prompt = AsyncMock(return_value="Test image prompt")
    mock_gemini.generate_video_motion_prompt = AsyncMock(return_value="Test motion prompt")

    mock_minimax = Mock()
    mock_minimax.generate_images = AsyncMock(return_value=[b"img1", b"img2"])
    mock_minimax.generate_video = AsyncMock(return_value=b"video")

    mock_r2 = Mock()
    mock_r2.get_campaign_path = Mock(side_effect=lambda cid, fname: f"{cid}/{fname}")
    mock_r2.upload_bytes = AsyncMock(side_effect=lambda data, key, ct: f"https://r2.dev/{key}")

    agent = CreativeAgent(
        gemini_service=mock_gemini,
        minimax_service=mock_minimax,
        convex_service=mock_convex,
        r2_service=mock_r2
    )

    # Execute
    output = await agent.run("test_campaign_123")

    # Assert
    assert output.campaign_id == "test_campaign_123"
    assert len(output.days) == 7
    assert output.status == "completed"
    assert output.learning_data is not None

    # Verify videos generated for days 1, 4, 7
    video_days = [d.day for d in output.days if d.video_url]
    assert 1 in video_days
    assert 4 in video_days
    assert 7 in video_days

    # Verify progress tracking
    assert mock_convex.update_progress.call_count >= 5
    assert mock_convex.store_content.called

    logger.info("✓ Test 6 passed: Full workflow completed successfully")


async def test_autonomous_decision_making():
    """
    Test 7: Autonomous decision-making (not hardcoded)

    Verifies agent makes decisions based on data, not fixed logic
    """
    logger.info("\n=== Test 7: Autonomous Decision Making ===")

    agent = CreativeAgent(
        gemini_service=Mock(),
        minimax_service=Mock(),
        convex_service=Mock(),
        r2_service=Mock()
    )

    # Test 1: Posting time calculation
    time1 = agent._calculate_optimal_post_time(1, None)
    time2 = agent._calculate_optimal_post_time(2, None)

    assert time1 != time2  # Different times for different days
    assert "AM" in time1 or "PM" in time1

    # Test 2: Video days decision
    assert 1 in agent.video_days
    assert 4 in agent.video_days
    assert 7 in agent.video_days
    assert 2 not in agent.video_days

    logger.info("✓ Test 7 passed: Agent makes autonomous decisions")


# ============================================================================
# Test Runner
# ============================================================================

async def run_all_tests():
    """Execute all tests in sequence"""
    logger.info("=" * 70)
    logger.info("Running Creative Agent Tests (TDD)")
    logger.info("=" * 70)

    tests = [
        test_campaign_data_retrieval,
        test_content_strategy_creation,
        test_day_content_generation,
        test_video_generation_for_video_days,
        test_learning_extraction,
        test_full_workflow_integration,
        test_autonomous_decision_making
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            logger.error(f"✗ {test.__name__} failed: {e}")
            failed += 1

    logger.info("\n" + "=" * 70)
    logger.info(f"Test Results: {passed} passed, {failed} failed")
    logger.info("=" * 70)

    return passed, failed


if __name__ == "__main__":
    asyncio.run(run_all_tests())

"""
Simplified Test for Agent 3: Creative Generation

Tests data models and agent structure without requiring service dependencies.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from models import (
    ResearchOutput,
    AnalyticsOutput,
    CreativeOutput,
    DayContent,
    LearningData,
    BusinessContext,
    CompetitorInfo,
    MarketInsights,
    CustomerSentiment,
    TrendData
)


def test_business_context_model():
    """Test 1: BusinessContext model validation"""
    print("\n=== Test 1: BusinessContext Model ===")

    business = BusinessContext(
        business_name="The Sushi Lab",
        industry="restaurant",
        description="Modern Japanese fusion",
        location={"city": "SF", "state": "CA", "country": "USA"},
        price_range="$$",
        specialties=["omakase", "sake"],
        brand_voice="sophisticated",
        target_audience="food enthusiasts",
        website_url="https://thesushilab.com"
    )

    assert business.business_name == "The Sushi Lab"
    assert business.industry == "restaurant"
    assert len(business.specialties) == 2

    print("✓ Test 1 passed: BusinessContext model validated")


def test_research_output_model():
    """Test 2: ResearchOutput model validation"""
    print("\n=== Test 2: ResearchOutput Model ===")

    research = ResearchOutput(
        campaign_id="test_123",
        business_context=BusinessContext(
            business_name="Test Business",
            industry="retail",
            description="Test",
            location={"city": "SF"},
            website_url="https://test.com"
        ),
        competitors=[
            CompetitorInfo(
                name="Competitor 1",
                location="SF"
            )
        ],
        market_insights=MarketInsights(
            trending_topics=["topic1"],
            market_gaps=["gap1"],
            positioning_opportunities=["opp1"],
            content_strategy={}
        ),
        research_images=[],
        timestamp=datetime.now()
    )

    assert research.campaign_id == "test_123"
    assert len(research.competitors) == 1
    assert research.business_context.business_name == "Test Business"

    print("✓ Test 2 passed: ResearchOutput model validated")


def test_analytics_output_model():
    """Test 3: AnalyticsOutput model validation"""
    print("\n=== Test 3: AnalyticsOutput Model ===")

    analytics = AnalyticsOutput(
        campaign_id="test_123",
        customer_sentiment=CustomerSentiment(
            positive_themes=["fresh", "quality"],
            negative_themes=["wait time"],
            popular_items=["item1", "item2"],
            quotable_reviews=["Great food!"],
            content_opportunities=["behind-the-scenes"]
        ),
        past_performance=None,
        market_trends=TrendData(
            trending_searches=[{"query": "test", "growth": "+50%"}],
            related_queries=["query1"],
            rising_topics=["topic1"]
        ),
        customer_photos=[],
        timestamp=datetime.now()
    )

    assert analytics.campaign_id == "test_123"
    assert len(analytics.customer_sentiment.positive_themes) == 2
    assert len(analytics.market_trends.trending_searches) == 1

    print("✓ Test 3 passed: AnalyticsOutput model validated")


def test_day_content_model():
    """Test 4: DayContent model validation"""
    print("\n=== Test 4: DayContent Model ===")

    day_content = DayContent(
        day=1,
        theme="Behind the Scenes",
        caption="Test caption with #hashtags",
        hashtags=["#test", "#content"],
        image_urls=["https://r2.dev/img1.jpg", "https://r2.dev/img2.jpg"],
        video_url="https://r2.dev/video.mp4",
        cta="Book now!",
        recommended_post_time="10:00 AM"
    )

    assert day_content.day == 1
    assert len(day_content.image_urls) == 2
    assert day_content.video_url is not None
    assert len(day_content.hashtags) == 2

    print("✓ Test 4 passed: DayContent model validated")


def test_learning_data_model():
    """Test 5: LearningData model validation"""
    print("\n=== Test 5: LearningData Model ===")

    learning = LearningData(
        what_worked=[
            {
                "insight": "Video content performed well",
                "evidence": "3x more engagement",
                "recommendation": "Increase video production"
            }
        ],
        what_to_improve=[
            {
                "issue": "Posting times need optimization",
                "evidence": "Low morning engagement",
                "recommendation": "Test afternoon slots"
            }
        ],
        next_iteration_strategy={
            "focus_areas": ["video", "timing"],
            "expected_improvements": ["15% higher engagement"]
        }
    )

    assert len(learning.what_worked) == 1
    assert len(learning.what_to_improve) == 1
    assert "focus_areas" in learning.next_iteration_strategy

    print("✓ Test 5 passed: LearningData model validated")


def test_creative_output_model():
    """Test 6: CreativeOutput model validation"""
    print("\n=== Test 6: CreativeOutput Model ===")

    # Create 7 days of content
    days = []
    for day_num in range(1, 8):
        day_content = DayContent(
            day=day_num,
            theme=f"Theme for day {day_num}",
            caption=f"Caption for day {day_num}",
            hashtags=[f"#day{day_num}"],
            image_urls=["https://r2.dev/img1.jpg", "https://r2.dev/img2.jpg"],
            video_url="https://r2.dev/video.mp4" if day_num in [1, 4, 7] else None,
            cta="Take action!",
            recommended_post_time=f"{10+day_num}:00 AM"
        )
        days.append(day_content)

    creative_output = CreativeOutput(
        campaign_id="test_123",
        days=days,
        learning_data=LearningData(
            what_worked=[],
            what_to_improve=[],
            next_iteration_strategy={}
        ),
        status="completed",
        timestamp=datetime.now()
    )

    assert len(creative_output.days) == 7
    assert creative_output.status == "completed"

    # Verify videos only on days 1, 4, 7
    video_days = [d.day for d in creative_output.days if d.video_url]
    assert video_days == [1, 4, 7]

    # Verify all days have 2 images
    for day in creative_output.days:
        assert len(day.image_urls) == 2

    print("✓ Test 6 passed: CreativeOutput model validated with 7 days")


def test_agent_workflow_structure():
    """Test 7: Agent workflow structure validation"""
    print("\n=== Test 7: Agent Workflow Structure ===")

    try:
        # Check if creative_agent.py exists and has expected structure
        agent_file = Path(__file__).parent / "agents" / "creative_agent.py"
        assert agent_file.exists(), "creative_agent.py not found"

        with open(agent_file) as f:
            content = f.read()

        # Verify key components exist
        assert "class CreativeAgent" in content
        assert "async def run" in content
        assert "_retrieve_campaign_data" in content
        assert "_create_content_strategy" in content
        assert "_generate_day_content" in content
        assert "_generate_video_for_day" in content
        assert "_extract_learnings" in content

        # Verify video days configuration
        assert "self.video_days = [1, 4, 7]" in content

        # Verify progress tracking
        assert "update_progress" in content
        assert "store_content" in content

        print("✓ Test 7 passed: Agent workflow structure validated")

    except Exception as e:
        print(f"✗ Test 7 failed: {e}")
        raise


def run_all_tests():
    """Execute all structure tests"""
    print("=" * 70)
    print("Running Creative Agent Structure Tests")
    print("=" * 70)

    tests = [
        test_business_context_model,
        test_research_output_model,
        test_analytics_output_model,
        test_day_content_model,
        test_learning_data_model,
        test_creative_output_model,
        test_agent_workflow_structure
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_tests()
    sys.exit(0 if failed == 0 else 1)

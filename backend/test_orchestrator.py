"""
Test suite for Campaign Orchestrator

Tests the complete 3-agent pipeline:
- Agent 1: Research & Intelligence
- Agent 2: Analytics & Feedback
- Agent 3: Creative Generation
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from orchestrator import CampaignOrchestrator
from models import (
    CampaignResponse,
    ResearchOutput,
    AnalyticsOutput,
    CreativeOutput,
    BusinessContext,
    CompetitorInfo,
    MarketInsights,
    CustomerSentiment,
    PerformancePatterns,
    TrendData,
    DayContent,
    LearningData
)


@pytest.fixture
def orchestrator():
    """Create orchestrator with mocked services for testing"""
    with patch('orchestrator.AGIService'), \
         patch('orchestrator.GeminiService'), \
         patch('orchestrator.ConvexService'), \
         patch('orchestrator.R2Service'), \
         patch('orchestrator.SocialService'):
        return CampaignOrchestrator()


@pytest.fixture
def mock_research_output():
    """Mock research agent output"""
    return ResearchOutput(
        campaign_id="test-campaign-123",
        business_context=BusinessContext(
            business_name="Test Coffee Shop",
            industry="restaurant",
            description="Premium coffee and pastries",
            location={"city": "San Francisco", "state": "CA", "country": "USA"},
            price_range="$$",
            specialties=["specialty coffee", "artisan pastries"],
            brand_voice="friendly, artisanal",
            target_audience="urban professionals",
            website_url="https://testcoffee.com"
        ),
        competitors=[
            CompetitorInfo(
                name="Competitor Coffee",
                website="https://competitor.com",
                location="San Francisco, CA",
                google_rating=4.5,
                review_count=500,
                social_handles={"instagram": "@competitor"},
                pricing_strategy="premium",
                brand_voice="modern, trendy",
                top_content_themes=["latte art", "sustainability"],
                differentiators=["organic beans"],
                similarity_score=0.85
            )
        ],
        market_insights=MarketInsights(
            trending_topics=["cold brew", "oat milk"],
            market_gaps=["late-night service"],
            positioning_opportunities=["emphasize local sourcing"],
            content_strategy={}
        ),
        research_images=[],
        timestamp=datetime.now()
    )


@pytest.fixture
def mock_analytics_output():
    """Mock analytics agent output"""
    return AnalyticsOutput(
        campaign_id="test-campaign-123",
        customer_sentiment=CustomerSentiment(
            positive_themes=["great coffee", "friendly staff"],
            negative_themes=["slow service"],
            popular_items=["cappuccino", "croissant"],
            quotable_reviews=["Best coffee in SF!"],
            content_opportunities=["showcase barista skills"]
        ),
        past_performance=PerformancePatterns(
            winning_patterns={
                "content_types": ["photo", "carousel"],
                "themes": ["behind-the-scenes", "product shots"],
                "posting_times": ["8am", "3pm"],
                "hashtags": ["#coffeelover", "#specialtycoffee"]
            },
            avoid_patterns={
                "low_performers": ["text-only posts"],
                "reasons": ["low engagement"]
            },
            recommendations=["Post more behind-the-scenes content"]
        ),
        market_trends=TrendData(
            trending_searches=[{"query": "cold brew coffee", "growth": "+50%"}],
            related_queries=["best coffee SF", "specialty coffee"],
            rising_topics=["sustainable coffee"]
        ),
        customer_photos=[],
        timestamp=datetime.now()
    )


@pytest.fixture
def mock_creative_output():
    """Mock creative agent output"""
    days = []
    for i in range(1, 8):
        days.append(DayContent(
            day=i,
            theme=f"Day {i}: Test Theme",
            caption=f"Test caption for day {i}",
            hashtags=["#coffee", "#test"],
            image_urls=["https://test.com/image1.jpg"],
            video_url=None,
            cta="Visit us today!",
            recommended_post_time="12:00 PM"
        ))

    return CreativeOutput(
        campaign_id="test-campaign-123",
        days=days,
        learning_data=LearningData(
            what_worked=[],
            what_to_improve=[],
            next_iteration_strategy={}
        ),
        status="completed",
        timestamp=datetime.now()
    )


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Test that orchestrator initializes all services and agents"""
    with patch('orchestrator.AGIService') as MockAGI, \
         patch('orchestrator.GeminiService') as MockGemini, \
         patch('orchestrator.ConvexService') as MockConvex, \
         patch('orchestrator.R2Service') as MockR2, \
         patch('orchestrator.SocialService') as MockSocial:

        orchestrator = CampaignOrchestrator()

        # Verify all services were initialized
        MockAGI.assert_called_once()
        MockGemini.assert_called_once()
        MockConvex.assert_called_once()
        MockR2.assert_called_once()
        MockSocial.assert_called_once()

        # Verify agents were created
        assert orchestrator.research_agent is not None
        assert orchestrator.strategy_agent is not None
        assert orchestrator.creative_agent is not None


@pytest.mark.asyncio
async def test_run_campaign_success(orchestrator, mock_research_output, mock_analytics_output, mock_creative_output):
    """Test successful campaign execution through all 3 agents"""

    # Mock agent methods
    orchestrator.research_agent.run = AsyncMock(return_value=mock_research_output)
    orchestrator.strategy_agent.run = AsyncMock(return_value=mock_analytics_output)
    orchestrator.convex_service.create_campaign = AsyncMock()
    orchestrator.convex_service.update_progress = AsyncMock()
    orchestrator.convex_service.get_full_campaign_data = AsyncMock(return_value={})

    # Run campaign
    result = await orchestrator.run_campaign(
        business_url="https://testcoffee.com",
        competitor_urls=None,
        facebook_page_id=None,
        instagram_account_id=None
    )

    # Verify result structure
    assert isinstance(result, CampaignResponse)
    assert result.success is True
    assert result.campaign_id is not None
    assert result.business_name == "Test Coffee Shop"

    # Verify research output
    assert result.research_report is not None
    assert result.research_report.business_context.business_name == "Test Coffee Shop"
    assert len(result.research_report.competitors) == 1

    # Verify analytics output
    assert result.analytics_report is not None
    assert len(result.analytics_report.customer_sentiment.positive_themes) == 2

    # Verify creative output
    assert result.campaign_content is not None
    assert len(result.campaign_content.days) == 7

    # Verify agents were called in sequence
    orchestrator.research_agent.run.assert_called_once()
    orchestrator.strategy_agent.run.assert_called_once()


@pytest.mark.asyncio
async def test_run_campaign_with_competitor_urls(orchestrator, mock_research_output, mock_analytics_output):
    """Test campaign with user-provided competitor URLs"""

    orchestrator.research_agent.run = AsyncMock(return_value=mock_research_output)
    orchestrator.strategy_agent.run = AsyncMock(return_value=mock_analytics_output)
    orchestrator.convex_service.create_campaign = AsyncMock()
    orchestrator.convex_service.update_progress = AsyncMock()
    orchestrator.convex_service.get_full_campaign_data = AsyncMock(return_value={})

    competitor_urls = ["https://competitor1.com", "https://competitor2.com"]

    result = await orchestrator.run_campaign(
        business_url="https://testcoffee.com",
        competitor_urls=competitor_urls,
        facebook_page_id="test-fb-page",
        instagram_account_id="test-ig-account"
    )

    # Verify competitor URLs were passed to research agent
    orchestrator.research_agent.run.assert_called_once()
    call_args = orchestrator.research_agent.run.call_args
    assert call_args.kwargs['competitor_urls'] == competitor_urls

    # Verify social IDs were passed to strategy agent
    orchestrator.strategy_agent.run.assert_called_once()
    strategy_call_args = orchestrator.strategy_agent.run.call_args
    assert strategy_call_args.kwargs['facebook_page_id'] == "test-fb-page"
    assert strategy_call_args.kwargs['instagram_account_id'] == "test-ig-account"


@pytest.mark.asyncio
async def test_run_campaign_agent1_failure(orchestrator):
    """Test error handling when Agent 1 fails"""

    # Mock Agent 1 to raise exception
    orchestrator.research_agent.run = AsyncMock(side_effect=Exception("Research failed"))
    orchestrator.convex_service.create_campaign = AsyncMock()
    orchestrator.convex_service.update_progress = AsyncMock()

    # Campaign should raise exception
    with pytest.raises(Exception, match="Research failed"):
        await orchestrator.run_campaign(
            business_url="https://testcoffee.com"
        )

    # Verify error status was updated in Convex
    orchestrator.convex_service.update_progress.assert_called()
    error_call = orchestrator.convex_service.update_progress.call_args_list[-1]
    assert error_call.kwargs['status'] == "failed"
    assert "Research failed" in error_call.kwargs['message']


@pytest.mark.asyncio
async def test_run_campaign_agent2_failure(orchestrator, mock_research_output):
    """Test error handling when Agent 2 fails"""

    orchestrator.research_agent.run = AsyncMock(return_value=mock_research_output)
    orchestrator.strategy_agent.run = AsyncMock(side_effect=Exception("Analytics failed"))
    orchestrator.convex_service.create_campaign = AsyncMock()
    orchestrator.convex_service.update_progress = AsyncMock()

    # Campaign should raise exception
    with pytest.raises(Exception, match="Analytics failed"):
        await orchestrator.run_campaign(
            business_url="https://testcoffee.com"
        )

    # Verify error status was updated
    orchestrator.convex_service.update_progress.assert_called()
    error_call = orchestrator.convex_service.update_progress.call_args_list[-1]
    assert error_call.kwargs['status'] == "failed"


@pytest.mark.asyncio
async def test_campaign_id_generation(orchestrator, mock_research_output, mock_analytics_output):
    """Test that unique campaign IDs are generated"""

    orchestrator.research_agent.run = AsyncMock(return_value=mock_research_output)
    orchestrator.strategy_agent.run = AsyncMock(return_value=mock_analytics_output)
    orchestrator.convex_service.create_campaign = AsyncMock()
    orchestrator.convex_service.update_progress = AsyncMock()
    orchestrator.convex_service.get_full_campaign_data = AsyncMock(return_value={})

    # Run two campaigns
    result1 = await orchestrator.run_campaign(business_url="https://test1.com")
    result2 = await orchestrator.run_campaign(business_url="https://test2.com")

    # Campaign IDs should be unique
    assert result1.campaign_id != result2.campaign_id


@pytest.mark.asyncio
async def test_progress_tracking(orchestrator, mock_research_output, mock_analytics_output):
    """Test that progress is tracked correctly through pipeline"""

    orchestrator.research_agent.run = AsyncMock(return_value=mock_research_output)
    orchestrator.strategy_agent.run = AsyncMock(return_value=mock_analytics_output)
    orchestrator.convex_service.create_campaign = AsyncMock()
    orchestrator.convex_service.update_progress = AsyncMock()
    orchestrator.convex_service.get_full_campaign_data = AsyncMock(return_value={})

    await orchestrator.run_campaign(business_url="https://testcoffee.com")

    # Verify progress updates were made
    progress_calls = orchestrator.convex_service.update_progress.call_args_list

    # Should have multiple progress updates
    assert len(progress_calls) > 0

    # Check that final progress is 100%
    final_call = progress_calls[-1]
    assert final_call.kwargs['progress'] == 100
    assert final_call.kwargs['status'] == "completed"


def test_get_orchestrator_singleton():
    """Test that get_orchestrator returns singleton instance"""
    from orchestrator import get_orchestrator

    with patch('orchestrator.AGIService'), \
         patch('orchestrator.GeminiService'), \
         patch('orchestrator.ConvexService'), \
         patch('orchestrator.R2Service'), \
         patch('orchestrator.SocialService'):

        orchestrator1 = get_orchestrator()
        orchestrator2 = get_orchestrator()

        # Should be the same instance
        assert orchestrator1 is orchestrator2


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

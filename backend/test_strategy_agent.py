import pytest
import asyncio
from agents.strategy_agent import StrategyAgent
from services.gemini_service import GeminiService
from services.social_service import SocialService
from services.convex_service import ConvexService
from services.r2_service import R2Service
from services.agi_service import AGIService

@pytest.mark.asyncio
async def test_strategy_agent_initialization():
    """Test Strategy Agent initialization"""
    gemini = GeminiService()
    social = SocialService()
    convex = ConvexService()
    r2 = R2Service()
    agi = AGIService()

    agent = StrategyAgent(gemini, social, convex, r2, agi)
    assert agent is not None
    print("✓ Strategy Agent initialized")

if __name__ == "__main__":
    asyncio.run(test_strategy_agent_initialization())

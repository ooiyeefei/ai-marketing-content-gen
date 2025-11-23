import pytest
import asyncio
from services.social_service import SocialService

@pytest.mark.asyncio
async def test_social_initialization():
    """Test Social service initialization"""
    service = SocialService()
    print("✓ Social Service initialized")

if __name__ == "__main__":
    asyncio.run(test_social_initialization())

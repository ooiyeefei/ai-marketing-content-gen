import pytest
import asyncio
from services.convex_service import ConvexService
from models import CampaignProgress

@pytest.mark.asyncio
async def test_convex_connection():
    """Test Convex client initialization"""
    service = ConvexService()
    assert service.client is not None
    print("✓ ConvexService initialized")

if __name__ == "__main__":
    asyncio.run(test_convex_connection())

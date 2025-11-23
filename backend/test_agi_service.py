import pytest
import asyncio
from services.agi_service import AGIService

@pytest.mark.asyncio
async def test_agi_initialization():
    """Test AGI service initialization"""
    service = AGIService()
    assert service.api_key is not None
    print("✓ AGI Service initialized")

# Skip actual API calls in unit tests (mock in integration tests)
# @pytest.mark.asyncio
# async def test_extract_business_context():
#     service = AGIService()
#     result = await service.extract_business_context("https://www.nike.com")
#     assert "business_name" in result

if __name__ == "__main__":
    asyncio.run(test_agi_initialization())

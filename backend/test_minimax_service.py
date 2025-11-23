import pytest
import asyncio
from services.minimax_service import MiniMaxService

@pytest.mark.asyncio
async def test_minimax_initialization():
    """Test MiniMax service initialization"""
    service = MiniMaxService()
    assert service.api_key is not None
    print("✓ MiniMax Service initialized")

# Skip actual API calls in unit tests

if __name__ == "__main__":
    asyncio.run(test_minimax_initialization())

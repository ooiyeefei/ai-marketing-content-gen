import pytest
import asyncio
import os
from services.gemini_service import GeminiService

@pytest.mark.asyncio
async def test_gemini_initialization():
    """Test Gemini service initialization"""
    # Set dummy API key for testing if not set
    if not os.getenv("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = "test-api-key-for-initialization"

    service = GeminiService()
    assert service.client is not None
    assert service.model == "gemini-3-pro-preview"
    assert service.api_key is not None
    print("✓ Gemini Service initialized")

# Skip actual API calls in unit tests
# Integration tests will use real API

if __name__ == "__main__":
    asyncio.run(test_gemini_initialization())

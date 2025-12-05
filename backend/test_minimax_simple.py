#!/usr/bin/env python3
import asyncio
import os
from services.minimax_service import MiniMaxService

async def test_initialization():
    """Test MiniMax service initialization"""
    try:
        service = MiniMaxService()
        print("✓ MiniMax Service initialized")
        print(f"  API Key present: {service.api_key is not None}")
        print(f"  Image URL: {service.image_url}")
        print(f"  Video URL: {service.video_url}")
        return True
    except ValueError as e:
        print(f"⚠ MiniMax Service initialization failed: {e}")
        print(f"  MINIMAX_API_KEY is {'set' if os.getenv('MINIMAX_API_KEY') else 'NOT set'}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_initialization())
    exit(0 if result else 1)

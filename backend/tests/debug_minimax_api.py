#!/usr/bin/env python3
"""
Debug script to test MiniMax API directly and see actual response format
"""
import asyncio
import os
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent.parent / ".env")

async def test_minimax_api():
    """Test MiniMax API with minimal payload"""

    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        print("❌ MINIMAX_API_KEY not set")
        return

    print(f"✓ API Key loaded (length: {len(api_key)})")

    # Test endpoint
    url = "https://api.minimax.chat/v1/image_generation"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "image-01",
        "prompt": "A red apple on a white table",
        "aspect_ratio": "1:1",
        "num_images": 1
    }

    print(f"\n📤 Request:")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            print(f"\n⏳ Sending request...")
            response = await client.post(url, headers=headers, json=payload)

            print(f"\n📥 Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")

            if response.status_code != 200:
                print(f"\n❌ Error Response:")
                print(response.text)
                return

            result = response.json()
            print(f"\n✓ Response JSON:")
            print(json.dumps(result, indent=2)[:1000])  # First 1000 chars

            # Check response structure
            print(f"\n🔍 Response Structure Analysis:")
            print(f"  - Top-level keys: {list(result.keys())}")

            if "data" in result:
                print(f"  - data type: {type(result['data'])}")
                print(f"  - data length: {len(result['data']) if isinstance(result['data'], list) else 'N/A'}")

                if isinstance(result['data'], list) and len(result['data']) > 0:
                    print(f"  - First item keys: {list(result['data'][0].keys())}")

                    # Check for different possible image field names
                    first_item = result['data'][0]
                    possible_image_fields = ['base64_image', 'image', 'url', 'image_url', 'b64_json']

                    print(f"\n  Checking for image data fields:")
                    for field in possible_image_fields:
                        if field in first_item:
                            value = first_item[field]
                            print(f"    ✓ Found '{field}' (type: {type(value)}, length: {len(str(value)) if value else 0})")
                        else:
                            print(f"    ✗ '{field}' not found")

            if "error" in result:
                print(f"\n❌ API returned error:")
                print(json.dumps(result['error'], indent=2))

    except httpx.HTTPStatusError as e:
        print(f"\n❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_minimax_api())

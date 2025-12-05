#!/usr/bin/env python3
"""
Debug script to test different MiniMax authentication methods
"""
import asyncio
import os
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

async def test_auth_methods():
    """Test different authentication methods"""

    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        print("❌ MINIMAX_API_KEY not set")
        return

    print(f"✓ API Key loaded (length: {len(api_key)})")
    print(f"First 50 chars: {api_key[:50]}...")
    print(f"Last 10 chars: ...{api_key[-10:]}")

    url = "https://api.minimax.chat/v1/image_generation"
    payload = {
        "model": "image-01",
        "prompt": "A red apple",
        "num_images": 1
    }

    # Method 1: Bearer token (current method)
    print(f"\n{'='*60}")
    print("Method 1: Bearer Authorization Header")
    print(f"{'='*60}")

    try:
        headers_bearer = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers_bearer, json=payload)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)[:500]}")

    except Exception as e:
        print(f"Error: {e}")

    # Method 2: Authorization without Bearer prefix
    print(f"\n{'='*60}")
    print("Method 2: Authorization Header (no Bearer)")
    print(f"{'='*60}")

    try:
        headers_plain = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers_plain, json=payload)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)[:500]}")

    except Exception as e:
        print(f"Error: {e}")

    # Method 3: X-API-Key header
    print(f"\n{'='*60}")
    print("Method 3: X-API-Key Header")
    print(f"{'='*60}")

    try:
        headers_xapi = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers_xapi, json=payload)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)[:500]}")

    except Exception as e:
        print(f"Error: {e}")

    # Method 4: Query parameter
    print(f"\n{'='*60}")
    print("Method 4: Query Parameter")
    print(f"{'='*60}")

    try:
        url_with_key = f"{url}?api_key={api_key}"
        headers_basic = {
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url_with_key, headers=headers_basic, json=payload)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)[:500]}")

    except Exception as e:
        print(f"Error: {e}")

    # Method 5: Check if group_id or other fields are needed
    print(f"\n{'='*60}")
    print("Method 5: Bearer with GroupID in payload")
    print(f"{'='*60}")

    try:
        # Try to extract group_id from JWT
        import base64
        jwt_parts = api_key.split('.')
        if len(jwt_parts) >= 2:
            # Decode JWT payload (add padding if needed)
            payload_part = jwt_parts[1]
            padding = 4 - len(payload_part) % 4
            if padding != 4:
                payload_part += '=' * padding

            decoded = base64.b64decode(payload_part)
            jwt_payload = json.loads(decoded)
            print(f"JWT Payload: {json.dumps(jwt_payload, indent=2)}")

            group_id = jwt_payload.get('GroupID')
            print(f"\nExtracted GroupID: {group_id}")

            # Try with group_id
            payload_with_group = {
                "model": "image-01",
                "prompt": "A red apple",
                "num_images": 1,
                "group_id": group_id
            }

            headers_bearer = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers_bearer, json=payload_with_group)
                print(f"\nStatus: {response.status_code}")
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)[:500]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_auth_methods())

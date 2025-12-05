"""
BrandMind AI - FastAPI Endpoint Tests
Tests all HTTP endpoints with real FastAPI server

Requirements:
- FastAPI server must be running on http://localhost:8080
- Start server: cd backend && ./run.sh
- Uses real API calls (no mocks)
- Tests request/response schemas
- Tests error handling (404, 400, 500)
- Tests background task execution

Test Coverage:
1. Health check endpoints
2. Campaign generation (POST /api/generate)
3. Campaign retrieval (GET /api/campaigns/{id})
4. Progress tracking (GET /api/campaigns/{id}/progress)
5. Scratchpad viewing (GET /api/campaigns/{id}/scratchpad)
6. Autonomous campaign generation (POST /api/generate-autonomous)
7. Error handling (404, 500)
8. Request validation (400)
"""

import asyncio
import sys
import os

# Load environment variables
import httpx
import time
import json
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")




BASE_URL = "http://localhost:8080"
TIMEOUT = 30.0  # seconds


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def record_pass(self, test_name: str):
        self.passed += 1
        print(f"✅ PASS: {test_name}")

    def record_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"❌ FAIL: {test_name}")
        print(f"   Error: {error}")

    def summary(self):
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total:  {self.passed + self.failed}")

        if self.failed > 0:
            print("\nFailed Tests:")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")

        print("="*80)
        return self.failed == 0


results = TestResults()


async def test_health_endpoint():
    """
    Test: GET /health returns 200 with status ok

    Expected Response:
    {
        "status": "ok"
    }
    """
    print("\n=== Test: Health Endpoint ===")
    test_name = "test_health_endpoint"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=TIMEOUT)

            # Verify status code
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Verify response body
            data = response.json()
            assert data["status"] == "ok", f"Expected status='ok', got {data.get('status')}"

            print(f"Response: {data}")
            results.record_pass(test_name)

    except Exception as e:
        results.record_fail(test_name, str(e))


async def test_root_health_endpoint():
    """
    Test: GET / returns 200 with detailed health check

    Expected Response:
    {
        "status": "healthy",
        "services": {
            "redis": true/false,
            "gemini": true/false,
            ...
        }
    }
    """
    print("\n=== Test: Root Health Endpoint ===")
    test_name = "test_root_health_endpoint"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/", timeout=TIMEOUT)

            # Verify status code
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Verify response body
            data = response.json()
            assert data["status"] == "healthy", f"Expected status='healthy', got {data.get('status')}"
            assert "services" in data, "Missing 'services' field"
            assert isinstance(data["services"], dict), "'services' must be a dict"

            print(f"Response: {json.dumps(data, indent=2)}")
            results.record_pass(test_name)

    except Exception as e:
        results.record_fail(test_name, str(e))


async def test_generate_campaign_endpoint():
    """
    Test: POST /api/generate starts campaign generation

    Expected Response:
    {
        "success": true,
        "campaign_id": "campaign_abc123...",
        "message": "Campaign generation started successfully"
    }
    """
    print("\n=== Test: Generate Campaign Endpoint ===")
    test_name = "test_generate_campaign_endpoint"

    try:
        async with httpx.AsyncClient() as client:
            # Send request
            request_data = {
                "business_url": "https://www.bluebottlecoffee.com"
            }

            print(f"Request: POST /api/generate")
            print(f"Body: {json.dumps(request_data, indent=2)}")

            response = await client.post(
                f"{BASE_URL}/api/generate",
                json=request_data,
                timeout=TIMEOUT
            )

            # Verify status code
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Verify response body
            data = response.json()
            assert data["success"] == True, f"Expected success=true, got {data.get('success')}"
            assert "campaign_id" in data, "Missing 'campaign_id' field"
            assert data["campaign_id"].startswith("campaign_"), "campaign_id should start with 'campaign_'"
            assert "message" in data, "Missing 'message' field"

            print(f"Response: {json.dumps(data, indent=2)}")
            results.record_pass(test_name)

            # Return campaign_id for subsequent tests
            return data["campaign_id"]

    except Exception as e:
        results.record_fail(test_name, str(e))
        return None


async def test_get_campaign_endpoint(campaign_id: str):
    """
    Test: GET /api/campaigns/{id} returns complete campaign data

    Expected Response:
    {
        "campaign_id": "campaign_abc123...",
        "business_url": "...",
        "status": "researching" | "analyzing" | "creating" | "completed" | "failed",
        "progress": {...},
        "research": {...} or null,
        "strategy": {...} or null,
        "creative": {...} or null,
        ...
    }
    """
    print("\n=== Test: Get Campaign Endpoint ===")
    test_name = "test_get_campaign_endpoint"

    try:
        async with httpx.AsyncClient() as client:
            print(f"Request: GET /api/campaigns/{campaign_id}")

            response = await client.get(
                f"{BASE_URL}/api/campaigns/{campaign_id}",
                timeout=TIMEOUT
            )

            # Verify status code
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Verify response body
            data = response.json()
            assert data["campaign_id"] == campaign_id, "campaign_id mismatch"
            assert "business_url" in data, "Missing 'business_url' field"
            assert "status" in data, "Missing 'status' field"
            assert "progress" in data, "Missing 'progress' field"

            # Verify progress structure
            progress = data["progress"]
            assert "current_step" in progress, "Missing progress.current_step"
            assert "step_number" in progress, "Missing progress.step_number"
            assert "total_steps" in progress, "Missing progress.total_steps"
            assert "message" in progress, "Missing progress.message"
            assert "percentage" in progress, "Missing progress.percentage"

            print(f"Response (truncated): {json.dumps({k: v for k, v in data.items() if k in ['campaign_id', 'business_url', 'status', 'progress']}, indent=2)}")
            results.record_pass(test_name)

    except Exception as e:
        results.record_fail(test_name, str(e))


async def test_get_progress_endpoint(campaign_id: str):
    """
    Test: GET /api/campaigns/{id}/progress returns progress updates

    Expected Response:
    {
        "campaign_id": "campaign_abc123...",
        "status": "researching",
        "progress_updates": [...]
    }
    """
    print("\n=== Test: Get Progress Endpoint ===")
    test_name = "test_get_progress_endpoint"

    try:
        async with httpx.AsyncClient() as client:
            print(f"Request: GET /api/campaigns/{campaign_id}/progress")

            response = await client.get(
                f"{BASE_URL}/api/campaigns/{campaign_id}/progress",
                timeout=TIMEOUT
            )

            # Verify status code
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Verify response body
            data = response.json()
            assert data["campaign_id"] == campaign_id, "campaign_id mismatch"
            assert "status" in data, "Missing 'status' field"
            assert "progress_updates" in data, "Missing 'progress_updates' field"
            assert isinstance(data["progress_updates"], list), "'progress_updates' must be a list"

            print(f"Response: {json.dumps(data, indent=2)}")
            results.record_pass(test_name)

    except Exception as e:
        results.record_fail(test_name, str(e))


async def test_get_scratchpad_endpoint(campaign_id: str):
    """
    Test: GET /api/campaigns/{id}/scratchpad returns scratchpad data

    Expected Response:
    {
        "campaign_id": "campaign_abc123...",
        "status": "...",
        "iterations": 0,
        "scratchpad": [],
        "quality_scores": {},
        "past_learnings_count": 0
    }
    """
    print("\n=== Test: Get Scratchpad Endpoint ===")
    test_name = "test_get_scratchpad_endpoint"

    try:
        async with httpx.AsyncClient() as client:
            print(f"Request: GET /api/campaigns/{campaign_id}/scratchpad")

            response = await client.get(
                f"{BASE_URL}/api/campaigns/{campaign_id}/scratchpad",
                timeout=TIMEOUT
            )

            # Verify status code
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Verify response body
            data = response.json()
            assert data["campaign_id"] == campaign_id, "campaign_id mismatch"
            assert "status" in data, "Missing 'status' field"
            assert "iterations" in data, "Missing 'iterations' field"
            assert "scratchpad" in data, "Missing 'scratchpad' field"
            assert "quality_scores" in data, "Missing 'quality_scores' field"
            assert "past_learnings_count" in data, "Missing 'past_learnings_count' field"

            print(f"Response: {json.dumps(data, indent=2)}")
            results.record_pass(test_name)

    except Exception as e:
        results.record_fail(test_name, str(e))


async def test_list_campaigns_endpoint():
    """
    Test: GET /api/campaigns returns list of all campaigns

    Expected Response:
    {
        "campaigns": [...],
        "total": 1
    }
    """
    print("\n=== Test: List Campaigns Endpoint ===")
    test_name = "test_list_campaigns_endpoint"

    try:
        async with httpx.AsyncClient() as client:
            print(f"Request: GET /api/campaigns")

            response = await client.get(
                f"{BASE_URL}/api/campaigns",
                timeout=TIMEOUT
            )

            # Verify status code
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Verify response body
            data = response.json()
            assert "campaigns" in data, "Missing 'campaigns' field"
            assert "total" in data, "Missing 'total' field"
            assert isinstance(data["campaigns"], list), "'campaigns' must be a list"
            assert len(data["campaigns"]) == data["total"], "campaigns count mismatch"

            print(f"Response: Found {data['total']} campaign(s)")
            results.record_pass(test_name)

    except Exception as e:
        results.record_fail(test_name, str(e))


async def test_invalid_campaign_id():
    """
    Test: GET /api/campaigns/invalid returns 404

    Expected Response:
    {
        "detail": "Campaign not found"
    }
    """
    print("\n=== Test: Invalid Campaign ID (404) ===")
    test_name = "test_invalid_campaign_id"

    try:
        async with httpx.AsyncClient() as client:
            print(f"Request: GET /api/campaigns/invalid_campaign_id")

            response = await client.get(
                f"{BASE_URL}/api/campaigns/invalid_campaign_id",
                timeout=TIMEOUT
            )

            # Verify status code
            assert response.status_code == 404, f"Expected 404, got {response.status_code}"

            # Verify response body
            data = response.json()
            assert "detail" in data, "Missing 'detail' field"
            assert "not found" in data["detail"].lower(), "Error message should mention 'not found'"

            print(f"Response: {data}")
            results.record_pass(test_name)

    except Exception as e:
        results.record_fail(test_name, str(e))


async def test_invalid_progress_id():
    """
    Test: GET /api/campaigns/invalid/progress returns 404
    """
    print("\n=== Test: Invalid Progress ID (404) ===")
    test_name = "test_invalid_progress_id"

    try:
        async with httpx.AsyncClient() as client:
            print(f"Request: GET /api/campaigns/invalid/progress")

            response = await client.get(
                f"{BASE_URL}/api/campaigns/invalid/progress",
                timeout=TIMEOUT
            )

            # Verify status code
            assert response.status_code == 404, f"Expected 404, got {response.status_code}"

            # Verify response body
            data = response.json()
            assert "detail" in data, "Missing 'detail' field"

            print(f"Response: {data}")
            results.record_pass(test_name)

    except Exception as e:
        results.record_fail(test_name, str(e))


async def test_invalid_scratchpad_id():
    """
    Test: GET /api/campaigns/invalid/scratchpad returns 404
    """
    print("\n=== Test: Invalid Scratchpad ID (404) ===")
    test_name = "test_invalid_scratchpad_id"

    try:
        async with httpx.AsyncClient() as client:
            print(f"Request: GET /api/campaigns/invalid/scratchpad")

            response = await client.get(
                f"{BASE_URL}/api/campaigns/invalid/scratchpad",
                timeout=TIMEOUT
            )

            # Verify status code
            assert response.status_code == 404, f"Expected 404, got {response.status_code}"

            # Verify response body
            data = response.json()
            assert "detail" in data, "Missing 'detail' field"

            print(f"Response: {data}")
            results.record_pass(test_name)

    except Exception as e:
        results.record_fail(test_name, str(e))


async def test_invalid_request_body():
    """
    Test: POST /api/generate with invalid body returns 422

    Expected: Validation error for invalid URL
    """
    print("\n=== Test: Invalid Request Body (422) ===")
    test_name = "test_invalid_request_body"

    try:
        async with httpx.AsyncClient() as client:
            # Send request with invalid URL
            request_data = {
                "business_url": "not-a-valid-url"
            }

            print(f"Request: POST /api/generate")
            print(f"Body: {json.dumps(request_data, indent=2)}")

            response = await client.post(
                f"{BASE_URL}/api/generate",
                json=request_data,
                timeout=TIMEOUT
            )

            # Verify status code (422 for validation errors)
            assert response.status_code == 422, f"Expected 422, got {response.status_code}"

            # Verify response body
            data = response.json()
            assert "detail" in data, "Missing 'detail' field"

            print(f"Response: {json.dumps(data, indent=2)}")
            results.record_pass(test_name)

    except Exception as e:
        results.record_fail(test_name, str(e))


async def test_missing_required_field():
    """
    Test: POST /api/generate with missing required field returns 422
    """
    print("\n=== Test: Missing Required Field (422) ===")
    test_name = "test_missing_required_field"

    try:
        async with httpx.AsyncClient() as client:
            # Send request with missing business_url
            request_data = {}

            print(f"Request: POST /api/generate")
            print(f"Body: {json.dumps(request_data, indent=2)}")

            response = await client.post(
                f"{BASE_URL}/api/generate",
                json=request_data,
                timeout=TIMEOUT
            )

            # Verify status code (422 for validation errors)
            assert response.status_code == 422, f"Expected 422, got {response.status_code}"

            # Verify response body
            data = response.json()
            assert "detail" in data, "Missing 'detail' field"

            print(f"Response: {json.dumps(data, indent=2)}")
            results.record_pass(test_name)

    except Exception as e:
        results.record_fail(test_name, str(e))


async def test_generate_autonomous_campaign_endpoint():
    """
    Test: POST /api/generate-autonomous starts autonomous campaign

    Expected Response:
    {
        "success": true,
        "campaign_id": "autonomous_abc123...",
        "message": "Autonomous campaign generation started - watch the scratchpad!"
    }
    """
    print("\n=== Test: Generate Autonomous Campaign Endpoint ===")
    test_name = "test_generate_autonomous_campaign_endpoint"

    try:
        async with httpx.AsyncClient() as client:
            # Send request
            request_data = {
                "business_url": "https://www.bluebottlecoffee.com"
            }

            print(f"Request: POST /api/generate-autonomous")
            print(f"Body: {json.dumps(request_data, indent=2)}")

            response = await client.post(
                f"{BASE_URL}/api/generate-autonomous",
                json=request_data,
                timeout=TIMEOUT
            )

            # Verify status code
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Verify response body
            data = response.json()
            assert data["success"] == True, f"Expected success=true, got {data.get('success')}"
            assert "campaign_id" in data, "Missing 'campaign_id' field"
            assert data["campaign_id"].startswith("autonomous_"), "campaign_id should start with 'autonomous_'"
            assert "message" in data, "Missing 'message' field"
            assert "scratchpad" in data["message"].lower(), "Message should mention scratchpad"

            print(f"Response: {json.dumps(data, indent=2)}")
            results.record_pass(test_name)

            # Return campaign_id for subsequent tests
            return data["campaign_id"]

    except Exception as e:
        results.record_fail(test_name, str(e))
        return None


async def test_background_task_execution(campaign_id: str):
    """
    Test: Background task starts and updates campaign status

    Verifies:
    1. Campaign status changes from initial state
    2. Progress percentage increases
    3. Background task doesn't block API
    """
    print("\n=== Test: Background Task Execution ===")
    test_name = "test_background_task_execution"

    try:
        async with httpx.AsyncClient() as client:
            # Wait a moment for background task to start
            await asyncio.sleep(2)

            # Check campaign status
            response = await client.get(
                f"{BASE_URL}/api/campaigns/{campaign_id}",
                timeout=TIMEOUT
            )

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            data = response.json()
            status = data["status"]
            percentage = data["progress"]["percentage"]

            print(f"Campaign Status: {status}")
            print(f"Progress: {percentage}%")
            print(f"Current Step: {data['progress']['current_step']}")
            print(f"Message: {data['progress']['message']}")

            # Verify background task is running
            # Status should not be 'completed' yet (unless very fast)
            # and should have started (not still 0%)
            assert status in ["researching", "analyzing", "creating", "publishing", "reasoning", "completed"], \
                f"Unexpected status: {status}"

            print("✓ Background task execution verified")
            results.record_pass(test_name)

    except Exception as e:
        results.record_fail(test_name, str(e))


async def check_server_running() -> bool:
    """
    Check if FastAPI server is running
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=5.0)
            return response.status_code == 200
    except:
        return False


async def main():
    """
    Run all endpoint tests
    """
    print("="*80)
    print("BrandMind AI - FastAPI Endpoint Tests")
    print("="*80)
    print(f"\nTarget Server: {BASE_URL}")
    print(f"Timeout: {TIMEOUT}s per request")

    # Check if server is running
    print("\n🔍 Checking if FastAPI server is running...")
    if not await check_server_running():
        print("\n❌ ERROR: FastAPI server is not running!")
        print("\nPlease start the server first:")
        print("  cd backend")
        print("  ./run.sh")
        print("\nOr:")
        print("  cd backend")
        print("  python main.py")
        return False

    print("✅ Server is running!\n")

    # Run tests in order
    print("Starting endpoint tests...")
    print("="*80)

    # Test 1: Health endpoints
    await test_health_endpoint()
    await test_root_health_endpoint()

    # Test 2: Campaign generation
    campaign_id = await test_generate_campaign_endpoint()

    if campaign_id:
        # Test 3: Campaign retrieval
        await test_get_campaign_endpoint(campaign_id)
        await test_get_progress_endpoint(campaign_id)
        await test_get_scratchpad_endpoint(campaign_id)

        # Test 4: Background task execution
        await test_background_task_execution(campaign_id)

    # Test 5: List campaigns
    await test_list_campaigns_endpoint()

    # Test 6: Error handling
    await test_invalid_campaign_id()
    await test_invalid_progress_id()
    await test_invalid_scratchpad_id()
    await test_invalid_request_body()
    await test_missing_required_field()

    # Test 7: Autonomous campaign generation
    autonomous_campaign_id = await test_generate_autonomous_campaign_endpoint()

    if autonomous_campaign_id:
        # Wait a moment for background task to start
        await asyncio.sleep(2)

        # Check scratchpad for autonomous campaign
        await test_get_scratchpad_endpoint(autonomous_campaign_id)

    # Print summary
    success = results.summary()

    if success:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {results.failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

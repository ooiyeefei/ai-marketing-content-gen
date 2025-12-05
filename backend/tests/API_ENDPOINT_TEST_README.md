# FastAPI Endpoint Tests - README

## Overview

Comprehensive test suite for all BrandMind AI FastAPI endpoints. Tests HTTP request/response handling, background task execution, error handling, and schema validation.

## Prerequisites

### 1. Running FastAPI Server

The server MUST be running before executing tests.

**Start server:**
```bash
cd backend
./run.sh
```

**Or manually:**
```bash
cd backend
python main.py
```

**Verify server is running:**
```bash
curl http://localhost:8080/health
# Expected: {"status":"ok"}
```

### 2. Environment Setup

Ensure `.env` file is configured with API keys (see `.env.example`).

## Running Tests

### Quick Run

```bash
cd backend/tests
python test_api_endpoints.py
```

### Expected Output

```
================================================================================
BrandMind AI - FastAPI Endpoint Tests
================================================================================

Target Server: http://localhost:8080
Timeout: 30.0s per request

🔍 Checking if FastAPI server is running...
✅ Server is running!

Starting endpoint tests...
================================================================================

=== Test: Health Endpoint ===
Response: {'status': 'ok'}
✅ PASS: test_health_endpoint

=== Test: Root Health Endpoint ===
Response: {
  "status": "healthy",
  "services": {
    "redis": true,
    "gemini": true,
    ...
  }
}
✅ PASS: test_root_health_endpoint

=== Test: Generate Campaign Endpoint ===
Request: POST /api/generate
Body: {
  "business_url": "https://www.bluebottlecoffee.com"
}
Response: {
  "success": true,
  "campaign_id": "campaign_abc123...",
  "message": "Campaign generation started successfully"
}
✅ PASS: test_generate_campaign_endpoint

... [continues for all tests]

================================================================================
TEST SUMMARY
================================================================================
Passed: 15
Failed: 0
Total:  15
================================================================================

🎉 All tests passed!
```

## Test Coverage

### 1. Health Check Endpoints

#### `test_health_endpoint()`
- **Endpoint:** `GET /health`
- **Expected:** `{"status": "ok"}` with HTTP 200
- **Verifies:** Basic server health check

#### `test_root_health_endpoint()`
- **Endpoint:** `GET /`
- **Expected:** Detailed health status with service availability
- **Verifies:** All service configuration checks

### 2. Campaign Generation

#### `test_generate_campaign_endpoint()`
- **Endpoint:** `POST /api/generate`
- **Request Body:**
  ```json
  {
    "business_url": "https://www.bluebottlecoffee.com"
  }
  ```
- **Expected Response:**
  ```json
  {
    "success": true,
    "campaign_id": "campaign_abc123...",
    "message": "Campaign generation started successfully"
  }
  ```
- **Verifies:**
  - Campaign ID generation
  - Background task queuing
  - Response schema validation

#### `test_generate_autonomous_campaign_endpoint()`
- **Endpoint:** `POST /api/generate-autonomous`
- **Expected:** Campaign ID starting with `autonomous_`
- **Verifies:** Autonomous agent system initialization

### 3. Campaign Retrieval

#### `test_get_campaign_endpoint(campaign_id)`
- **Endpoint:** `GET /api/campaigns/{campaign_id}`
- **Expected Response:**
  ```json
  {
    "campaign_id": "campaign_abc123...",
    "business_url": "...",
    "status": "researching",
    "progress": {
      "current_step": "research",
      "step_number": 1,
      "total_steps": 4,
      "message": "...",
      "percentage": 25
    },
    "research": null,
    "strategy": null,
    "creative": null,
    ...
  }
  ```
- **Verifies:**
  - Campaign data structure
  - Progress tracking fields
  - Status values

#### `test_list_campaigns_endpoint()`
- **Endpoint:** `GET /api/campaigns`
- **Expected Response:**
  ```json
  {
    "campaigns": [...],
    "total": 1
  }
  ```
- **Verifies:** Campaign listing functionality

### 4. Progress Tracking

#### `test_get_progress_endpoint(campaign_id)`
- **Endpoint:** `GET /api/campaigns/{campaign_id}/progress`
- **Expected Response:**
  ```json
  {
    "campaign_id": "campaign_abc123...",
    "status": "researching",
    "progress_updates": [...]
  }
  ```
- **Verifies:** Real-time progress updates

#### `test_get_scratchpad_endpoint(campaign_id)`
- **Endpoint:** `GET /api/campaigns/{campaign_id}/scratchpad`
- **Expected Response:**
  ```json
  {
    "campaign_id": "campaign_abc123...",
    "status": "reasoning",
    "iterations": 3,
    "scratchpad": [...],
    "quality_scores": {},
    "past_learnings_count": 0
  }
  ```
- **Verifies:** Autonomous agent scratchpad access

### 5. Background Task Execution

#### `test_background_task_execution(campaign_id)`
- **Verifies:**
  - Background task starts after API response
  - Campaign status updates (not still at 0%)
  - Progress percentage increases
  - API remains responsive during execution

### 6. Error Handling

#### `test_invalid_campaign_id()`
- **Endpoint:** `GET /api/campaigns/invalid_campaign_id`
- **Expected:** HTTP 404 with error message
- **Verifies:** Proper 404 handling

#### `test_invalid_progress_id()`
- **Endpoint:** `GET /api/campaigns/invalid/progress`
- **Expected:** HTTP 404
- **Verifies:** Progress endpoint error handling

#### `test_invalid_scratchpad_id()`
- **Endpoint:** `GET /api/campaigns/invalid/scratchpad`
- **Expected:** HTTP 404
- **Verifies:** Scratchpad endpoint error handling

#### `test_invalid_request_body()`
- **Request:** Invalid URL format
- **Expected:** HTTP 422 (validation error)
- **Verifies:** Pydantic request validation

#### `test_missing_required_field()`
- **Request:** Missing `business_url`
- **Expected:** HTTP 422
- **Verifies:** Required field validation

## Test Execution Flow

```
1. Check server health
   ↓
2. Test health endpoints
   ↓
3. Create test campaign (POST /api/generate)
   ↓
4. Retrieve campaign data (GET /api/campaigns/{id})
   ↓
5. Check progress (GET /api/campaigns/{id}/progress)
   ↓
6. Check scratchpad (GET /api/campaigns/{id}/scratchpad)
   ↓
7. Verify background task execution
   ↓
8. Test autonomous campaign (POST /api/generate-autonomous)
   ↓
9. Test error handling (404, 422)
   ↓
10. Print summary
```

## Success Criteria

✅ **All tests must pass:**
- All HTTP status codes correct (200, 404, 422)
- All response schemas match expected structure
- Background tasks start successfully
- Error handling works properly
- No unhandled exceptions

## Troubleshooting

### Server Not Running Error

```
❌ ERROR: FastAPI server is not running!

Please start the server first:
  cd backend
  ./run.sh
```

**Solution:** Start the FastAPI server before running tests.

### Timeout Errors

**Symptom:** Tests timeout after 30 seconds

**Possible Causes:**
1. Server overloaded
2. Background tasks taking too long
3. API rate limits exceeded

**Solution:** Increase `TIMEOUT` in test script or restart server.

### Validation Errors (422)

**Symptom:** Test passes but you expected 200

**Cause:** Request body doesn't match Pydantic schema

**Solution:** Verify request body matches `GenerateCampaignRequest` model.

### Campaign Not Found (404)

**Symptom:** `test_get_campaign_endpoint()` fails

**Possible Causes:**
1. Campaign ID not generated correctly
2. In-memory storage cleared (server restarted)

**Solution:** Ensure `test_generate_campaign_endpoint()` runs first.

## Test Output Artifacts

Tests do not create output artifacts (unlike service layer tests). All validation is done via HTTP responses.

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Start FastAPI Server
  run: |
    cd backend
    python main.py &
    sleep 5  # Wait for server to start

- name: Run API Endpoint Tests
  run: |
    cd backend/tests
    python test_api_endpoints.py

- name: Stop FastAPI Server
  run: |
    pkill -f "python main.py"
```

## Test Statistics

- **Total Tests:** 15
- **Expected Duration:** 30-60 seconds
- **API Calls:** ~20 HTTP requests
- **No Mock Data:** All tests use real FastAPI server

## Next Steps After Tests Pass

1. ✅ Verify all endpoints return correct HTTP status codes
2. ✅ Verify response schemas match Pydantic models
3. ✅ Verify background tasks execute correctly
4. ✅ Verify error handling is proper
5. ✅ Run integration tests (orchestrator + API)
6. ✅ Deploy to staging environment

## Related Documentation

- **Test Plan:** `TEST_PLAN.md` (Section 4.1)
- **API Specification:** `../main.py` (FastAPI endpoints)
- **Models:** `../models.py` (Request/response schemas)
- **Orchestrator Tests:** `test_orchestrator.py`

---

**Last Updated:** 2025-11-23
**Test Coverage:** 15 tests covering all HTTP endpoints
**Status:** ✅ Ready for use

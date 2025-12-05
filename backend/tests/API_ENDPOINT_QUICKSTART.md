# API Endpoint Tests - Quick Start Guide

## 5-Minute Quick Start

### Option 1: Automated Test Runner (Recommended)

```bash
cd backend/tests
./RUN_API_TESTS.sh
```

**What it does:**
- Automatically starts FastAPI server
- Waits for server to be ready
- Runs all endpoint tests
- Stops server when done
- Shows test results

**Expected output:**
```
==========================================
BrandMind AI - API Endpoint Test Runner
==========================================

🚀 Starting FastAPI server...
✅ Server is ready!

==========================================
Running API Endpoint Tests
==========================================

✅ PASS: test_health_endpoint
✅ PASS: test_root_health_endpoint
✅ PASS: test_generate_campaign_endpoint
... [15 tests total]

==========================================
TEST SUMMARY
==========================================
Passed: 15
Failed: 0
Total:  15
==========================================

🎉 All tests passed!
```

---

### Option 2: Manual Execution

**Step 1: Start server**
```bash
cd backend
python main.py
```

**Step 2: Run tests (in new terminal)**
```bash
cd backend/tests
python test_api_endpoints.py
```

**Step 3: Stop server**
```bash
# Press Ctrl+C in server terminal
```

---

## What Tests Are Executed?

### Health Checks (2 tests)
- ✅ `GET /health` - Simple health check
- ✅ `GET /` - Detailed health with service status

### Campaign Operations (6 tests)
- ✅ `POST /api/generate` - Start campaign generation
- ✅ `POST /api/generate-autonomous` - Start autonomous campaign
- ✅ `GET /api/campaigns/{id}` - Get campaign data
- ✅ `GET /api/campaigns/{id}/progress` - Get progress updates
- ✅ `GET /api/campaigns/{id}/scratchpad` - Get reasoning scratchpad
- ✅ `GET /api/campaigns` - List all campaigns

### Error Handling (5 tests)
- ✅ Invalid campaign ID (404)
- ✅ Invalid progress ID (404)
- ✅ Invalid scratchpad ID (404)
- ✅ Invalid request body (422)
- ✅ Missing required field (422)

### Background Tasks (2 tests)
- ✅ Background task execution starts
- ✅ Progress updates during execution

---

## Expected Duration

⏱️ **Total Time:** 30-60 seconds

Breakdown:
- Server startup: 5-10 seconds
- Test execution: 20-40 seconds
- Server shutdown: 2-5 seconds

---

## Success Criteria

All 15 tests must pass:
```
Passed: 15
Failed: 0
Total:  15
```

---

## Common Issues

### Issue 1: Server Already Running

**Error:**
```
⚠️  Server is already running
Using existing server instance
```

**Solution:** This is OK! Tests will use the running server.

---

### Issue 2: Port Already in Use

**Error:**
```
Error: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port 8080
lsof -i :8080

# Kill it
kill -9 <PID>

# Or use the test runner (handles this automatically)
./RUN_API_TESTS.sh
```

---

### Issue 3: Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'httpx'
```

**Solution:**
```bash
pip install httpx
```

---

### Issue 4: Test Timeout

**Error:**
```
httpx.ReadTimeout: timed out
```

**Cause:** Server overloaded or slow API calls

**Solution:** Restart server and try again

---

## Test Output Examples

### Successful Test

```
=== Test: Health Endpoint ===
Response: {'status': 'ok'}
✅ PASS: test_health_endpoint
```

### Failed Test

```
=== Test: Generate Campaign Endpoint ===
❌ FAIL: test_generate_campaign_endpoint
   Error: Expected 200, got 500
```

---

## Viewing Server Logs

**During automated run:**
```bash
tail -f /tmp/brandmind_server.log
```

**During manual run:**
Server logs appear in terminal where you ran `python main.py`

---

## Advanced Usage

### Run Single Test

Edit `test_api_endpoints.py` and comment out tests you don't want:

```python
async def main():
    # Comment out tests you don't want
    await test_health_endpoint()
    # await test_root_health_endpoint()  # Skip this one
    await test_generate_campaign_endpoint()
    # ... etc
```

### Increase Timeout

Edit `test_api_endpoints.py`:

```python
TIMEOUT = 60.0  # Increase from 30 to 60 seconds
```

### Change Server URL

```python
BASE_URL = "http://localhost:8080"  # Change port if needed
```

---

## Integration with Other Tests

### Full Test Suite

```bash
# 1. Service layer tests
cd backend/tests
python test_minimax_service.py
python test_agi_service.py
python test_gemini_service.py

# 2. API endpoint tests
./RUN_API_TESTS.sh

# 3. Orchestrator tests
python test_orchestrator.py
```

### CI/CD Pipeline

```bash
#!/bin/bash
# run_all_tests.sh

cd backend/tests

# Run service tests in parallel
python test_minimax_service.py &
python test_agi_service.py &
python test_gemini_service.py &
wait

# Run API tests (auto-starts server)
./RUN_API_TESTS.sh

# Run orchestrator test
python test_orchestrator.py
```

---

## Test Coverage Summary

| Category | Tests | Status |
|----------|-------|--------|
| Health Checks | 2 | ✅ |
| Campaign Operations | 6 | ✅ |
| Error Handling | 5 | ✅ |
| Background Tasks | 2 | ✅ |
| **Total** | **15** | **✅** |

---

## Next Steps After Tests Pass

1. ✅ Review test output for any warnings
2. ✅ Check server logs for errors
3. ✅ Run agent integration tests
4. ✅ Run full orchestrator E2E test
5. ✅ Deploy to staging environment

---

## Related Files

- **Test Script:** `test_api_endpoints.py`
- **Test Runner:** `RUN_API_TESTS.sh`
- **Full Docs:** `API_ENDPOINT_TEST_README.md`
- **Test Plan:** `TEST_PLAN.md` (Section 4.1)
- **FastAPI Server:** `../main.py`

---

**Questions?**

See full documentation: `API_ENDPOINT_TEST_README.md`

---

**Last Updated:** 2025-11-23
**Test Coverage:** 15 endpoint tests
**Expected Duration:** 30-60 seconds
**Status:** ✅ Ready for use

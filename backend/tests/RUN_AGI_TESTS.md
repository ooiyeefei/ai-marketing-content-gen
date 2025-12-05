# AGI Service Test Execution Guide

## Quick Start

```bash
cd backend/tests
python test_agi_service.py
```

## Prerequisites

### 1. Environment Variables
Ensure `AGI_API_KEY` is set in your environment:

```bash
# Check if AGI_API_KEY is set
echo $AGI_API_KEY

# If not set, add to .env file
# backend/.env.development or backend/.env
AGI_API_KEY=your_agi_api_key_here
```

### 2. Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

## Test Cases

The test suite includes **5 test cases**:

### 1. `test_agi_scrape_business_context`
- **Input:** https://www.bluebottlecoffee.com
- **Expected:** Business name, industry, description, location, specialties
- **Duration:** ~60-120 seconds
- **Output:** `outputs/agi/business_context.json`

### 2. `test_agi_discover_competitors`
- **Input:** Business context from test 1
- **Expected:** 3-5 competitors with names, URLs, ratings
- **Duration:** ~120-180 seconds
- **Output:** `outputs/agi/competitors.json`

### 3. `test_agi_scrape_online_reviews`
- **Input:** "Blue Bottle Coffee" in "San Francisco, CA"
- **Expected:** Reviews from Google Maps, Yelp, etc.
- **Duration:** ~120-180 seconds
- **Output:** `outputs/agi/reviews.json`

### 4. `test_agi_research_competitor`
- **Input:** First competitor from test 2
- **Expected:** Menu, pricing, brand voice, content themes
- **Duration:** ~120-180 seconds
- **Output:** `outputs/agi/competitor_research_*.json`

### 5. `test_agi_error_handling`
- **Input:** Invalid URLs and empty parameters
- **Expected:** Graceful error handling (no crashes)
- **Duration:** ~60-120 seconds
- **Output:** Console output only

## Expected Test Duration

- **Total time:** 8-15 minutes (all tests)
- **Per test:** 1-3 minutes average
- AGI API tasks involve web navigation and scraping, which takes time

## Success Criteria

### Test Output
```
======================================================================
TEST SUMMARY
======================================================================
Total Tests: 5
✅ Passed: 5
❌ Failed: 0
⏭️  Skipped: 0
Duration: XXX.XXs
======================================================================
```

### Output Files
```
backend/tests/outputs/agi/
├── business_context.json          (✅ valid JSON, size > 100 bytes)
├── competitors.json               (✅ valid JSON, size > 100 bytes)
├── reviews.json                   (✅ valid JSON, size > 100 bytes)
└── competitor_research_*.json     (✅ valid JSON, size > 100 bytes)
```

### JSON Validation
All JSON files should:
- Parse without errors
- Contain required keys (see TEST_PLAN.md)
- Have non-empty values for critical fields

## Troubleshooting

### Test Skipped: "AGI_API_KEY not set"
**Solution:** Set the `AGI_API_KEY` environment variable
```bash
export AGI_API_KEY=your_api_key_here
# Or add to backend/.env
```

### Test Failed: "No competitors discovered"
**Possible causes:**
- AGI API rate limit exceeded
- Search query returned no results
- API timeout (increase timeout in agi_service.py)

**Solution:**
- Wait a few minutes and retry
- Check AGI API dashboard for status

### Test Failed: "No reviews found"
**Note:** This is sometimes expected behavior
- Not all businesses have online reviews
- Business may not be on Google Maps/Yelp
- If `overall_rating = 0.0`, test will be **skipped** (not failed)

### Import Error: "ModuleNotFoundError"
**Solution:** Install dependencies
```bash
cd backend
pip install httpx asyncio
```

### Timeout Error: "AGI task timed out"
**Possible causes:**
- Complex website taking long to process
- AGI API server slow response

**Solution:**
- Increase timeout in `agi_service.py` (line 86, 167, 229, 310)
- Retry the test

## Verification Steps

After tests complete:

1. **Check test output**
   ```bash
   # Should show "✅ PASS" for all tests
   python test_agi_service.py
   ```

2. **Verify output files exist**
   ```bash
   ls -lh outputs/agi/*.json
   # Should show 3-4 JSON files with reasonable sizes
   ```

3. **Validate JSON structure**
   ```bash
   # Test each JSON file can be parsed
   python -m json.tool outputs/agi/business_context.json > /dev/null && echo "✅ Valid JSON"
   python -m json.tool outputs/agi/competitors.json > /dev/null && echo "✅ Valid JSON"
   python -m json.tool outputs/agi/reviews.json > /dev/null && echo "✅ Valid JSON"
   ```

4. **Inspect JSON content**
   ```bash
   # Check business context
   cat outputs/agi/business_context.json | jq '.business_name, .industry, .description'

   # Check competitors count
   cat outputs/agi/competitors.json | jq 'length'

   # Check reviews count
   cat outputs/agi/reviews.json | jq '.reviews | length'
   ```

## Test Philosophy (from CLAUDE.md)

These tests follow BrandMind AI development principles:

- ✅ **No Mocks:** Uses REAL AGI API calls (not mock data)
- ✅ **Evidence-Based:** Saves all outputs for manual verification
- ✅ **Error Handling:** Tests graceful failure scenarios
- ✅ **Verification Before Completion:** Checks JSON structure and content

## Next Steps

After AGI tests pass:

1. Review output JSON files manually
2. Verify data quality meets requirements
3. Run remaining service tests (Gemini, MiniMax, etc.)
4. Proceed to agent integration tests
5. Run full orchestrator E2E test

## Related Files

- **Service Implementation:** `backend/services/agi_service.py`
- **Test Plan:** `backend/tests/TEST_PLAN.md`
- **Development Principles:** `CLAUDE.md`
- **Output Documentation:** `backend/tests/outputs/agi/README.md`

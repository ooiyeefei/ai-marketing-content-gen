# Social Service Test Suite

## Overview

This test suite validates the Social Service integration with real APIs (no mocks). It verifies GMB API integration, AGI fallback logic, and optional social media APIs.

## Test File

- **Location**: `/backend/tests/test_social_service.py`
- **Type**: Integration tests with real API calls
- **Duration**: ~2-5 minutes (depending on AGI API response time)

## Tests Included

### 1. `test_social_gmb_reviews_success()`
- **Purpose**: Test Google My Business API for claimed businesses
- **Expected**: Returns reviews with `source="gmb_api"` if GMB API available
- **Fallback**: Gracefully skips if GMB API not configured (common scenario)

### 2. `test_social_gmb_fallback_to_agi()` ⭐ CRITICAL
- **Purpose**: Test AGI API fallback for unclaimed businesses
- **Expected**: Scrapes public reviews from Google Maps, Yelp, TripAdvisor, etc.
- **Why Critical**: Most businesses don't have claimed GMB profiles
- **Duration**: 30-60 seconds (AGI web scraping)

### 3. `test_social_facebook_insights()`
- **Purpose**: Test Facebook Marketing API (optional)
- **Expected**: Returns insights if token configured, None otherwise
- **Behavior**: Gracefully skips if token unavailable

### 4. `test_social_instagram_insights()`
- **Purpose**: Test Instagram Graph API (optional)
- **Expected**: Returns insights if token configured, None otherwise
- **Behavior**: Gracefully skips if token unavailable

### 5. `test_social_google_trends()`
- **Purpose**: Test Google Trends API (optional)
- **Expected**: Returns trend data if API key configured, empty dict otherwise
- **Behavior**: Gracefully skips if API key unavailable

### 6. `test_social_error_handling()`
- **Purpose**: Verify graceful failure when all APIs unavailable
- **Expected**: Returns empty structure with `source="none"`, no crash

## Required Environment Variables

### Critical (for tests to pass)
```bash
AGI_API_KEY=your_agi_api_key_here
```

### Optional (tests will skip if missing)
```bash
GOOGLE_MY_BUSINESS_API_KEY=your_gmb_api_key
FACEBOOK_ACCESS_TOKEN=your_facebook_token
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
GOOGLE_TRENDS_API_KEY=your_trends_api_key

# For testing specific pages/accounts
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_ACCOUNT_ID=your_account_id
```

## Running Tests

### Method 1: Direct Execution
```bash
cd /backend
python tests/test_social_service.py
```

### Method 2: From Test Directory
```bash
cd /backend/tests
python test_social_service.py
```

### Method 3: Run All Service Tests (Parallel)
```bash
cd /backend/tests
python test_minimax_service.py &
python test_agi_service.py &
python test_gemini_service.py &
python test_convex_service.py &
python test_r2_service.py &
python test_social_service.py &
wait
```

## Expected Output

```
================================================================================
BRANDMIND AI - SOCIAL SERVICE TEST SUITE
================================================================================

This test suite uses REAL API calls (no mocks)
Tests will verify GMB API, AGI fallback, and optional social APIs

Output directory: /backend/tests/outputs/social

================================================================================

================================================================================
TEST: Social GMB Reviews Success
================================================================================
⚠ SKIP: GOOGLE_MY_BUSINESS_API_KEY not configured
   This is expected if you don't have GMB API access
   Test will fallback to AGI scraping in next test

✓ PASS: GMB API gracefully skipped

================================================================================
TEST: Social GMB Fallback to AGI
================================================================================
✓ AGI API key configured
✓ AGI Service initialized

   Testing AGI fallback for: The Mill
   Location: San Francisco, CA
   This will scrape public reviews from Google Maps, Yelp, etc.
   Please wait, this may take 30-60 seconds...

✓ AGI fallback activated successfully

   Results:
   - Reviews scraped: 15
   - Overall rating: 4.5
   - Total reviews: 234
   - Customer photos: 8

   Sample reviews (first 2):
   1. Rating: 5/5
      Text: Amazing coffee and pastries! The barista was super friendly...
      Date: 2025-01-15
      Source: Google Maps
   2. Rating: 4/5
      Text: Good coffee, but can get crowded on weekends...
      Date: 2025-01-10
      Source: Yelp

✓ AGI successfully scraped reviews
   Saved result to: /backend/tests/outputs/social/agi_fallback_success_20251123_021730.json

✓ PASS: AGI fallback returned valid reviews

[... additional tests ...]

================================================================================
TEST SUMMARY
================================================================================
✓ PASS: gmb_reviews
✓ PASS: agi_fallback
✓ PASS: facebook_insights
✓ PASS: instagram_insights
✓ PASS: google_trends
✓ PASS: error_handling

Total: 6 tests
Passed: 6
Failed: 0

================================================================================

✓ All tests passed!
```

## Test Outputs

All test results are saved to:
```
/backend/tests/outputs/social/
├── agi_fallback_success_20251123_021730.json
├── google_trends_20251123_021735.json
└── ... (other test results)
```

Each JSON file contains:
- Full API response
- Metadata (source, timestamp)
- Sample data for manual inspection

## Success Criteria

### Must Pass
- ✅ AGI fallback test returns reviews (source="agi_scrape")
- ✅ No unhandled exceptions
- ✅ Error handling returns empty structure (not crash)

### Should Pass (if tokens configured)
- ✅ GMB API returns reviews if available
- ✅ Facebook API returns insights or None
- ✅ Instagram API returns insights or None
- ✅ Google Trends returns data or empty dict

## Common Issues

### Issue: AGI test fails with "AGI_API_KEY not configured"
**Solution**: Set the environment variable:
```bash
export AGI_API_KEY=your_key_here
```

### Issue: AGI returns 0 reviews
**Possible Causes**:
1. Business name/location not found
2. No public reviews available for that business
3. AGI API rate limit reached
4. AGI API error

**Solution**: Check AGI API logs, try different business name, or wait if rate limited

### Issue: Optional API tests fail
**Expected Behavior**: Tests should SKIP (not FAIL) when tokens unavailable
**Check**: Ensure tests print "⚠ SKIP" not "✗ FAIL"

## Test Philosophy (Per CLAUDE.md)

1. **No Mocks**: All API calls are real
2. **Graceful Degradation**: Missing tokens = skip (not fail)
3. **Evidence-Based**: Save outputs for manual verification
4. **Error Handling**: Catch real errors, don't crash
5. **Agent Adaptation**: Future: Agent should adapt when APIs fail

## Next Steps

After tests pass:
1. Review saved JSON outputs in `/outputs/social/`
2. Verify data quality matches expectations
3. Check logs for any warnings or performance issues
4. Integrate into CI/CD pipeline (with proper credentials)
5. Add to Agent 1 (Research Agent) workflow

## Related Files

- Service: `/backend/services/social_service.py`
- AGI Service: `/backend/services/agi_service.py`
- Test Plan: `/backend/tests/TEST_PLAN.md`
- Development Guide: `/CLAUDE.md`

## Questions?

See TEST_PLAN.md section 1.6 for detailed test specifications.

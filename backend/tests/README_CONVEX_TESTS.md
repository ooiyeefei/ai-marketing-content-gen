# Convex Service Test Suite

## Overview

Comprehensive test suite for `ConvexService` that validates async database operations for campaigns, research, analytics, and creative content storage.

## Test Philosophy

Following **CLAUDE.md** principles:
- **No mocks** - Uses real Convex deployment
- **Evidence before claims** - Every assertion verified with actual data
- **Autonomous agent testing** - Tests the full data flow for 3-agent system

## Test Coverage

### 8 Test Functions

1. **test_convex_create_campaign()**
   - Creates campaign record in Convex
   - Verifies initial state (status='pending', progress=0)
   - Tests: Campaign CRUD operations

2. **test_convex_update_progress()**
   - Updates campaign progress multiple times
   - Verifies progress tracking (0% → 50% → 100%)
   - Tests: Progress tracking accuracy

3. **test_convex_store_research()**
   - Stores Agent 1 research output
   - Verifies data integrity (business context, competitors, insights)
   - Tests: Complex nested object storage

4. **test_convex_store_analytics()**
   - Stores Agent 2 analytics output
   - Verifies customer sentiment, performance patterns, trends
   - Tests: Analytics data persistence

5. **test_convex_store_creative()**
   - Stores Agent 3 creative output
   - Verifies 7 days of content + learning data
   - Tests: Large object storage with arrays

6. **test_convex_async_operations()**
   - Creates/updates 3 campaigns concurrently
   - Verifies non-blocking behavior
   - Tests: Async performance

7. **test_convex_full_campaign_data()**
   - Retrieves all campaign data (research + analytics + progress)
   - Verifies complete data retrieval
   - Tests: Full campaign data aggregation

8. **test_convex_error_handling()**
   - Tests retrieval of non-existent campaigns
   - Verifies graceful error handling (returns None)
   - Tests: Error handling

## Prerequisites

### Environment Variables

Ensure `.env` contains:
```bash
CONVEX_URL=https://your-deployment.convex.cloud
```

### Convex Schema

The following tables must be defined in Convex dashboard:

```javascript
// campaigns table
{
  campaign_id: string,
  status: string,
  progress: number,
  current_agent: string | null,
  message: string
}

// research table
{
  campaign_id: string,
  business_context: object,
  competitors: array,
  market_insights: object,
  research_images: array,
  timestamp: string
}

// analytics table
{
  campaign_id: string,
  customer_sentiment: object,
  past_performance: object | null,
  market_trends: object,
  customer_photos: array,
  timestamp: string
}

// content table
{
  campaign_id: string,
  days: array,
  learning_data: object,
  status: string,
  timestamp: string
}
```

## Running Tests

### Run All Tests

```bash
cd backend/tests
python test_convex_service.py
```

### Expected Output

```
======================================================================
CONVEX SERVICE TEST SUITE
======================================================================

Testing with REAL Convex deployment (no mocks)
Following CLAUDE.md principles:
  ✓ Real API calls only
  ✓ Evidence before completion claims
  ✓ Test autonomous agent data flows

======================================================================
TEST: Convex Create Campaign
======================================================================
Creating campaign: test_campaign_a1b2c3d4
✓ Campaign created in 0.42s
✓ Campaign verified:
  Status: pending
  Progress: 0%
✅ TEST PASSED: Campaign created successfully

[... 7 more tests ...]

======================================================================
TEST SUMMARY
======================================================================
✅ PASSED: Create Campaign
✅ PASSED: Update Progress
✅ PASSED: Store Research
✅ PASSED: Store Analytics
✅ PASSED: Store Creative
✅ PASSED: Async Operations
✅ PASSED: Full Campaign Data
✅ PASSED: Error Handling

Total: 8/8 tests passed

🎉 ALL TESTS PASSED!
```

### Expected Time

- **Total execution time**: 5-10 seconds
- **Per test**: 0.5-2 seconds (network latency dependent)
- **Async test**: Should complete faster than sequential operations

## Test Artifacts

### Output Directory

```
backend/tests/outputs/convex/
└── test_results_1234567890.json
```

### Test Results JSON

```json
{
  "timestamp": "2024-11-23T12:34:56.789Z",
  "results": [
    {"test": "Create Campaign", "passed": true},
    {"test": "Update Progress", "passed": true},
    ...
  ],
  "summary": {
    "total": 8,
    "passed": 8,
    "failed": 0
  },
  "test_campaigns": [
    "test_campaign_a1b2c3d4",
    "test_progress_e5f6g7h8",
    ...
  ]
}
```

## Success Criteria

### All Tests Must Pass
- ✅ Campaign creation works
- ✅ Progress tracking accurate
- ✅ Research data stored/retrieved
- ✅ Analytics data stored/retrieved
- ✅ Creative data stored/retrieved
- ✅ Async operations non-blocking
- ✅ Full data retrieval works
- ✅ Error handling graceful

### Performance Requirements
- ✅ Each test completes < 5 seconds
- ✅ Async operations faster than sequential
- ✅ No connection timeouts

### Data Integrity
- ✅ Write-read consistency
- ✅ Nested objects preserved
- ✅ Arrays maintained
- ✅ Timestamps stored correctly

## Cleanup

### Test Data Cleanup

Test campaigns are prefixed with `test_*` for easy identification.

**Manual cleanup via Convex dashboard:**
1. Go to [Convex Dashboard](https://dashboard.convex.dev)
2. Navigate to Data tab
3. Filter by `campaign_id` starting with "test_"
4. Delete test records

**Test campaigns logged in output:**
```
Test campaigns created (for manual cleanup if needed):
  - test_campaign_a1b2c3d4
  - test_progress_e5f6g7h8
  - test_research_i9j0k1l2
  ...
```

## Troubleshooting

### Test Failures

#### "CONVEX_URL environment variable not set"
**Cause**: Missing Convex URL in `.env`
**Fix**: Add `CONVEX_URL=https://your-deployment.convex.cloud` to `.env`

#### "Cannot connect to Convex"
**Cause**: Invalid Convex URL or network issues
**Fix**:
1. Verify URL in Convex dashboard
2. Check network connectivity
3. Ensure Convex deployment is active

#### "Campaign not found after creation"
**Cause**: Convex schema mismatch
**Fix**:
1. Verify campaigns table exists in Convex
2. Check schema matches expected structure
3. Review Convex logs for mutation errors

#### "Data integrity verification failed"
**Cause**: Schema version mismatch or data corruption
**Fix**:
1. Check Convex schema definitions
2. Verify mutation functions exist
3. Review Convex function logs

### Performance Issues

#### Tests taking > 10 seconds
**Likely causes**:
- Network latency to Convex servers
- Cold start (first operation slower)
- Rate limiting (too many tests run consecutively)

**Mitigation**:
- Run tests during off-peak hours
- Add delays between test runs
- Check Convex dashboard for performance metrics

## Integration with Test Plan

This test suite implements Section 1.4 of `TEST_PLAN.md`:

```
✅ test_convex_create_campaign() - Create and verify campaign
✅ test_convex_update_progress() - Update progress tracking
✅ test_convex_store_research() - Store and retrieve research data
✅ test_convex_store_analytics() - Store and retrieve analytics data
✅ test_convex_store_creative() - Store and retrieve creative data
✅ test_convex_async_operations() - Verify non-blocking behavior
✅ test_convex_full_campaign_data() - Retrieve all campaign data (bonus)
✅ test_convex_error_handling() - Graceful error handling (bonus)
```

## Next Steps

1. **Run tests** to verify Convex integration
2. **Review output artifacts** in `outputs/convex/`
3. **Verify test data** in Convex dashboard
4. **Clean up test campaigns** after verification
5. **Proceed to Agent tests** (require Convex working)

## Notes

- Tests use **real Convex API** (no mocks per CLAUDE.md)
- Each test is **independent** (can run in any order)
- Test data is **isolated** (unique campaign IDs per test)
- **Async operations tested** for non-blocking behavior
- **Data integrity verified** for all stored/retrieved data

## Contact

For issues with Convex service tests, check:
1. Convex dashboard logs
2. Test output artifacts
3. Environment variables
4. Schema definitions

# Campaign Orchestrator E2E Tests

Comprehensive end-to-end testing for the 3-agent campaign orchestration system.

---

## Overview

These tests verify the complete campaign pipeline from business URL to finished 7-day content strategy.

**⚠️ WARNING: Each test takes 20-30 minutes with real APIs**
**⚠️ Total runtime: 60-90 minutes for all tests**

---

## Test Coverage

### Test 1: Full Pipeline E2E (`test_orchestrator_full_pipeline`)

**Purpose:** Verify complete 3-agent pipeline execution

**What it tests:**
- Agent 1 (Research) extracts business context and discovers competitors
- Agent 2 (Analytics) analyzes sentiment and performance
- Agent 3 (Creative) generates 7-day content campaign
- All data saved to Convex
- Total execution time < 30 minutes
- Complete campaign data returned

**Expected outputs:**
```json
{
  "campaign_id": "uuid",
  "business_name": "Blue Bottle Coffee",
  "research_report": {...},
  "analytics_report": {...},
  "campaign_content": {
    "days": [7 days of content]
  }
}
```

**Verification checks:**
- ✅ Campaign ID generated
- ✅ Business name extracted
- ✅ Research has competitors and market insights
- ✅ Analytics has sentiment data
- ✅ Creative has 7 days of content
- ✅ Completed within 30 minutes

---

### Test 2: Progress Tracking (`test_orchestrator_progress_tracking`)

**Purpose:** Verify real-time progress monitoring

**What it tests:**
- Progress starts at 0%
- Progress updates through 0% → 25% → 50% → 100%
- Status updates: `pending` → `agent1_running` → `agent2_running` → `agent3_running` → `completed`
- Current agent updates correctly
- Final status is "completed"
- Final progress is 100%

**Progress milestones:**
```
0%   - Campaign created
1-25% - Agent 1 running (Research)
26-50% - Agent 2 running (Analytics)
51-99% - Agent 3 running (Creative)
100% - Campaign complete
```

**Verification checks:**
- ✅ Progress reaches 100%
- ✅ Status becomes "completed"
- ✅ All agent transitions recorded

---

### Test 3: Error Recovery (`test_orchestrator_error_recovery`)

**Purpose:** Verify error handling and graceful failure

**What it tests:**
- Invalid URLs handled gracefully
- Empty URLs rejected
- Error status updated in Convex
- Proper error messages returned
- No partial data corruption

**Test cases:**
1. **Invalid URL:** `https://this-domain-does-not-exist-12345.com`
   - Expected: Exception raised, no campaign created
2. **Empty URL:** `""`
   - Expected: Validation error, no campaign created

**Verification checks:**
- ✅ Errors caught and handled
- ✅ Error messages are descriptive
- ✅ Convex status updated to "failed"
- ✅ No corrupted partial data

---

## Running Tests

### Prerequisites

1. **Environment variables configured:**
   ```bash
   # Check all required env vars
   python backend/tests/check_all_env.py
   ```

2. **Services available:**
   - Convex (database)
   - R2 (image storage)
   - Claude API (AGI service)
   - Gemini API (strategy service)
   - Social APIs (Facebook, Instagram)

3. **Stable internet connection** (20-30 min per test)

---

### Run All Tests

```bash
cd backend/tests
python test_orchestrator.py
```

**⚠️ This will take 60-90 minutes total**

The script will:
1. Wait 10 seconds (press Ctrl+C to cancel)
2. Run Test 1: Full Pipeline (20-30 min)
3. Run Test 2: Progress Tracking (20-30 min)
4. Run Test 3: Error Recovery (5-10 min)
5. Generate final report

---

### Run Individual Tests

**Test 1 only:**
```python
# Edit test_orchestrator.py, comment out tests 2 and 3 in main()
python test_orchestrator.py
```

**Test 3 only (faster):**
```python
# Edit test_orchestrator.py, comment out tests 1 and 2 in main()
python test_orchestrator.py
```

---

## Output Files

All outputs saved to: `backend/tests/outputs/orchestrator/`

### Test 1 Outputs

```
test1_full_pipeline_response.json   - Complete campaign data
test1_verification_report.json      - Data completeness checks
test1_summary.json                  - Test execution summary
test1_error_report.json             - (if failed) Error details
```

### Test 2 Outputs

```
test2_progress_tracking_response.json - Complete campaign data
test2_final_progress.json             - Final progress state
test2_summary.json                    - Test execution summary
test2_error_report.json               - (if failed) Error details
```

### Test 3 Outputs

```
test3_error_recovery_results.json   - Error handling test results
test3_summary.json                  - Test execution summary
```

### Final Report

```
FINAL_REPORT.json                   - Overall test results
```

---

## Interpreting Results

### Success Example

```
================================================================================
FINAL TEST SUMMARY
================================================================================

Total runtime: 85m 34s

Tests passed: 3/3

✅ Full Pipeline
✅ Progress Tracking
✅ Error Recovery

================================================================================
ALL TESTS PASSED ✅
================================================================================
```

### Failure Example

```
================================================================================
FINAL TEST SUMMARY
================================================================================

Total runtime: 45m 12s

Tests passed: 2/3

✅ Full Pipeline
❌ Progress Tracking
   Error: Connection timeout to Convex
✅ Error Recovery

================================================================================
SOME TESTS FAILED ❌
================================================================================
```

---

## Verification Reports

### test1_verification_report.json

```json
{
  "checks": {
    "campaign_id": true,
    "business_name": true,
    "research_complete": true,
    "analytics_complete": true,
    "creative_complete": true,
    "research_has_competitors": true,
    "research_has_market_insights": true,
    "analytics_has_sentiment": true,
    "creative_has_7_days": true
  },
  "passed": 9,
  "total": 9,
  "success_rate": 1.0
}
```

**All checks should be `true` for a complete campaign.**

---

## Troubleshooting

### Test takes too long (>30 min)

**Possible causes:**
- Slow API responses (Lightpanda, Gemini)
- Network throttling
- Rate limiting

**Solutions:**
- Check API quotas
- Verify network connection
- Run during off-peak hours

---

### Agent 1 fails immediately

**Possible causes:**
- Invalid business URL
- Lightpanda scraping failed
- Claude API down

**Solutions:**
- Verify URL is accessible
- Check Lightpanda status
- Verify AGI_SERVICE_URL

---

### Agent 2 fails

**Possible causes:**
- Gemini API unavailable
- Social API credentials invalid
- No reviews found

**Solutions:**
- Check GEMINI_API_KEY
- Verify Facebook/Instagram tokens
- Try different business URL

---

### Agent 3 fails

**Possible causes:**
- Minimax API unavailable
- R2 upload failed
- Missing research data

**Solutions:**
- Check MINIMAX_API_KEY
- Verify R2 credentials
- Check Agents 1 & 2 completed

---

### Progress not updating

**Possible causes:**
- Convex connection lost
- Progress update calls failing
- Campaign ID mismatch

**Solutions:**
- Check Convex status
- Verify CONVEX_URL
- Check logs for errors

---

## Performance Benchmarks

### Expected Timings

| Agent | Expected Duration | Operations |
|-------|------------------|------------|
| Agent 1 | 8-12 minutes | Scrape business, discover competitors, market research |
| Agent 2 | 5-10 minutes | Fetch reviews, analyze sentiment, get social performance |
| Agent 3 | 7-10 minutes | Generate 7 captions, 7 images, 7 videos |
| **Total** | **20-32 minutes** | Complete pipeline |

### Timing Breakdown

```
0:00 - Campaign created
0:30 - Agent 1 started (Business scraping)
3:00 - Competitor discovery
8:00 - Agent 1 complete, Agent 2 started
10:00 - Sentiment analysis
13:00 - Agent 2 complete, Agent 3 started
15:00 - Caption generation
18:00 - Image generation
22:00 - Video generation
25:00 - Campaign complete ✅
```

---

## API Call Estimates

### Agent 1 (Research)
- 1x Lightpanda scrape (business)
- 1x Perplexity search (competitors)
- 3x Lightpanda scrape (competitors)
- 1x Claude HIGH (market analysis)
- **Total: ~6 API calls**

### Agent 2 (Analytics)
- 1x Google Places API (reviews)
- 1x Gemini HIGH (sentiment)
- 1x Facebook API (posts)
- 1x Instagram API (posts)
- 1x Gemini HIGH (performance)
- **Total: ~5 API calls**

### Agent 3 (Creative)
- 1x Gemini HIGH (strategy)
- 7x Claude (captions)
- 7x Minimax (images)
- 7x Minimax (videos)
- 7x R2 (uploads)
- **Total: ~29 API calls**

### Total Pipeline
**~40 API calls per campaign**

---

## Cost Estimates

### Per Campaign

| Service | Calls | Cost per Call | Total |
|---------|-------|---------------|-------|
| Lightpanda | 4 | $0.01 | $0.04 |
| Claude | 8 | $0.015 | $0.12 |
| Gemini | 3 | $0.001 | $0.003 |
| Minimax | 14 | $0.02 | $0.28 |
| Social APIs | 2 | Free | $0 |
| R2 Storage | 7 | $0.001 | $0.007 |
| **TOTAL** | | | **~$0.45** |

**Note:** Costs are estimates and may vary based on:
- Token usage (Claude/Gemini)
- Image resolution (Minimax)
- Video duration (Minimax)

---

## Next Steps

After running these tests:

1. **Review outputs** in `outputs/orchestrator/`
2. **Verify data quality** - Check that generated content makes sense
3. **Test with different businesses** - Try different industries
4. **Measure improvement** - Run multiple campaigns, check learning

---

## Related Documentation

- [TEST_PLAN.md](./TEST_PLAN.md) - Overall testing strategy
- [CLAUDE.md](../../CLAUDE.md) - Development principles
- [orchestrator.py](../orchestrator.py) - Implementation

---

## Support

If tests fail consistently:

1. Check environment variables
2. Verify API credentials
3. Review logs in `outputs/orchestrator/`
4. Check service status pages
5. Try with different test business URL

---

**Last Updated:** 2025-11-23
**Test Version:** 1.0.0

# Orchestrator Tests - Quick Start Guide

**5-minute guide to running E2E orchestrator tests**

---

## TL;DR

```bash
# 1. Check environment
cd backend/tests
python check_all_env.py

# 2. Run tests (60-90 minutes)
python test_orchestrator.py

# 3. Check results
cat outputs/orchestrator/FINAL_REPORT.json
```

---

## What These Tests Do

Tests the **complete 3-agent pipeline**:

```
Business URL → Agent 1 (Research) → Agent 2 (Analytics) → Agent 3 (Creative) → 7-Day Campaign
```

---

## Prerequisites (5 min)

### 1. Environment Variables

**Required:**
```bash
CONVEX_URL=https://your-convex-url.convex.cloud
AGI_SERVICE_URL=http://localhost:8000  # Claude API
GEMINI_API_KEY=your_gemini_key
MINIMAX_API_KEY=your_minimax_key
R2_ACCOUNT_ID=your_r2_account
R2_ACCESS_KEY_ID=your_r2_access
R2_SECRET_ACCESS_KEY=your_r2_secret
R2_BUCKET_NAME=your_bucket
```

**Optional (for full Agent 2 features):**
```bash
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_ACCESS_TOKEN=your_token
INSTAGRAM_ACCOUNT_ID=your_account_id
```

### 2. Check Setup

```bash
cd backend/tests
python check_all_env.py
```

Should show all ✅ green checks.

---

## Running Tests

### All Tests (60-90 min)

```bash
python test_orchestrator.py
```

**⚠️ This will:**
- Wait 10 seconds (press Ctrl+C to cancel)
- Run Test 1: Full Pipeline (20-30 min)
- Run Test 2: Progress Tracking (20-30 min)
- Run Test 3: Error Recovery (5-10 min)

### Test 3 Only (5 min - good for quick validation)

Edit `test_orchestrator.py`:

```python
async def main():
    # Comment out tests 1 and 2
    # test_results.append(await test_orchestrator_full_pipeline())
    # test_results.append(await test_orchestrator_progress_tracking())

    # Only run Test 3
    result = await test_orchestrator_error_recovery()
    test_results.append({"test": "Error Recovery", "passed": result})
```

Then run:
```bash
python test_orchestrator.py
```

---

## Watching Progress

The test will print real-time updates:

```
================================================================================
TEST 1: ORCHESTRATOR FULL PIPELINE
================================================================================

Target: https://www.bluebottlecoffee.com
Max duration: 30m 0s

Initializing orchestrator...
Starting campaign...
⚠️ This will take 20-30 minutes with real APIs

================================================================================
AGENT 1: Research & Intelligence
================================================================================
[3m 45s] Scraping business website...
[5m 12s] Discovering competitors...
[8m 30s] Analyzing market...

Agent 1 complete: Blue Bottle Coffee
  - Competitors researched: 3
  - Market insights: 8 trending topics

================================================================================
AGENT 2: Analytics & Feedback
================================================================================
[10m 15s] Fetching reviews...
[12m 40s] Analyzing sentiment...

Agent 2 complete: Sentiment & Performance analyzed
  - Positive themes: 12
  - Recommendations: 8

================================================================================
AGENT 3: Creative Generation
================================================================================
[15m 20s] Generating captions...
[18m 45s] Creating images...
[22m 10s] Generating videos...

Agent 3 complete: 7 days of content generated

✅ Campaign completed in 25m 34s
```

---

## Checking Results

### Quick Check

```bash
# See if tests passed
cat outputs/orchestrator/FINAL_REPORT.json | grep success_rate

# Output:
# "success_rate": 1.0  <- All passed!
```

### Full Report

```bash
# Pretty print results
cat outputs/orchestrator/FINAL_REPORT.json | python -m json.tool
```

### Individual Test Results

```bash
# Test 1 - Full Pipeline
cat outputs/orchestrator/test1_summary.json

# Test 2 - Progress Tracking
cat outputs/orchestrator/test2_summary.json

# Test 3 - Error Recovery
cat outputs/orchestrator/test3_summary.json
```

### View Campaign Data

```bash
# Complete campaign output
cat outputs/orchestrator/test1_full_pipeline_response.json | python -m json.tool

# Shows:
# - Business context
# - Competitors
# - Market insights
# - Customer sentiment
# - 7 days of content (captions, images, videos)
```

---

## Success Criteria

### Test 1: Full Pipeline ✅

- Campaign completes in < 30 minutes
- All 3 agents run successfully
- Complete data returned:
  - Business context
  - 3+ competitors
  - Market insights
  - Customer sentiment
  - 7 days of content

### Test 2: Progress Tracking ✅

- Progress starts at 0%
- Progress updates through 25%, 50%, 100%
- Final status is "completed"

### Test 3: Error Recovery ✅

- Invalid URLs handled gracefully
- Error messages descriptive
- No data corruption

---

## Troubleshooting

### Test hangs / takes too long

```bash
# Check if APIs are responding
curl $AGI_SERVICE_URL/health
curl https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY
```

### Agent 1 fails

```bash
# Check Lightpanda is available
curl https://api.lightpanda.io/status
```

### Agent 2 fails

```bash
# Check Gemini API
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-thinking-exp:generateContent?key=$GEMINI_API_KEY"
```

### Agent 3 fails

```bash
# Check Minimax API
curl -H "Authorization: Bearer $MINIMAX_API_KEY" https://api.minimaxi.chat/v1/models
```

### Can't connect to Convex

```bash
# Verify CONVEX_URL
echo $CONVEX_URL

# Should be: https://something.convex.cloud
```

---

## Expected Outputs

### After Test 1

```
outputs/orchestrator/
├── test1_full_pipeline_response.json  (20-50 KB)
├── test1_verification_report.json     (1 KB)
└── test1_summary.json                 (2 KB)
```

### After All Tests

```
outputs/orchestrator/
├── test1_full_pipeline_response.json
├── test1_verification_report.json
├── test1_summary.json
├── test2_progress_tracking_response.json
├── test2_final_progress.json
├── test2_summary.json
├── test3_error_recovery_results.json
├── test3_summary.json
└── FINAL_REPORT.json
```

---

## What to Do Next

### If Tests Pass ✅

1. **Review campaign quality:**
   ```bash
   cat outputs/orchestrator/test1_full_pipeline_response.json
   ```

2. **Check content generated:**
   - Are captions relevant?
   - Do images match business?
   - Are videos on-brand?

3. **Run with different business:**
   ```python
   # Edit test_orchestrator.py
   TEST_BUSINESS_URL = "https://your-business.com"
   ```

4. **Test learning/improvement:**
   - Run 2 campaigns sequentially
   - Verify quality scores improve

### If Tests Fail ❌

1. **Check error report:**
   ```bash
   cat outputs/orchestrator/test1_error_report.json
   ```

2. **Review logs:**
   ```bash
   # Look for error details
   grep -r "ERROR" outputs/orchestrator/
   ```

3. **Verify environment:**
   ```bash
   python check_all_env.py
   ```

4. **Try simpler test first:**
   - Run Test 3 only (error recovery)
   - Should complete in 5 minutes
   - Tests basic connectivity

---

## Cost Estimate

**Per full test run:**
- API calls: ~40
- Estimated cost: ~$0.45
- Total for 3 tests: ~$1.35

**Breakdown:**
- Lightpanda: $0.04
- Claude: $0.12
- Gemini: $0.003
- Minimax: $0.28
- R2 Storage: $0.007

---

## Time Estimate

| Test | Duration | Can Skip? |
|------|----------|-----------|
| Test 1: Full Pipeline | 20-30 min | No - Core test |
| Test 2: Progress Tracking | 20-30 min | Yes - Similar to Test 1 |
| Test 3: Error Recovery | 5-10 min | No - Fast validation |

**Recommended order:**
1. Run Test 3 first (5 min) - validates setup
2. Run Test 1 (30 min) - validates full pipeline
3. Skip Test 2 if time-constrained (it's similar to Test 1)

---

## Quick Commands Reference

```bash
# Run all tests
python test_orchestrator.py

# Check results
cat outputs/orchestrator/FINAL_REPORT.json | grep success_rate

# View campaign data
cat outputs/orchestrator/test1_full_pipeline_response.json | python -m json.tool

# View errors (if any)
cat outputs/orchestrator/*error*.json

# Clean outputs
rm -rf outputs/orchestrator/*.json
```

---

## Need Help?

1. **Check environment:** `python check_all_env.py`
2. **Review logs:** `cat outputs/orchestrator/*.json`
3. **Read full docs:** `README_ORCHESTRATOR_TESTS.md`
4. **Check TEST_PLAN.md:** Section 3.1 (Integration Tests)

---

**Ready? Let's go!**

```bash
cd backend/tests
python test_orchestrator.py
```

Press Ctrl+C within 10 seconds to cancel, or let it run!

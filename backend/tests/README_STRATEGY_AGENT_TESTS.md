# Strategy Agent (Agent 2) Tests

## Overview

Comprehensive integration tests for Strategy Agent (Agent 2) - Analytics & Feedback system.

**Agent 2 Responsibilities:**
- Fetch Google My Business reviews (with AGI fallback)
- Analyze customer sentiment with Gemini HIGH thinking
- Fetch Facebook/Instagram performance (optional)
- Analyze performance patterns with Gemini HIGH thinking
- Fetch Google Trends data
- Store all data in Convex + R2

## Test Philosophy

Following TDD principles from `CLAUDE.md`:

1. **Use REAL APIs** - No mocks, no dummy data
2. **Test Autonomous Behavior** - Verify agent decisions, not just data flow
3. **Verify Quality** - Check Gemini HIGH thinking produces strategic insights
4. **Test Fallbacks** - AGI scraping for unclaimed businesses
5. **Test Resilience** - Graceful handling of missing social tokens
6. **Evidence-Based** - Save all outputs for manual inspection

## Prerequisites

### Required Environment Variables

```bash
# Gemini 3.0 Pro (for sentiment analysis)
export GEMINI_API_KEY="your-gemini-api-key"

# AGI API (for review scraping fallback)
export AGI_API_KEY="your-agi-api-key"

# Convex (for data storage)
export CONVEX_URL="https://your-convex-deployment.convex.cloud"

# Cloudflare R2 (for media storage)
export CLOUDFLARE_ACCOUNT_ID="your-account-id"
export R2_ACCESS_KEY_ID="your-r2-access-key"
export R2_SECRET_ACCESS_KEY="your-r2-secret-key"
export R2_BUCKET="superscrat"

# Optional: Social Media APIs (tests handle gracefully if missing)
export GOOGLE_MY_BUSINESS_API_KEY="your-gmb-key"  # Optional
export FACEBOOK_ACCESS_TOKEN="your-fb-token"       # Optional
export INSTAGRAM_ACCESS_TOKEN="your-ig-token"      # Optional
export GOOGLE_TRENDS_API_KEY="your-trends-key"     # Optional
```

### Check Environment Setup

```bash
cd backend/tests
python check_social_env.py
```

## Test Cases

### Test 1: Full Workflow
**File:** `test_strategy_agent_full_workflow()`

**What it tests:**
- Complete Agent 2 workflow from start to finish
- Fetches reviews (GMB or AGI fallback)
- Analyzes sentiment with Gemini HIGH thinking
- Fetches social media insights (if available)
- Analyzes performance patterns
- Fetches Google Trends
- Stores data in Convex
- Progress tracking: 25% → 50%

**Success Criteria:**
- ✅ Reviews fetched (from any source)
- ✅ Sentiment analysis produces positive_themes, negative_themes, content_opportunities
- ✅ Market trends data retrieved
- ✅ Data stored in Convex successfully
- ✅ Progress reaches 50%
- ✅ No unhandled exceptions

**Output Files:**
```
outputs/agents/strategy/{campaign_id}_research.json    # Agent 1 output
outputs/agents/strategy/{campaign_id}_analytics.json   # Agent 2 output
outputs/agents/strategy/{campaign_id}_report.txt       # Detailed report
```

---

### Test 2: AGI Fallback
**File:** `test_strategy_agent_agi_fallback()`

**What it tests:**
- AGI scraping activates when GMB unavailable
- Reviews scraped from Google Maps, Yelp, etc.
- Sentiment analysis works with AGI-scraped reviews

**Success Criteria:**
- ✅ AGI scraping completes successfully
- ✅ Reviews fetched from multiple sources
- ✅ Sentiment analysis produces insights
- ✅ No crashes when GMB unavailable

**Output Files:**
```
outputs/agents/strategy/{campaign_id}_agi_fallback.json
```

---

### Test 3: No Social Tokens
**File:** `test_strategy_agent_no_social_tokens()`

**What it tests:**
- Graceful handling when FB/IG tokens unavailable
- Agent completes without social insights
- Sentiment analysis still works

**Success Criteria:**
- ✅ Agent completes successfully
- ✅ past_performance = None (no social data)
- ✅ customer_sentiment available
- ✅ market_trends available
- ✅ No crashes

**Output Files:**
```
outputs/agents/strategy/{campaign_id}_no_social.json
```

---

### Test 4: Error Handling
**File:** `test_strategy_agent_error_handling()`

**What it tests:**
- Graceful error when invalid campaign_id
- Clear error messages
- No crashes

**Success Criteria:**
- ✅ ValueError raised for missing research data
- ✅ Clear error message
- ✅ No unhandled exceptions

---

### Test 5: Gemini HIGH Thinking Verification
**File:** `test_strategy_agent_gemini_high_thinking()`

**What it tests:**
- Gemini HIGH thinking mode used for sentiment analysis
- Strategic insights (not just literal review extraction)
- Multiple themes and opportunities identified

**Success Criteria:**
- ✅ Multiple positive themes identified (≥2)
- ✅ Multiple content opportunities identified (≥2)
- ✅ Insights are detailed and actionable
- ✅ Strategic analysis evident

---

## Running Tests

### Run All Tests

```bash
cd backend/tests
python test_strategy_agent.py
```

### Run Individual Test (modify main() to comment out others)

```bash
python test_strategy_agent.py
```

### Expected Output

```
================================================================================
BRANDMIND AI - STRATEGY AGENT (AGENT 2) TESTS
================================================================================
Output directory: outputs/agents/strategy
Test started: 2025-11-23T02:30:00

================================================================================
TEST: test_strategy_agent_full_workflow
================================================================================

📋 Setting up test campaign: test_strategy_abc123

🔍 Running Agent 1 to generate research data...
✓ Research complete: Blue Bottle Coffee
💾 Saved research to: outputs/agents/strategy/test_strategy_abc123_research.json

📊 Running Agent 2 for campaign: test_strategy_abc123

✓ Agent 2 completed

📋 Analytics Output:
   - Positive themes: 5
   - Negative themes: 2
   - Popular items: 8
   - Content opportunities: 4
   - Quotable reviews: 3
   - Trending searches: 6
   - Past performance: None

✅ Data stored in Convex successfully

✅ Progress tracking: 50% - Analytics complete ✓

💾 Saved analytics to: outputs/agents/strategy/test_strategy_abc123_analytics.json
💾 Saved report to: outputs/agents/strategy/test_strategy_abc123_report.txt

✅ PASS: test_strategy_agent_full_workflow

[... more tests ...]

================================================================================
TEST SUMMARY
================================================================================
Total Tests: 5
Passed: 5
Failed: 0
Duration: 180.45s

✅ Passed Tests:
   - test_strategy_agent_full_workflow
   - test_strategy_agent_agi_fallback
   - test_strategy_agent_no_social_tokens
   - test_strategy_agent_error_handling
   - test_strategy_agent_gemini_high_thinking
================================================================================
```

## Output Files

### JSON Outputs
- `{campaign_id}_research.json` - Agent 1 research data (setup)
- `{campaign_id}_analytics.json` - Agent 2 analytics output
- `{campaign_id}_agi_fallback.json` - AGI fallback test output
- `{campaign_id}_no_social.json` - No social tokens test output

### Text Reports
- `{campaign_id}_report.txt` - Detailed human-readable report with:
  - Customer sentiment themes
  - Popular items
  - Content opportunities
  - Quotable reviews
  - Performance patterns (if available)
  - Market trends

## Verification Checklist

After running tests, manually verify:

### 1. Agent 2 Output Quality
```bash
cat outputs/agents/strategy/test_strategy_*_report.txt
```

**Check:**
- [ ] Positive themes are specific and actionable
- [ ] Negative themes identify real pain points
- [ ] Popular items are actual products/services
- [ ] Content opportunities are strategic (not generic)
- [ ] Quotable reviews are compelling

### 2. Convex Data Storage

**Check Convex Dashboard:**
- [ ] `research` table has entries
- [ ] `analytics` table has entries
- [ ] `campaigns` table shows progress 50%
- [ ] All JSON structures are valid

### 3. Gemini HIGH Thinking Verification

**Look for strategic analysis:**
- [ ] Multiple themes identified (not just one)
- [ ] Themes are synthesized (not verbatim from reviews)
- [ ] Content opportunities connect to customer insights
- [ ] Recommendations are specific and actionable

### 4. AGI Fallback Verification

**Check AGI fallback output:**
- [ ] Reviews fetched from multiple sources
- [ ] Sources listed: "Google Maps", "Yelp", etc.
- [ ] Sentiment analysis works with scraped reviews
- [ ] No crashes when GMB unavailable

## Troubleshooting

### Issue: "No research data found for campaign"
**Solution:** Agent 1 must run first to populate research data.
```python
campaign_id = await setup_test_campaign(with_research=True)
```

### Issue: "AGI API error: Timeout"
**Solution:** AGI web scraping can be slow (up to 60s). Increase timeout if needed.

### Issue: "Convex connection error"
**Solution:** Check `CONVEX_URL` environment variable. Ensure Convex deployment is running.

### Issue: "Gemini API rate limit"
**Solution:** Tests use HIGH thinking mode (slower but better quality). Add delays between tests if needed.

### Issue: "past_performance = None"
**Expected:** This is normal when no social tokens provided. Test verifies graceful handling.

## Test Duration

- **Full workflow:** ~60-90 seconds (includes Agent 1 setup)
- **AGI fallback:** ~60-90 seconds
- **No social tokens:** ~60 seconds
- **Error handling:** <5 seconds
- **Gemini HIGH thinking:** ~60 seconds

**Total:** ~3-5 minutes for all tests

## Next Steps

After Strategy Agent tests pass:

1. **Run Creative Agent tests:** `test_creative_agent.py`
2. **Run Orchestrator tests:** `test_orchestrator.py`
3. **Run API endpoint tests:** `test_api_endpoints.py`
4. **Run full E2E test:** Complete campaign generation

## Success Criteria Summary

Agent 2 tests are considered successful when:

1. ✅ All 5 tests pass without exceptions
2. ✅ Sentiment analysis produces strategic insights (not just data extraction)
3. ✅ AGI fallback works for unclaimed businesses
4. ✅ Graceful handling when social tokens unavailable
5. ✅ Data stored correctly in Convex
6. ✅ Progress tracking works (25% → 50%)
7. ✅ Output files are human-readable and accurate

## Related Documentation

- `CLAUDE.md` - Development principles (TDD, no mocks, autonomous agents)
- `TEST_PLAN.md` - Complete test strategy
- `README_CONVEX_TESTS.md` - Convex service tests
- `GEMINI_TEST_SUMMARY.md` - Gemini service tests
- `AGI_TEST_SUMMARY.md` - AGI service tests

---

**Note:** These tests use real API calls. Costs incurred:
- Gemini HIGH thinking: ~$0.10 per test
- AGI API: ~$0.50 per test (web scraping)
- Total per run: ~$3-5

Budget accordingly for test execution.

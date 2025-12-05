# Strategy Agent (Agent 2) Test Suite - Complete Summary

## Overview

Comprehensive integration test suite for Strategy Agent (Agent 2) - Analytics & Feedback system that validates real API integrations, autonomous behavior, and quality of AI-generated insights.

**Created:** 2025-11-23
**Files:** 4 (test script, runner, docs, quickstart)
**Test Cases:** 5 comprehensive integration tests
**Coverage:** Full Agent 2 workflow + edge cases

---

## Files Created

### 1. Test Implementation
**File:** `/backend/tests/test_strategy_agent.py` (22KB)

**Contains:**
- 5 comprehensive test functions
- Setup/teardown utilities
- Real API integration (no mocks)
- Output file generation
- Progress tracking verification
- Convex storage validation

**Test Functions:**
```python
async def test_strategy_agent_full_workflow()           # Main workflow test
async def test_strategy_agent_agi_fallback()            # AGI scraping fallback
async def test_strategy_agent_no_social_tokens()        # Graceful degradation
async def test_strategy_agent_error_handling()          # Error recovery
async def test_strategy_agent_gemini_high_thinking()    # Quality verification
```

---

### 2. Test Runner Script
**File:** `/backend/tests/run_strategy_tests.sh` (4.1KB)

**Features:**
- Environment variable validation
- Required vs optional vars distinction
- Output directory creation
- Colored console output
- Exit code handling

**Usage:**
```bash
cd backend/tests
./run_strategy_tests.sh
```

---

### 3. Detailed Documentation
**File:** `/backend/tests/README_STRATEGY_AGENT_TESTS.md` (11KB)

**Sections:**
- Test philosophy (from CLAUDE.md)
- Prerequisites and environment setup
- Detailed test case descriptions
- Success criteria for each test
- Output file explanations
- Troubleshooting guide
- Verification checklist
- Cost estimates

---

### 4. Quick Reference
**File:** `/backend/tests/STRATEGY_AGENT_TEST_QUICKSTART.md` (3.5KB)

**Content:**
- TL;DR commands
- Expected outputs
- Success criteria summary
- Quick troubleshooting
- Key differences from traditional tests

---

## Test Architecture

### Agent Workflow Tested

```
┌─────────────────────────────────────────────────────────────────┐
│ Agent 1: Research (Setup Phase)                                  │
│ - Extract business context                                       │
│ - Discover competitors                                           │
│ - Market research                                                │
│ → Store in Convex                                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Agent 2: Strategy & Analytics (TEST FOCUS)                       │
│                                                                   │
│ Step 1: Fetch Reviews                                            │
│   ├─→ Try: Google My Business API                                │
│   └─→ Fallback: AGI scraping (Google Maps, Yelp, etc.)          │
│                                                                   │
│ Step 2: Analyze Sentiment (Gemini HIGH thinking)                 │
│   ├─→ Positive themes                                            │
│   ├─→ Negative themes                                            │
│   ├─→ Popular items                                              │
│   ├─→ Quotable reviews                                           │
│   └─→ Content opportunities                                      │
│                                                                   │
│ Step 3: Fetch Social Media Insights (Optional)                   │
│   ├─→ Facebook Page insights                                     │
│   └─→ Instagram account insights                                 │
│                                                                   │
│ Step 4: Analyze Performance (Gemini HIGH thinking)               │
│   ├─→ Winning patterns                                           │
│   ├─→ Avoid patterns                                             │
│   └─→ Recommendations                                            │
│                                                                   │
│ Step 5: Fetch Google Trends                                      │
│   ├─→ Trending searches                                          │
│   ├─→ Related queries                                            │
│   └─→ Rising topics                                              │
│                                                                   │
│ Step 6: Store Analytics Output                                   │
│   ├─→ Save to Convex                                             │
│   └─→ Update progress (25% → 50%)                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Test Cases Breakdown

### Test 1: Full Workflow (Primary Test)

**Purpose:** Verify complete Agent 2 pipeline from research retrieval to analytics storage

**Flow:**
1. Setup test campaign with Agent 1 (research data)
2. Run Agent 2 analytics workflow
3. Verify sentiment analysis (Gemini HIGH)
4. Verify optional social insights
5. Verify Google Trends data
6. Verify Convex storage
7. Verify progress tracking (25% → 50%)

**Assertions:**
```python
assert isinstance(analytics_output, AnalyticsOutput)
assert analytics_output.campaign_id == campaign_id
assert isinstance(analytics_output.customer_sentiment, CustomerSentiment)
assert len(analytics_output.customer_sentiment.positive_themes) > 0
assert retrieved_analytics is not None  # Convex storage
assert progress.percentage >= 50  # Progress tracking
```

**Output Files:**
- `{campaign_id}_research.json` - Agent 1 setup data
- `{campaign_id}_analytics.json` - Agent 2 output
- `{campaign_id}_report.txt` - Human-readable report

**Duration:** ~60-90 seconds

---

### Test 2: AGI Fallback (Resilience Test)

**Purpose:** Verify AGI scraping activates when GMB API unavailable (unclaimed businesses)

**Scenario:**
- Business doesn't have claimed Google My Business profile
- GMB API returns no data or errors
- AGI service scrapes public reviews from:
  - Google Maps (public reviews)
  - Yelp
  - TripAdvisor
  - Facebook page reviews

**Assertions:**
```python
# Verify reviews were fetched (from any source)
assert len(analytics_output.customer_sentiment.positive_themes) > 0 or \
       len(analytics_output.customer_sentiment.negative_themes) > 0

# Verify sentiment analysis worked with scraped reviews
assert analytics_output.customer_sentiment is not None
```

**Output Files:**
- `{campaign_id}_agi_fallback.json`

**Duration:** ~60-90 seconds (web scraping is slow)

---

### Test 3: No Social Tokens (Graceful Degradation)

**Purpose:** Verify Agent 2 completes successfully when optional social tokens unavailable

**Scenario:**
- No `FACEBOOK_ACCESS_TOKEN` in environment
- No `INSTAGRAM_ACCESS_TOKEN` in environment
- Agent should skip social insights gracefully
- Sentiment analysis and trends still work

**Assertions:**
```python
assert isinstance(analytics_output, AnalyticsOutput)
assert analytics_output.past_performance is None  # No social data
assert analytics_output.customer_sentiment is not None  # Still works
assert analytics_output.market_trends is not None  # Still works
```

**Output Files:**
- `{campaign_id}_no_social.json`

**Duration:** ~60 seconds

---

### Test 4: Error Handling (Error Recovery)

**Purpose:** Verify graceful error handling and clear error messages

**Scenario:**
- Invalid campaign_id (no research data)
- Should raise ValueError with clear message
- No crashes or unhandled exceptions

**Assertions:**
```python
try:
    await strategy_agent.run(campaign_id="invalid_id")
    raise AssertionError("Should have raised ValueError")
except ValueError as e:
    assert "No research data found" in str(e)
```

**Duration:** <5 seconds

---

### Test 5: Gemini HIGH Thinking (Quality Verification)

**Purpose:** Verify Gemini HIGH thinking produces strategic insights (not just data extraction)

**What to Check:**
- Multiple positive themes identified (≥2)
- Multiple content opportunities identified (≥2)
- Insights are synthesized (not verbatim from reviews)
- Recommendations are specific and actionable

**Assertions:**
```python
assert len(sentiment.positive_themes) >= 2
assert len(sentiment.content_opportunities) >= 2

# Verify insights are detailed
for opp in sentiment.content_opportunities:
    assert len(opp) > 10  # Not just one-word themes
```

**What HIGH Thinking Should Produce:**

❌ **Low Quality (literal extraction):**
```json
{
  "positive_themes": ["good", "nice", "great"],
  "content_opportunities": ["post about coffee", "show food"]
}
```

✅ **High Quality (strategic insights):**
```json
{
  "positive_themes": [
    "Customers appreciate the sustainable sourcing and transparency about origin",
    "Barista expertise and personalized brewing recommendations create loyalty",
    "Minimalist aesthetic and natural lighting appeal to remote workers"
  ],
  "content_opportunities": [
    "Behind-the-scenes content showing direct trade relationships with farmers",
    "Barista profiles highlighting their craft and favorite brewing methods",
    "Customer stories about their 'third place' experiences in your space"
  ]
}
```

**Duration:** ~60 seconds

---

## Output Directory Structure

```
backend/tests/outputs/agents/strategy/
├── test_strategy_abc123_research.json       # Agent 1 setup (business context, competitors)
├── test_strategy_abc123_analytics.json      # Agent 2 output (sentiment, trends)
├── test_strategy_abc123_report.txt          # Human-readable analysis report
├── test_strategy_def456_agi_fallback.json   # AGI scraping test output
└── test_strategy_ghi789_no_social.json      # No social tokens test output
```

### Example Report Output

```txt
Strategy Agent Test Report
Campaign ID: test_strategy_abc123
Test: test_strategy_agent_full_workflow
Timestamp: 2025-11-23T02:30:00

=== Customer Sentiment ===

Positive Themes:
  - Customers appreciate the sustainable sourcing and transparency about origin
  - Barista expertise and personalized brewing recommendations
  - Minimalist aesthetic and natural lighting
  - Premium quality coffee beans
  - Consistent product quality across locations

Negative Themes:
  - Occasional long wait times during morning rush
  - Higher price point compared to competitors

Popular Items:
  - New Orleans Iced Coffee
  - Single Origin Pour Over
  - Almond Croissants
  - Cold Brew
  - Espresso Tonic

Content Opportunities:
  - Behind-the-scenes content showing direct trade relationships with farmers
  - Barista profiles highlighting their craft and favorite brewing methods
  - Customer stories about their 'third place' experiences
  - Educational content about coffee origins and brewing methods

Quotable Reviews:
  - "Best coffee in SF - you can taste the difference in quality"
  - "The baristas really know their stuff and helped me find my perfect brew"
  - "Love the sustainable practices and transparent sourcing"

=== Market Trends ===

Trending Searches:
  - sustainable coffee San Francisco
  - third wave coffee
  - specialty coffee shops
  - cold brew near me
  - coffee tasting flights

Related Queries:
  - best pour over coffee SF
  - ethical coffee roasters
  - barista workshops
```

---

## Environment Variables

### Required (Tests Will Fail Without These)

```bash
export GEMINI_API_KEY="your-gemini-api-key"           # Sentiment analysis
export AGI_API_KEY="your-agi-api-key"                 # Review scraping fallback
export CONVEX_URL="https://your-convex.cloud"         # Data storage
export CLOUDFLARE_ACCOUNT_ID="your-account-id"        # R2 storage
export R2_ACCESS_KEY_ID="your-r2-access-key"          # R2 storage
export R2_SECRET_ACCESS_KEY="your-r2-secret-key"      # R2 storage
export R2_BUCKET="superscrat"                         # R2 bucket name
```

### Optional (Tests Handle Gracefully If Missing)

```bash
export GOOGLE_MY_BUSINESS_API_KEY="your-gmb-key"      # Will use AGI fallback if missing
export FACEBOOK_ACCESS_TOKEN="your-fb-token"          # Will skip if missing
export INSTAGRAM_ACCESS_TOKEN="your-ig-token"         # Will skip if missing
export GOOGLE_TRENDS_API_KEY="your-trends-key"        # Will skip if missing
```

---

## Running Tests

### Quick Start

```bash
cd backend/tests
./run_strategy_tests.sh
```

### Manual Run

```bash
cd backend/tests
python3 test_strategy_agent.py
```

### Run Individual Test (modify main())

```python
async def main():
    await test_strategy_agent_full_workflow()  # Run only this one
    results.summary()
```

---

## Success Criteria

### Tests Pass When:

1. ✅ **All 5 tests complete without exceptions**
2. ✅ **Sentiment analysis produces strategic insights**
   - Not just literal review extraction
   - Multiple themes and opportunities
   - Actionable recommendations
3. ✅ **AGI fallback works for unclaimed businesses**
   - Reviews scraped from multiple sources
   - Sentiment analysis works with scraped data
4. ✅ **Graceful handling when social tokens unavailable**
   - No crashes
   - past_performance = None (expected)
   - Other analytics still work
5. ✅ **Data stored correctly in Convex**
   - Research data retrievable
   - Analytics data retrievable
   - JSON structure valid
6. ✅ **Progress tracking works (25% → 50%)**
   - Campaign status updates
   - Progress percentage accurate
   - Current agent tracked

---

## Verification Checklist

After tests pass, manually verify:

### 1. Sentiment Quality (Human Review)
```bash
cat outputs/agents/strategy/*_report.txt
```

**Check:**
- [ ] Positive themes are specific (not "good", "nice", "great")
- [ ] Negative themes identify real pain points (not just "bad")
- [ ] Popular items are actual products/services
- [ ] Content opportunities are strategic and actionable
- [ ] Quotable reviews are compelling and specific

### 2. Convex Storage (Database Check)

**Open Convex Dashboard and verify:**
- [ ] `research` table has test campaign entries
- [ ] `analytics` table has sentiment data
- [ ] `campaigns` table shows progress = 50%
- [ ] All JSON structures are valid (no errors)
- [ ] Timestamps are correct

### 3. AGI Fallback (Review Source Check)

**Check AGI fallback output:**
- [ ] Reviews fetched from multiple sources (not just one)
- [ ] Sources listed: "Google Maps", "Yelp", "TripAdvisor", etc.
- [ ] Review text is meaningful (not empty)
- [ ] Sentiment analysis worked with scraped data

### 4. Gemini HIGH Thinking (Strategic Analysis)

**Look for evidence of strategic analysis:**
- [ ] Themes are synthesized (not verbatim quotes)
- [ ] Multiple themes identified (not just one)
- [ ] Content opportunities connect to customer insights
- [ ] Recommendations are specific and actionable
- [ ] Analysis considers business context

---

## Test Duration & Costs

### Duration
- **Full workflow:** 60-90 seconds (includes Agent 1 setup)
- **AGI fallback:** 60-90 seconds (web scraping is slow)
- **No social tokens:** 60 seconds
- **Error handling:** <5 seconds
- **Gemini HIGH thinking:** 60 seconds
- **Total:** 3-5 minutes for all tests

### API Costs (Estimate)
- **Gemini HIGH thinking:** ~$0.10 per test × 5 = $0.50
- **AGI web scraping:** ~$0.50 per test × 3 = $1.50
- **Convex operations:** Free (hobby tier)
- **R2 storage:** Free (minimal usage)
- **Total per run:** ~$2-3

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "No research data found" | Agent 1 didn't run | Test calls `setup_test_campaign(with_research=True)` automatically |
| "AGI API timeout" | Web scraping takes time | Normal - AGI scraping can take 60s |
| "Convex connection error" | Invalid CONVEX_URL | Check environment variable, ensure deployment is running |
| "Gemini rate limit" | Too many requests | Add delays between tests or use lower rate |
| "past_performance = None" | No social tokens | Expected behavior - test verifies graceful handling |
| "R2 upload failed" | Invalid credentials | Check R2 environment variables |

### Debug Mode

Add debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## What Makes This Test Suite Special

Following `CLAUDE.md` development principles:

### 1. No Mocks or Dummy Data ✅
- Real API calls to Gemini, AGI, Convex, R2
- No fallback to mock data
- Tests actual integration and error handling

### 2. Autonomous Agent Testing ✅
- Tests agent decisions (not just data flow)
- Verifies quality of AI-generated insights
- Checks strategic analysis (not just data extraction)

### 3. Resilience Testing ✅
- AGI fallback for unclaimed businesses
- Graceful degradation without social tokens
- Clear error messages

### 4. Quality-Driven ✅
- Verifies Gemini HIGH thinking produces strategic insights
- Checks for actionable recommendations
- Validates content opportunities are specific

### 5. Evidence-Based ✅
- Saves all outputs for manual inspection
- Human-readable reports
- JSON outputs for programmatic verification

---

## Next Steps

After Strategy Agent tests pass:

1. **Run Creative Agent tests** → `test_creative_agent.py`
   - Content generation (captions, images, videos)
   - MiniMax integration
   - Quality evaluation
   - Learning extraction

2. **Run Orchestrator tests** → `test_orchestrator.py`
   - Full 3-agent pipeline
   - Progress tracking across agents
   - Error recovery
   - Campaign completion

3. **Run API endpoint tests** → `test_api_endpoints.py`
   - FastAPI endpoints
   - Request/response validation
   - WebSocket progress streaming

4. **Run full E2E test**
   - Complete campaign generation
   - All agents working together
   - Real business use case

---

## Related Documentation

- `CLAUDE.md` - Development principles (TDD, no mocks, autonomous agents)
- `TEST_PLAN.md` - Complete test strategy for all agents
- `README_CONVEX_TESTS.md` - Convex service tests
- `GEMINI_TEST_SUMMARY.md` - Gemini service tests
- `AGI_TEST_SUMMARY.md` - AGI service tests
- `README_STRATEGY_AGENT_TESTS.md` - Detailed test documentation
- `STRATEGY_AGENT_TEST_QUICKSTART.md` - Quick reference guide

---

## Summary

The Strategy Agent test suite provides comprehensive validation of Agent 2's analytics workflow with:

- ✅ **5 comprehensive integration tests**
- ✅ **Real API integrations** (Gemini HIGH, AGI, Convex, R2)
- ✅ **Autonomous behavior verification** (strategic insights, not just data)
- ✅ **Resilience testing** (AGI fallback, graceful degradation)
- ✅ **Quality validation** (Gemini HIGH thinking verification)
- ✅ **Evidence-based testing** (all outputs saved for inspection)
- ✅ **Clear success criteria** (actionable, specific insights)
- ✅ **Complete documentation** (4 supporting docs)

This test suite ensures Agent 2 meets hackathon requirements for "autonomous, self-improving AI agents" by testing real decision-making, strategic analysis, and quality improvement.

**Tests created:** 2025-11-23
**Author:** Claude Code (following CLAUDE.md principles)
**Status:** Ready for execution

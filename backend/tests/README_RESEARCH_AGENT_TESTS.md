# Research Agent (Agent 1) - Integration Tests

## Overview

Comprehensive integration tests for the Research Agent that verify autonomous competitor discovery, web research capabilities, and data storage with real API integrations.

## Test Coverage

### Test 1: Full Workflow with Autonomous Discovery
**Purpose:** Verify Agent 1 can autonomously discover and research competitors without user input

**What it tests:**
- ✅ Business context extraction from website (AGI API)
- ✅ Autonomous competitor discovery (3-5 competitors)
- ✅ Deep research on each discovered competitor
- ✅ Market trends analysis
- ✅ Data storage in Convex
- ✅ Progress tracking (0% → 25%)

**Input:** Business URL only (no competitor URLs)
**Expected:** Complete research data with autonomously discovered competitors

### Test 2: Provided Competitors Workflow
**Purpose:** Verify Agent 1 can research user-provided competitor URLs

**What it tests:**
- ✅ Business context extraction
- ✅ Research on provided competitor URLs
- ✅ Competitor count matches input
- ✅ All competitor data fields populated
- ✅ Data storage in Convex

**Input:** Business URL + list of competitor URLs
**Expected:** Research data with exact competitors provided

### Test 3: Error Handling
**Purpose:** Verify Agent 1 handles invalid URLs gracefully

**What it tests:**
- ✅ Invalid URL detection
- ✅ No crashes or unhandled exceptions
- ✅ Clear error messages
- ✅ Fallback behavior

**Input:** Invalid/non-existent URL
**Expected:** Graceful error handling, no crash

## Prerequisites

### Required Environment Variables
```bash
# AGI API (critical for web research)
AGI_API_KEY=your-agi-api-key

# Convex Database (for data storage)
CONVEX_URL=https://your-project.convex.cloud

# Cloudflare R2 (for media storage)
CLOUDFLARE_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET=your-bucket-name
```

### Python Dependencies
All dependencies are in `backend/requirements.txt`:
```bash
pip install -r backend/requirements.txt
```

## Running the Tests

### Quick Start
```bash
# From project root
cd backend/tests
python test_research_agent.py
```

### What to Expect

**Test Execution Time:** 5-15 minutes (depends on AGI API response times)

**Console Output:**
```
======================================================================
BrandMind AI - Research Agent Integration Tests
======================================================================
Output directory: /backend/tests/outputs/agents/research
Test started: 2025-11-23 14:30:00
======================================================================

[14:30:01] ℹ️ Environment variables verified

======================================================================
Test 1: Research Agent Full Workflow (Autonomous Discovery)
======================================================================
[14:30:02] ℹ️ Campaign ID: test_a1b2c3d4
[14:30:03] ✅ Campaign created in Convex
[14:30:04] ✅ Research Agent initialized
[14:30:05] ℹ️ Starting research for: https://www.bluebottlecoffee.com
[14:30:06] ⚠️ Mode: AUTONOMOUS COMPETITOR DISCOVERY
...
[14:35:42] ✅ Research workflow completed

--- Verification 1: Business Context ---
[14:35:43] ✅ Business: Blue Bottle Coffee
[14:35:43] ✅ Industry: Coffee
[14:35:43] ✅ Location: {'city': 'Oakland', 'state': 'CA', 'country': 'USA'}
[14:35:43] ✅ Specialties: 5 found

--- Verification 2: Competitor Discovery ---
[14:35:44] ✅ Competitors discovered: 5
[14:35:44] ℹ️   1. Philz Coffee (San Francisco, CA)
[14:35:44] ℹ️   2. Sightglass Coffee (San Francisco, CA)
[14:35:44] ℹ️   3. Verve Coffee Roasters (Santa Cruz, CA)
...

--- Verification 3: Market Insights ---
[14:35:45] ✅ Trending topics: 8
[14:35:45] ✅ Market gaps: 3
[14:35:45] ✅ Positioning opportunities: 4

--- Verification 4: Convex Storage ---
[14:35:46] ✅ Convex verification: Research data found

--- Verification 5: Progress Tracking ---
[14:35:47] ℹ️ Progress: 25% (expected: 25%)
[14:35:47] ✅ Progress tracking verified

--- Saving Test Outputs ---
[14:35:48] ℹ️ Saved output: test_a1b2c3d4_full_research_output.json
[14:35:48] ℹ️ Saved output: test_a1b2c3d4_business_context.json
[14:35:48] ℹ️ Saved output: test_a1b2c3d4_competitors.json
[14:35:48] ℹ️ Saved output: test_a1b2c3d4_market_insights.json

✅ Test 1: PASSED - Full workflow with autonomous discovery

======================================================================
TEST SUMMARY
======================================================================
✅ PASSED - Full Workflow (Autonomous Discovery)
✅ PASSED - Provided Competitors Workflow
✅ PASSED - Error Handling
======================================================================
Results: 3/3 tests passed
🎉 ALL TESTS PASSED

Test completed: 2025-11-23 14:45:00
Outputs saved to: /backend/tests/outputs/agents/research
======================================================================
```

## Output Artifacts

After successful test execution, you'll find these files in `backend/tests/outputs/agents/research/`:

### Test 1 Outputs (Autonomous Discovery)
```
test_[campaign_id]_full_research_output.json    # Complete research output
test_[campaign_id]_business_context.json        # Business context only
test_[campaign_id]_competitors.json             # Competitor list
test_[campaign_id]_market_insights.json         # Market insights
```

### Test 2 Outputs (Provided Competitors)
```
test_[campaign_id]_provided_competitors_output.json   # Complete output
test_[campaign_id]_provided_competitors_list.json     # Competitor list
```

### Example Output Structure

**business_context.json:**
```json
{
  "business_name": "Blue Bottle Coffee",
  "industry": "Coffee",
  "description": "Specialty coffee roaster...",
  "location": {
    "city": "Oakland",
    "state": "CA",
    "country": "USA"
  },
  "price_range": "premium",
  "specialties": ["single-origin", "pour-over", "espresso"],
  "brand_voice": "minimalist, artisanal, quality-focused",
  "target_audience": "coffee enthusiasts, professionals",
  "website_url": "https://www.bluebottlecoffee.com"
}
```

**competitors.json:**
```json
[
  {
    "name": "Philz Coffee",
    "website": "https://www.philzcoffee.com",
    "location": "San Francisco, CA",
    "google_rating": 4.5,
    "review_count": 1234,
    "social_handles": {
      "instagram": "@philzcoffee"
    },
    "pricing_strategy": "premium",
    "brand_voice": "personalized, friendly",
    "top_content_themes": [
      "behind-the-scenes",
      "new locations",
      "signature drinks"
    ],
    "differentiators": [
      "customized coffee blends",
      "no espresso menu"
    ],
    "similarity_score": 0.85
  }
  // ... 4 more competitors
]
```

**market_insights.json:**
```json
{
  "trending_topics": [
    "sustainable coffee sourcing",
    "cold brew innovations",
    "coffee subscriptions",
    "farm-to-cup transparency"
  ],
  "market_gaps": [
    "late-night coffee shops",
    "coffee education events",
    "mobile ordering at drive-thrus"
  ],
  "positioning_opportunities": [
    "Emphasize direct trade relationships",
    "Highlight roasting expertise",
    "Create educational content series"
  ],
  "content_strategy": {}
}
```

## Success Criteria

### Critical Requirements
- ✅ All 3 tests pass without crashes
- ✅ Business context extracted with all fields
- ✅ 3-5 competitors discovered autonomously (Test 1)
- ✅ Competitor count matches input (Test 2)
- ✅ All data stored in Convex successfully
- ✅ Progress tracking 0% → 25% verified

### Data Quality Requirements
- ✅ Business name is not "Unknown"
- ✅ Industry is correctly identified
- ✅ Location has city/state/country
- ✅ Each competitor has name, website, location
- ✅ Market insights have 3+ items each

### Performance Requirements
- ✅ Business context extraction: < 60 seconds
- ✅ Competitor discovery: < 2 minutes per competitor
- ✅ Full workflow: < 15 minutes total

## Troubleshooting

### Test Fails with "AGI_API_KEY not set"
**Solution:** Add AGI API key to `.env`:
```bash
AGI_API_KEY=your-key-here
```

### Test Fails with "Cannot connect to Convex"
**Solution:** Verify CONVEX_URL is correct:
```bash
# Check your Convex deployment URL
echo $CONVEX_URL

# Should be: https://[project-name].convex.cloud
```

### AGI API Timeout
**Issue:** AGI API calls timeout after 60 seconds

**Solution:** This is expected for complex research tasks. The test will retry or skip if timeout occurs.

### Competitor Discovery Returns 0 Competitors
**Issue:** AGI API couldn't find competitors

**Possible causes:**
1. Business URL is invalid
2. Business has no clear competitors
3. AGI API is down

**Solution:** Check AGI API status, try different test URL

### R2 Connection Fails
**Issue:** R2Service initialization fails

**Solution:** Verify Cloudflare R2 credentials:
```bash
echo $CLOUDFLARE_ACCOUNT_ID
echo $R2_ACCESS_KEY_ID
echo $R2_BUCKET
```

## Manual Verification

After tests pass, manually verify:

1. **Check Convex Dashboard**
   - Go to https://dashboard.convex.dev/
   - Verify `campaigns` table has test entries
   - Verify `research` table has research data
   - Check progress values are 25%

2. **Inspect Output Files**
   - Open JSON files in `outputs/agents/research/`
   - Verify business context looks correct
   - Check competitor data quality
   - Review market insights relevance

3. **Validate Data Completeness**
   ```bash
   # Check that all output files exist
   ls -lh backend/tests/outputs/agents/research/

   # Verify JSON is valid
   cat backend/tests/outputs/agents/research/test_*_business_context.json | python -m json.tool
   ```

## Next Steps

After Research Agent tests pass:

1. ✅ Run Strategy Agent tests (`test_strategy_agent.py`)
2. ✅ Run Creative Agent tests (`test_creative_agent.py`)
3. ✅ Run full orchestrator test (`test_orchestrator.py`)
4. ✅ Verify end-to-end campaign generation

## Notes

- Tests use **REAL API calls** (no mocks)
- AGI API calls may take 30-120 seconds each
- Test data is saved for manual inspection
- Convex data persists after tests (not cleaned up automatically)
- Test campaign IDs start with `test_` prefix

## Verification Before Completion

Before claiming tests pass, ensure:

- [ ] All 3 tests show "PASSED" status
- [ ] Output files exist in `outputs/agents/research/`
- [ ] All JSON files are valid (parse without errors)
- [ ] Convex dashboard shows test campaign data
- [ ] No error messages in console output
- [ ] Business context has non-empty fields
- [ ] Competitors list has 3-5 entries (Test 1)
- [ ] Progress tracking reached 25%

**Evidence Required:**
1. Terminal output showing "3/3 tests passed"
2. File listing of `outputs/agents/research/`
3. Screenshot of Convex dashboard with test data

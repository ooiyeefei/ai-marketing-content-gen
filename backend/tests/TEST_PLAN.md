# BrandMind AI - Comprehensive Test Plan

## Overview

This document outlines the test strategy for verifying all components work correctly with real API integrations.

**Test Philosophy:**
- Use REAL API calls (no mocks) to verify integration
- Each component testable independently
- Clear pass/fail criteria with evidence
- Save outputs for manual inspection
- Follow verification-before-completion: evidence before claims

---

## Test Structure

```
backend/tests/
├── TEST_PLAN.md                 # This file
├── test_minimax_service.py      # MiniMax image/video generation
├── test_agi_service.py          # AGI web research
├── test_gemini_service.py       # Gemini HIGH/LOW thinking
├── test_convex_service.py       # Convex database operations
├── test_r2_service.py           # R2 storage operations
├── test_social_service.py       # Social APIs + AGI fallback
├── test_research_agent.py       # Agent 1 integration
├── test_strategy_agent.py       # Agent 2 integration
├── test_creative_agent.py       # Agent 3 integration
├── test_orchestrator.py         # Full pipeline E2E
├── test_api_endpoints.py        # FastAPI endpoints
└── outputs/                     # Test output artifacts
    ├── minimax/                 # Generated images/videos
    ├── agi/                     # Research results
    ├── gemini/                  # LLM outputs
    └── campaigns/               # Full campaign results
```

---

## Test Categories

### 1. Service Layer Tests (Unit/Integration)

#### 1.1 MiniMax Service (`test_minimax_service.py`)

**Purpose:** Verify image and video generation API integration

**Test Cases:**
```python
test_minimax_image_generation_simple()
    Input: "A serene coffee shop interior with natural lighting"
    Expected: 2 images (bytes), verify not empty, save to outputs/minimax/
    Verification: Check file size > 10KB, valid JPEG format

test_minimax_image_generation_with_reference()
    Input: Prompt + subject_reference_url
    Expected: 2 images with subject consistency
    Verification: Images generated, saved successfully

test_minimax_video_generation()
    Input: First frame image + prompt
    Expected: Video file (bytes), verify not empty
    Verification: Check file size > 100KB, valid MP4 format

test_minimax_error_handling()
    Input: Invalid API key
    Expected: Proper error message, no crash
    Verification: Exception raised with clear message
```

**Success Criteria:**
- ✅ All API calls return valid data (not empty bytes)
- ✅ Files saved to disk are openable
- ✅ Image file sizes > 10KB
- ✅ Video file sizes > 100KB
- ✅ No unhandled exceptions

**Run Command:**
```bash
python test_minimax_service.py
```

---

#### 1.2 AGI Service (`test_agi_service.py`)

**Purpose:** Verify web research and review scraping

**Test Cases:**
```python
test_agi_scrape_business_context()
    Input: "https://www.bluebottlecoffee.com"
    Expected: Business name, industry, mission, UVP
    Verification: All fields non-empty, industry = "Coffee"

test_agi_discover_competitors()
    Input: Business context
    Expected: 3-5 competitors with URLs
    Verification: Each competitor has name, url, positioning

test_agi_scrape_online_reviews()
    Input: Business name + location
    Expected: Reviews list, overall_rating, sources
    Verification: reviews > 0, rating between 1-5

test_agi_error_handling()
    Input: Invalid URL
    Expected: Graceful error handling
    Verification: Clear error message, no crash
```

**Success Criteria:**
- ✅ All API calls complete within 60 seconds
- ✅ Business context contains all required fields
- ✅ Competitor discovery returns 3+ competitors
- ✅ Review scraping returns reviews from multiple sources
- ✅ No unhandled exceptions

**Run Command:**
```bash
python test_agi_service.py
```

---

#### 1.3 Gemini Service (`test_gemini_service.py`)

**Purpose:** Verify HIGH/LOW thinking modes and JSON output

**Test Cases:**
```python
test_gemini_high_thinking_sentiment_analysis()
    Input: List of reviews
    Expected: Sentiment analysis with positive_themes, negative_themes
    Verification: JSON structure matches AnalysisSummary schema

test_gemini_low_thinking_caption_generation()
    Input: Content theme + style
    Expected: Caption 150-250 chars, hashtags
    Verification: Caption length in range, hashtags present

test_gemini_json_output_parsing()
    Input: Prompt requesting JSON
    Expected: Valid JSON response (no markdown)
    Verification: json.loads() succeeds without errors

test_gemini_error_handling()
    Input: Empty prompt
    Expected: Graceful error handling
    Verification: Clear error message, no crash
```

**Success Criteria:**
- ✅ HIGH thinking mode produces detailed analysis
- ✅ LOW thinking mode produces quick content
- ✅ All outputs are valid JSON
- ✅ Response times: HIGH < 30s, LOW < 10s
- ✅ No unhandled exceptions

**Run Command:**
```bash
python test_gemini_service.py
```

---

#### 1.4 Convex Service (`test_convex_service.py`)

**Purpose:** Verify async database operations

**Test Cases:**
```python
test_convex_create_campaign()
    Input: campaign_id
    Expected: Campaign record created in Convex
    Verification: Query returns record with matching ID

test_convex_update_progress()
    Input: campaign_id, progress=50
    Expected: Progress updated
    Verification: Query returns progress=50

test_convex_store_research()
    Input: ResearchOutput object
    Expected: Research data stored
    Verification: Retrieve and compare data matches

test_convex_store_analytics()
    Input: AnalyticsOutput object
    Expected: Analytics data stored
    Verification: Retrieve and compare data matches

test_convex_store_creative()
    Input: CreativeOutput object
    Expected: Creative data stored
    Verification: Retrieve and compare data matches

test_convex_async_operations()
    Input: Multiple concurrent operations
    Expected: All complete without blocking
    Verification: Total time < sum of individual times
```

**Success Criteria:**
- ✅ All CRUD operations succeed
- ✅ Async operations don't block event loop
- ✅ Data integrity maintained (write-read consistency)
- ✅ No connection errors
- ✅ No unhandled exceptions

**Run Command:**
```bash
python test_convex_service.py
```

---

#### 1.5 R2 Service (`test_r2_service.py`)

**Purpose:** Verify async S3-compatible storage operations

**Test Cases:**
```python
test_r2_upload_bytes()
    Input: Image bytes + object_key
    Expected: Public URL returned
    Verification: URL accessible, file downloadable

test_r2_upload_multiple_concurrent()
    Input: 5 images in parallel
    Expected: All uploads succeed
    Verification: All URLs accessible

test_r2_error_handling()
    Input: Invalid credentials
    Expected: Graceful error handling
    Verification: Clear error message, no crash
```

**Success Criteria:**
- ✅ All uploads complete successfully
- ✅ Public URLs return HTTP 200
- ✅ Downloaded files match uploaded bytes
- ✅ Concurrent uploads work without blocking
- ✅ No unhandled exceptions

**Run Command:**
```bash
python test_r2_service.py
```

---

#### 1.6 Social Service (`test_social_service.py`)

**Purpose:** Verify GMB API and AGI fallback logic

**Test Cases:**
```python
test_social_gmb_reviews_success()
    Input: Business with claimed GMB profile
    Expected: Reviews from GMB API
    Verification: source = "gmb_api"

test_social_gmb_fallback_to_agi()
    Input: Business without claimed profile
    Expected: Reviews from AGI scraping
    Verification: source = "agi_scrape", reviews > 0

test_social_facebook_insights()
    Input: facebook_page_id
    Expected: Insights or None if token unavailable
    Verification: No crash if token missing

test_social_instagram_insights()
    Input: instagram_account_id
    Expected: Insights or None if token unavailable
    Verification: No crash if token missing

test_social_google_trends()
    Input: Location + keywords
    Expected: Trend data or None if API unavailable
    Verification: No crash if API key missing
```

**Success Criteria:**
- ✅ GMB API works when available
- ✅ AGI fallback activates when GMB unavailable
- ✅ Optional APIs (FB, IG, Trends) gracefully skip
- ✅ No crashes when tokens missing
- ✅ No unhandled exceptions

**Run Command:**
```bash
python test_social_service.py
```

---

### 2. Agent Layer Tests (Integration)

#### 2.1 Research Agent (`test_research_agent.py`)

**Purpose:** Verify Agent 1 autonomous research workflow

**Test Cases:**
```python
test_research_agent_full_workflow()
    Input: business_url only (no competitors)
    Expected: ResearchOutput with:
        - business_context (all fields)
        - competitors (3-5 discovered autonomously)
        - market_trends (5+)
    Verification: All data non-empty, stored in Convex

test_research_agent_with_competitors()
    Input: business_url + competitor_urls
    Expected: Uses provided competitors, no discovery
    Verification: Competitor count matches input

test_research_agent_error_handling()
    Input: Invalid URL
    Expected: Graceful error, clear message
    Verification: No crash, error logged
```

**Success Criteria:**
- ✅ Agent discovers competitors autonomously
- ✅ All research data fields populated
- ✅ Data stored in Convex successfully
- ✅ Progress updates 0% → 25%
- ✅ No unhandled exceptions

**Run Command:**
```bash
python test_research_agent.py
```

---

#### 2.2 Strategy Agent (`test_strategy_agent.py`)

**Purpose:** Verify Agent 2 analytics and sentiment analysis

**Test Cases:**
```python
test_strategy_agent_full_workflow()
    Input: campaign_id with research data
    Expected: AnalyticsOutput with:
        - reviews_summary (rating, count, sources)
        - sentiment_analysis (themes, pain points)
        - social_insights (or None if unavailable)
    Verification: All data non-empty, stored in Convex

test_strategy_agent_agi_fallback()
    Input: Unclaimed business (no GMB)
    Expected: Reviews from AGI scraping
    Verification: source = "agi_scrape"

test_strategy_agent_no_social_tokens()
    Input: No FB/IG tokens in .env
    Expected: Completes without social insights
    Verification: social_insights = None, no crash
```

**Success Criteria:**
- ✅ Sentiment analysis completes with Gemini HIGH
- ✅ AGI fallback works for reviews
- ✅ Optional social APIs handled gracefully
- ✅ Data stored in Convex successfully
- ✅ Progress updates 25% → 50%
- ✅ No unhandled exceptions

**Run Command:**
```bash
python test_strategy_agent.py
```

---

#### 2.3 Creative Agent (`test_creative_agent.py`)

**Purpose:** Verify Agent 3 content generation workflow

**Test Cases:**
```python
test_creative_agent_full_workflow()
    Input: campaign_id with research + analytics
    Expected: CreativeOutput with:
        - 7 days of content
        - Each day: caption, 2 images, video (days 1,4,7)
        - All media uploaded to R2
    Verification: All URLs accessible, learning data extracted

test_creative_agent_quality_evaluation()
    Input: Trigger low quality score
    Expected: Agent regenerates content
    Verification: generation_attempts > 1

test_creative_agent_image_generation()
    Input: Single day content
    Expected: 2 images generated with MiniMax
    Verification: Images saved to R2, URLs valid

test_creative_agent_video_generation()
    Input: Day with video (1, 4, or 7)
    Expected: Video generated with MiniMax
    Verification: Video saved to R2, URL valid
```

**Success Criteria:**
- ✅ All 7 days of content generated
- ✅ 14 images + 3 videos created
- ✅ All media accessible via R2 URLs
- ✅ Learning data extracted
- ✅ Progress updates 50% → 100%
- ✅ No unhandled exceptions

**Run Command:**
```bash
python test_creative_agent.py
```

---

### 3. Orchestrator Tests (E2E)

#### 3.1 Orchestrator (`test_orchestrator.py`)

**Purpose:** Verify full 3-agent pipeline

**Test Cases:**
```python
test_orchestrator_full_pipeline()
    Input: business_url
    Expected: Complete CampaignResponse with:
        - research data
        - analytics data
        - 7-day content calendar
    Verification: All sections populated, status="completed"

test_orchestrator_progress_tracking()
    Input: Monitor progress during execution
    Expected: Progress updates 0→25→50→75→100
    Verification: current_agent changes correctly

test_orchestrator_error_recovery()
    Input: Inject error in Agent 2
    Expected: Campaign status="failed", error logged
    Verification: Convex updated with error status
```

**Success Criteria:**
- ✅ All 3 agents execute sequentially
- ✅ Progress tracking accurate
- ✅ Error handling works
- ✅ Campaign data stored in Convex
- ✅ Total time < 30 minutes
- ✅ No unhandled exceptions

**Run Command:**
```bash
python test_orchestrator.py
```

---

### 4. API Layer Tests (E2E)

#### 4.1 FastAPI Endpoints (`test_api_endpoints.py`)

**Purpose:** Verify HTTP endpoints work correctly

**Test Cases:**
```python
test_health_endpoint()
    Request: GET /health
    Expected: {"status": "ok"}
    Verification: HTTP 200

test_generate_campaign_endpoint()
    Request: POST /api/generate
    Expected: {"campaign_id": "...", "status": "processing"}
    Verification: HTTP 200, valid UUID

test_get_progress_endpoint()
    Request: GET /api/campaigns/{id}/progress
    Expected: Progress data with status
    Verification: HTTP 200, progress 0-100

test_get_campaign_endpoint()
    Request: GET /api/campaigns/{id}
    Expected: Complete campaign data
    Verification: HTTP 200, all sections present

test_invalid_campaign_id()
    Request: GET /api/campaigns/invalid
    Expected: HTTP 404
    Verification: Error message present
```

**Success Criteria:**
- ✅ All endpoints return correct HTTP status
- ✅ Response bodies match expected schema
- ✅ Background task execution works
- ✅ Error handling returns proper 4xx/5xx codes
- ✅ No unhandled exceptions

**Run Command:**
```bash
python test_api_endpoints.py
```

---

## Test Execution Strategy

### Phase 1: Service Layer (Parallel)
Run all service tests concurrently to verify integrations:

```bash
cd backend/tests
python test_minimax_service.py &
python test_agi_service.py &
python test_gemini_service.py &
python test_convex_service.py &
python test_r2_service.py &
python test_social_service.py &
wait
```

**Expected time:** 5-10 minutes

### Phase 2: Agent Layer (Sequential)
Run agent tests one at a time (they depend on services):

```bash
python test_research_agent.py
python test_strategy_agent.py
python test_creative_agent.py
```

**Expected time:** 10-20 minutes

### Phase 3: Orchestrator (E2E)
Run full pipeline test:

```bash
python test_orchestrator.py
```

**Expected time:** 20-30 minutes

### Phase 4: API Endpoints
Run API tests:

```bash
python test_api_endpoints.py
```

**Expected time:** 2-5 minutes

---

## Success Criteria Summary

### Critical Requirements
- ✅ All service API integrations work (MiniMax, AGI, Gemini, Convex, R2)
- ✅ All agents complete successfully
- ✅ Full orchestrator pipeline completes
- ✅ All FastAPI endpoints return correct responses
- ✅ No unhandled exceptions in any test

### Performance Requirements
- ✅ Service tests complete < 10 minutes
- ✅ Agent tests complete < 20 minutes
- ✅ Orchestrator test completes < 30 minutes
- ✅ API tests complete < 5 minutes

### Quality Requirements
- ✅ All generated images are valid JPEG files > 10KB
- ✅ All generated videos are valid MP4 files > 100KB
- ✅ All R2 URLs return HTTP 200
- ✅ All Convex data is retrievable
- ✅ All error handling works gracefully

---

## Output Artifacts

After test execution, verify these artifacts exist:

```
backend/tests/outputs/
├── minimax/
│   ├── test_image_1.jpg
│   ├── test_image_2.jpg
│   └── test_video_1.mp4
├── agi/
│   ├── business_context.json
│   ├── competitors.json
│   └── reviews.json
├── gemini/
│   ├── sentiment_analysis.json
│   └── caption_generation.json
└── campaigns/
    └── test_campaign_550e8400/
        ├── research.json
        ├── analytics.json
        ├── creative.json
        └── media/
            ├── day1_image1.jpg
            ├── day1_image2.jpg
            ├── day1_video.mp4
            └── ... [continues for all 7 days]
```

---

## Verification Checklist

Before claiming "tests pass", verify:

- [ ] All test scripts executed without crashes
- [ ] All test outputs saved to `outputs/` directory
- [ ] All images are viewable (open in image viewer)
- [ ] All videos are playable (open in video player)
- [ ] All JSON files are valid (parse without errors)
- [ ] All R2 URLs are accessible (HTTP 200)
- [ ] All Convex records exist (query returns data)
- [ ] Test summary shows: X passed, 0 failed
- [ ] No error messages in logs

**Evidence required:** Terminal output showing test results + file listings of outputs/

---

## Notes

- Tests use REAL API calls (no mocks) to verify actual integration
- API keys must be configured in `.env` before running tests
- Some tests may fail if API rate limits are exceeded
- Video generation tests are slow (~3-5 minutes each)
- Convex tests require active Convex deployment
- R2 tests require valid Cloudflare credentials

---

## Next Steps After Tests Pass

1. Review all output artifacts manually
2. Verify image/video quality meets standards
3. Check Convex database for correct data structure
4. Verify R2 storage for correct file organization
5. Run full orchestrator test with real business URL
6. Prepare demo with test evidence

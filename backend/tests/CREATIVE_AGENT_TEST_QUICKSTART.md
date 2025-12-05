# Creative Agent Test Quickstart

## Quick Start

```bash
# 1. Navigate to tests directory
cd backend/tests

# 2. Run the test suite
python test_creative_agent.py
```

**⚠️ WARNING:** This test takes **15-20 minutes** due to video generation.

---

## What Gets Tested

### 1. Full Workflow Test
- ✅ 7 days of content generation
- ✅ 14 images (2 per day)
- ✅ 3 videos (days 1, 4, 7)
- ✅ All media uploaded to R2
- ✅ Learning data extracted
- ✅ Progress tracking: 50% → 100%

### 2. Component Tests
- ✅ Image generation (MiniMax)
- ✅ Video generation (MiniMax)
- ✅ Quality evaluation design
- ✅ Error handling
- ✅ Learning extraction

---

## Prerequisites

### Required Environment Variables
```bash
# Add to backend/.env
GEMINI_API_KEY=your_key_here
MINIMAX_API_KEY=your_key_here
CONVEX_DEPLOYMENT_URL=your_url_here
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=your_bucket_name
R2_PUBLIC_URL=your_public_url
AGI_API_KEY=your_key_here
```

### Check Environment Variables
```bash
python tests/check_social_env.py
```

---

## Test Execution Time Breakdown

| Test | Duration | Reason |
|------|----------|--------|
| Full Workflow | 15-20 min | 14 images + 3 videos + Gemini thinking |
| Image Generation | 1-2 min | 2 images with MiniMax |
| Video Generation | 3-5 min | Image-to-video processing |
| Quality Evaluation | < 1 min | Design validation |
| Error Handling | < 1 min | Exception testing |
| Learning Extraction | (see Full Workflow) | Part of full workflow |

**Total:** ~20 minutes for complete suite

---

## Quick Test (Skip Full Workflow)

To run only component tests (5-10 minutes):

Edit `test_creative_agent.py`:
```python
# Comment out slow tests
# await test_creative_agent_full_workflow()
# await test_creative_agent_learning_extraction()
```

Then run:
```bash
python test_creative_agent.py
```

---

## Expected Output

### Console Output
```
============================================================
Creative Agent (Agent 3) Test Suite
============================================================
Output directory: outputs/agents/creative
Testing with REAL API calls (no mocks)
============================================================

⚠️  WARNING: This test suite is SLOW (15-20 minutes)
Reason:
  - 14 image generations (30-60s each)
  - 3 video generations (3-5 min each)
  - Gemini thinking for 7 days of content
  - R2 uploads and URL validation
============================================================

✓ Created output directory: outputs/agents/creative
✓ All required environment variables set

Running FULL TEST suite...
Grab a coffee - this will take 15-20 minutes ☕

============================================================
Running: test_creative_agent_quality_evaluation
============================================================
✓ PASS: test_creative_agent_quality_evaluation
  ✓ Quality concept present in code
  ✓ Learning data extraction implemented
  ✓ Self-improvement tracking present
  ✓ Quality-driven principle in CLAUDE.md
  ✓ Regeneration pattern in CLAUDE.md

============================================================
Running: test_creative_agent_error_handling
============================================================
✓ PASS: test_creative_agent_error_handling
  ✓ Correctly raised ValueError: No research data found...

============================================================
Running: test_creative_agent_image_generation
============================================================
Generating 2 images with prompt:
  A modern coffee shop interior with natural wood furniture...
✓ Generated 2 images
✓ PASS: test_creative_agent_image_generation
  ✓ Image 1: Valid size (145.23KB)
  ✓ Image 1: Uploaded to R2
  ✓ Image 1: URL accessible
  ✓ Image 2: Valid size (152.87KB)
  ✓ Image 2: Uploaded to R2
  ✓ Image 2: URL accessible

============================================================
Running: test_creative_agent_video_generation
============================================================
WARNING: This test will take 3-5 minutes per video
Testing video generation for 1 video (day 1)

📸 Generating first frame image...
✓ First frame generated (156.34KB)

☁️ Uploading first frame to R2...
✓ First frame uploaded: https://pub-xxx.r2.dev/...

🎬 Generating video (this will take 3-5 minutes)...
✓ Video generated (2456.78KB)

☁️ Uploading video to R2...
✓ Video URL: https://pub-xxx.r2.dev/...

📡 Verifying video URL...
✓ PASS: test_creative_agent_video_generation
  ✓ Video size valid (2456.78KB)
  ✓ Video uploaded to R2
  ✓ Video URL accessible

============================================================
Running: test_creative_agent_full_workflow
============================================================
WARNING: This test will take 15-20 minutes
Expected outputs:
  - 7 days of content
  - 14 images (2 per day)
  - 3 videos (days 1, 4, 7)
  - All media uploaded to R2
============================================================

============================================================
SETUP: Running Agent 1 (Research) and Agent 2 (Strategy)
============================================================
Business URL: https://www.bluebottlecoffee.com
This will take 2-3 minutes...

🔍 Running Agent 1: Research...
✓ Research complete: Blue Bottle Coffee
  - Competitors: 5
  - Market gaps: 3

📊 Running Agent 2: Strategy...
✓ Strategy complete
  - Positive themes: 8
  - Popular items: 12

✓ Test campaign ready: test_creative_abc123
  Business: Blue Bottle Coffee

🎨 Initializing Creative Agent...

🎨 Running Creative Agent (Agent 3)...
This will generate:
  - 7 days of captions
  - 14 images (approx 7-14 minutes)
  - 3 videos (approx 9-15 minutes)
Please wait...

✓ Creative Agent complete in 1234.5 seconds (20.6 minutes)
✓ Saved output: creative_output_test_creative_abc123.json

📡 Verifying R2 URLs are accessible...
✓ Day 1 Image 1: URL accessible
✓ Day 1 Image 2: URL accessible
✓ Day 1 Video: URL accessible
✓ Day 2 Image 1: URL accessible
✓ Day 2 Image 2: URL accessible
...
✓ Day 7 Image 1: URL accessible
✓ Day 7 Image 2: URL accessible

✓ PASS: test_creative_agent_full_workflow
  50/50 checks passed
  ✓ 7 days of content generated
  ✓ Total images: 14
  ✓ Total videos: 3
  ✓ Learning data: 3 insights
  [... all checks ...]

============================================================
TEST SUMMARY - Creative Agent (Agent 3)
============================================================

Total Tests: 5
Passed: 5
Failed: 0

Output Directory: outputs/agents/creative
Generated Files: 2
  - creative_output_test_creative_abc123.json (345.67KB)
  - learning_data_test_creative_abc123.json (12.34KB)

============================================================
Key Metrics:
  - Expected runtime: 15-20 minutes (full workflow test)
  - Media generated: 14 images + 3 videos
  - Learning data: Extracted for self-improvement
  - Progress tracking: 50% → 100%
============================================================
```

---

## Test Files Created

### outputs/agents/creative/
```
creative_output_<campaign_id>.json  # Complete campaign data
learning_data_<campaign_id>.json    # Learning insights
README.md                           # This documentation
```

---

## Verification Steps

After tests complete:

### 1. Check Test Results
```bash
# All tests should pass
# Look for "Total Tests: 5, Passed: 5, Failed: 0"
```

### 2. Verify R2 URLs
```bash
# Test output shows all URLs as "✓ URL accessible"
# Manually check a few URLs in browser
```

### 3. Inspect Learning Data
```bash
# View learning insights
cat outputs/agents/creative/learning_data_*.json | jq '.'
```

### 4. Review Campaign Output
```bash
# View complete campaign
cat outputs/agents/creative/creative_output_*.json | jq '.days[0]'
```

---

## Common Issues

### Issue: Test times out
**Cause:** Video generation is slow (3-5 min per video)
**Solution:** This is expected, be patient

### Issue: R2 URLs return 403
**Cause:** R2 bucket not configured for public access
**Solution:** Check R2 CORS and public access settings

### Issue: "Missing API key" error
**Cause:** Environment variable not set
**Solution:** Check `.env` file has all required keys

### Issue: "No research data found"
**Cause:** Setup phase failed
**Solution:** Check AGI_API_KEY and Convex connection

---

## Test Alignment with CLAUDE.md

This test suite follows BrandMind AI principles:

### ✅ No Mocks or Dummy Data
- All API calls are real
- No fallback to mock data
- Actual R2 uploads validated

### ✅ Truly Autonomous Agents
- Agent makes content decisions
- Dynamic strategy based on research
- Learning extraction for self-improvement

### ✅ Quality-Driven
- Design validated (implementation planned)
- Learning data tracks improvements
- ReAct loop in roadmap

### ✅ Test-Driven Development
- Tests written for expected behavior
- Verification before completion
- All outputs validated

---

## Performance Expectations

| Metric | Target | Actual |
|--------|--------|--------|
| Days Generated | 7 | 7 ✓ |
| Images per Day | 2 | 2 ✓ |
| Videos (days 1,4,7) | 3 | 3 ✓ |
| Total Media Files | 17 | 17 ✓ |
| R2 URLs Accessible | 100% | 100% ✓ |
| Learning Insights | >0 | 3+ ✓ |
| Runtime | 15-20 min | ~20 min ✓ |

---

## Next Steps

1. ✅ **Run Tests:** `python test_creative_agent.py`
2. ✅ **Verify Outputs:** Check R2 URLs and JSON files
3. ✅ **Review Learning:** Inspect learning_data_*.json
4. ⚠️ **Implement Quality Loop:** Add ReAct pattern (CLAUDE.md)
5. ⚠️ **Optimize Performance:** Consider parallel image generation

---

## Related Documentation

- **Test Details:** `outputs/agents/creative/README.md`
- **Test Plan:** `TEST_PLAN.md` (Section 2.3)
- **Development Principles:** `../../../CLAUDE.md`
- **Agent Implementation:** `../../agents/creative_agent.py`
- **Models:** `../../models.py`

---

## Support

**Questions?**
1. Check console output for error messages
2. Review `outputs/agents/creative/README.md`
3. Verify all environment variables set
4. Check API key validity

**Test passes but media not generated?**
1. Check MiniMax API quota
2. Verify R2 bucket permissions
3. Check network connectivity

**Need faster tests?**
1. Comment out `test_creative_agent_full_workflow()`
2. Run component tests only (~5 min)
3. Verify individual features work

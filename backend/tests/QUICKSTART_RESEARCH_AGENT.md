# Quick Start: Research Agent Tests

## Prerequisites Checklist

- [ ] AGI_API_KEY set in `.env`
- [ ] CONVEX_URL set in `.env`
- [ ] R2 credentials set in `.env`
- [ ] Python dependencies installed

## 1-Minute Setup

```bash
# 1. Copy .env.example to .env (if not done)
cp backend/.env.example backend/.env

# 2. Edit .env and add your API keys
nano backend/.env  # or use your favorite editor

# 3. Install dependencies (if not done)
pip install -r backend/requirements.txt
```

## Run Tests

```bash
# From project root
cd backend/tests

# Run the test script
python test_research_agent.py
```

## Expected Output

```
======================================================================
BrandMind AI - Research Agent Integration Tests
======================================================================

Test 1: Research Agent Full Workflow (Autonomous Discovery)
✅ Test 1: PASSED - Full workflow with autonomous discovery

Test 2: Research Agent with Provided Competitors
✅ Test 2: PASSED - Provided competitors workflow

Test 3: Research Agent Error Handling
✅ Test 3: PASSED - Error handling verified

======================================================================
TEST SUMMARY
======================================================================
✅ PASSED - Full Workflow (Autonomous Discovery)
✅ PASSED - Provided Competitors Workflow
✅ PASSED - Error Handling
======================================================================
Results: 3/3 tests passed
🎉 ALL TESTS PASSED
======================================================================
```

## What Gets Tested

### Test 1: Autonomous Competitor Discovery
- ✅ Extracts business context from URL
- ✅ Discovers 3-5 competitors automatically
- ✅ Researches each competitor deeply
- ✅ Analyzes market trends
- ✅ Stores data in Convex
- ✅ Tracks progress 0% → 25%

### Test 2: Provided Competitors
- ✅ Uses your competitor list
- ✅ Researches each provided URL
- ✅ Verifies data quality

### Test 3: Error Handling
- ✅ Handles invalid URLs gracefully
- ✅ No crashes

## Output Files

Check `backend/tests/outputs/agents/research/` for:
- Business context JSON
- Competitor data JSON
- Market insights JSON
- Full research output JSON

## Time Required

- **Setup:** 2 minutes
- **Test Execution:** 5-15 minutes
- **Total:** ~20 minutes max

## Troubleshooting

### "AGI_API_KEY not set"
Add to `.env`:
```bash
AGI_API_KEY=your-agi-api-key
```

### "Cannot connect to Convex"
Verify `.env` has:
```bash
CONVEX_URL=https://your-project.convex.cloud
```

### Tests Take Too Long
AGI API calls can take 30-120 seconds each. This is normal.

## Verification

Before claiming success:
1. ✅ All tests show "PASSED"
2. ✅ Output files exist in `outputs/agents/research/`
3. ✅ No errors in console
4. ✅ Convex dashboard shows test data

## Next Steps

After tests pass:
1. Review output files manually
2. Check Convex dashboard for data
3. Run Strategy Agent tests next
4. Proceed to full orchestrator test

## Need Help?

- See `README_RESEARCH_AGENT_TESTS.md` for detailed documentation
- Check `TEST_PLAN.md` for overall test strategy
- Review `CLAUDE.md` for development principles

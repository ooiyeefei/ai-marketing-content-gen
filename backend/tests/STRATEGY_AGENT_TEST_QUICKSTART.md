# Strategy Agent Tests - Quick Start

## TL;DR

```bash
cd backend/tests
./run_strategy_tests.sh
```

## What Gets Tested

### 1. Full Workflow ✅
- Agent 1 → Agent 2 pipeline
- Reviews fetching (GMB or AGI fallback)
- Sentiment analysis (Gemini HIGH)
- Social media insights (optional)
- Performance patterns (Gemini HIGH)
- Google Trends
- Convex storage
- Progress tracking (25% → 50%)

### 2. AGI Fallback ✅
- Reviews scraped when GMB unavailable
- Multi-source aggregation (Google Maps, Yelp, etc.)
- Sentiment analysis with scraped reviews

### 3. No Social Tokens ✅
- Graceful handling when FB/IG unavailable
- past_performance = None (expected)
- Sentiment and trends still work

### 4. Error Handling ✅
- Invalid campaign_id → ValueError
- Clear error messages
- No crashes

### 5. Gemini HIGH Thinking ✅
- Strategic insights (not just data extraction)
- Multiple themes and opportunities
- Actionable recommendations

## Expected Outputs

```
outputs/agents/strategy/
├── test_strategy_abc123_research.json      # Agent 1 setup
├── test_strategy_abc123_analytics.json     # Agent 2 output
├── test_strategy_abc123_report.txt         # Human-readable report
├── test_strategy_def456_agi_fallback.json  # AGI fallback test
└── test_strategy_ghi789_no_social.json     # No social tokens test
```

## Success Criteria

All tests pass when:
1. ✅ All 5 tests complete without exceptions
2. ✅ Sentiment analysis produces strategic insights
3. ✅ AGI fallback works for unclaimed businesses
4. ✅ Graceful handling when social tokens missing
5. ✅ Data stored in Convex correctly
6. ✅ Progress tracking 25% → 50%

## Test Duration

- **Total:** 3-5 minutes
- **Per test:** 30-90 seconds

## Verification

### Check sentiment quality:
```bash
cat outputs/agents/strategy/*_report.txt
```

Look for:
- [ ] Positive themes are specific (not generic)
- [ ] Content opportunities are strategic
- [ ] Quotable reviews are compelling

### Check Convex storage:
1. Open Convex dashboard
2. Check `research` table for test campaigns
3. Check `analytics` table for sentiment data
4. Check `campaigns` table for progress = 50%

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No research data found" | Agent 1 runs automatically in setup |
| "AGI timeout" | Normal for web scraping, wait 60s |
| "Convex error" | Check CONVEX_URL env var |
| "Gemini rate limit" | Add delays between tests |
| "past_performance = None" | Expected when no social tokens |

## What Makes This Different

Following CLAUDE.md principles:

1. **No Mocks** - Real API calls to Gemini, AGI, Convex, R2
2. **Autonomous Testing** - Agent decides what to analyze
3. **Quality-Driven** - Verifies strategic insights (not just data flow)
4. **Resilient** - Tests fallbacks and graceful degradation
5. **Evidence-Based** - Saves all outputs for inspection

## Next Steps

After tests pass:
1. `test_creative_agent.py` - Agent 3 content generation
2. `test_orchestrator.py` - Full 3-agent pipeline
3. `test_api_endpoints.py` - FastAPI endpoints

## API Costs (Estimate)

Per test run:
- Gemini HIGH thinking: ~$0.10/test × 5 = $0.50
- AGI web scraping: ~$0.50/test × 3 = $1.50
- **Total:** ~$2-3 per run

## Key Files

- `test_strategy_agent.py` - Test implementation
- `run_strategy_tests.sh` - Test runner script
- `README_STRATEGY_AGENT_TESTS.md` - Detailed documentation
- `TEST_PLAN.md` - Complete test strategy

---

**Questions?** See `README_STRATEGY_AGENT_TESTS.md` for detailed explanations.

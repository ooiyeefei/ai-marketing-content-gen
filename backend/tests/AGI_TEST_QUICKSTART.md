# AGI Service Test - Quick Start

## Run Tests (1 command)

```bash
cd backend/tests && python test_agi_service.py
```

## Verify Outputs (1 command)

```bash
cd backend/tests && python verify_agi_outputs.py
```

## Prerequisites

1. Set `AGI_API_KEY` in environment:
   ```bash
   export AGI_API_KEY=your_key_here
   ```

2. Install dependencies:
   ```bash
   cd backend && pip install httpx asyncio
   ```

## Expected Results

### Console Output
```
======================================================================
TEST SUMMARY
======================================================================
Total Tests: 5
✅ Passed: 5
❌ Failed: 0
⏭️  Skipped: 0
Duration: 480.25s
======================================================================
```

### Output Files
```
backend/tests/outputs/agi/
├── business_context.json          # Business info
├── competitors.json               # 3-5 competitors
├── reviews.json                   # Online reviews
└── competitor_research_*.json     # Deep research
```

## Test Coverage

| Test | Duration | Output |
|------|----------|--------|
| Business Context Extraction | 60-120s | `business_context.json` |
| Competitor Discovery | 120-180s | `competitors.json` |
| Review Scraping | 120-180s | `reviews.json` |
| Competitor Research | 120-180s | `competitor_research_*.json` |
| Error Handling | 60-120s | Console only |

**Total Time:** 8-15 minutes

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "AGI_API_KEY not set" | `export AGI_API_KEY=your_key` |
| "No competitors discovered" | Wait and retry (rate limit) |
| "Timeout error" | Normal for slow websites |
| Import error | `pip install httpx` |

## Success Criteria

- ✅ All 5 tests pass
- ✅ 3-4 JSON files created in `outputs/agi/`
- ✅ All JSON files > 100 bytes
- ✅ JSON files are parseable
- ✅ business_context has `business_name`, `industry`, `description`
- ✅ competitors has at least 1 competitor
- ✅ reviews has `overall_rating` (0-5)

## Next Steps

1. Review JSON outputs manually
2. Run other service tests (Gemini, MiniMax)
3. Proceed to agent integration tests
4. Run full orchestrator E2E test

## Full Documentation

- **Detailed Guide:** `RUN_AGI_TESTS.md`
- **Output Schema:** `outputs/agi/README.md`
- **Test Plan:** `TEST_PLAN.md`
- **Service Code:** `../services/agi_service.py`

# Gemini Service Test - Quick Start

**Run tests in 3 steps. Takes ~40 seconds.**

## Step 1: Set API Key

```bash
export GEMINI_API_KEY='your-gemini-api-key-here'
```

## Step 2: Run Tests

```bash
cd backend
python tests/test_gemini_service.py
```

## Step 3: Check Results

Expected output:

```
======================================================================
GEMINI SERVICE TEST SUITE
======================================================================
Start Time: 2025-01-23 14:30:00
Testing: Gemini 3.0 Pro with HIGH/LOW thinking modes
Environment: GEMINI_API_KEY = ✓ Set
======================================================================

🚀 Initializing Gemini Service...
✅ Service initialized successfully

... (6 tests run)

======================================================================
TEST SUMMARY
======================================================================
Total Tests: 6
✅ Passed: 6
❌ Failed: 0
Success Rate: 100.0%

📊 Full results saved: backend/tests/outputs/gemini/test_results_TIMESTAMP.json
📁 All outputs saved to: backend/tests/outputs/gemini
🏁 Tests completed at: 2025-01-23 14:30:45
======================================================================
```

## What Gets Tested?

1. **JSON Output** - Clean JSON (no markdown wrappers)
2. **HIGH Thinking** - Complex sentiment analysis (5-15s)
3. **HIGH Thinking** - 7-day strategy creation (10-20s)
4. **LOW Thinking** - Fast caption generation (1-3s)
5. **Performance** - LOW is 1.5x+ faster than HIGH
6. **Error Handling** - Service doesn't crash

## Output Files

All saved to `backend/tests/outputs/gemini/`:

- `json_output_parsing_test.json` - JSON validation
- `high_thinking_sentiment_analysis.json` - Sentiment analysis
- `high_thinking_strategy_creation.json` - 7-day strategy
- `low_thinking_caption_generation.txt` - Generated caption
- `performance_comparison.json` - Speed comparison
- `error_handling_empty_input.json` - Edge cases
- `test_results_TIMESTAMP.json` - Full summary

## Success Criteria

✅ All 6 tests pass
✅ HIGH thinking: 5-20 seconds
✅ LOW thinking: 1-5 seconds
✅ JSON output is clean

## Troubleshooting

**API Key Not Set?**
```
❌ ERROR: GEMINI_API_KEY environment variable not set
```
Fix: `export GEMINI_API_KEY='your-key'`

**Module Not Found?**
```
ModuleNotFoundError: No module named 'google.genai'
```
Fix: `pip install google-genai`

**Tests Failing?**
- Check API key is correct
- Verify internet connection
- Check API quota not exceeded

## Full Documentation

- **Complete Guide:** `backend/tests/README.md`
- **Example Outputs:** `backend/tests/GEMINI_TEST_EXAMPLES.md`
- **Quick Reference:** `backend/tests/GEMINI_QUICK_REFERENCE.md`
- **Full Summary:** `backend/tests/GEMINI_TEST_SUMMARY.md`

## Next Steps

After tests pass:
1. Review output files for quality
2. Run full agent pipeline tests
3. Test with real business data
4. Verify learning extraction works

---

**That's it! Set the key, run the tests, check the results.**

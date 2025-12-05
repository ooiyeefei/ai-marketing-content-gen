# Gemini Service Tests

Comprehensive test suite for Gemini 3.0 Pro service with HIGH and LOW thinking modes.

## Prerequisites

1. **Set GEMINI_API_KEY environment variable:**
   ```bash
   export GEMINI_API_KEY='your-gemini-api-key-here'
   ```

2. **Install dependencies:**
   ```bash
   pip install google-genai
   ```

## Running Tests

### Run all tests:
```bash
cd backend
python tests/test_gemini_service.py
```

### Expected Output:
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

======================================================================
🧪 Gemini JSON Output Parsing
======================================================================
🔍 Testing JSON output cleanliness...
✅ JSON Validation:
  Is Dictionary: True
  Has Keys: True
  Keys Found: ['positive_themes', 'negative_themes', 'popular_items', 'quotable_reviews', 'content_opportunities']
   📁 Saved output: backend/tests/outputs/gemini/json_output_parsing_test.json
✅ Gemini JSON Output Parsing - PASSED (2.34s)

... (more tests)

======================================================================
TEST SUMMARY
======================================================================
Total Tests: 6
✅ Passed: 6
❌ Failed: 0
Success Rate: 100.0%

📊 Full results saved: backend/tests/outputs/gemini/test_results_20250123_143045.json
📁 All outputs saved to: backend/tests/outputs/gemini
🏁 Tests completed at: 2025-01-23 14:30:45
======================================================================
```

## Test Cases

### 1. JSON Output Parsing
- **Purpose:** Verify clean JSON output (no markdown wrappers)
- **Expected:** Valid dict with all required keys
- **Output:** `json_output_parsing_test.json`

### 2. HIGH Thinking - Sentiment Analysis
- **Purpose:** Test complex analysis with deep reasoning
- **Expected:** 5-15 seconds, detailed insights with examples
- **Output:** `high_thinking_sentiment_analysis.json`
- **Validates:**
  - All required keys present (positive_themes, negative_themes, popular_items, quotable_reviews, content_opportunities)
  - Non-empty arrays
  - Actionable insights

### 3. HIGH Thinking - Strategy Creation
- **Purpose:** Test strategic planning with 7-day content plan
- **Expected:** 10-20 seconds, 7-day plan with rationale
- **Output:** `high_thinking_strategy_creation.json`
- **Validates:**
  - 7 days in output
  - Each day has: day, theme, content_type, message, hashtags, cta, rationale
  - Rationale explains strategic choices

### 4. LOW Thinking - Caption Generation
- **Purpose:** Test fast content generation
- **Expected:** 1-3 seconds, 100-150 word caption
- **Output:** `low_thinking_caption_generation.txt`
- **Validates:**
  - String output (not JSON)
  - Has hashtags from input
  - Reasonable length (< 200 words)
  - Fast response time

### 5. Performance Comparison
- **Purpose:** Compare HIGH vs LOW thinking speeds
- **Expected:** LOW should be 1.5x+ faster than HIGH
- **Output:** `performance_comparison.json`
- **Validates:**
  - LOW thinking completes in < 5 seconds
  - HIGH thinking takes longer (deeper analysis)
  - Speed ratio documented

### 6. Error Handling
- **Purpose:** Test graceful handling of edge cases
- **Expected:** Service doesn't crash, raises appropriate errors
- **Output:** `error_handling_empty_input.json`
- **Validates:**
  - Empty input handled gracefully
  - Either returns empty structure or raises error
  - Service remains stable

## Test Outputs

All test outputs are saved to: `backend/tests/outputs/gemini/`

### Output Files:
- `json_output_parsing_test.json` - JSON structure validation
- `high_thinking_sentiment_analysis.json` - Complex sentiment analysis results
- `high_thinking_strategy_creation.json` - 7-day strategy with rationale
- `low_thinking_caption_generation.txt` - Generated Instagram caption
- `performance_comparison.json` - HIGH vs LOW speed comparison
- `error_handling_empty_input.json` - Edge case handling
- `test_results_YYYYMMDD_HHMMSS.json` - Full test run summary

### Sample Test Results JSON:
```json
{
  "summary": {
    "total": 6,
    "passed": 6,
    "failed": 0,
    "success_rate": 100.0
  },
  "tests": [
    {
      "test": "Gemini JSON Output Parsing",
      "passed": true,
      "duration_seconds": 2.34,
      "details": {
        "is_dict": true,
        "has_keys": true,
        "keys": ["positive_themes", "negative_themes", ...],
        "error": null
      },
      "timestamp": "2025-01-23T14:30:10.123456"
    }
  ]
}
```

## Performance Benchmarks

### HIGH Thinking Mode:
- **Use Case:** Complex analysis, strategic planning, pattern recognition
- **Expected Duration:** 5-20 seconds
- **Output Quality:** Detailed insights with reasoning and examples
- **Best For:** Sentiment analysis, strategy creation, performance analysis

### LOW Thinking Mode:
- **Use Case:** Fast content generation, template-based output
- **Expected Duration:** 1-5 seconds
- **Output Quality:** Quick, focused results
- **Best For:** Captions, image prompts, motion descriptions

## Troubleshooting

### API Key Not Found:
```
❌ ERROR: GEMINI_API_KEY environment variable not set
   Set it with: export GEMINI_API_KEY='your-key-here'
```
**Solution:** Set the environment variable before running tests.

### Import Errors:
```
ModuleNotFoundError: No module named 'google.genai'
```
**Solution:** Install dependencies:
```bash
pip install google-genai
```

### API Rate Limits:
If you hit rate limits, the tests will fail with API errors.
**Solution:** Wait a few minutes and retry, or reduce test frequency.

### Slow Performance:
If tests consistently take longer than expected:
- Check your internet connection
- Verify API quota/rate limits
- Consider running tests during off-peak hours

## Integration with CI/CD

To run tests in CI/CD pipelines:

```yaml
# .github/workflows/test.yml
- name: Run Gemini Tests
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  run: |
    cd backend
    python tests/test_gemini_service.py
```

## Interpreting Results

### Success Criteria:
- ✅ All 6 tests pass
- ✅ HIGH thinking takes 5-20 seconds
- ✅ LOW thinking takes 1-5 seconds
- ✅ JSON output is clean (no markdown)
- ✅ All required keys present in responses
- ✅ LOW thinking is 1.5x+ faster than HIGH

### What to Check if Tests Fail:
1. **JSON Parsing Fails:** Check if API changed response format
2. **HIGH Thinking Times Out:** API might be slow, increase timeout
3. **LOW Thinking Too Slow:** Check network latency or API load
4. **Missing Keys:** API response format changed, update service code
5. **Error Handling Fails:** Service crashed instead of raising error

## Next Steps

After verifying Gemini service works:
1. Run integration tests with full agent pipeline
2. Test with real business data
3. Verify quality scores meet thresholds (>75)
4. Test learning extraction from generated content
5. Verify strategy adapts based on learnings

## Related Tests

- `test_vertex_service.py` - Vertex AI (grounded search)
- `test_lightpanda_service.py` - Web scraping
- `test_redis_service.py` - Data persistence
- `test_langgraph_orchestrator.py` - Full agent pipeline

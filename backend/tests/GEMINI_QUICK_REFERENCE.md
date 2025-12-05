# Gemini Service Quick Reference

**Fast reference for using Gemini 3.0 Pro in BrandMind AI**

## Setup

```bash
# Set API key
export GEMINI_API_KEY='your-api-key-here'

# Run tests
cd backend
python tests/test_gemini_service.py
```

## Thinking Modes

### HIGH Thinking (5-20 seconds)
**Use for:** Complex analysis, strategic planning, pattern recognition

```python
# Sentiment Analysis
result = await gemini.analyze_customer_sentiment(
    reviews=[...],
    business_name="Sakura Sushi"
)
# Output: {positive_themes, negative_themes, popular_items, quotable_reviews, content_opportunities}

# Performance Analysis
result = await gemini.analyze_performance_patterns(
    posts=[...],
    business_name="Sakura Sushi"
)
# Output: {winning_patterns, avoid_patterns, recommendations}

# Strategy Creation
result = await gemini.create_content_strategy(
    business_context={...},
    market_insights={...},
    customer_sentiment={...},
    past_performance={...},
    market_trends={...}
)
# Output: {days: [7 days with theme, content_type, message, hashtags, cta, rationale]}
```

### LOW Thinking (1-5 seconds)
**Use for:** Fast content generation, template-based output

```python
# Caption Generation
caption = await gemini.generate_caption(
    day_plan={
        "day": 1,
        "theme": "...",
        "message": "...",
        "hashtags": [...],
        "cta": "..."
    },
    business_context={"business_name": "...", "brand_voice": "..."}
)
# Output: Plain text caption with hook, story, CTA, hashtags

# Image Prompt Generation
prompt = await gemini.generate_image_prompt(
    day_plan={...},
    business_context={...},
    customer_favorites=[...]
)
# Output: Concise image generation prompt (max 200 chars)

# Video Motion Prompt
motion = await gemini.generate_video_motion_prompt(
    day_plan={...},
    business_name="..."
)
# Output: Motion description for video animation (max 150 chars)
```

## Test Quick Start

```bash
# Basic test run
python tests/test_gemini_service.py

# Expected: 6 tests, all pass, ~40 seconds total
```

## Performance Expectations

| Mode | Duration | Output | Use Case |
|------|----------|--------|----------|
| HIGH | 5-20s | Detailed JSON | Strategy, analysis, insights |
| LOW | 1-5s | Focused text | Captions, prompts, quick generation |

## Output Locations

All test outputs saved to: `backend/tests/outputs/gemini/`

```
gemini/
├── json_output_parsing_test.json          # JSON structure validation
├── high_thinking_sentiment_analysis.json  # Sentiment analysis results
├── high_thinking_strategy_creation.json   # 7-day strategy
├── low_thinking_caption_generation.txt    # Generated caption
├── performance_comparison.json            # Speed comparison
├── error_handling_empty_input.json        # Edge case handling
└── test_results_YYYYMMDD_HHMMSS.json     # Full test summary
```

## Common Issues

### API Key Not Set
```
❌ ERROR: GEMINI_API_KEY environment variable not set
```
**Fix:** `export GEMINI_API_KEY='your-key'`

### Slow Performance
- HIGH thinking taking > 20s: Normal during API load, check network
- LOW thinking taking > 5s: Check rate limits or network latency

### JSON Parsing Errors
- Should never happen (API returns clean JSON)
- If it does, check API response format changed

## Integration Example

```python
from services.gemini_service import GeminiService

gemini = GeminiService()

# Step 1: Analyze customer reviews (HIGH thinking)
sentiment = await gemini.analyze_customer_sentiment(
    reviews=customer_reviews,
    business_name=business_name
)

# Step 2: Create 7-day strategy (HIGH thinking)
strategy = await gemini.create_content_strategy(
    business_context=context,
    market_insights=insights,
    customer_sentiment=sentiment,
    past_performance=None,
    market_trends=trends
)

# Step 3: Generate content for each day (LOW thinking)
for day in strategy["days"]:
    caption = await gemini.generate_caption(day, context)
    image_prompt = await gemini.generate_image_prompt(day, context, favorites)

    if day["content_type"] == "video":
        motion_prompt = await gemini.generate_video_motion_prompt(day, business_name)
```

## Test Validation

All tests must pass with:
- ✅ JSON output is clean (no markdown wrappers)
- ✅ HIGH thinking: 5-20 seconds, detailed insights
- ✅ LOW thinking: 1-5 seconds, focused output
- ✅ Speed ratio: LOW is 1.5x+ faster than HIGH
- ✅ All required keys present in JSON responses
- ✅ Error handling: Service doesn't crash

## Next Steps

1. ✅ Verify all 6 tests pass
2. Run integration tests with full agent pipeline
3. Test with real business data
4. Verify quality scores meet thresholds (>75)
5. Test learning extraction and application

## Related Services

- **Vertex AI:** Grounded search, web scraping
- **MiniMax:** Image and video generation
- **Redis:** Data persistence and learning storage
- **LangGraph:** Agent orchestration and ReAct loop

## Documentation

- Full test guide: `backend/tests/README.md`
- Example outputs: `backend/tests/GEMINI_TEST_EXAMPLES.md`
- Test plan: `backend/tests/TEST_PLAN.md`

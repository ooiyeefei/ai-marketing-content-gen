# Gemini Service Test Examples

This document shows expected outputs for each test case to help verify correct behavior.

## Test 1: JSON Output Parsing

### Input:
```json
{
  "reviews": [
    {
      "rating": 5,
      "text": "Amazing coffee! The cold brew is incredible and the baristas are so friendly.",
      "author": "Emma S."
    }
  ],
  "business_name": "Test Coffee Shop"
}
```

### Expected Output:
```json
{
  "positive_themes": [
    "Excellent coffee quality",
    "Friendly staff",
    "Great cold brew selection"
  ],
  "negative_themes": [],
  "popular_items": [
    "Cold brew"
  ],
  "quotable_reviews": [
    "Amazing coffee! The cold brew is incredible"
  ],
  "content_opportunities": [
    "Highlight cold brew preparation process",
    "Feature barista interactions",
    "Behind-the-scenes coffee sourcing"
  ]
}
```

### Validation Checks:
- ✅ Response is Python `dict` (not string)
- ✅ No markdown wrappers (````json`)
- ✅ All keys present: positive_themes, negative_themes, popular_items, quotable_reviews, content_opportunities
- ✅ Arrays are not empty (at least positive_themes and content_opportunities)

---

## Test 2: HIGH Thinking - Sentiment Analysis

### Input:
```json
{
  "reviews": [
    {
      "rating": 5,
      "text": "The freshest sushi in San Francisco! The chef recommended the omakase and every piece was perfectly crafted. The spicy tuna roll is a MUST try!",
      "author": "Sarah M.",
      "date": "2025-01-15"
    },
    {
      "rating": 5,
      "text": "Incredible sake selection and the staff really knows their stuff. The yellowtail was buttery perfection. Only downside is it can get crowded on Friday nights.",
      "author": "David L.",
      "date": "2025-01-10"
    },
    {
      "rating": 4,
      "text": "Great food but service was a bit slow during dinner rush. The dragon roll is beautifully presented and tastes amazing. Would come back for lunch.",
      "author": "Jennifer K.",
      "date": "2025-01-08"
    },
    {
      "rating": 5,
      "text": "Authentic Japanese experience. The chef sources ingredients daily from the fish market. You can taste the quality. The miso soup is also excellent.",
      "author": "Michael T.",
      "date": "2025-01-05"
    },
    {
      "rating": 3,
      "text": "Food was good but pricey. Expected better ambiance for the price point. The salmon sashimi was fresh though.",
      "author": "Lisa P.",
      "date": "2025-01-03"
    }
  ],
  "business_name": "Sakura Sushi House"
}
```

### Expected Output:
```json
{
  "positive_themes": [
    "Fresh, high-quality ingredients",
    "Expert chef craftsmanship",
    "Authentic Japanese experience",
    "Knowledgeable staff",
    "Excellent sake selection",
    "Daily ingredient sourcing from fish market"
  ],
  "negative_themes": [
    "Crowded on Friday nights",
    "Slow service during dinner rush",
    "High prices",
    "Ambiance could be improved"
  ],
  "popular_items": [
    "Omakase experience",
    "Spicy tuna roll",
    "Yellowtail",
    "Dragon roll",
    "Sake selection",
    "Miso soup",
    "Salmon sashimi"
  ],
  "quotable_reviews": [
    "The freshest sushi in San Francisco!",
    "Every piece was perfectly crafted",
    "The yellowtail was buttery perfection",
    "You can taste the quality"
  ],
  "content_opportunities": [
    "Video series: Behind-the-scenes daily fish market sourcing",
    "Chef spotlight: Showcase omakase craftsmanship process",
    "Sake pairing guide: Leverage staff expertise",
    "Lunch special promotion to manage dinner crowds",
    "Instagram stories: Show ingredient quality and freshness",
    "Customer testimonial campaign using quotable reviews"
  ]
}
```

### Performance Expectations:
- ⏱️ Duration: 5-15 seconds (HIGH thinking mode)
- 🧠 Thinking Level: HIGH (complex analysis)
- 📊 Quality: Detailed insights with specific examples
- ✅ Actionable content opportunities based on feedback patterns

---

## Test 3: HIGH Thinking - Strategy Creation

### Input:
```json
{
  "business_context": {
    "business_name": "Sakura Sushi House",
    "industry": "restaurant",
    "brand_voice": "warm and storytelling"
  },
  "market_insights": {
    "market_gaps": [
      "Limited video content in local sushi scene",
      "No one showcasing ingredient sourcing"
    ],
    "positioning_opportunities": [
      "Authentic craftsmanship",
      "Sustainability story"
    ],
    "trending_topics": [
      "Behind-the-scenes content",
      "Chef collaborations"
    ]
  },
  "customer_sentiment": {
    "positive_themes": [
      "Fresh ingredients",
      "Authentic taste",
      "Chef expertise"
    ],
    "popular_items": [
      "Spicy tuna roll",
      "Omakase",
      "Sake selection"
    ]
  },
  "past_performance": {
    "winning_patterns": {
      "content_types": ["video > carousel > photo"],
      "best_posting_times": ["7-9 PM weekdays"]
    },
    "avoid_patterns": {
      "low_performers": ["generic food photos"]
    }
  },
  "market_trends": {
    "trending_searches": [
      "sushi near me",
      "omakase SF",
      "fresh sushi"
    ],
    "rising_topics": [
      "sustainable seafood",
      "chef stories"
    ]
  }
}
```

### Expected Output:
```json
{
  "days": [
    {
      "day": 1,
      "theme": "Behind the Scenes: Daily Market Sourcing",
      "content_type": "video",
      "message": "Show our chef's 5am journey to the fish market, selecting only the freshest ingredients",
      "hashtags": [
        "#SushiArt",
        "#FreshDaily",
        "#BehindTheScenes",
        "#SustainableSeafood"
      ],
      "cta": "Reserve your omakase experience today",
      "rationale": "Addresses market gap (no one showcasing sourcing) + customer positive theme (fresh ingredients) + proven format (video performs best)"
    },
    {
      "day": 2,
      "theme": "Chef Spotlight: The Art of Omakase",
      "content_type": "video",
      "message": "Watch our master chef craft each piece with precision and passion",
      "hashtags": [
        "#OmakaseSF",
        "#ChefLife",
        "#AuthenticJapanese",
        "#SushiCraftsmanship"
      ],
      "cta": "Book your omakase tonight",
      "rationale": "Popular item (omakase) + trending topic (chef stories) + positioning opportunity (authentic craftsmanship)"
    },
    {
      "day": 3,
      "theme": "Customer Favorite: Spicy Tuna Roll Perfection",
      "content_type": "carousel",
      "message": "Our most-loved roll: Fresh tuna, house-made spicy mayo, and perfect rice. See the layers.",
      "hashtags": [
        "#SpicyTuna",
        "#SushiLovers",
        "#CustomerFavorite",
        "#SFFoodie"
      ],
      "cta": "Try it today - You'll taste the difference",
      "rationale": "Popular item from reviews + carousel format (2nd best performer) + trending search (fresh sushi)"
    },
    {
      "day": 4,
      "theme": "Sake Pairing 101: Expert Recommendations",
      "content_type": "video",
      "message": "Our sake sommelier shares perfect pairings for your favorite rolls",
      "hashtags": [
        "#SakePairing",
        "#JapaneseCuisine",
        "#FoodAndDrink",
        "#ExpertTips"
      ],
      "cta": "Ask our staff for pairing recommendations",
      "rationale": "Customer positive theme (knowledgeable staff) + popular item (sake selection) + educational content (performs well)"
    },
    {
      "day": 5,
      "theme": "Sustainability Story: Our Ocean-to-Table Commitment",
      "content_type": "video",
      "message": "How we ensure every fish is sustainably sourced and traceable",
      "hashtags": [
        "#SustainableSeafood",
        "#OceanFriendly",
        "#ResponsibleSourcing",
        "#GreenRestaurant"
      ],
      "cta": "Dine with us guilt-free",
      "rationale": "Rising topic (sustainable seafood) + positioning opportunity (sustainability story) + differentiator from competitors"
    },
    {
      "day": 6,
      "theme": "Weekend Special: Limited Omakase Seats",
      "content_type": "carousel",
      "message": "This weekend only: Extended omakase menu with rare seasonal fish",
      "hashtags": [
        "#WeekendVibes",
        "#OmakaseNight",
        "#SeasonalSpecial",
        "#SushiSF"
      ],
      "cta": "Book now - Limited seats available",
      "rationale": "Popular item (omakase) + urgency driver + best posting time (Friday evening for weekend traffic)"
    },
    {
      "day": 7,
      "theme": "Customer Love: Your Reviews Inspire Us",
      "content_type": "carousel",
      "message": "Thank you for calling us 'The freshest sushi in SF!' Here's what else customers are saying...",
      "hashtags": [
        "#CustomerLove",
        "#Reviews",
        "#ThankYou",
        "#SFFoodie"
      ],
      "cta": "Share your experience with us",
      "rationale": "Build community + showcase quotable reviews + encourage user-generated content + end week on positive note"
    }
  ]
}
```

### Performance Expectations:
- ⏱️ Duration: 10-20 seconds (complex strategic reasoning)
- 🧠 Thinking Level: HIGH (synthesizing multiple data sources)
- 📊 Quality: Each day has clear rationale tied to data
- ✅ Strategy coherence: Days build on each other, addressing different aspects

---

## Test 4: LOW Thinking - Caption Generation

### Input:
```json
{
  "day_plan": {
    "day": 1,
    "theme": "Behind the Scenes: The Art of Sushi",
    "content_type": "video",
    "message": "Showcase our daily ingredient sourcing from local fish market",
    "hashtags": [
      "#SushiArt",
      "#FreshDaily",
      "#BehindTheScenes",
      "#SFFood"
    ],
    "cta": "Book your omakase experience today"
  },
  "business_context": {
    "business_name": "Sakura Sushi House",
    "brand_voice": "warm and storytelling",
    "industry": "restaurant"
  }
}
```

### Expected Output (Plain Text):
```
The best sushi starts long before the restaurant opens. 🌅

Every morning at 5am, our chef visits the local fish market, hand-selecting only the freshest catch. It's not just about quality—it's about honoring the craft and respecting the ingredients. Each piece of sushi you enjoy begins with this dedication.

Come experience the difference that fresh, carefully sourced ingredients make. Your perfect omakase moment awaits.

Book your omakase experience today → Link in bio

#SushiArt #FreshDaily #BehindTheScenes #SFFood
```

### Performance Expectations:
- ⏱️ Duration: 1-3 seconds (fast generation)
- 🧠 Thinking Level: LOW (template-based)
- 📝 Format: Plain text (not JSON)
- ✅ Contains: Hook, story, CTA, hashtags
- ✅ Length: 100-150 words
- ✅ Tone: Matches brand voice (warm and storytelling)

---

## Test 5: Performance Comparison

### Expected Results:

```json
{
  "low_thinking": {
    "duration_seconds": 2.1,
    "output_type": "string",
    "output_length": 487
  },
  "high_thinking": {
    "duration_seconds": 8.3,
    "output_type": "dict",
    "output_keys": [
      "positive_themes",
      "negative_themes",
      "popular_items",
      "quotable_reviews",
      "content_opportunities"
    ]
  },
  "analysis": {
    "speed_ratio": 3.95,
    "low_is_faster": true
  }
}
```

### Performance Benchmarks:
- ✅ LOW thinking: < 5 seconds
- ✅ HIGH thinking: 5-20 seconds
- ✅ Speed ratio: LOW is 1.5x+ faster than HIGH
- ✅ LOW produces focused output (caption text)
- ✅ HIGH produces deeper insights (structured analysis)

---

## Test 6: Error Handling

### Test Case: Empty Reviews

**Input:**
```json
{
  "reviews": [],
  "business_name": "Test Business"
}
```

**Expected Behavior:**

Option A - Graceful Handling (Valid):
```json
{
  "positive_themes": [],
  "negative_themes": [],
  "popular_items": [],
  "quotable_reviews": [],
  "content_opportunities": []
}
```

Option B - Error Raised (Also Valid):
```python
ValueError: Cannot analyze sentiment with empty reviews list
```

### Validation:
- ✅ Service doesn't crash
- ✅ Either returns empty structure OR raises appropriate error
- ✅ Error message is clear and actionable
- ✅ Service remains stable after error

---

## Running the Tests

```bash
cd backend
python tests/test_gemini_service.py
```

### Expected Console Output:

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

======================================================================
🧪 Gemini HIGH Thinking - Sentiment Analysis
======================================================================
📊 Analyzing 5 customer reviews...
🧠 Thinking Mode: HIGH (complex analysis)

📋 Sample Output:
  Positive Themes: ['Fresh, high-quality ingredients', 'Expert chef craftsmanship', 'Authentic Japanese experience']
  Popular Items: ['Omakase experience', 'Spicy tuna roll', 'Yellowtail']
  Content Opportunities: 6 found
   📁 Saved output: backend/tests/outputs/gemini/high_thinking_sentiment_analysis.json
✅ Gemini HIGH Thinking - Sentiment Analysis - PASSED (8.72s)

======================================================================
🧪 Gemini HIGH Thinking - Strategy Creation
======================================================================
🎯 Creating 7-day content strategy...
🧠 Thinking Mode: HIGH (strategic planning)

📅 Sample Days:
  Day 1: Behind the Scenes: Daily Market Sourcing
    Type: video
    Rationale: Addresses market gap (no one showcasing sourcing) + customer positive ...
  Day 2: Chef Spotlight: The Art of Omakase
    Type: video
    Rationale: Popular item (omakase) + trending topic (chef stories) + positioning...
  Day 3: Customer Favorite: Spicy Tuna Roll Perfection
    Type: carousel
    Rationale: Popular item from reviews + carousel format (2nd best performer) + tre...
   📁 Saved output: backend/tests/outputs/gemini/high_thinking_strategy_creation.json
✅ Gemini HIGH Thinking - Strategy Creation - PASSED (12.45s)

======================================================================
🧪 Gemini LOW Thinking - Caption Generation
======================================================================
✍️  Generating Instagram caption...
🧠 Thinking Mode: LOW (fast generation)
📝 Theme: Behind the Scenes: The Art of Sushi

📝 Generated Caption:
----------------------------------------------------------------------
The best sushi starts long before the restaurant opens. 🌅

Every morning at 5am, our chef visits the local fish market, hand-selecting only the freshest catch. It's not just about quality—it's about honoring the craft and respecting the ingredients. Each piece of sushi you enjoy begins with this dedication.

Come experience the difference that fresh, carefully sourced ingredients make. Your perfect omakase moment awaits.

Book your omakase experience today → Link in bio

#SushiArt #FreshDaily #BehindTheScenes #SFFood
----------------------------------------------------------------------
  Word Count: 78
  Has Hashtags: ✓
   📁 Saved output: backend/tests/outputs/gemini/low_thinking_caption_generation.txt
✅ Gemini LOW Thinking - Caption Generation - PASSED (2.18s)

======================================================================
🧪 Gemini Performance Comparison
======================================================================
⚡ Testing LOW thinking mode...
🧠 Testing HIGH thinking mode...

📊 Performance Results:
  LOW Thinking:  2.1s
  HIGH Thinking: 8.3s
  Speed Ratio:   3.9x
  LOW is faster: ✓
   📁 Saved output: backend/tests/outputs/gemini/performance_comparison.json
✅ Gemini Performance Comparison - PASSED (10.40s)

======================================================================
🧪 Gemini Error Handling
======================================================================
🔧 Testing error handling with empty reviews...

✅ Service raised appropriate error: ValueError
✅ Gemini Error Handling - PASSED (0.05s)

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

---

## Success Criteria

All tests MUST pass with these criteria:

1. **JSON Output Parsing:**
   - Response is dict, not string
   - No markdown wrappers
   - All required keys present

2. **HIGH Thinking - Sentiment Analysis:**
   - Duration: 5-15 seconds
   - Detailed insights with examples
   - Arrays not empty

3. **HIGH Thinking - Strategy Creation:**
   - Duration: 10-20 seconds
   - 7 days with full structure
   - Each day has rationale

4. **LOW Thinking - Caption Generation:**
   - Duration: 1-3 seconds
   - Plain text format
   - Has hashtags and CTA

5. **Performance Comparison:**
   - LOW is 1.5x+ faster than HIGH
   - Both complete successfully

6. **Error Handling:**
   - Service doesn't crash
   - Raises appropriate errors

If any test fails, check:
1. API key is set correctly
2. Network connection is stable
3. API quota not exceeded
4. Service implementation matches expected interface

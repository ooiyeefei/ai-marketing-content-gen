# BrandMind AI - Demo & Testing Guide

## Overview

This guide walks you through running and testing the **truly autonomous, self-improving AI agent system** for social media campaign generation.

**What makes this autonomous?**
- Agents make decisions based on ReAct pattern (Reason → Act → Observe)
- Quality evaluation triggers automatic regeneration (no human intervention)
- Agents adapt when APIs fail (AGI fallback for unclaimed businesses)
- System learns from each campaign to improve future performance

---

## Prerequisites

### Required API Keys

You **MUST** have these API keys to run the demo:

1. **Gemini API Key** - Primary AI for strategy and content
   - Get from: https://aistudio.google.com/app/apikey

2. **AGI API Key** - Web research and competitor analysis
   - Get from: https://agi.tech/

3. **MiniMax API Key** - Image and video generation
   - Get from: https://www.minimaxi.com/

4. **Convex Database URL** - Campaign data storage
   - Get from: https://dashboard.convex.dev/

5. **Cloudflare R2 Credentials** - Media file storage
   - Get from: https://dash.cloudflare.com/

### Optional API Keys

These are **NOT required** for demo (AGI API fallback handles missing data):

- Google My Business API Key (for claimed businesses)
- Facebook Access Token (for past performance analysis)
- Instagram Access Token (for engagement insights)
- Google Trends API Key (for market trends)

---

## Setup Instructions

### Step 1: Clone and Navigate

```bash
cd backend
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Expected output:
```
Successfully installed fastapi-0.115.0 uvicorn-0.32.0 httpx-0.27.2 ...
```

### Step 4: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:

```bash
# REQUIRED
GEMINI_API_KEY=your-gemini-api-key-here
AGI_API_KEY=your-agi-api-key-here
MINIMAX_API_KEY=your-minimax-api-key-here
CONVEX_URL=https://your-deployment.convex.cloud
CLOUDFLARE_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET=your-bucket-name

# OPTIONAL (can leave blank)
GOOGLE_MY_BUSINESS_API_KEY=
FACEBOOK_ACCESS_TOKEN=
INSTAGRAM_ACCESS_TOKEN=
```

**Important:**
- Replace `your-*` placeholders with actual values
- Social media tokens are optional (AGI fallback handles missing data)
- NEVER commit `.env` file to git (already in `.gitignore`)

### Step 5: Verify Convex Schema

Make sure your Convex deployment has the required schema:

```bash
cd convex
npx convex dev  # This will push schema to Convex
```

Required tables:
- `campaigns` - Campaign metadata and progress tracking
- `research` - Agent 1 outputs (business context, competitors)
- `analytics` - Agent 2 outputs (reviews, sentiment, insights)
- `creative` - Agent 3 outputs (7-day content calendar)
- `learnings` - Self-improvement data extracted after campaigns

---

## Running the Server

### Option 1: Using Run Script (Recommended)

```bash
chmod +x run.sh
./run.sh
```

### Option 2: Manual Start

```bash
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

**Server is ready when you see:** `Uvicorn running on http://0.0.0.0:8080`

---

## Testing the System

### Test 1: Health Check

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2025-01-22T12:00:00Z"
}
```

---

### Test 2: Generate Campaign (Full Demo)

#### Request

```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "business_url": "https://www.bluebottlecoffee.com",
    "competitor_urls": [
      "https://www.starbucks.com",
      "https://www.intelligentsiacoffee.com"
    ]
  }'
```

**Note:** You can omit `competitor_urls` - Agent 1 will autonomously discover competitors using AGI API.

#### Expected Response

```json
{
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Campaign generation started. Use /api/campaigns/{campaign_id}/progress to track."
}
```

---

### Test 3: Monitor Real-Time Progress

```bash
curl http://localhost:8080/api/campaigns/550e8400-e29b-41d4-a716-446655440000/progress
```

#### Progress Phases

**Phase 1: Agent 1 - Intelligence & Research (0-25%)**

```json
{
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": 15,
  "current_agent": "research",
  "message": "Analyzing business context with AGI API..."
}
```

Agent 1 Tasks:
- Scrapes business website (AGI API)
- Discovers competitors autonomously if not provided
- Analyzes competitor strategies
- Identifies market trends

**Phase 2: Agent 2 - Analytics & Feedback (25-50%)**

```json
{
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": 35,
  "current_agent": "strategy",
  "message": "Analyzing customer sentiment with Gemini HIGH thinking..."
}
```

Agent 2 Tasks:
- Fetches Google reviews (GMB API or AGI scraping fallback)
- Analyzes sentiment with Gemini HIGH thinking mode
- Fetches Facebook/Instagram insights (optional, skips if unavailable)
- Retrieves market trends (Google Trends or AGI fallback)

**Phase 3: Agent 3 - Creative Generation (50-100%)**

```json
{
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": 75,
  "current_agent": "creative",
  "message": "Generating Day 4 content: images and video..."
}
```

Agent 3 Tasks:
- Creates 7-day content strategy (Gemini HIGH)
- For each day (1-7):
  - Generates caption (Gemini LOW, high-throughput)
  - Generates image prompt (Gemini LOW)
  - Creates 2 images (MiniMax)
  - Creates video for days 1, 4, 7 (MiniMax)
- Extracts learning data for self-improvement

**Campaign Complete (100%)**

```json
{
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "current_agent": null,
  "message": "Campaign generation completed successfully"
}
```

---

### Test 4: Retrieve Campaign Results

```bash
curl http://localhost:8080/api/campaigns/550e8400-e29b-41d4-a716-446655440000
```

#### Response Structure

```json
{
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "business_name": "Blue Bottle Coffee",
  "business_summary": "Specialty coffee roaster and retailer...",

  "research": {
    "business_context": {
      "name": "Blue Bottle Coffee",
      "industry": "Specialty Coffee",
      "mission": "We're here to share delicious coffee...",
      "target_audience": "Coffee enthusiasts, professionals, millennials",
      "unique_value_proposition": "Single-origin beans, precision brewing..."
    },
    "competitors": [
      {
        "name": "Starbucks",
        "url": "https://www.starbucks.com",
        "positioning": "Mainstream coffee chain",
        "strengths": ["Brand recognition", "Global reach"],
        "weaknesses": ["Less focus on quality"]
      }
    ],
    "market_trends": [
      "Cold brew and nitro coffee growth",
      "Sustainability focus in coffee sourcing",
      "Home brewing equipment popularity"
    ]
  },

  "analytics": {
    "reviews_summary": {
      "overall_rating": 4.5,
      "total_reviews": 234,
      "sources": ["Google Maps", "Yelp"]
    },
    "sentiment_analysis": {
      "positive_themes": ["Quality beans", "Knowledgeable staff"],
      "negative_themes": ["High prices", "Limited locations"],
      "customer_pain_points": ["Accessibility", "Cost"],
      "recommendations": ["Highlight quality", "Address pricing perception"]
    },
    "social_insights": {
      "facebook": null,  // Optional - skipped if token unavailable
      "instagram": null  // Optional - skipped if token unavailable
    }
  },

  "content_calendar": [
    {
      "day": 1,
      "theme": "Brand Introduction",
      "caption": "☕ Discover the art of specialty coffee at Blue Bottle...",
      "caption_length": 187,
      "hashtags": ["#SpecialtyCoffee", "#BlueBottle"],
      "images": [
        "https://pub-abc123.r2.dev/campaigns/550e8400/day1_image1.jpg",
        "https://pub-abc123.r2.dev/campaigns/550e8400/day1_image2.jpg"
      ],
      "video": "https://pub-abc123.r2.dev/campaigns/550e8400/day1_video.mp4"
    },
    // Days 2-7...
  ],

  "learnings": {
    "what_worked": [
      "Highlighting single-origin sourcing resonates with audience",
      "Visual content with brewing process drives engagement"
    ],
    "improvements_for_next_campaign": [
      "Address pricing perception proactively",
      "Emphasize accessibility through online ordering"
    ],
    "quality_scores": {
      "average_caption_quality": 87,
      "average_image_prompt_quality": 91,
      "campaign_coherence": 94
    }
  }
}
```

---

## Autonomous Behavior Verification

### How to Verify Agents Are Truly Autonomous

#### 1. **Dynamic Decision Making**

Test with minimal input:

```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "business_url": "https://www.airbnb.com"
  }'
```

**Watch for:**
- Agent 1 autonomously discovers competitors (Booking.com, VRBO)
- Agent 1 decides which data sources to query based on available data
- Agent 2 chooses AGI scraping when GMB API unavailable

**Logs to check:**
```
INFO: 🤖 Agent 1 autonomously discovered 3 competitors
INFO: 📍 GMB API unavailable, switching to AGI scraping fallback
INFO: 🔍 Using AGI API to scrape Google Maps reviews
```

#### 2. **Quality-Driven Regeneration**

Agent 3 evaluates its own content quality and regenerates if needed.

**Watch for in logs:**
```
INFO: 📊 Caption quality score: 45 (threshold: 75)
INFO: 🔄 Quality below threshold, regenerating with different approach...
INFO: ✓ Regenerated caption quality: 88
```

**Verify:**
- Check `generation_attempts` in campaign response
- If quality was low, `generation_attempts > 1`
- Final content always meets quality threshold

#### 3. **Self-Improvement Between Campaigns**

Run two campaigns sequentially:

**Campaign 1:**
```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{"business_url": "https://www.bluebottlecoffee.com"}'
```

Wait for completion, then:

**Campaign 2:**
```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{"business_url": "https://www.intelligentsiacoffee.com"}'
```

**Verify learning application:**
- Check `learnings/past_campaigns.json` file was created after Campaign 1
- Campaign 2 logs show: `✓ Loaded learnings from 1 past campaign(s)`
- Campaign 2 quality scores > Campaign 1 quality scores

#### 4. **Adaptive Error Handling**

Test with invalid/unavailable APIs:

1. Remove FACEBOOK_ACCESS_TOKEN from `.env`
2. Run campaign

**Expected behavior:**
```
WARN: ⚠ Facebook API token unavailable, skipping past performance analysis
INFO: ✓ Continuing campaign without Facebook data
```

**Verify:**
- Campaign completes successfully
- No Facebook data in `social_insights`
- Agent adapts by using available data sources

---

## Common Issues & Solutions

### Issue 1: "CONVEX_URL environment variable not set"

**Solution:**
```bash
# Check .env file exists
ls backend/.env

# Verify CONVEX_URL is set
grep CONVEX_URL backend/.env
```

### Issue 2: "Failed to connect to AGI API"

**Possible causes:**
1. Invalid AGI_API_KEY
2. Network connectivity issues
3. AGI API rate limit exceeded

**Solution:**
```bash
# Test AGI API directly
curl -H "Authorization: Bearer YOUR_AGI_KEY" \
  https://api.agi.tech/v1/health
```

### Issue 3: Campaign stuck at 50%

**Possible cause:** MiniMax API image generation taking longer than expected

**Solution:**
- Check logs: `tail -f backend/logs/app.log`
- Wait up to 5 minutes (image generation can take 2-3 minutes per image)
- If truly stuck, check MiniMax API status

### Issue 4: "No past learnings yet"

**Expected behavior:** This is normal for first campaign.

**How to verify learning works:**
1. Complete first campaign
2. Check `backend/learnings/past_campaigns.json` was created
3. Run second campaign
4. Verify logs show: `✓ Loaded learnings from 1 past campaign(s)`

---

## Performance Benchmarks

### Expected Timing (Real APIs, No Mocks)

| Phase | Agent | Duration | Operations |
|-------|-------|----------|------------|
| 0-25% | Research | 2-4 min | 5-10 AGI API calls |
| 25-50% | Strategy | 3-5 min | Gemini HIGH (2x), Social APIs |
| 50-100% | Creative | 10-15 min | 14 images + 3 videos (MiniMax) |

**Total:** ~15-25 minutes for complete campaign

### Why This Is Slow (And That's Okay for Demo)

- **No Mocks:** All API calls are real (AGI, Gemini, MiniMax)
- **Quality-Driven:** Agent regenerates content if quality < 75
- **Video Generation:** MiniMax video takes ~3-5 minutes each
- **Autonomous Decisions:** Agent reasons about next steps (adds thinking time)

**This proves the system is truly autonomous with real data.**

---

## Understanding the Logs

### Agent 1 (Research) Logs

```
INFO: 🚀 Starting Agent 1: Intelligence & Research
INFO: 📊 Extracting business context from https://www.bluebottlecoffee.com
INFO: ✓ Business context extracted: Blue Bottle Coffee (Specialty Coffee)
INFO: 🔍 Autonomously discovering competitors...
INFO: ✓ Discovered 3 competitors: Starbucks, Intelligentsia, Verve
INFO: 📈 Analyzing market trends with AGI API...
INFO: ✓ Agent 1 completed: Stored research in Convex
```

### Agent 2 (Strategy) Logs

```
INFO: 🚀 Starting Agent 2: Analytics & Feedback
INFO: 📍 Attempting GMB API for Blue Bottle Coffee
WARN: ⚠ GMB API unavailable (business may not be claimed)
INFO: 🔍 Using AGI API fallback to scrape public reviews
INFO: ✓ Scraped 47 reviews from Google Maps, Yelp
INFO: 🧠 Analyzing sentiment with Gemini HIGH thinking mode...
INFO: ✓ Sentiment analysis complete: 78% positive
INFO: ✓ Agent 2 completed: Stored analytics in Convex
```

### Agent 3 (Creative) Logs

```
INFO: 🚀 Starting Agent 3: Creative Generation
INFO: 🎯 Creating 7-day content strategy...
INFO: ✓ Strategy created (Gemini HIGH thinking)
INFO: 📝 Day 1: Generating caption...
INFO: 📊 Caption quality score: 88 ✓
INFO: 🎨 Day 1: Generating 2 images (MiniMax)...
INFO: ⏳ Image generation task created: task_abc123
INFO: ⏳ Polling MiniMax for completion...
INFO: ✓ Images generated successfully
INFO: 🎬 Day 1: Generating video (MiniMax)...
INFO: ✓ Video generated: https://pub-abc.r2.dev/campaigns/550e8400/day1_video.mp4
INFO: 📅 Day 1 complete, moving to Day 2...
... [Days 2-7]
INFO: 📚 Extracting learning data...
INFO: ✓ Agent 3 completed: Campaign ready!
```

---

## Hackathon Demo Script

### 5-Minute Demo Flow

**1. Introduction (30 seconds)**
> "We built a truly autonomous AI agent system for social media campaigns. The agents make decisions, evaluate their own work, and learn from each campaign."

**2. Show Autonomy (2 minutes)**

Terminal 1: Start server
```bash
./run.sh
```

Terminal 2: Minimal input demo
```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{"business_url": "https://www.airbnb.com"}'
```

> "Notice: We only provided a URL. The agent will autonomously discover competitors, decide data sources, and adapt when APIs fail."

**3. Monitor Progress (1 minute)**

```bash
# Show real-time progress
watch -n 2 'curl -s http://localhost:8080/api/campaigns/CAMPAIGN_ID/progress | jq'
```

Point out:
- Agent switching (Research → Strategy → Creative)
- Dynamic decisions in logs
- Real API calls (no mocks)

**4. Show Results (1 minute)**

```bash
curl http://localhost:8080/api/campaigns/CAMPAIGN_ID | jq '.content_calendar[0]'
```

Highlight:
- Complete 7-day campaign
- All images/videos hosted on R2
- Learning data extracted for next campaign

**5. Self-Improvement Demo (30 seconds)**

Show `learnings/past_campaigns.json`:
```bash
cat backend/learnings/past_campaigns.json
```

> "After each campaign, agents extract learnings. Next campaign uses these insights to improve quality."

---

## Next Steps

### For Production Deployment

1. **Add Authentication**
   - JWT tokens for `/api/generate` endpoint
   - API key validation

2. **Implement Rate Limiting**
   - Prevent API abuse
   - Queue campaigns if concurrent limit exceeded

3. **Add Webhook Notifications**
   - Notify client when campaign completes
   - Real-time updates via WebSocket

4. **Vector Database for Learnings**
   - Replace simple JSON file with RedisVL
   - Semantic search for relevant past learnings

5. **A/B Testing Framework**
   - Test multiple caption variants
   - Track engagement metrics
   - Auto-select best performing content

### For Enhanced Autonomy

1. **Automated Publishing**
   - Agent posts content directly to social media
   - Monitors engagement metrics
   - Adjusts strategy based on performance

2. **Continuous Learning Loop**
   - Fetch engagement data after posts go live
   - Analyze what content performed best
   - Apply learnings to future campaigns

3. **Multi-Modal Understanding**
   - Agent analyzes customer photos with vision API
   - Generates content matching visual style
   - Creates videos from product images

---

## API Reference

### POST /api/generate

Create new campaign.

**Request Body:**
```json
{
  "business_url": "https://example.com",
  "competitor_urls": ["https://competitor1.com"],  // Optional
  "facebook_page_id": "123456789",  // Optional
  "instagram_account_id": "987654321"  // Optional
}
```

**Response:**
```json
{
  "campaign_id": "uuid",
  "status": "processing",
  "message": "Campaign generation started"
}
```

### GET /api/campaigns/{campaign_id}/progress

Get real-time campaign progress.

**Response:**
```json
{
  "campaign_id": "uuid",
  "status": "running" | "completed" | "failed",
  "progress": 0-100,
  "current_agent": "research" | "strategy" | "creative" | null,
  "message": "Current operation description"
}
```

### GET /api/campaigns/{campaign_id}

Get complete campaign results.

**Response:** See "Test 4: Retrieve Campaign Results" above

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "ISO-8601 datetime"
}
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Server (main.py)                  │
│                     Port 8080, Async/Await                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ orchestrates
                          ▼
┌─────────────────────────────────────────────────────────────┐
│          Campaign Orchestrator (orchestrator.py)             │
│     Sequential execution: Agent 1 → Agent 2 → Agent 3       │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Agent 1    │  │   Agent 2    │  │   Agent 3    │
│  Research    │  │  Strategy    │  │  Creative    │
│   (0-25%)    │  │  (25-50%)    │  │  (50-100%)   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       │ uses            │ uses            │ uses
       ▼                 ▼                 ▼
┌──────────────────────────────────────────────────────┐
│                   Service Layer                       │
├──────────────────────────────────────────────────────┤
│ • AGI Service (web research, competitor discovery)   │
│ • Gemini Service (HIGH thinking: analysis,           │
│                   LOW thinking: content generation)  │
│ • MiniMax Service (image & video generation)         │
│ • Social Service (GMB, Facebook, Instagram)          │
│ • Convex Service (campaign data storage)             │
│ • R2 Service (media file storage)                    │
└──────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Enable Debug Logging

Edit `.env`:
```bash
LOG_LEVEL=DEBUG
```

Restart server:
```bash
./run.sh
```

### Check Detailed Logs

```bash
tail -f backend/logs/app.log
```

### Verify Dependencies

```bash
pip list | grep -E "fastapi|httpx|google-genai|convex|boto3"
```

### Test Individual Services

```bash
# Test Gemini
python -c "from services.gemini_service import GeminiService; s = GeminiService(); print('✓ Gemini OK')"

# Test AGI
python -c "from services.agi_service import AGIService; import asyncio; s = AGIService(); print('✓ AGI OK')"

# Test MiniMax
python -c "from services.minimax_service import MiniMaxService; s = MiniMaxService(); print('✓ MiniMax OK')"
```

---

## Support

For issues or questions:
1. Check logs: `tail -f backend/logs/app.log`
2. Verify `.env` configuration
3. Test individual services (see Troubleshooting)
4. Review API documentation:
   - AGI: https://docs.agi.tech
   - Gemini: https://ai.google.dev/docs
   - MiniMax: https://platform.minimax.io/docs

---

## License

This project is for hackathon demonstration purposes.

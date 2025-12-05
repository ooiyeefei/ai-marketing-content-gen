# BrandMind AI - Autonomous Marketing Content Generation System

> From URL to 7-day campaign: AI agents that autonomously research your business, analyze competitors, and generate complete branded social media content with AI-generated images and videos.

## Overview

BrandMind AI is an autonomous production-grade multi-agent system that transforms a single website URL into a complete 7-day social media campaign with:
- Autonomous business discovery and brand analysis
- Competitor research and industry trend analysis
- Data-driven 7-day content strategy
- AI-generated captions, images, and videos (MiniMax)
- Real-time database with Convex
- Cloud storage with Cloudflare R2

**Key Innovation**: Zero user input required beyond URL - agents autonomously discover everything about your business, brand voice, products, and market positioning.

## Architecture

### 3-Agent Production System

1. **Agent 1: Research & Discovery** (`backend/agents/research_agent.py`)
   - Autonomous website scraping and analysis
   - Product image extraction and business context analysis
   - Brand voice extraction from website content
   - Competitor research and analysis
   - Industry trend discovery

2. **Agent 2: Content Strategy** (`backend/agents/content_strategist.py`)
   - Data-driven 7-day content strategy generation
   - Competitor insights integration
   - Optimal posting time recommendations
   - Platform-specific content optimization

3. **Agent 3: Creative Generation** (`backend/agents/creative_agent.py`)
   - Caption generation with Gemini
   - **Image generation with MiniMax** (text-to-image with subject reference)
   - **Video generation with MiniMax** (image-to-video)
   - Cloudflare R2 asset storage

### Tech Stack

**Frontend**:
- Next.js 14 with TypeScript
- Tailwind CSS
- Real-time progress tracking
- Campaign results dashboard

**Backend**:
- FastAPI with async/await
- Pydantic v2 for type safety
- Convex real-time database

**AI & Media Generation**:
- **Gemini** - AI reasoning and content generation
- **MiniMax** - Image generation (text-to-image with subject reference) and video generation (image-to-video)
- **AGI.tech** - Intelligent web research and competitor analysis

**Storage & Database**:
- **Convex** - Real-time database for campaign data
- **Cloudflare R2** - S3-compatible object storage for generated media

## Prerequisites

- Python 3.11+
- Node.js 18+
- API keys for: Gemini, MiniMax, AGI.tech, Convex, Cloudflare R2

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/ooiyeefei/ai-marketing-content-gen.git
cd ai-marketing-content-gen
```

### 2. Configure Environment Variables

```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

**Required Environment Variables**:

```bash
# AI Services
GEMINI_API_KEY=your-gemini-api-key
AGI_API_KEY=your-agi-api-key

# MiniMax (Image & Video Generation)
MINIMAX_API_KEY=your-minimax-jwt-token
MINIMAX_GROUP_ID=your-minimax-group-id

# Database (Convex)
CONVEX_URL=https://your-project.convex.cloud
CONVEX_API_KEY=your-convex-api-key

# Storage (Cloudflare R2)
CLOUDFLARE_ACCOUNT_ID=your-cloudflare-account-id
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
R2_BUCKET_NAME=your-bucket-name
```

### 3. Install Backend Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 5. Run Backend

```bash
cd backend
source venv/bin/activate
python main.py
# Server runs on http://localhost:8080
```

### 6. Run Frontend (in new terminal)

```bash
cd frontend
npm run dev
# App runs on http://localhost:3000
```

### 7. Test the System

1. Open http://localhost:3000
2. Enter a business website URL (e.g., https://www.example-business.com)
3. Optionally add competitor URLs
4. Click "Generate 7-Day Campaign"
5. Watch agents work in real-time
6. View your 7-day campaign with captions, images, and videos!

## How It Works

### 3-Agent Autonomous Pipeline

**Input**: Business Website URL (+ optional competitor URLs)

**Agent 1: Research (0-33%)**
- Scrapes website and extracts:
  - Business name, industry, products
  - Brand voice from website copy
  - Product images (filtered for quality)
  - Target audience
- Researches competitor websites (if provided)
- Analyzes industry trends
- Stores all findings in Convex database

**Agent 2: Strategy (33-66%)**
- Analyzes research findings
- Incorporates competitor insights and trends
- Generates 7-day content calendar with:
  - Daily themes (e.g., "Behind the scenes", "Product showcase")
  - Content types (image/video/carousel)
  - Image/video concepts
  - Optimal posting times
  - CTAs and hashtag recommendations

**Agent 3: Creative (66-100%)**
- Generates captions with Gemini:
  - Hook, body, CTA structure
  - Brand voice consistency
  - Hashtag integration
- **Generates images with MiniMax**:
  - Text-to-image with subject reference URLs
  - Product images as style references
  - 1:1 aspect ratio for Instagram
- **Generates videos with MiniMax**:
  - Image-to-video generation
  - 5-second video clips from generated images
- Uploads all assets to Cloudflare R2
- Stores content in Convex database

**Output**:
- 7 days of complete social media content
- Captions, AI-generated images, AI-generated videos
- Hashtags and CTAs
- Downloadable assets from R2

## MiniMax Integration

BrandMind AI uses MiniMax for both image and video generation:

### Image Generation
```python
# Text-to-image with optional subject reference
images = await minimax.generate_images(
    prompt="Professional product photo of coffee beans...",
    subject_reference_url="https://r2.example.com/product-image.jpg",
    num_images=2,
    aspect_ratio="1:1"
)
```

### Video Generation
```python
# Image-to-video generation
video = await minimax.generate_video(
    prompt="Smooth camera pan across the coffee shop...",
    first_frame_image=image_bytes  # Generated image as first frame
)
```

## Project Structure

```
ai-marketing-content-gen/
├── backend/
│   ├── agents/
│   │   ├── research_agent.py         # Agent 1: Autonomous research
│   │   ├── content_strategist.py     # Agent 2: Content strategy
│   │   └── creative_agent.py         # Agent 3: MiniMax image/video generation
│   ├── services/
│   │   ├── gemini_service.py         # Google Gemini API
│   │   ├── minimax_service.py        # MiniMax image & video generation
│   │   ├── agi_service.py            # AGI.tech web research
│   │   ├── convex_service.py         # Convex database
│   │   └── r2_service.py             # Cloudflare R2 storage
│   ├── models.py                      # Pydantic data models
│   ├── orchestrator.py                # 3-agent coordinator
│   ├── main.py                        # FastAPI server
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx                   # Input form
│   │   └── gallery/page.tsx           # Campaign results
│   ├── components/
│   │   ├── InputForm.tsx              # Business URL input
│   │   ├── LoadingProgress.tsx        # Real-time progress
│   │   └── ContentCard.tsx            # Day content display
│   ├── lib/
│   │   └── api.ts                     # Backend API client
│   └── types/
│       └── index.ts                   # TypeScript types
├── convex/
│   ├── schema.ts                      # Database schema
│   ├── campaigns.ts                   # Campaign mutations/queries
│   ├── research.ts                    # Research data storage
│   └── content.ts                     # Content storage
└── README.md
```

## API Endpoints

### Backend (FastAPI)

**POST /api/generate**
- Input: `{ business_url: string, competitor_urls?: string[] }`
- Returns: `{ success: boolean, campaign_id: string, message: string }`
- Triggers: Background task that runs all 3 agents

**GET /api/campaigns/{campaign_id}**
- Returns: Full campaign object with progress and results
- Updates in real-time as agents complete work

**GET /api/campaigns/{campaign_id}/progress**
- Returns: Real-time progress updates for the campaign

**GET /api/campaigns**
- Returns: List of all campaigns

## Development

### Running Tests

```bash
cd backend
pytest
```

### Code Formatting

```bash
cd backend
black .
ruff check .
```

### Docker Deployment

```bash
# Backend
cd backend
docker build -t brandmind-backend .
docker run -p 8080:8080 --env-file .env brandmind-backend

# Frontend
cd frontend
docker build -t brandmind-frontend .
docker run -p 3000:3000 brandmind-frontend
```

## Troubleshooting

**MiniMax Image/Video Generation Issues**:
- Verify MINIMAX_API_KEY is a valid JWT token
- Check MINIMAX_GROUP_ID is correct
- API has rate limits - wait between requests

**AGI.tech Connection Issues**:
- Check API key is valid
- Sessions may timeout after 180s for complex scraping

**Convex Database Issues**:
- Ensure CONVEX_URL and CONVEX_API_KEY are correct
- Check Convex dashboard for schema deployment status

**R2 Storage Issues**:
- Verify Cloudflare account ID and R2 credentials
- Check bucket name and permissions

## Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details

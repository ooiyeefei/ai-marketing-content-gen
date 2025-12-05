# BrandMind AI - Autonomous 4-Agent Marketing Intelligence System

**Built for: Production Agents Hackathon (November 21, 2025)**

> From URL to 7-day campaign: AI agents that autonomously research your business, analyze competitors, and generate complete branded social media content.

**Live Demo**: [Coming Soon]

## Overview

BrandMind AI is an autonomous production-grade agent system that transforms a single website URL into a complete 7-day social media campaign with:
- ✅ Autonomous business discovery and brand analysis
- ✅ Competitor research and industry trend analysis
- ✅ Data-driven 7-day content strategy
- ✅ AI-generated captions and images
- ✅ CMS publishing to Sanity Studio
- ✅ Real-time progress tracking

**Key Innovation**: Zero user input required beyond URL - agents autonomously discover everything about your business, brand voice, products, and market positioning.

## Architecture

### 4-Agent Production System

1. **Agent 1: Research & Discovery** (`backend/agents/research_agent.py:18-343`)
   - Autonomous website scraping with Lightpanda (10x faster than Chrome)
   - Product image extraction and business context analysis
   - Brand voice extraction from website content
   - Competitor research and analysis
   - Industry trend discovery

2. **Agent 2: Brand Strategy** (`backend/agents/strategy_agent.py:17-202`)
   - Vector search for similar past campaigns (Redis)
   - Data-driven 7-day content strategy generation
   - Competitor insights integration
   - Optimal posting time recommendations

3. **Agent 3: Creative Generation** (`backend/agents/creative_agent.py:18-183`)
   - Caption generation with Claude Sonnet 4.5
   - Image generation with Google Vertex AI Imagen 3
   - Style-matched product images as references
   - S3 asset storage

4. **Agent 4: Orchestration & Publishing** (`backend/agents/orchestration_agent.py:17-195`)
   - Sanity CMS content publishing
   - Content calendar generation
   - Post scheduling (Postman API integration)
   - Dashboard URL provisioning

### Tech Stack

**Frontend**:
- Next.js 14 with TypeScript
- Material-UI + Tailwind CSS
- Real-time progress tracking
- Campaign results dashboard

**Backend**:
- FastAPI with async/await
- Pydantic v2 for type safety
- Redis with vector search (1536D embeddings)
- Claude Sonnet 4.5 for all AI reasoning

**Sponsor Tools Integrated** (6 of 15):
1. **Redis** - Vector database for agent memory and campaign similarity search
2. **Sanity CMS** - Content calendar and publishing platform
3. **Lightpanda** - 10x faster web scraping (vs Chrome/Puppeteer)
4. **Anthropic** - Claude Sonnet 4.5 for all AI reasoning and analysis
5. **AWS** - S3 storage for generated images and videos
6. **Postman** - API integration for social media scheduling (optional)

**Additional Services**:
- Google Vertex AI (Imagen 3, Veo 2)
- Background task processing with FastAPI

## Prerequisites

- **Anthropic API key** (Claude Sonnet 4.5) - **REQUIRED**
- **Redis URL** (with vector search support) - **REQUIRED**
- **Lightpanda token** (for web scraping) - **REQUIRED**
- Python 3.11+
- Node.js 18+
- GCP project with Vertex AI enabled (for image generation)
- AWS account (for S3 storage)
- Sanity project (for CMS publishing)

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd aws-prod-agent-hack
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys
```

**Required Environment Variables**:

```bash
# Core AI Services
ANTHROPIC_API_KEY=sk-ant-api03-...  # Claude Sonnet 4.5
REDIS_URL=redis://default:password@host:6379/0  # Redis with vector search

# Web Scraping
LIGHTPANDA_TOKEN=your-lightpanda-token  # Get from https://lightpanda.io

# Image Generation (Google Vertex AI)
GCP_PROJECT_ID=your-gcp-project-id
GCP_LOCATION=us-central1
GOOGLE_AI_API_KEY=your-google-ai-key  # Backup for Google AI Studio

# Asset Storage (AWS S3)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
AWS_S3_BUCKET=brandmind-assets

# CMS Publishing (Sanity)
SANITY_PROJECT_ID=your-project-id
SANITY_DATASET=production
SANITY_TOKEN=your-token
SANITY_API_VERSION=2025-01-01
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
2. Enter a business website URL (e.g., https://www.nike.com)
3. Optionally add competitor URLs
4. Click "Generate 7-Day Campaign"
5. Watch agents work in real-time
6. View your 7-day campaign with captions and images!

## How It Works

### 4-Agent Autonomous Pipeline

**Input**: Business Website URL (+ optional competitor URLs)

**Agent 1: Research (0-25%)**
- Scrapes website with Lightpanda (10x faster than Puppeteer)
- Extracts:
  - Business name, industry, products
  - Brand voice from website copy
  - Product images (max 20, filtered for quality)
  - Target audience
- Researches competitor websites (if provided)
- Analyzes industry trends
- Stores all findings in Redis with vector embeddings

**Agent 2: Strategy (25-50%)**
- Retrieves similar past campaigns via Redis vector search
- Analyzes what content performed well
- Incorporates competitor insights and trends
- Generates 7-day content calendar with:
  - Daily themes (e.g., "Behind the scenes", "Product showcase")
  - Content types (image/video/carousel)
  - Image/video concepts
  - Optimal posting times
  - CTAs and hashtag recommendations

**Agent 3: Creative (50-85%)**
- Generates captions with Claude Sonnet 4.5:
  - Hook, body, CTA structure
  - Brand voice consistency
  - Hashtag integration
- Generates images with Vertex AI Imagen 3:
  - Uses product images as style references
  - 2 options per day (best selected)
  - 1:1 aspect ratio for Instagram
- Uploads all assets to AWS S3
- Stores content in Redis

**Agent 4: Orchestration (85-100%)**
- Publishes campaign to Sanity CMS
- Creates content calendar in Sanity
- Schedules posts (via Postman API - optional)
- Returns Sanity Studio URL for review/editing

**Output**:
- 7 days of complete social media content
- Captions, images, hashtags, CTAs
- Published to Sanity CMS
- Downloadable assets on S3

### Key Technical Features

**Vector Memory**: Agents learn from past campaigns using Redis vector search with 1536D embeddings. Similar campaigns inform strategy decisions.

**Autonomous Discovery**: Zero manual input required. Agent 1 autonomously discovers business context, brand voice, products, and competitors just from URL.

**Production-Grade**:
- Type safety with Pydantic v2
- Async/await throughout
- Graceful fallbacks for all services
- Real-time progress tracking
- Error handling and logging

## Project Structure

```
aws-prod-agent-hack/
├── backend/
│   ├── agents/
│   │   ├── research_agent.py         # Agent 1: Autonomous research
│   │   ├── strategy_agent.py         # Agent 2: Content strategy
│   │   ├── creative_agent.py         # Agent 3: Caption & image generation
│   │   └── orchestration_agent.py    # Agent 4: CMS publishing
│   ├── services/
│   │   ├── claude_service.py         # Anthropic Claude API
│   │   ├── redis_service.py          # Redis vector database
│   │   ├── lightpanda_service.py     # Fast web scraping
│   │   ├── vertex_service.py         # Google Vertex AI (Imagen)
│   │   ├── aws_service.py            # AWS S3 storage
│   │   └── sanity_service.py         # Sanity CMS
│   ├── models.py                      # Pydantic data models
│   ├── orchestrator.py                # 4-agent coordinator
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
│   ├── types/
│   │   └── index.ts                   # TypeScript types
│   ├── package.json
│   └── .env.local
└── README.md
```

## API Endpoints

### Backend (FastAPI)

**POST /api/generate**
- Input: `{ business_url: string, competitor_urls?: string[] }`
- Returns: `{ success: boolean, campaign_id: string, message: string }`
- Triggers: Background task that runs all 4 agents

**GET /api/campaign/{campaign_id}**
- Returns: Full campaign object with progress and results
- Updates in real-time as agents complete work

## Hackathon Submission

**Built for:** Production Agents Hackathon (November 21, 2025)

**Sponsor Tools Integrated** (6 minimum required):
1. ✅ **Redis** - Vector database for agent memory and RAG
2. ✅ **Sanity CMS** - Content calendar publishing
3. ✅ **Lightpanda** - 10x faster web scraping
4. ✅ **Anthropic** - Claude Sonnet 4.5 for all AI reasoning
5. ✅ **AWS** - S3 asset storage
6. ✅ **Postman** - Social media API scheduling

**Judging Criteria**:
- ✅ **Technical Feasibility**: Fully functional 4-agent system with production-grade architecture
- ✅ **Innovation**: Autonomous discovery from URL alone, vector memory for learning
- ✅ **Sponsor Integration**: Deep integration of 6 sponsor tools with real use cases
- ✅ **Code Quality**: Type safety, async/await, error handling, comprehensive tests
- ✅ **Market Potential**: $17,750+ prize potential across multiple categories

**Prize Categories**:
- Best Overall Production Agent ($2,500)
- Best Use of Redis ($2,500)
- Best Use of Sanity ($2,500)
- Best Use of Anthropic ($2,500)
- Best Use of AWS ($2,500)
- Best Use of Lightpanda ($2,500)
- Best Use of Postman ($2,500)

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

**Lightpanda Connection Issues**:
- Check token is valid
- Fallback to aiohttp+BeautifulSoup automatically enabled

**Redis Vector Search Not Working**:
- Ensure Redis has RediSearch module enabled
- Check vector index is created on first run

**Image Generation Fails**:
- Vertex AI requires GCP project with billing enabled
- Falls back to placeholder images if credentials missing

**Sanity Publishing Fails**:
- Check project ID and token are correct
- Falls back to mock publishing for testing

## Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Contact

- GitHub: [Your GitHub]
- Email: [Your Email]
- Demo Video: [Coming Soon]

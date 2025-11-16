# Veo-licious Gems - AI Marketing Agency-in-a-Box

**Built for: GDG Stanford Hackathon - Build with Google Gemini (Nov 15, 2024)**

> Transform 5 minutes of input into 7 days of branded social media content. What agencies charge $2-5K/month for, powered by AI agents in minutes.

Generate complete social media campaigns (captions + images + videos) using Google Gemini, Veo 2.0, and a 3-agent system.

## Architecture

- **Frontend**: Next.js 14 (Cloud Run)
- **Backend**: Python FastAPI with 3-agent system (Cloud Run)
- **AI Models**:
  - Gemini 2.0 Flash & 2.5 Flash (text generation, analysis) via **Google AI Studio**
  - Veo 2.0 (video generation) via **Google AI Studio**
  - Gemini 2.5 Flash Image (image generation with style matching) via **Google AI Studio**
- **Services**: Google Maps Places API, Google Trends API, Cloud Storage, Search Grounding
- **Infrastructure**: Cloud Run deployment

## Prerequisites

- **Google AI Studio API key** (get from: https://aistudio.google.com/app/apikey) - **REQUIRED**
- GCP project with billing enabled (for Cloud Storage)
- Python 3.11+
- Node.js 18+
- Docker (for deployment)
- Google Maps API key (optional - for enhanced business data)

## Quick Start

### 1. Set Up Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env and add your Google AI Studio API key
```

Required:
```
GOOGLE_AI_API_KEY=your_api_key_here  # Get from https://aistudio.google.com/app/apikey
```

Optional (for enhanced features):
```
GOOGLE_MAPS_API_KEY=your_maps_key
GCP_PROJECT_ID=your-project-id
STORAGE_BUCKET=your-bucket-name
```

### 3. Run Backend

```bash
cd backend
source venv/bin/activate
python main.py
# Server runs on http://localhost:8080
```

### 4. Run Frontend

```bash
cd frontend
npm install
npm run dev
# App runs on http://localhost:3000
```

### 5. Access the Application

Open http://localhost:3000 in your browser!

## How It Works

### Three-Agent System

1. **Business Analyst Agent**
   - Analyzes website with Gemini + Search Grounding
   - Fetches business data from Google Maps Places API
   - Gets local trends from Google Trends API

2. **Content Strategist Agent**
   - Creates 7-day content calendar
   - Generates video concepts with 1-3 segments each
   - Incorporates local trends and review themes

3. **Creative Producer Agent**
   - Generates captions with Gemini
   - Creates videos with Veo using video extension
   - Chains 8-second segments for 8-24 second videos

### Video Extension

Veo can generate 8-second videos. For longer content, we use video extension:

1. Generate first 8s clip at 720p
2. Use video URI as context for next segment
3. Veo uses last frame for seamless continuation
4. Chain up to 3 segments (24 seconds total)

## Project Structure

```
.
├── backend/
│   ├── agents/                 # Three AI agents
│   ├── services/               # Google services wrapper
│   ├── main.py                 # FastAPI server
│   ├── orchestrator.py         # Agent orchestration
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Input form
│   │   └── gallery/page.tsx    # Content gallery
│   ├── components/
│   └── Dockerfile
└── terraform/
    ├── main.tf
    ├── apis.tf
    ├── iam.tf
    ├── cloud-run-*.tf
    └── build-push.tf
```

## Technologies

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Material-UI
- **Backend**: Python 3.11, FastAPI, google-genai SDK (Google AI Studio)
- **AI Models**:
  - Gemini 2.0 Flash (fast text generation, analysis)
  - Gemini 2.5 Flash (advanced reasoning)
  - Gemini 2.5 Flash Image (native image generation with style references)
  - Veo 2.0 (video generation with extension)
- **APIs**: Google Maps Places API, Google Trends API, Search Grounding
- **Infrastructure**: Docker, Cloud Run
- **Storage**: Cloud Storage (for video/image assets)

## Why This Matters (For VCs)

**Market Opportunity:**
- 33M small businesses in the US struggle with social media
- Current options: $2-5K/month agencies OR spend 5-10 hours/week doing it themselves
- Our solution: $99-299/month, 5 minutes of setup

**Defensible Moat:**
- **Speed + Quality**: Real photo style-matching creates authentic branded content (not generic AI slop)
- **3-Agent Architecture**: Modular system that learns and improves
- **Multimodal AI Stack**: Combining text, image, and video generation in one workflow

**Path to Scale:**
- Viral demo (social engagement = distribution)
- Land: SMBs via self-serve ($99/mo)
- Expand: Agencies via white-label ($500-2K/mo)
- Future: Industry-specific models with network effects

## Cost Estimation

**For Testing/Demo:**
- Google AI Studio API: Free tier available, then pay-per-use
- Gemini 2.0 Flash: Very low cost per request
- Veo 2.0 Video Generation: ~$0.50-2 per video
- Image Generation: ~$0.04 per image

**For Production:**
- Cloud Run: ~$5-10/month (generous free tier)
- Storage: ~$1-5/month for assets
- Total: Can serve 100-500 businesses/month for ~$20-50 in infrastructure

## Hackathon Submission

**Built for:** GDG Stanford - Build with Google Gemini Hackathon (November 15, 2024)

**Submission Components:**
1. ✅ **Live Demo**: https://veo-licious-gems-frontend-t5666p4y5q-uc.a.run.app
2. ✅ **Backend API**: https://veo-licious-gems-backend-t5666p4y5q-uc.a.run.app
3. ✅ **Code Repository**: Shared via Google AI Studio (link in SUBMISSION.md)
4. 🎥 **Demo Video**: [YouTube link coming soon]
5. 📄 **One-Pager**: See SUBMISSION.md

**Judging Criteria Addressed:**
- ✅ Technical Feasibility: Fully functional 3-agent system with real AI generation
- ✅ Innovation & Novelty: Style-matching with real business photos, video extension, multimodal approach
- ✅ Real-World Applicability: Solving real pain point for 33M small businesses
- ✅ Market Potential: Clear path to $10M+ ARR with recurring revenue model
- ✅ Go-to-Market Traction: Viral demo strategy with social engagement tracking

## Team

[Add your team members here]

## License

MIT

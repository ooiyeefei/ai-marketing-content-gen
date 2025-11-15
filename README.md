# Social Media AI Agency

Generate 7 days of AI-powered social media content with videos using Google Cloud Run, Gemini, and Veo.

## Architecture

- **Frontend**: Next.js 14 (Cloud Run)
- **Backend**: Python FastAPI with Google ADK agents (Cloud Run)
- **AI Models**: Gemini Pro (text), Veo 2.0 (video generation)
- **Services**: Google Maps Places API, Google Trends API, Cloud Storage
- **Infrastructure**: Fully automated with Terraform

## Prerequisites

- GCP project with billing enabled
- Docker installed
- Terraform >= 1.5
- Node.js 18+
- Python 3.11+
- Google Maps API key

## Quick Start

### 1. Authenticate with GCP

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### 2. Configure Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your project ID and API key
```

### 3. Deploy Everything

```bash
terraform init
terraform apply
```

This will:
- Enable required GCP APIs
- Create Artifact Registry
- Build and push Docker images
- Deploy frontend and backend to Cloud Run
- Set up IAM, secrets, and storage

**Deployment takes ~10-15 minutes**

### 4. Access the Application

After deployment completes, Terraform will output the frontend URL:

```
frontend_url = "https://social-media-ai-agency-frontend-xxx.run.app"
```

Open this URL in your browser!

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
# Server runs on http://localhost:8080
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# App runs on http://localhost:3000
```

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

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: Python 3.11, FastAPI, google-genai SDK
- **AI**: Gemini Pro, Veo 2.0, Google Maps, Google Trends
- **Infrastructure**: Terraform, Docker, Cloud Run, Artifact Registry
- **Storage**: Cloud Storage, Secret Manager

## Cost Estimation

- Cloud Run: ~$5-10/month (with generous free tier)
- Storage: ~$1-5/month
- Vertex AI (Gemini, Veo): Pay per use (~$0.50-2 per video)

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy
```

## License

MIT

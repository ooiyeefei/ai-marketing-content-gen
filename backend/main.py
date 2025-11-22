"""
BrandMind AI - FastAPI Server
Main entry point for the autonomous marketing intelligence agent system
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uuid
from typing import Dict, List
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from models import (
    GenerateCampaignRequest,
    GenerateCampaignResponse,
    Campaign,
    CampaignProgress,
    HealthCheckResponse,
)
from orchestrator import AgentOrchestrator
from langgraph_orchestrator import get_autonomous_orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="BrandMind AI",
    description="Autonomous 4-agent system for marketing intelligence and content generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory campaign storage (use Redis in production)
campaigns: Dict[str, Campaign] = {}
progress_updates: Dict[str, List[CampaignProgress]] = {}


@app.get("/", response_model=HealthCheckResponse)
async def root():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        services={
            "redis": bool(os.getenv("REDIS_HOST")),
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "lightpanda": bool(os.getenv("LIGHTPANDA_TOKEN")),
            "sanity": bool(os.getenv("SANITY_PROJECT_ID")),
            "aws": bool(os.getenv("AWS_ACCESS_KEY_ID")),
            "gcp": bool(os.getenv("GCP_PROJECT_ID")),
        }
    )


@app.get("/health")
async def health():
    """Simple health check"""
    return {"status": "ok"}


@app.post("/api/generate", response_model=GenerateCampaignResponse)
async def generate_campaign(
    request: GenerateCampaignRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a complete marketing campaign from business URL.

    This endpoint triggers all 4 agents:
    1. Research Agent: Analyzes business, competitors, trends
    2. Strategy Agent: Creates 7-day content calendar
    3. Creative Agent: Generates captions, images, videos
    4. Orchestration Agent: Publishes to Sanity CMS

    Args:
        request: Campaign generation request with business URL

    Returns:
        Campaign ID and initial status
    """
    try:
        # Generate unique campaign ID
        campaign_id = f"campaign_{uuid.uuid4().hex[:12]}"

        logger.info(f"Starting campaign generation: {campaign_id}")
        logger.info(f"Business URL: {request.business_url}")

        # Initialize campaign tracking
        campaign = Campaign(
            campaign_id=campaign_id,
            business_url=str(request.business_url),
            status="researching",
            progress=CampaignProgress(
                current_step="research",
                step_number=1,
                total_steps=4,
                message="Initializing campaign...",
                percentage=0
            )
        )
        campaigns[campaign_id] = campaign
        progress_updates[campaign_id] = []

        # Start generation in background
        background_tasks.add_task(
            generate_campaign_task,
            campaign_id,
            request
        )

        logger.info(f"Campaign {campaign_id} queued for generation")

        return GenerateCampaignResponse(
            success=True,
            campaign_id=campaign_id,
            message="Campaign generation started successfully"
        )

    except Exception as e:
        logger.error(f"Error starting campaign generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start campaign generation: {str(e)}"
        )


@app.get("/api/campaigns/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str):
    """Get campaign status and results"""
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return campaigns[campaign_id]


@app.get("/api/campaigns/{campaign_id}/progress")
async def get_campaign_progress(campaign_id: str):
    """Get real-time progress updates for a campaign"""
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return {
        "campaign_id": campaign_id,
        "status": campaigns[campaign_id].status,
        "progress_updates": progress_updates.get(campaign_id, [])
    }


@app.get("/api/campaigns")
async def list_campaigns():
    """List all campaigns"""
    return {
        "campaigns": list(campaigns.values()),
        "total": len(campaigns)
    }


@app.post("/api/generate-autonomous", response_model=GenerateCampaignResponse)
async def generate_campaign_autonomous(
    request: GenerateCampaignRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a campaign using AUTONOMOUS LangGraph orchestrator.

    This uses the new ReAct reasoning loop:
    - Master reasoner decides next actions dynamically
    - Quality evaluation and self-correction
    - Learning from past campaigns
    - Full scratchpad visibility for transparent AI

    Args:
        request: Campaign generation request with business URL

    Returns:
        Campaign ID and initial status
    """
    try:
        # Generate unique campaign ID
        campaign_id = f"autonomous_{uuid.uuid4().hex[:12]}"

        logger.info(f"🤖 Starting AUTONOMOUS campaign generation: {campaign_id}")
        logger.info(f"Business URL: {request.business_url}")

        # Initialize campaign tracking
        campaign = Campaign(
            campaign_id=campaign_id,
            business_url=str(request.business_url),
            status="reasoning",
            progress=CampaignProgress(
                current_step="initializing",
                step_number=0,
                total_steps=15,  # Max iterations
                message="Initializing autonomous agent system...",
                percentage=0
            )
        )
        campaigns[campaign_id] = campaign
        progress_updates[campaign_id] = []

        # Start autonomous generation in background
        background_tasks.add_task(
            generate_autonomous_campaign_task,
            campaign_id,
            request
        )

        logger.info(f"Autonomous campaign {campaign_id} queued")

        return GenerateCampaignResponse(
            success=True,
            campaign_id=campaign_id,
            message="Autonomous campaign generation started - watch the scratchpad!"
        )

    except Exception as e:
        logger.error(f"Error starting autonomous campaign: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start autonomous campaign: {str(e)}"
        )


@app.get("/api/campaigns/{campaign_id}/scratchpad")
async def get_campaign_scratchpad(campaign_id: str):
    """
    Get the autonomous reasoning scratchpad.

    This shows the AI's thought process in real-time:
    - What it's thinking
    - What action it chooses
    - What it observes
    - Quality scores

    Perfect for demos and debugging!
    """
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign = campaigns[campaign_id]

    # Get scratchpad from campaign (if autonomous)
    scratchpad = getattr(campaign, 'scratchpad', [])

    return {
        "campaign_id": campaign_id,
        "status": campaign.status,
        "iterations": len(scratchpad),
        "scratchpad": scratchpad,
        "quality_scores": getattr(campaign, 'quality_scores', {}),
        "past_learnings_count": len(getattr(campaign, 'past_learnings', []))
    }


async def generate_autonomous_campaign_task(
    campaign_id: str,
    request: GenerateCampaignRequest
):
    """
    Background task using AUTONOMOUS LangGraph orchestrator.

    Features:
    - ReAct reasoning loop (Reason → Act → Observe → Learn)
    - Dynamic decision making (not fixed pipeline)
    - Quality evaluation and self-correction
    - Learning from past campaigns
    - Full scratchpad visibility

    Updates campaign with reasoning history in real-time.
    """
    campaign = campaigns[campaign_id]
    start_time = datetime.now()

    try:
        # Initialize autonomous orchestrator
        autonomous_orchestrator = get_autonomous_orchestrator()

        logger.info(f"🤖 Running AUTONOMOUS campaign generation")

        # Run autonomous workflow
        final_state = await autonomous_orchestrator.run(
            campaign_id=campaign_id,
            business_url=str(request.business_url),
            competitor_urls=[str(url) for url in (request.competitor_urls or [])]
        )

        # Update campaign with results from autonomous system
        campaign.research = final_state.get("research")
        campaign.strategy = final_state.get("strategy")
        campaign.creative = final_state.get("creative")
        campaign.orchestration = final_state.get("orchestration")
        campaign.status = final_state.get("status", "completed")
        campaign.completed_at = final_state.get("completed_at", datetime.now())

        # Store autonomous-specific data
        campaign.scratchpad = final_state.get("scratchpad", [])
        campaign.quality_scores = final_state.get("quality_scores", {})
        campaign.past_learnings = final_state.get("past_learnings", [])
        campaign.iterations = final_state.get("iterations", 0)

        # Update progress
        campaign.progress = CampaignProgress(
            current_step="completed",
            step_number=campaign.iterations,
            total_steps=15,
            message=f"✅ Autonomous campaign complete in {campaign.iterations} iterations",
            percentage=100
        )

        # Calculate total time
        total_time = (datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Autonomous campaign {campaign_id} completed in {total_time:.1f}s")
        logger.info(f"   Iterations: {campaign.iterations}")
        logger.info(f"   Quality scores: {campaign.quality_scores}")

    except Exception as e:
        logger.error(f"Autonomous campaign {campaign_id} failed: {str(e)}", exc_info=True)
        campaign.status = "failed"
        campaign.error_message = str(e)
        campaign.progress = CampaignProgress(
            current_step="error",
            step_number=0,
            total_steps=15,
            message=f"❌ Error: {str(e)}",
            percentage=0
        )


async def generate_campaign_task(
    campaign_id: str,
    request: GenerateCampaignRequest
):
    """
    Background task that orchestrates all 4 agents to generate campaign.

    Agents run sequentially:
    Agent 1 → Agent 2 → Agent 3 → Agent 4

    Updates campaign object and progress in real-time.
    """
    campaign = campaigns[campaign_id]
    start_time = datetime.now()

    def update_progress(status: str, agent: str, step_num: int, percentage: int, message: str):
        """Helper to update progress"""
        progress = CampaignProgress(
            current_step=agent,
            step_number=step_num,
            total_steps=4,
            message=message,
            percentage=percentage
        )
        progress_updates[campaign_id].append(progress)
        campaign.status = status
        campaign.progress = progress
        logger.info(f"[{campaign_id}] {message} ({percentage}%)")

    try:
        # Initialize orchestrator
        orchestrator = AgentOrchestrator()

        # Run complete campaign generation pipeline (all 4 agents)
        logger.info(f"🚀 Running campaign generation for {request.business_url}")

        updated_campaign = await orchestrator.run(
            campaign=campaign,
            business_url=str(request.business_url),
            competitor_urls=[str(url) for url in (request.competitor_urls or [])]
        )

        # Update campaign with results
        campaign.research = updated_campaign.research
        campaign.strategy = updated_campaign.strategy
        campaign.creative = updated_campaign.creative
        campaign.orchestration = updated_campaign.orchestration
        campaign.status = updated_campaign.status
        campaign.progress = updated_campaign.progress
        campaign.completed_at = updated_campaign.completed_at

        # Calculate total time
        total_time = (datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Campaign {campaign_id} completed successfully")

        logger.info(f"Campaign {campaign_id} completed in {total_time:.1f}s")

    except Exception as e:
        logger.error(f"Campaign {campaign_id} failed: {str(e)}", exc_info=True)
        campaign.status = "failed"
        campaign.error_message = str(e)
        update_progress("failed", "error", 0, 0, f"❌ Error: {str(e)}")


# For local development
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("BACKEND_PORT", "8080"))
    logger.info(f"Starting BrandMind AI server on port {port}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

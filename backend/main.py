from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uuid
from typing import Dict
import logging

from models import (
    GenerateContentRequest,
    GenerateContentResponse,
    GenerationJob,
)
from config import settings
from orchestrator import AgentOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Social Media AI Agency",
    description="Multi-agent system for generating social media content",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage (use Redis/Firestore in production)
jobs: Dict[str, GenerationJob] = {}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Social Media AI Agency Backend",
        "version": "1.0.0"
    }


@app.post("/api/generate", response_model=GenerateContentResponse)
async def generate_content(
    request: GenerateContentRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate social media content from business input.
    Returns job ID for tracking progress.
    """
    # Create job ID
    job_id = str(uuid.uuid4())

    # Initialize job tracking
    job = GenerationJob(
        job_id=job_id,
        status="pending",
        progress=0,
        current_step="Initializing agents...",
        posts=[]
    )
    jobs[job_id] = job

    # Start content generation in background
    background_tasks.add_task(
        generate_content_task,
        job_id,
        request.business_input
    )

    logger.info(f"Created job {job_id} for content generation")

    return GenerateContentResponse(
        job_id=job_id,
        status="pending",
        message="Content generation started. Use /api/status/{job_id} to track progress."
    )


@app.get("/api/status/{job_id}", response_model=GenerationJob)
async def get_job_status(job_id: str):
    """Get status of content generation job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs[job_id]


async def generate_content_task(job_id: str, business_input):
    """
    Background task for content generation using agent orchestrator.
    """
    orchestrator = AgentOrchestrator()
    job = jobs[job_id]

    await orchestrator.generate_content(
        business_input=business_input,
        job=job,
        jobs_store=jobs
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

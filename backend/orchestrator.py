import logging
from typing import Dict
from models import BusinessInput, GenerationJob, ContentPost
from agents.business_analyst import BusinessAnalystAgent
from agents.content_strategist import ContentStrategistAgent
from agents.creative_producer import CreativeProducerAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates the three-agent workflow:
    Business Analyst → Content Strategist → Creative Producer
    """

    def __init__(self):
        self.agent1 = BusinessAnalystAgent()
        self.agent2 = ContentStrategistAgent()
        self.agent3 = CreativeProducerAgent()
        logger.info("AgentOrchestrator initialized with 3 agents")

    async def generate_content(
        self,
        business_input: BusinessInput,
        job: GenerationJob,
        jobs_store: Dict[str, GenerationJob]
    ) -> None:
        """
        Run the complete agent workflow.
        Updates job status throughout execution.

        Args:
            business_input: User input with website/address
            job: Job tracking object
            jobs_store: Reference to jobs dictionary for updates

        """
        try:
            # Agent 1: Business Analysis
            logger.info(f"Job {job.job_id}: Starting Agent 1 (Business Analyst)")
            job.status = "processing"
            job.current_step = "Agent 1: Analyzing business context..."
            job.progress = 10
            jobs_store[job.job_id] = job

            business_profile = await self.agent1.analyze(business_input)

            logger.info(f"Job {job.job_id}: Agent 1 complete")
            job.current_step = "Agent 1: Complete ✓"
            job.progress = 30
            jobs_store[job.job_id] = job

            # Agent 2: Content Strategy
            logger.info(f"Job {job.job_id}: Starting Agent 2 (Content Strategist)")
            job.current_step = "Agent 2: Creating content calendar..."
            job.progress = 35
            jobs_store[job.job_id] = job

            # Get days from business_input (default to 7)
            days = getattr(business_input, 'days', 7) or 7
            content_calendar = await self.agent2.create_calendar(business_profile, days)

            logger.info(f"Job {job.job_id}: Agent 2 complete")
            job.current_step = "Agent 2: Complete ✓"
            job.progress = 50
            jobs_store[job.job_id] = job

            # Agent 3: Creative Production
            logger.info(f"Job {job.job_id}: Starting Agent 3 (Creative Producer)")
            job.current_step = "Agent 3: Generating captions and videos..."
            job.progress = 55
            jobs_store[job.job_id] = job

            posts = await self.agent3.produce_content(
                content_calendar,
                business_profile,
                job_id=job.job_id
            )

            logger.info(f"Job {job.job_id}: Agent 3 complete")
            job.current_step = "Agent 3: Complete ✓"
            job.progress = 95
            jobs_store[job.job_id] = job

            # Finalize
            job.posts = posts
            job.status = "completed"
            job.current_step = "All content generated successfully!"
            job.progress = 100
            jobs_store[job.job_id] = job

            logger.info(f"Job {job.job_id}: Complete with {len(posts)} posts")

        except Exception as e:
            logger.error(f"Job {job.job_id} failed: {str(e)}")
            job.status = "failed"
            job.error = str(e)
            job.current_step = f"Failed: {str(e)}"
            jobs_store[job.job_id] = job

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field


class BusinessInput(BaseModel):
    """Input from user for business context gathering"""
    website_url: Optional[HttpUrl] = Field(None, description="Business website URL")
    business_address: Optional[str] = Field(None, description="Business physical address")
    business_name: Optional[str] = Field(None, description="Manual business name")
    industry: Optional[str] = Field(None, description="Manual industry")
    description: Optional[str] = Field(None, description="Manual business description")
    brand_voice: Optional[str] = Field("professional", description="Brand voice: casual, professional, playful")
    days: Optional[int] = Field(7, description="Number of days of content to generate (1-7)", ge=1, le=7)


class VideoSegment(BaseModel):
    """Single video segment with URI"""
    segment_number: int
    uri: str
    duration_seconds: int
    prompt_used: str


class ImageSegment(BaseModel):
    """Single image segment with URI"""
    segment_number: int
    uri: str
    prompt_used: str


class ContentPost(BaseModel):
    """Generated social media post"""
    day: int
    platform: str
    caption: str
    video_segments: List[VideoSegment]
    image_segments: List[ImageSegment] = []
    total_duration_seconds: int
    hashtags: List[str]


class GenerationJob(BaseModel):
    """Job tracking for content generation"""
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    current_step: str
    posts: List[ContentPost] = []
    error: Optional[str] = None


class GenerateContentRequest(BaseModel):
    """Request to generate content"""
    business_input: BusinessInput


class GenerateContentResponse(BaseModel):
    """Response with job ID for tracking"""
    job_id: str
    status: str
    message: str


# ============================================
# NEW CAMPAIGN-BASED MODELS
# ============================================

class BrandVoice(BaseModel):
    """Brand voice characteristics"""
    tone: str = "professional"
    style: str = "clear"
    colors: List[str] = []
    personality_traits: List[str] = []
    dos: List[str] = []
    donts: List[str] = []


class BusinessContext(BaseModel):
    """Business context from research"""
    business_name: str
    business_url: str
    industry: str
    products: List[str] = []
    target_audience: str = "General audience"
    description: str = ""
    brand_voice: Optional[BrandVoice] = None


class CompetitorInsight(BaseModel):
    """Competitor analysis"""
    competitor_name: str
    competitor_url: str
    content_themes: List[str] = []
    visual_style: str = "Unknown"


class TrendAnalysis(BaseModel):
    """Industry trend analysis"""
    industry: str
    trends: List[str] = []
    actionable_themes: List[str] = []
    best_practices: List[str] = []


class ResearchOutput(BaseModel):
    """Output from Research Agent"""
    business_context: BusinessContext
    product_images: List[str] = []
    competitor_insights: List[CompetitorInsight] = []
    industry_trends: Optional[TrendAnalysis] = None
    redis_keys: List[str] = []
    timestamp: datetime


class DayPlan(BaseModel):
    """Content plan for one day"""
    day: int
    theme: str
    content_type: str = "image"  # image, video, carousel
    caption_direction: str
    image_concept: str
    video_concept: Optional[str] = None
    cta: str
    hashtags: List[str] = []
    optimal_post_time: str = "10:00"


class ContentStrategy(BaseModel):
    """7-day content strategy"""
    business_url: str
    campaign_id: str
    created_at: datetime
    days: List[DayPlan]


class DayContent(BaseModel):
    """Generated content for one day"""
    day: int
    theme: str
    content_type: str
    caption: str
    hashtags: List[str]
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    cta: str
    scheduled_time: str


class CreativeOutput(BaseModel):
    """Output from Creative Agent"""
    campaign_id: str
    days: List[DayContent]
    total_images_generated: int = 0
    total_videos_generated: int = 0
    created_at: datetime


class OrchestrationOutput(BaseModel):
    """Output from Orchestration Agent"""
    campaign_id: str
    sanity_campaign_id: str
    sanity_studio_url: str
    published_content_ids: List[str] = []
    calendar_summary: Dict[str, Any] = {}
    status: str = "completed"
    scheduled_posts: List[Dict[str, Any]] = []
    created_at: datetime


class CampaignProgress(BaseModel):
    """Real-time campaign progress"""
    current_step: str
    step_number: int
    total_steps: int = 4
    message: str
    percentage: int  # 0-100


class Campaign(BaseModel):
    """Complete campaign state"""
    campaign_id: str
    business_url: str
    status: str  # researching, strategizing, creating, publishing, completed, failed
    progress: CampaignProgress
    research: Optional[ResearchOutput] = None
    strategy: Optional[ContentStrategy] = None
    creative: Optional[CreativeOutput] = None
    orchestration: Optional[OrchestrationOutput] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class GenerateCampaignRequest(BaseModel):
    """Request to generate campaign"""
    business_url: HttpUrl
    competitor_urls: Optional[List[HttpUrl]] = None


class GenerateCampaignResponse(BaseModel):
    """Response with campaign ID"""
    success: bool
    campaign_id: str
    message: str


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str

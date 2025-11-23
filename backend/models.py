from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


# ============================================================================
# Agent 1: Research & Intelligence Models
# ============================================================================

class BusinessContext(BaseModel):
    """Extracted business information from website"""
    business_name: str
    industry: str
    description: str
    location: Dict[str, str]  # {city, state, country}
    price_range: Optional[str] = None
    specialties: List[str] = []
    brand_voice: Optional[str] = None
    target_audience: Optional[str] = None
    website_url: HttpUrl


class CompetitorInfo(BaseModel):
    """Competitor research data"""
    name: str
    website: Optional[HttpUrl] = None
    location: str
    google_rating: Optional[float] = None
    review_count: Optional[int] = None
    social_handles: Dict[str, str] = Field(default_factory=dict)  # {instagram, facebook}
    pricing_strategy: Optional[str] = None
    brand_voice: Optional[str] = None
    top_content_themes: List[str] = []
    differentiators: List[str] = []
    similarity_score: Optional[float] = None


class MarketInsights(BaseModel):
    """Market research and trend analysis"""
    trending_topics: List[str]
    market_gaps: List[str]
    positioning_opportunities: List[str]
    content_strategy: Dict[str, Any]  # {winning_formats, high_engagement_themes, etc}


class ResearchOutput(BaseModel):
    """Agent 1 complete output"""
    campaign_id: str
    business_context: BusinessContext
    competitors: List[CompetitorInfo]
    market_insights: MarketInsights
    research_images: List[HttpUrl] = []  # R2 URLs
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# Agent 2: Analytics & Feedback Models
# ============================================================================

class CustomerReview(BaseModel):
    """Single customer review"""
    rating: int
    text: str
    date: str
    reviewer_name: Optional[str] = None
    helpful_count: Optional[int] = 0


class CustomerSentiment(BaseModel):
    """Analyzed customer sentiment"""
    positive_themes: List[str]
    negative_themes: List[str]
    popular_items: List[str]
    quotable_reviews: List[str]
    content_opportunities: List[str]


class SocialPostPerformance(BaseModel):
    """Individual post metrics"""
    post_id: str
    message: str
    created_time: str
    reach: int
    engagement: int
    likes: int
    comments: int
    shares: int
    content_type: str  # photo, video, carousel
    engagement_rate: float


class PerformancePatterns(BaseModel):
    """Analyzed performance patterns"""
    winning_patterns: Dict[str, Any]  # {content_types, themes, posting_times, hashtags}
    avoid_patterns: Dict[str, Any]  # {low_performers, reasons}
    recommendations: List[str]


class TrendData(BaseModel):
    """Google Trends data"""
    trending_searches: List[Dict[str, str]]  # [{query, growth}]
    related_queries: List[str]
    rising_topics: List[str]


class AnalyticsOutput(BaseModel):
    """Agent 2 complete output"""
    campaign_id: str
    customer_sentiment: CustomerSentiment
    past_performance: Optional[PerformancePatterns] = None
    market_trends: TrendData
    customer_photos: List[HttpUrl] = []  # R2 URLs
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# Agent 3: Content Generation Models
# ============================================================================

class DayPlan(BaseModel):
    """Content plan for a single day"""
    day: int
    theme: str
    content_type: str  # video, photo, carousel
    message: str
    hashtags: List[str]
    cta: str
    rationale: str


class ContentStrategy(BaseModel):
    """7-day content strategy"""
    days: List[DayPlan]


class DayContent(BaseModel):
    """Generated content for a single day"""
    day: int
    theme: str
    caption: str
    hashtags: List[str]
    image_urls: List[HttpUrl]  # R2 URLs (2 options)
    video_url: Optional[HttpUrl] = None  # R2 URL
    cta: str
    recommended_post_time: str


class LearningData(BaseModel):
    """Self-evolving feedback data"""
    what_worked: List[Dict[str, str]]  # [{insight, evidence, recommendation}]
    what_to_improve: List[Dict[str, str]]  # [{issue, evidence, recommendation}]
    next_iteration_strategy: Dict[str, Any]


class CreativeOutput(BaseModel):
    """Agent 3 complete output"""
    campaign_id: str
    days: List[DayContent]
    learning_data: LearningData
    status: str = "completed"
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# Campaign Request & Response Models
# ============================================================================

class CampaignRequest(BaseModel):
    """User input to generate campaign"""
    business_url: HttpUrl
    competitor_urls: Optional[List[HttpUrl]] = None
    facebook_token: Optional[str] = None
    instagram_token: Optional[str] = None


class CampaignProgress(BaseModel):
    """Real-time progress tracking"""
    current_step: str
    step_number: int
    total_steps: int
    message: str
    percentage: int = 0  # 0-100


class CampaignResponse(BaseModel):
    """Complete campaign output"""
    success: bool
    campaign_id: str
    business_name: str
    research_report: ResearchOutput
    analytics_report: AnalyticsOutput
    campaign_content: CreativeOutput
    sanity_url: Optional[HttpUrl] = None


# ============================================================================
# Additional API Models for FastAPI Endpoints
# ============================================================================

class GenerateCampaignRequest(BaseModel):
    """Request model for campaign generation endpoint"""
    business_url: HttpUrl
    competitor_urls: Optional[List[HttpUrl]] = None
    facebook_token: Optional[str] = None
    instagram_token: Optional[str] = None


class GenerateCampaignResponse(BaseModel):
    """Response model for campaign generation endpoint"""
    success: bool
    campaign_id: str
    message: str


class Campaign(BaseModel):
    """Campaign tracking model with all agent outputs"""
    campaign_id: str
    business_url: str
    status: str  # researching, analyzing, creating, publishing, completed, failed
    progress: CampaignProgress
    research: Optional[ResearchOutput] = None
    strategy: Optional[Any] = None
    creative: Optional[CreativeOutput] = None
    orchestration: Optional[Any] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    # Autonomous agent specific fields
    scratchpad: List[Any] = Field(default_factory=list)
    quality_scores: Dict[str, float] = Field(default_factory=dict)
    past_learnings: List[str] = Field(default_factory=list)
    iterations: int = 0


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    services: Dict[str, bool] = Field(default_factory=dict)

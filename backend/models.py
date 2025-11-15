from typing import List, Optional, Dict, Any
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

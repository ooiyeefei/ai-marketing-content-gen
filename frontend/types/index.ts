export interface CampaignRequest {
  business_url: string
  competitor_urls?: string[]
}

export interface DayContent {
  day: number
  theme: string
  content_type: 'image' | 'video' | 'carousel'
  caption: string
  hashtags: string[]
  image_url: string | null
  video_url: string | null
  cta: string
  scheduled_time: string
}

export interface CampaignProgress {
  current_step: string
  step_number: number
  total_steps: number
  message: string
  percentage: number
}

export interface Campaign {
  campaign_id: string
  business_url: string
  status: 'researching' | 'strategizing' | 'creating' | 'publishing' | 'completed' | 'failed'
  progress: CampaignProgress
  days?: DayContent[]
  sanity_studio_url?: string
  error_message?: string
  created_at?: string
  completed_at?: string
}

export interface CampaignResponse {
  success: boolean
  campaign_id: string
  message: string
}

export interface BusinessInput {
  website_url?: string
  business_address?: string
  business_name?: string
  industry?: string
  description?: string
  brand_voice?: 'casual' | 'professional' | 'playful'
  days?: number
}

export interface VideoSegment {
  segment_number: number
  uri: string
  duration_seconds: number
  prompt_used: string
}

export interface ImageSegment {
  segment_number: number
  uri: string
  prompt_used: string
}

export interface ContentPost {
  day: number
  platform: string
  caption: string
  video_segments: VideoSegment[]
  image_segments: ImageSegment[]
  total_duration_seconds: number
  hashtags: string[]
}

export interface GenerationJob {
  job_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  current_step: string
  posts: ContentPost[]
  error?: string
}

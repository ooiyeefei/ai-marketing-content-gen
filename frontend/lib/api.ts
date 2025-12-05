import { CampaignRequest, Campaign, CampaignResponse } from '@/types'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8080'

export async function generateCampaign(
  request: CampaignRequest
): Promise<CampaignResponse> {
  const response = await fetch(`${BACKEND_URL}/api/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error('Failed to start campaign generation')
  }

  return response.json()
}

export async function getCampaignStatus(campaignId: string): Promise<Campaign> {
  const response = await fetch(`${BACKEND_URL}/api/campaigns/${campaignId}`)

  if (!response.ok) {
    throw new Error('Failed to get campaign status')
  }

  return response.json()
}

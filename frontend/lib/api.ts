import { BusinessInput, GenerationJob } from '@/types'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080'

export async function generateContent(
  businessInput: BusinessInput
): Promise<{ job_id: string; status: string; message: string }> {
  const response = await fetch(`${BACKEND_URL}/api/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ business_input: businessInput }),
  })

  if (!response.ok) {
    throw new Error('Failed to start content generation')
  }

  return response.json()
}

export async function getJobStatus(jobId: string): Promise<GenerationJob> {
  const response = await fetch(`${BACKEND_URL}/api/status/${jobId}`)

  if (!response.ok) {
    throw new Error('Failed to get job status')
  }

  return response.json()
}

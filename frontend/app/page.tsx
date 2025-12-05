'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import InputForm from '@/components/InputForm'
import { generateCampaign } from '@/lib/api'
import { CampaignRequest } from '@/types'

export default function Home() {
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async (request: CampaignRequest) => {
    setLoading(true)

    try {
      const response = await generateCampaign(request)

      // Redirect to gallery page with campaign ID
      router.push(`/gallery?campaign_id=${response.campaign_id}`)
    } catch (error) {
      console.error('Error generating campaign:', error)
      alert('Failed to generate campaign. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen py-12">
      <InputForm onSubmit={handleSubmit} loading={loading} />
    </main>
  )
}

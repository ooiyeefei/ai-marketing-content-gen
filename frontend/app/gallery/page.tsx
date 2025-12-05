'use client'

import { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { getCampaignStatus } from '@/lib/api'
import { Campaign } from '@/types'
import LoadingProgress from '@/components/LoadingProgress'
import ContentCard from '@/components/ContentCard'

function GalleryContent() {
  const searchParams = useSearchParams()
  const campaignId = searchParams.get('campaign_id')

  const [campaign, setCampaign] = useState<Campaign | null>(null)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    if (!campaignId) {
      setError('No campaign ID provided')
      return
    }

    // Poll campaign status
    const pollInterval = setInterval(async () => {
      try {
        const campaignStatus = await getCampaignStatus(campaignId)
        setCampaign(campaignStatus)

        // Stop polling if completed or failed
        if (campaignStatus.status === 'completed' || campaignStatus.status === 'failed') {
          clearInterval(pollInterval)
        }
      } catch (err) {
        console.error('Error fetching campaign status:', err)
        setError('Failed to fetch campaign status')
        clearInterval(pollInterval)
      }
    }, 3000) // Poll every 3 seconds

    return () => clearInterval(pollInterval)
  }, [campaignId])

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">Error</h2>
          <p className="text-gray-400">{error}</p>
        </div>
      </div>
    )
  }

  if (!campaign) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    )
  }

  // Show loading progress
  if (['researching', 'strategizing', 'creating', 'publishing'].includes(campaign.status)) {
    return (
      <main className="min-h-screen py-12">
        <LoadingProgress progress={campaign.progress.percentage} currentStep={campaign.progress.message} />
      </main>
    )
  }

  // Show error state
  if (campaign.status === 'failed') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2 text-red-500">
            Campaign Failed
          </h2>
          <p className="text-gray-400">{campaign.error_message || 'Unknown error occurred'}</p>
        </div>
      </div>
    )
  }

  // Show gallery
  return (
    <main className="min-h-screen py-12">
      <div className="max-w-6xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-2">Your 7-Day Campaign is Ready!</h1>
          <p className="text-gray-400">
            {campaign.days?.length || 7} days of content with captions and images
          </p>
          {campaign.sanity_studio_url && (
            <a
              href={campaign.sanity_studio_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block mt-4 px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
            >
              View in Sanity Studio 📋
            </a>
          )}
        </div>

        {/* Content Grid */}
        {campaign.days && campaign.days.length > 0 && (
          <div className="grid md:grid-cols-2 gap-6">
            {campaign.days.map((day) => (
              <ContentCard key={day.day} post={day} />
            ))}
          </div>
        )}

        {/* Footer Actions */}
        <div className="mt-12 text-center space-x-4">
          <button
            onClick={() => window.location.href = '/'}
            className="px-6 py-3 bg-primary hover:bg-secondary text-white rounded-lg transition-colors"
          >
            Generate Another Campaign
          </button>
        </div>
      </div>
    </main>
  )
}

export default function GalleryPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    }>
      <GalleryContent />
    </Suspense>
  )
}

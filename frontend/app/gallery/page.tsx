'use client'

import { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { getJobStatus } from '@/lib/api'
import { GenerationJob } from '@/types'
import LoadingProgress from '@/components/LoadingProgress'
import ContentCard from '@/components/ContentCard'

function GalleryContent() {
  const searchParams = useSearchParams()
  const jobId = searchParams.get('job_id')

  const [job, setJob] = useState<GenerationJob | null>(null)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    if (!jobId) {
      setError('No job ID provided')
      return
    }

    // Poll job status
    const pollInterval = setInterval(async () => {
      try {
        const jobStatus = await getJobStatus(jobId)
        setJob(jobStatus)

        // Stop polling if completed or failed
        if (jobStatus.status === 'completed' || jobStatus.status === 'failed') {
          clearInterval(pollInterval)
        }
      } catch (err) {
        console.error('Error fetching job status:', err)
        setError('Failed to fetch job status')
        clearInterval(pollInterval)
      }
    }, 3000) // Poll every 3 seconds

    return () => clearInterval(pollInterval)
  }, [jobId])

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

  if (!job) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    )
  }

  // Show loading progress
  if (job.status === 'pending' || job.status === 'processing') {
    return (
      <main className="min-h-screen py-12">
        <LoadingProgress progress={job.progress} currentStep={job.current_step} />
      </main>
    )
  }

  // Show error state
  if (job.status === 'failed') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2 text-red-500">
            Generation Failed
          </h2>
          <p className="text-gray-400">{job.error || 'Unknown error occurred'}</p>
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
          <h1 className="text-4xl font-bold mb-2">Your Content is Ready!</h1>
          <p className="text-gray-400">
            {job.posts.length} posts generated with AI videos and captions
          </p>
        </div>

        {/* Content Grid */}
        <div className="grid md:grid-cols-2 gap-6">
          {job.posts.map((post) => (
            <ContentCard key={post.day} post={post} />
          ))}
        </div>

        {/* Footer Actions */}
        <div className="mt-12 text-center">
          <button
            onClick={() => window.location.href = '/'}
            className="px-6 py-3 bg-primary hover:bg-secondary text-white rounded-lg transition-colors"
          >
            Generate More Content
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

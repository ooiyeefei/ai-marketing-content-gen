'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import InputForm from '@/components/InputForm'
import { generateContent } from '@/lib/api'
import { BusinessInput } from '@/types'

export default function Home() {
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async (businessInput: BusinessInput) => {
    setLoading(true)

    try {
      const response = await generateContent(businessInput)

      // Redirect to gallery page with job ID
      router.push(`/gallery?job_id=${response.job_id}`)
    } catch (error) {
      console.error('Error generating content:', error)
      alert('Failed to generate content. Please try again.')
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

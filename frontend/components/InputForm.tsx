'use client'

import { useState } from 'react'
import { CampaignRequest } from '@/types'
import Button from '@mui/material/Button'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'

interface InputFormProps {
  onSubmit: (input: CampaignRequest) => void
  loading: boolean
}

export default function InputForm({ onSubmit, loading }: InputFormProps) {
  const [formData, setFormData] = useState<CampaignRequest>({
    business_url: '',
    competitor_urls: [],
  })
  const [competitorInput, setCompetitorInput] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  const addCompetitor = () => {
    if (competitorInput.trim()) {
      setFormData({
        ...formData,
        competitor_urls: [...(formData.competitor_urls || []), competitorInput.trim()],
      })
      setCompetitorInput('')
    }
  }

  const removeCompetitor = (index: number) => {
    setFormData({
      ...formData,
      competitor_urls: formData.competitor_urls?.filter((_, i) => i !== index),
    })
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <Box className="mb-8 text-center">
        <Typography
          variant="h2"
          component="h1"
          sx={{
            fontWeight: 'bold',
            mb: 2,
            color: 'primary.main',
            fontSize: { xs: '2rem', md: '2.5rem' }
          }}
        >
          BrandMind AI
        </Typography>
        <Typography variant="body1" sx={{ color: 'text.secondary' }}>
          Autonomous AI agents that generate 7 days of social media content
        </Typography>
      </Box>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Business URL */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Business Website URL *
          </label>
          <input
            type="url"
            required
            value={formData.business_url}
            onChange={(e) =>
              setFormData({ ...formData, business_url: e.target.value })
            }
            placeholder="https://yourbusiness.com"
            className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg focus:border-primary focus:ring-1 focus:ring-primary outline-none"
          />
          <p className="text-xs text-gray-500 mt-1">
            Our AI agents will autonomously analyze your website, extract brand voice, and discover your products
          </p>
        </div>

        {/* Competitor URLs (optional) */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Competitor Websites (optional)
          </label>
          <div className="flex gap-2 mb-2">
            <input
              type="url"
              value={competitorInput}
              onChange={(e) => setCompetitorInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  addCompetitor()
                }
              }}
              placeholder="https://competitor.com"
              className="flex-1 px-4 py-3 bg-white border border-gray-300 rounded-lg focus:border-primary focus:ring-1 focus:ring-primary outline-none"
            />
            <Button
              type="button"
              onClick={addCompetitor}
              variant="outlined"
              color="primary"
              sx={{ minWidth: '100px' }}
            >
              Add
            </Button>
          </div>

          {/* Competitor list */}
          {formData.competitor_urls && formData.competitor_urls.length > 0 && (
            <div className="space-y-2 mt-3">
              {formData.competitor_urls.map((url, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between px-4 py-2 bg-gray-50 rounded-lg"
                >
                  <span className="text-sm text-gray-700 truncate flex-1">{url}</span>
                  <button
                    type="button"
                    onClick={() => removeCompetitor(index)}
                    className="ml-2 text-red-500 hover:text-red-700"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}
          <p className="text-xs text-gray-500 mt-1">
            Add competitor URLs to analyze what content works in your industry
          </p>
        </div>

        <Button
          type="submit"
          disabled={loading}
          variant="contained"
          color="primary"
          fullWidth
          size="large"
          sx={{
            py: 1.5,
            ...(loading && {
              backgroundColor: 'primary.main',
              '&.Mui-disabled': {
                backgroundColor: 'primary.main',
                color: 'white',
                opacity: 0.9,
              },
              animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
              '@keyframes pulse': {
                '0%, 100%': {
                  opacity: 1,
                },
                '50%': {
                  opacity: 0.8,
                },
              },
            }),
          }}
          startIcon={loading ? <CircularProgress size={24} sx={{ color: 'white' }} /> : null}
        >
          {loading ? 'Agents Working...' : 'Generate 7-Day Campaign'}
        </Button>

        <Box className="mt-4 text-center">
          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
            🤖 4 AI agents • 🔍 Autonomous research • 🎨 Image generation • 📋 Sanity CMS
          </Typography>
        </Box>
      </form>
    </div>
  )
}

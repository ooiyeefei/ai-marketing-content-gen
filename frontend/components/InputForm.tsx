'use client'

import { useState } from 'react'
import { BusinessInput } from '@/types'
import Button from '@mui/material/Button'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'

interface InputFormProps {
  onSubmit: (input: BusinessInput) => void
  loading: boolean
}

export default function InputForm({ onSubmit, loading }: InputFormProps) {
  const [mode, setMode] = useState<'quick' | 'manual'>('quick')
  const [formData, setFormData] = useState<BusinessInput>({
    website_url: '',
    business_address: '',
    brand_voice: 'professional',
    days: 7,
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
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
          Social Media AI Agency
        </Typography>
        <Typography variant="body1" sx={{ color: 'text.secondary' }}>
          Generate 1-7 days of AI-powered content in minutes
        </Typography>
      </Box>

      {/* Mode Toggle */}
      <div className="flex gap-2 mb-6">
        <Button
          type="button"
          onClick={() => setMode('quick')}
          variant={mode === 'quick' ? 'contained' : 'outlined'}
          color="primary"
          fullWidth
        >
          Quick Start
        </Button>
        <Button
          type="button"
          onClick={() => setMode('manual')}
          variant={mode === 'manual' ? 'contained' : 'outlined'}
          color="primary"
          fullWidth
        >
          Manual Input
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {mode === 'quick' ? (
          // Quick Start Mode
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Website URL *
              </label>
              <input
                type="url"
                required
                value={formData.website_url}
                onChange={(e) =>
                  setFormData({ ...formData, website_url: e.target.value })
                }
                placeholder="https://yourbusiness.com"
                className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg focus:border-primary focus:ring-1 focus:ring-primary outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Business Address *
              </label>
              <input
                type="text"
                required
                value={formData.business_address}
                onChange={(e) =>
                  setFormData({ ...formData, business_address: e.target.value })
                }
                placeholder="123 Main St, City, Country"
                className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg focus:border-primary focus:ring-1 focus:ring-primary outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Brand Voice (optional)
              </label>
              <div className="flex gap-4">
                {(['casual', 'professional', 'playful'] as const).map((voice) => (
                  <label key={voice} className="flex items-center">
                    <input
                      type="radio"
                      name="brand_voice"
                      value={voice}
                      checked={formData.brand_voice === voice}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          brand_voice: e.target.value as any,
                        })
                      }
                      className="mr-2"
                    />
                    <span className="capitalize">{voice}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Number of Days (1-7)
              </label>
              <select
                value={formData.days || 7}
                onChange={(e) =>
                  setFormData({ ...formData, days: parseInt(e.target.value) })
                }
                className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg focus:border-primary focus:ring-1 focus:ring-primary outline-none text-gray-900 font-medium"
              >
                {[1, 2, 3, 4, 5, 6, 7].map((day) => (
                  <option key={day} value={day}>
                    {day} {day === 1 ? 'day' : 'days'}
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-1">
                Select fewer days to save on generation costs
              </p>
            </div>
          </div>
        ) : (
          // Manual Input Mode
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Business Name *
              </label>
              <input
                type="text"
                required
                value={formData.business_name}
                onChange={(e) =>
                  setFormData({ ...formData, business_name: e.target.value })
                }
                placeholder="Your Business Name"
                className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg focus:border-primary focus:ring-1 focus:ring-primary outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Industry *
              </label>
              <input
                type="text"
                required
                value={formData.industry}
                onChange={(e) =>
                  setFormData({ ...formData, industry: e.target.value })
                }
                placeholder="e.g., Restaurant, Retail, Services"
                className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg focus:border-primary focus:ring-1 focus:ring-primary outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Brief Description *
              </label>
              <textarea
                required
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                placeholder="Tell us about your business..."
                rows={4}
                className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg focus:border-primary focus:ring-1 focus:ring-primary outline-none"
              />
            </div>
          </div>
        )}

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
          {loading ? 'Generating Content...' : 'Generate Content'}
        </Button>
      </form>
    </div>
  )
}

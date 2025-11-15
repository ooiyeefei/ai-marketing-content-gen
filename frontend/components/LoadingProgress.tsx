'use client'

import CircularProgress from '@mui/material/CircularProgress'
import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography'

interface LoadingProgressProps {
  progress: number
  currentStep: string
}

export default function LoadingProgress({ progress, currentStep }: LoadingProgressProps) {
  const steps = [
    { icon: '🔍', label: 'Analyzing your website', color: '#4285F4' },
    { icon: '📍', label: 'Discovering your business', color: '#34A853' },
    { icon: '📊', label: 'Understanding local trends', color: '#FBBC04' },
    { icon: '🤖', label: 'Agents creating content', color: '#EA4335' },
    { icon: '🎬', label: 'Generating videos', color: '#9C27B0' },
  ]

  return (
    <div className="max-w-3xl mx-auto p-6">
      {/* Header with animated spinner */}
      <div className="text-center mb-12">
        <Box sx={{ position: 'relative', display: 'inline-flex', mb: 3 }}>
          <CircularProgress
            variant="determinate"
            value={progress}
            size={120}
            thickness={4}
            sx={{
              color: '#4285F4',
              '& .MuiCircularProgress-circle': {
                strokeLinecap: 'round',
              },
            }}
          />
          <Box
            sx={{
              top: 0,
              left: 0,
              bottom: 0,
              right: 0,
              position: 'absolute',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexDirection: 'column',
            }}
          >
            <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: '#4285F4' }}>
              {progress}%
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary', fontSize: '0.7rem' }}>
              Complete
            </Typography>
          </Box>
        </Box>

        <Typography variant="h5" sx={{ fontWeight: 600, mb: 1, color: 'text.primary' }}>
          Creating Your Content
        </Typography>
        <Typography variant="body1" sx={{ color: 'text.secondary', fontStyle: 'italic' }}>
          {currentStep}
        </Typography>
      </div>

      {/* Enhanced Progress Bar */}
      <div className="mb-10">
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden shadow-inner">
          <div
            className="h-full transition-all duration-700 ease-out rounded-full"
            style={{
              width: `${progress}%`,
              background: 'linear-gradient(90deg, #4285F4 0%, #34A853 33%, #FBBC04 66%, #EA4335 100%)',
              boxShadow: '0 2px 8px rgba(66, 133, 244, 0.4)',
            }}
          />
        </div>
      </div>

      {/* Enhanced Progress Steps */}
      <div className="space-y-3">
        {steps.map((step, index) => {
          const stepProgress = (index / steps.length) * 100
          const isActive = progress >= stepProgress
          const isComplete = progress > stepProgress + 15

          return (
            <div
              key={index}
              className={`flex items-center gap-4 p-5 rounded-xl border-2 transition-all duration-500 transform ${
                isActive
                  ? 'border-primary bg-blue-50 shadow-lg scale-105'
                  : 'border-gray-200 bg-white opacity-60'
              }`}
              style={{
                borderColor: isActive ? step.color : undefined,
              }}
            >
              <div
                className={`text-3xl transition-transform duration-300 ${
                  isActive ? 'animate-bounce' : ''
                }`}
              >
                {step.icon}
              </div>
              <div className="flex-1">
                <Typography
                  variant="body1"
                  sx={{
                    fontWeight: isActive ? 600 : 400,
                    color: isActive ? 'text.primary' : 'text.secondary',
                    transition: 'all 0.3s',
                  }}
                >
                  {step.label}
                </Typography>
              </div>
              {isComplete && (
                <div className="flex items-center gap-2">
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center animate-pulse"
                    style={{ backgroundColor: step.color }}
                  >
                    <span className="text-white font-bold">✓</span>
                  </div>
                </div>
              )}
              {isActive && !isComplete && (
                <CircularProgress size={24} sx={{ color: step.color }} />
              )}
            </div>
          )
        })}
      </div>

      {/* Fun loading message */}
      <div className="mt-8 text-center">
        <Typography variant="body2" sx={{ color: 'text.secondary', fontStyle: 'italic' }}>
          ✨ Our AI agents are working their magic...
        </Typography>
      </div>
    </div>
  )
}

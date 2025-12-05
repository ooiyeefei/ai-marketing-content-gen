'use client'

import { DayContent } from '@/types'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Button from '@mui/material/Button'
import Chip from '@mui/material/Chip'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'

interface ContentCardProps {
  post: DayContent
}

export default function ContentCard({ post }: ContentCardProps) {
  const copyCaption = () => {
    navigator.clipboard.writeText(post.caption)
    alert('Caption copied!')
  }

  const downloadImage = () => {
    if (post.image_url) {
      window.open(post.image_url, '_blank')
    }
  }

  const downloadVideo = () => {
    if (post.video_url) {
      window.open(post.video_url, '_blank')
    }
  }

  return (
    <Card elevation={3} sx={{ bgcolor: 'white', border: 1, borderColor: 'grey.300' }}>
      {/* Media Display */}
      {post.video_url ? (
        <Box sx={{ position: 'relative', aspectRatio: '16/9', bgcolor: 'grey.100' }}>
          <video
            controls
            style={{ width: '100%', height: '100%' }}
            src={post.video_url}
          >
            Your browser does not support the video tag.
          </video>
        </Box>
      ) : post.image_url ? (
        <Box sx={{ position: 'relative', aspectRatio: '1/1', bgcolor: 'grey.100' }}>
          <img
            src={post.image_url}
            alt={`Day ${post.day} content`}
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
        </Box>
      ) : (
        <Box
          sx={{
            aspectRatio: '1/1',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: 'grey.100',
            color: 'grey.600',
          }}
        >
          No media available
        </Box>
      )}

      {/* Content Details */}
      <CardContent>
        {/* Day Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h5" component="span" color="primary" fontWeight="bold">
              Day {post.day}
            </Typography>
            <Typography component="span" color="grey.400">
              •
            </Typography>
            <Typography component="span" color="grey.600" sx={{ textTransform: 'capitalize' }}>
              {post.content_type}
            </Typography>
          </Box>
          <Chip
            label={post.scheduled_time}
            size="small"
            color="primary"
            variant="outlined"
          />
        </Box>

        {/* Theme */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle1" fontWeight="medium" color="grey.900" sx={{ mb: 0.5 }}>
            Theme: {post.theme}
          </Typography>
        </Box>

        {/* Caption */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="subtitle1" fontWeight="medium" color="grey.900">
              Caption
            </Typography>
            <Button
              onClick={copyCaption}
              size="small"
              color="primary"
            >
              Copy
            </Button>
          </Box>
          <Typography variant="body2" color="grey.700" sx={{ whiteSpace: 'pre-wrap' }}>
            {post.caption}
          </Typography>
        </Box>

        {/* CTA */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" fontWeight="medium" color="grey.900">
            CTA: {post.cta}
          </Typography>
        </Box>

        {/* Hashtags */}
        {post.hashtags.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" fontWeight="medium" color="grey.900" sx={{ mb: 1 }}>
              Hashtags
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {post.hashtags.map((tag, index) => (
                <Chip
                  key={index}
                  label={tag}
                  color="primary"
                  variant="outlined"
                  size="small"
                />
              ))}
            </Box>
          </Box>
        )}

        {/* Download Options */}
        <Box>
          <Typography variant="subtitle1" fontWeight="medium" color="grey.900" sx={{ mb: 1 }}>
            Download
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {post.video_url && (
              <Button
                onClick={downloadVideo}
                variant="outlined"
                size="small"
              >
                Video
              </Button>
            )}
            {post.image_url && (
              <Button
                onClick={downloadImage}
                variant="outlined"
                color="primary"
                size="small"
              >
                Image
              </Button>
            )}
            <Button
              onClick={copyCaption}
              variant="outlined"
              size="small"
            >
              Caption
            </Button>
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
}

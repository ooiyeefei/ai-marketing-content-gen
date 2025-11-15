'use client'

import { useState } from 'react'
import { ContentPost } from '@/types'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Button from '@mui/material/Button'
import Chip from '@mui/material/Chip'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'

interface ContentCardProps {
  post: ContentPost
}

export default function ContentCard({ post }: ContentCardProps) {
  const [activeSegment, setActiveSegment] = useState(0)
  const [activeImage, setActiveImage] = useState(0)

  const copyCaption = () => {
    navigator.clipboard.writeText(post.caption)
    alert('Caption copied!')
  }

  const downloadSegment = (uri: string, segmentNumber: number) => {
    // In production, this would trigger download from GCS
    window.open(uri, '_blank')
  }

  const downloadImage = (uri: string, segmentNumber: number) => {
    // In production, this would trigger download from GCS
    window.open(uri, '_blank')
  }

  return (
    <Card elevation={3} sx={{ bgcolor: 'white', border: 1, borderColor: 'grey.300' }}>
      {/* Video Player */}
      <Box sx={{ position: 'relative', aspectRatio: '16/9', bgcolor: 'grey.100' }}>
        {post.video_segments.length > 0 ? (
          <>
            <video
              key={activeSegment}
              controls
              style={{ width: '100%', height: '100%' }}
              src={post.video_segments[activeSegment].uri}
            >
              Your browser does not support the video tag.
            </video>

            {/* Segment Selector */}
            {post.video_segments.length > 1 && (
              <Box
                sx={{
                  position: 'absolute',
                  bottom: 16,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  display: 'flex',
                  gap: 1,
                }}
              >
                {post.video_segments.map((segment, index) => (
                  <Button
                    key={segment.segment_number}
                    onClick={() => setActiveSegment(index)}
                    variant={activeSegment === index ? 'contained' : 'outlined'}
                    color="primary"
                    size="small"
                  >
                    Seg {segment.segment_number}
                  </Button>
                ))}
              </Box>
            )}
          </>
        ) : (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              color: 'grey.600',
            }}
          >
            No video available
          </Box>
        )}
      </Box>

      {/* Image Gallery */}
      {post.image_segments && post.image_segments.length > 0 && (
        <Box sx={{ position: 'relative', aspectRatio: '1/1', bgcolor: 'grey.100', borderTop: 1, borderColor: 'grey.300' }}>
          <img
            key={activeImage}
            src={post.image_segments[activeImage].uri}
            alt={`Generated image ${activeImage + 1}`}
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />

          {/* Image Selector */}
          {post.image_segments.length > 1 && (
            <Box
              sx={{
                position: 'absolute',
                bottom: 16,
                left: '50%',
                transform: 'translateX(-50%)',
                display: 'flex',
                gap: 1,
              }}
            >
              {post.image_segments.map((image, index) => (
                <Button
                  key={image.segment_number}
                  onClick={() => setActiveImage(index)}
                  variant={activeImage === index ? 'contained' : 'outlined'}
                  color="primary"
                  size="small"
                >
                  Img {image.segment_number}
                </Button>
              ))}
            </Box>
          )}
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
              {post.platform}
            </Typography>
          </Box>
          <Typography variant="body2" color="grey.600">
            {post.total_duration_seconds}s total
            {post.video_segments.length > 1 &&
              ` (${post.video_segments.length} segments)`}
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
            {post.video_segments.map((segment) => (
              <Button
                key={segment.segment_number}
                onClick={() =>
                  downloadSegment(segment.uri, segment.segment_number)
                }
                variant="outlined"
                size="small"
              >
                Video {segment.segment_number}
              </Button>
            ))}
            {post.image_segments && post.image_segments.map((image) => (
              <Button
                key={`img-${image.segment_number}`}
                onClick={() =>
                  downloadImage(image.uri, image.segment_number)
                }
                variant="outlined"
                color="primary"
                size="small"
              >
                Image {image.segment_number}
              </Button>
            ))}
            <Button
              onClick={copyCaption}
              variant="outlined"
              size="small"
            >
              Caption (.txt)
            </Button>
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
}

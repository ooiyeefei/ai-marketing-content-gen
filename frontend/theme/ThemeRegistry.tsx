'use client'

import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { googleTheme } from './google-theme'

export default function ThemeRegistry({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ThemeProvider theme={googleTheme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  )
}

import { createTheme } from '@mui/material/styles';

export const googleTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#4285F4',  // Google Blue
    },
    secondary: {
      main: '#34A853',  // Google Green
    },
    error: {
      main: '#EA4335',  // Google Red
    },
    warning: {
      main: '#FBBC04',  // Google Yellow
    },
    background: {
      default: '#FFFFFF',
      paper: '#F8F9FA',
    },
    text: {
      primary: '#202124',
      secondary: '#5F6368',
    },
  },
  typography: {
    fontFamily: '"Google Sans", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

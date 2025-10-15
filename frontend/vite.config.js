/* eslint-env node */
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Get API URL from environment variable or use default
const apiUrl = process.env.VITE_API_URL || 'http://127.0.0.1:5000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Allow connections from outside the container
    proxy: {
      '/api': {
        target: apiUrl,
        changeOrigin: true,
        secure: false,
      }
    }
  },
  // Define environment variables to be used in the app
  define: {
    'process.env.VITE_API_URL': JSON.stringify(apiUrl)
  }
})

import { defineNitroConfig } from 'nitro/config'

export default defineNitroConfig({
  routeRules: {
    // Proxy all /api/** requests to Django backend
    '/api/**': {
      proxy: `${process.env.API_URL || 'http://localhost:8000'}/**`,
    },
    // Proxy Django media files (uploaded images)
    '/media/**': {
      proxy: `${process.env.API_URL || 'http://localhost:8000'}/media/**`,
    },
  },
})

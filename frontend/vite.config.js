import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    // While developing, send every /api/... request to the FastAPI backend.
    // The browser then sees one single origin, so no CORS setup is needed.
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
})

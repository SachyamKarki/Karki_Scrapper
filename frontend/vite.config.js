import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// VITE_PROXY_TARGET: Backend URL for dev proxy (default localhost:5555). Not used in production build.
const proxyTarget = process.env.VITE_PROXY_TARGET || 'http://127.0.0.1:5555'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': { target: proxyTarget, changeOrigin: true },
      '/auth': { target: proxyTarget, changeOrigin: true },
      '/admin': { target: proxyTarget, changeOrigin: true },
      '/messages': { target: proxyTarget, changeOrigin: true },
      '/socket.io': { target: proxyTarget, ws: true },
    }
  }
})

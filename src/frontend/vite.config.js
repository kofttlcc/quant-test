import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 8888,
    proxy: {
      '/api/v1': {
        target: 'http://127.0.0.1:666',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})

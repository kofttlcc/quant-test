import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd() + '/../../', '')
  const BACKEND_URL = env.BACKEND_URL || 'http://localhost:666'
  const FRONTEND_PORT = parseInt(env.FRONTEND_PORT) || 8888

  return {
    plugins: [react()],
    // Load env from project root
    envDir: '../../',
    server: {
      port: FRONTEND_PORT,
      proxy: {
        '/api/v1': {
          target: BACKEND_URL,
          changeOrigin: true,
          secure: false,
        }
      }
    }
  }
})

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 获取后端地址，默认 localhost
const target = process.env.VITE_API_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: target,
        changeOrigin: true,
        ws: true
      }
    }
  }
})

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 后端 API 地址
const target = 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    host: '0.0.0.0',  // 允许外部访问
    proxy: {
      '/api': {
        target: target,
        changeOrigin: true,
        ws: true
      }
    }
  }
})

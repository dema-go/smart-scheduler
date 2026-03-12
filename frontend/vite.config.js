import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// WSL 环境下使用 WSL 的 IP，Windows 环境使用 localhost
// 根据 VITE_API_TARGET 环境变量动态配置
const target = process.env.VITE_API_TARGET || 'http://127.0.0.1:8000'

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

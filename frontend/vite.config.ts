import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_')

  return {
    envDir: '../',
    plugins: [
      vue(),
      vueDevTools(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    server: {
      host: env.VITE_HOST || '0.0.0.0',
      port: Number(env.VITE_PORT) || 3000,
      proxy: {
        '/api': {
          target: env.VITE_BACKEND_URL || 'http://127.0.0.1:8001',
          changeOrigin: true,
          configure: (proxy) => {
            proxy.on('proxyReq', (proxyReq) => {
              // Django APPEND_SLASH 要求 POST URL 以 / 结尾，在 proxy 层补上
              if (proxyReq.path && !proxyReq.path.includes('?') && !proxyReq.path.endsWith('/')) {
                proxyReq.path += '/'
              } else if (proxyReq.path) {
                const q = proxyReq.path.indexOf('?')
                if (q > 0 && !proxyReq.path.substring(0, q).endsWith('/')) {
                  proxyReq.path = proxyReq.path.substring(0, q) + '/' + proxyReq.path.substring(q)
                }
              }
            })
          },
        },
      },
    },
  }
})

import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const envDir = fileURLToPath(new URL('../', import.meta.url))
  const env = loadEnv(mode, envDir, 'VITE_')

  return {
    envDir,
    plugins: [
      vue(),
      vueDevTools(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      host: env.VITE_HOST || '0.0.0.0',
      port: Number(env.VITE_PORT) || 3000,
      proxy: {
        '/api': {
          target: env.VITE_BACKEND_URL || 'http://127.0.0.1:8001',
          changeOrigin: true,
          rewrite: (path) => {
            const queryIndex = path.indexOf('?')
            const pathname = queryIndex >= 0 ? path.slice(0, queryIndex) : path
            const query = queryIndex >= 0 ? path.slice(queryIndex) : ''
            return pathname.endsWith('/') ? path : `${pathname}/${query}`
          },
        },
        '/media': {
          target: env.VITE_BACKEND_URL || 'http://127.0.0.1:8001',
          changeOrigin: true,
        },
      },
    },
  }
})

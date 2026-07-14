import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import path from 'node:path'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icons/apple-touch-icon.png', 'icons/adam.svg'],
      manifest: {
        name: 'Adam — Panel Opiekuna',
        short_name: 'Adam',
        description: 'Adam — cyfrowy opiekun seniora. SilverTech, Poznań.',
        lang: 'pl',
        theme_color: '#1a2744',
        background_color: '#fbfaf7',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/panel',
        scope: '/',
        icons: [
          { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: '/icons/maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,woff2}'],
        navigateFallback: '/index.html',
        runtimeCaching: [
          {
            urlPattern: ({ url }) => url.origin === 'https://fonts.googleapis.com' || url.origin === 'https://fonts.gstatic.com',
            handler: 'CacheFirst',
            options: { cacheName: 'google-fonts', expiration: { maxEntries: 20, maxAgeSeconds: 60 * 60 * 24 * 365 } },
          },
        ],
      },
      devOptions: { enabled: false },
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    // Zezwól na hosty sandboxa/podglądu (novita/e2b) + dowolne subdomeny
    allowedHosts: ['.sandbox.novita.ai', '.e2b.dev', '.e2b.app', 'localhost'],
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})

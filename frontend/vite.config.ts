import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'

export default defineConfig({
  plugins: [react()],
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

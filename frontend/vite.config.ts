import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './',
  server: {
    port: 5173
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
    // Use different port for test server to avoid conflicts with dev server (5173)
    server: {
      port: 15173,
    },
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/.git/**',
      '**/*integration*.test.{ts,tsx}',
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/dist/',
        '**/build/',
        '**/*integration*.test.{ts,tsx}',
      ],
    },
  },
})

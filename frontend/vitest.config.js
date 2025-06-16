import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.js'],
    css: true,
    include: [
      'src/**/*.{test,spec}.{js,jsx,ts,tsx}'
    ],
    exclude: [
      'node_modules/',
      'tests/e2e/**',
      'playwright-report/**',
      'test-results/**',
      'dist/',
      'build/'
    ],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/tests/',
        'tests/e2e/**',
        '**/*.config.js',
        '**/*.config.ts',
        'dist/',
        'build/'
      ]
    }
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  }
})

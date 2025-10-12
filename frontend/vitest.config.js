/**
 * Vitest Configuration
 * 
 * Configuration for running component tests with Vitest
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/tests/setup.js',
    css: true,
    include: ['tests/kits/**/*.test.{js,jsx}'],
    exclude: [
      'node_modules/**',
      'tests/e2e/**',
      'src/tests/**',
      'src/components/**/**.test.{js,jsx}',
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/tests/',
        '**/*.test.{js,jsx}',
        '**/*.config.{js,jsx}',
        '**/dist/**',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});


import { cp, mkdir } from 'node:fs/promises'
import { resolve } from 'node:path'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

function copyConfirmedMedia() {
  return {
    name: 'copy-confirmed-media',
    apply: 'build',
    async closeBundle() {
      const source = resolve('../backend/media/activities/confirmed')
      const destination = resolve('dist/media/activities/confirmed')
      await mkdir(destination, { recursive: true })
      await cp(source, destination, { recursive: true, force: true })
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  envDir: '..',
  plugins: [vue(), copyConfirmedMedia()],
  server: {
    host: '127.0.0.1',
    port: 5173,
  },
})

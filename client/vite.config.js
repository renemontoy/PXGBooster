import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  base: '/',
  plugins: [react()],
  build: {
    outDir: 'dist' // esto asegura que Vite cree el directorio que Render espera
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // solo para desarrollo
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
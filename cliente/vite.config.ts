import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * Configuracion de Vite para la app cliente.
 *
 * El servidor de desarrollo escucha en el puerto 5173, que ya esta declarado en
 * CORS_ALLOWED_ORIGINS de Django. La URL de la API se toma de la variable de
 * entorno VITE_API_URL para que el mismo build sirva en desarrollo y en
 * produccion sin tocar el codigo.
 */
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    // Vite solo acepta peticiones dirigidas a localhost. Al exponer el
    // servidor de desarrollo por un tunel o una IP de red local, hay que
    // autorizar ese nombre; `allowsAnyHost` evita el error
    // "Blocked request. This host is not allowed" durante el desarrollo.
    // Esta opcion no afecta al build de produccion: solo aplica al servidor
    // de desarrollo, que nunca debe publicarse en internet.
    allowedHosts: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})

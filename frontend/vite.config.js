import path from 'path'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import frappeui from 'frappe-ui/vite'
import { VitePWA } from 'vite-plugin-pwa';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const frappeUrl = env.VITE_FRAPPE_URL

  // When VITE_FRAPPE_URL is set, disable the built-in localhost proxy and
  // replace it with one that points to the production ERPNext instance.
  const plugins = [
    frappeui({ frappeProxy: frappeUrl ? false : true, buildConfig: false }),
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      // Let Workbox decide what to precache from the build output
      includeAssets: ['logo.png', 'favicon.png', 'img/icons/*.png'],
      manifest: {
        name: 'Sales Live',
        short_name: 'Sales Live',
        description: 'Field sales companion powered by ERPNext',
        theme_color: '#1d4ed8',
        background_color: '#0f172a',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/frontend',
        scope: '/frontend',
        icons: [
          {
            src: '/assets/live/frontend/img/icons/android-chrome-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: '/assets/live/frontend/img/icons/android-chrome-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
          {
            src: '/assets/live/frontend/img/icons/android-chrome-maskable-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
        shortcuts: [
          {
            name: 'New Sales Order',
            url: '/frontend/add-sales-order',
            icons: [{ src: '/assets/live/frontend/img/icons/android-chrome-192x192.png', sizes: '192x192' }],
          },
        ],
      },
      workbox: {
        // Cache app shell assets with cache-first
        globPatterns: ['**/*.{js,css,html,png,svg,ico}'],
        // Never cache API or Frappe desk calls — always hit the network
        navigateFallbackDenylist: [/^\/api/, /^\/desk/, /^\/app/],
        runtimeCaching: [
          {
            // ERPNext API — network first, fallback to cache for offline reads
            urlPattern: /^https?:\/\/.*\/api\//,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              networkTimeoutSeconds: 10,
              expiration: { maxEntries: 50, maxAgeSeconds: 60 * 60 * 24 },
            },
          },
          {
            // Static assets (images, fonts) — cache first
            urlPattern: /\.(?:png|jpg|jpeg|svg|gif|woff2?)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'assets-cache',
              expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 30 },
            },
          },
        ],
      },
    }),
  ]

  const serverProxy = frappeUrl
    ? {
        '^/(desk|app|login|api|assets|files|private)': {
          target: frappeUrl,
          changeOrigin: true,
          ws: true,
          secure: true,
        },
      }
    : undefined

  return {
    plugins,
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
    build: {
      outDir: `../${path.basename(path.resolve('..'))}/public/frontend`,
      emptyOutDir: true,
      target: 'es2015',
    },
    optimizeDeps: {
      include: ['frappe-ui > feather-icons', 'showdown', 'engine.io-client'],
    },
    server: serverProxy ? { proxy: serverProxy } : undefined,
  }
})

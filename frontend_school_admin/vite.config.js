import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig(({ mode }) => {
  // ໂຫຼດ environment variables
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [
      vue(),
      VitePWA({
        registerType: 'autoUpdate',
        
        // ✅ 4. ເພີ່ມການຕັ້ງຄ່າ Workbox (ແກ້ໄຂບັນຫາ Route error)
        workbox: {
          // ໃຫ້ມັນ Cache ໄຟລ໌ເຫຼົ່ານີ້ໄວ້ໃຊ້ Offline
          globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
          
          // ຖ້າເຂົ້າ Route ທີ່ບໍ່ມີຈິງ ຫຼື Offline ໃຫ້ກັບໄປ index.html (ສຳຄັນສຳລັບ SPA)
          navigateFallback: '/index.html',
          
          // ❌ ຫ້າມ Cache ເສັ້ນທາງເຫຼົ່ານີ້ (API, ຮູບ Static, ແລະ ໄຟລ໌ນາມສະກຸນຕ່າງໆ)
          navigateFallbackDenylist: [/^\/api\//, /^\/static\//, /\.[a-z]+$/],
        },

        devOptions: {
          enabled: mode === 'development', 
          type: 'module',
        },
        manifest: {
          name: env.VITE_APP_TITLE || 'School Tracking', // ໃສ່ default ກັນພາດ
          short_name: 'School App',
          description: 'ລະບົບຕິດຕາມການຮຽນການສອນ',
          theme_color: '#1976D2',
          background_color: '#ffffff',
          display: 'standalone',
          icons: [
            {
              src: 'pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png',
              purpose: 'any maskable'
            },
            {
              src: 'pwa-512x512.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'any maskable'
            }
          ]
        }
      })
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
  }
})
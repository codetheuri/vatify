import { defineNuxtConfig } from 'nuxt/config'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  
  devtools: { enabled: true },

  // Enable Nuxt 4 features and directory structure
  future: {
    compatibilityVersion: 4,
  },

  css: ['~/assets/css/main.css'],

  app: {
    head: {
      title: 'Vatify - KRA Compliance Simplified',
      meta: [
        { name: 'description', content: 'Auto-reconcile M-Pesa statements with KRA eTIMS and file tax returns in seconds.' }
      ],
      link: [
        { rel: 'icon', type: 'image/png', href: '/favicon.png' }
      ]
    }
  }
})

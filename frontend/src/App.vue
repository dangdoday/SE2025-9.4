<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import NavBar from '@/components/layout/NavBar.vue'
import { useBotStore } from '@/stores/botStore'

const botStore = useBotStore()
const router = useRouter()
const route = useRoute()

// Pages that should NOT be cached
// Exclude all data-rich views to prevent stale data after user switch
const excludeFromCache = ['Home', 'Login', 'DashboardView', 'TradeView', 'Settings', 'ApiSettings']

// Check auth immediately (before mount)
// Clean up old localStorage tokens if present
localStorage.removeItem('bot_token')
localStorage.removeItem('bot_refresh_token')
botStore.checkAuth()

// Watch for auth state changes to redirect from login page
watch(() => botStore.isConnected, (connected) => {
  if (connected && route.name === 'Login') {
    router.push('/dashboard')
  }
})

onMounted(() => {
  // Any other mount logic
})
</script>

<template>
  <div class="min-h-screen bg-dark-300 dark-mode">
    <NavBar v-if="!['Home', 'Login'].includes(route.name as string)" />
    <main class="container mx-auto px-4 py-6">
      <router-view v-slot="{ Component, route: currentRoute }">
        <keep-alive :exclude="excludeFromCache">
          <component :is="Component" :key="currentRoute.path" />
        </keep-alive>
      </router-view>
    </main>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

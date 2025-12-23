<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBotStore } from '@/stores/botStore'
import { useSettingsStore } from '@/stores/settingsStore'
import { isAdminUser } from '@/utils/auth'

const router = useRouter()
const route = useRoute()
const botStore = useBotStore()
const settingsStore = useSettingsStore()

const isMobileMenuOpen = ref(false)

const baseNavItems = [
  { label: 'Dashboard', to: '/dashboard', icon: '📊' },
  { label: 'Trading', to: '/trade', icon: '💹' },
  { label: 'Charts', to: '/graph', icon: '📈' },
  { label: 'Settings', to: '/settings', icon: '⚙️' }
]
const isAdmin = computed(() => isAdminUser())
const navItems = computed(() => {
  const items = [...baseNavItems]
  if (isAdmin.value) {
    items.push({ label: 'Logs', to: '/logs', icon: '📝' })
  }
  return items
})

const isActive = (path: string) => route.path === path

// Check if we have botState data
const hasData = computed(() => botStore.botState !== null)

const statusColor = computed(() => {
  if (!hasData.value) return 'bg-gray-500'
  return botStore.isBotRunning ? 'bg-success' : 'bg-primary'
})

const statusText = computed(() => {
  if (!hasData.value) return 'Disconnected'
  return botStore.isBotRunning ? 'Running' : 'Stopped'
})

function toggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

function navigate(path: string) {
  router.push(path)
  isMobileMenuOpen.value = false
}

function logout() {
  botStore.disconnect()
  router.push('/')
}
</script>

<template>
  <nav class="bg-dark-50 border-b border-dark-50 sticky top-0 z-50">
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
            <span class="text-dark-300 font-bold text-xl">B</span>
          </div>
          <span class="text-xl font-bold text-white hidden sm:block">BinanceBot</span>
        </router-link>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center gap-1">
          <router-link
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
            :class="isActive(item.to) 
              ? 'bg-primary text-dark-300' 
              : 'text-gray-400 hover:text-white hover:bg-dark-100'"
          >
            {{ item.label }}
          </router-link>
        </div>

        <!-- Status & Actions -->
        <div class="flex items-center gap-3">
          <!-- Connection Status Badge -->
          <div class="hidden sm:flex items-center gap-2">
            <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-dark-100">
              <span class="w-2 h-2 rounded-full" :class="statusColor"></span>
              <span class="text-sm" :class="hasData ? (botStore.isBotRunning ? 'text-success' : 'text-danger') : 'text-gray-400'">{{ statusText }}</span>
            </div>
          </div>

          <!-- Balance & Buttons (always visible when connected) -->
          <div v-if="botStore.isConnected" class="flex items-center gap-3">
            <div class="text-right">
              <div class="text-xs text-gray-500">Balance</div>
              <div class="text-sm font-semibold text-primary">
                {{ botStore.totalBalance.toFixed(2) }} {{ botStore.stakeCurrency }}
              </div>
            </div>
            
            <!-- Management Dropdown / Buttons -->
            <button 
              @click="logout"
              class="px-3 py-1.5 text-xs font-bold uppercase tracking-wider rounded bg-danger/10 text-danger hover:bg-danger hover:text-white transition-all"
              title="Logout"
            >
              Logout
            </button>
          </div>
          
          <!-- Mobile menu button -->
          <button 
            @click="toggleMobileMenu"
            class="md:hidden p-2 rounded-lg hover:bg-dark-100 transition-colors"
          >
            <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!isMobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Navigation -->
      <div v-if="isMobileMenuOpen" class="md:hidden py-4 border-t border-dark-100">
        <div class="flex flex-col gap-1">
          <button
            v-for="item in navItems"
            :key="item.to"
            @click="navigate(item.to)"
            class="flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-all duration-200"
            :class="isActive(item.to) 
              ? 'bg-primary text-dark-300' 
              : 'text-gray-400 hover:text-white hover:bg-dark-100'"
          >
            <span>{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </button>
          <!-- Logout for Mobile -->
          <button @click="logout" class="flex items-center gap-3 px-4 py-3 rounded-lg text-left text-danger hover:bg-danger/10 transition-all">
            <span>🚪</span>
            <span>Logout</span>
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

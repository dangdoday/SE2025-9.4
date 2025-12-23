<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useBotStore } from '@/stores/botStore'
import TradeList from '@/components/ftbot/TradeList.vue'
import ForceEntryForm from '@/components/ftbot/ForceEntryForm.vue'
import BotControls from '@/components/ftbot/BotControls.vue'
import PairListLive from '@/components/ftbot/PairListLive.vue'
import { isAdminUser } from '@/utils/auth'

const botStore = useBotStore()
const activeTab = ref('open')
const showForceEntry = ref(false)
const isAdmin = computed(() => isAdminUser())
let refreshInterval: number | null = null

async function refreshTrades() {
  await botStore.fetchTrades()
  await botStore.fetchWhitelist()
}

onMounted(() => {
  refreshTrades()
  // Auto-refresh every 10 seconds
  refreshInterval = window.setInterval(refreshTrades, 10000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<template>
  <div class="space-y-6 fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div>
        <h1 class="text-2xl font-bold text-white">Trading</h1>
        <p class="text-gray-500 text-sm">Manage your active trades</p>
      </div>
      <div class="flex items-center gap-3">
        <button v-if="isAdmin" @click="showForceEntry = true" class="btn btn-primary">
          ➕ Force Entry
        </button>
        <button @click="refreshTrades" class="btn btn-outline">
          🔄 Refresh
        </button>
      </div>
    </div>

    <!-- Bot Controls -->
    <BotControls />

    <!-- Main Content -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- Trades Panel -->
      <div class="lg:col-span-3 space-y-4">
        <!-- Tabs -->
        <div class="flex gap-2 border-b border-dark-100 pb-2">
          <button 
            @click="activeTab = 'open'"
            class="px-4 py-2 rounded-t-lg font-medium transition-colors"
            :class="activeTab === 'open' 
              ? 'bg-primary text-dark-300' 
              : 'text-gray-400 hover:text-white'"
          >
            Open Trades ({{ botStore.openTrades.length }})
          </button>
          <button 
            @click="activeTab = 'closed'"
            class="px-4 py-2 rounded-t-lg font-medium transition-colors"
            :class="activeTab === 'closed' 
              ? 'bg-primary text-dark-300' 
              : 'text-gray-400 hover:text-white'"
          >
            Closed Trades ({{ botStore.closedTrades.length }})
          </button>
        </div>

        <!-- Trade List -->
        <div class="card">
          <TradeList 
            v-if="activeTab === 'open'"
            :trades="botStore.openTrades" 
            :is-open="true"
            show-actions
          />
          <TradeList 
            v-else
            :trades="botStore.closedTrades" 
            :is-open="false"
          />
        </div>
      </div>

      <!-- Sidebar - Pair List -->
      <div class="space-y-4">
        <PairListLive />
      </div>
    </div>

    <!-- Force Entry Dialog -->
    <Dialog 
      v-if="isAdmin"
      v-model:visible="showForceEntry" 
      header="Force Entry" 
      :modal="true"
      class="w-full max-w-md"
    >
      <ForceEntryForm @close="showForceEntry = false" />
    </Dialog>
  </div>
</template>

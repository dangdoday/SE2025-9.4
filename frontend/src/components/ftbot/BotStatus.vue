<script setup lang="ts">
import { computed } from 'vue'
import { useBotStore } from '@/stores/botStore'

const botStore = useBotStore()

// Check if we have botState data (meaning we're connected and have data)
const hasData = computed(() => botStore.botState !== null)

const statusClass = computed(() => {
  if (!hasData.value) return 'text-gray-500'
  return botStore.isBotRunning ? 'text-success' : 'text-danger'
})

const statusText = computed(() => {
  if (!hasData.value) return 'Disconnected'
  return botStore.isBotRunning ? 'Running' : 'Stopped'
})

const statusDot = computed(() => {
  if (!hasData.value) return 'bg-gray-500'
  return botStore.isBotRunning ? 'bg-success' : 'bg-danger'
})
</script>

<template>
  <div class="card">
    <div class="card-header">
      <span>🤖 Bot Status</span>
      <span class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full" :class="statusDot"></span>
        <span class="text-sm" :class="statusClass">{{ statusText }}</span>
      </span>
    </div>

    <div class="space-y-3">
      <div class="flex justify-between py-2 border-b border-dark-100">
        <span class="text-gray-500 text-sm">Mode</span>
        <span class="text-white text-sm">{{ botStore.botState?.dry_run ? 'Dry Run' : 'Live' }}</span>
      </div>
      <div class="flex justify-between py-2 border-b border-dark-100">
        <span class="text-gray-500 text-sm">Strategy</span>
        <span class="text-primary text-sm">{{ botStore.botState?.strategy || 'N/A' }}</span>
      </div>
      <div class="flex justify-between py-2 border-b border-dark-100">
        <span class="text-gray-500 text-sm">Open Trades</span>
        <span class="text-white text-sm">{{ botStore.openTradeCount }} / {{ botStore.botState?.max_open_trades || 3 }}</span>
      </div>
      <div class="flex justify-between py-2">
        <span class="text-gray-500 text-sm">Stake</span>
        <span class="text-white text-sm">{{ botStore.botState?.stake_amount || 100 }} USDT</span>
      </div>
    </div>
  </div>
</template>

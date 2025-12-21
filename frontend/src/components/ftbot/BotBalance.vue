<script setup lang="ts">
import { useBotStore } from '@/stores/botStore'

const botStore = useBotStore()
</script>

<template>
  <div class="card">
    <div class="card-header">
      <span>💰 Balance</span>
      <button @click="botStore.fetchBalance()" class="text-xs text-gray-500 hover:text-primary">
        🔄
      </button>
    </div>

    <div class="mb-4">
      <div class="text-3xl font-bold text-primary">
        {{ (botStore.totalBalance || 0).toFixed(2) }}
      </div>
      <div class="text-sm text-gray-500">USDT Total</div>
    </div>

    <div class="space-y-2">
      <div 
        v-for="b in (botStore.balance || []).slice(0, 5)" 
        :key="b.currency"
        class="flex justify-between items-center py-1 text-sm"
      >
        <span class="text-gray-400">{{ b.currency }}</span>
        <span class="text-white">{{ (b.balance || 0).toFixed(4) }}</span>
      </div>
      <div v-if="!botStore.balance || botStore.balance.length === 0" class="text-gray-500 text-sm text-center py-2">
        No balance data
      </div>
    </div>
  </div>
</template>


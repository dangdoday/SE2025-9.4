<script setup lang="ts">
import { useBotStore } from '@/stores/botStore'

const botStore = useBotStore()
</script>

<template>
  <div class="card">
    <div class="card-header">
      <span>📋 Pair Whitelist</span>
      <span class="badge badge-warning">{{ botStore.whitelist.length }}</span>
    </div>

    <div class="max-h-64 overflow-y-auto">
      <div 
        v-for="pair in botStore.whitelist" 
        :key="pair"
        class="flex items-center justify-between py-2 px-2 hover:bg-dark-100 rounded transition-colors"
      >
        <span class="text-sm text-white">{{ pair }}</span>
      </div>
      <div v-if="botStore.whitelist.length === 0" class="text-center py-4 text-gray-500 text-sm">
        No pairs in whitelist
      </div>
    </div>
  </div>
</template>

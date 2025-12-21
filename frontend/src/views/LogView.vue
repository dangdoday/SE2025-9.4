<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useBotStore } from '@/stores/botStore'

const botStore = useBotStore()
const autoScroll = ref(true)
const logContainer = ref<HTMLElement | null>(null)
let refreshInterval: number | null = null

onMounted(() => {
  botStore.fetchLogs()
  refreshInterval = window.setInterval(() => {
    botStore.fetchLogs()
  }, 5000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})

function scrollToBottom() {
  if (logContainer.value && autoScroll.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
}

function getLogClass(log: string) {
  if (log.includes('ERROR')) return 'text-danger'
  if (log.includes('WARNING')) return 'text-warning'
  if (log.includes('INFO')) return 'text-gray-400'
  return 'text-gray-500'
}
</script>

<template>
  <div class="space-y-6 fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white">Logs</h1>
        <p class="text-gray-500 text-sm">View bot activity logs</p>
      </div>
      <div class="flex items-center gap-4">
        <label class="flex items-center gap-2 text-sm text-gray-400">
          <input type="checkbox" v-model="autoScroll" class="rounded" />
          Auto-scroll
        </label>
        <button @click="botStore.fetchLogs()" class="btn btn-outline">
          🔄 Refresh
        </button>
      </div>
    </div>

    <!-- Log Viewer -->
    <div class="card p-0">
      <div 
        ref="logContainer"
        class="h-[calc(100vh-250px)] min-h-[400px] overflow-y-auto p-4 font-mono text-sm"
      >
        <div 
          v-for="(log, index) in botStore.logs" 
          :key="index"
          class="py-1 border-b border-dark-100 last:border-0"
          :class="getLogClass(log)"
        >
          {{ log }}
        </div>
        <div v-if="botStore.logs.length === 0" class="text-center py-12 text-gray-500">
          No logs available
        </div>
      </div>
    </div>
  </div>
</template>

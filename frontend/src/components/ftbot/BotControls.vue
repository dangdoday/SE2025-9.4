<script setup lang="ts">
import { ref } from 'vue'
import { useBotStore } from '@/stores/botStore'

const botStore = useBotStore()
const isLoading = ref(false)

async function handleStart() {
  isLoading.value = true
  try {
    await botStore.startBot()
  } finally {
    isLoading.value = false
  }
}

async function handleStop() {
  isLoading.value = true
  try {
    await botStore.stopBot()
  } finally {
    isLoading.value = false
  }
}

async function handleReloadConfig() {
  isLoading.value = true
  try {
    await botStore.refreshAll()
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="card">
    <div class="flex items-center justify-between gap-4 flex-wrap">
      <!-- Status -->
      <div class="flex items-center gap-3">
        <div 
          class="w-3 h-3 rounded-full"
          :class="botStore.isBotRunning ? 'bg-success pulse' : 'bg-danger'"
        ></div>
        <span class="font-medium" :class="botStore.isBotRunning ? 'text-success' : 'text-danger'">
          {{ botStore.isBotRunning ? 'Bot Running' : 'Bot Stopped' }}
        </span>
      </div>

      <!-- Controls -->
      <div class="flex gap-2">
        <button 
          v-if="!botStore.isBotRunning"
          @click="handleStart" 
          class="btn btn-success"
          :disabled="isLoading"
        >
          ▶ Start
        </button>
        <button 
          v-else
          @click="handleStop" 
          class="btn btn-danger"
          :disabled="isLoading"
        >
          ⏹ Stop
        </button>
        <button 
          @click="handleReloadConfig" 
          class="btn btn-outline"
          :disabled="isLoading"
        >
          🔄 Reload
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useBotStore } from '@/stores/botStore'

const botStore = useBotStore()
const hoveredItem = ref<any>(null)

const chartData = computed(() => {
  return botStore.dailyStats.map((d, i) => ({
    date: d.date,
    profit: d.abs_profit || 0,
    cumulative: botStore.dailyStats.slice(0, i + 1).reduce((sum, s) => sum + (s.abs_profit || 0), 0)
  }))
})

const maxProfit = computed(() => {
  const profits = chartData.value.map(d => Math.abs(d.profit))
  return Math.max(...profits, 1)
})
</script>

<template>
  <div class="h-48 relative group">
    <!-- Hover Info Overlay -->
    <div 
      v-if="hoveredItem" 
      class="absolute top-0 left-0 right-0 z-10 flex justify-center pointer-events-none"
    >
      <div class="bg-gray-800 text-xs px-2 py-1 rounded shadow border border-gray-700 opacity-90">
        <span class="font-bold text-gray-300">{{ hoveredItem.date }}: </span>
        <span :class="hoveredItem.profit >= 0 ? 'text-success' : 'text-danger'">
          {{ hoveredItem.profit >= 0 ? '+' : ''}}{{ hoveredItem.profit.toFixed(2) }} USDT
        </span>
      </div>
    </div>

    <div v-if="chartData.length > 0" class="h-full flex items-end gap-1 pt-6">
      <div 
        v-for="(d, i) in chartData.slice(-14)" 
        :key="i"
        class="flex-1 flex flex-col justify-end h-full hover:bg-white/5 rounded transition-colors"
        @mouseenter="hoveredItem = d"
        @mouseleave="hoveredItem = null"
      >
        <div class="flex-1 flex items-end justify-center w-full">
            <div 
            class="w-full mx-0.5 rounded-t transition-all duration-300"
            :class="d.profit >= 0 ? 'bg-success' : 'bg-danger'"
            :style="{ height: `${Math.min((Math.abs(d.profit) / maxProfit) * 100, 100)}%`, minHeight: '4px' }"
            ></div>
        </div>
        
        <div class="text-[10px] text-gray-500 text-center mt-1 truncate" :class="{'text-white font-bold': hoveredItem === d}">
          {{ d.date.slice(5) }}
        </div>
      </div>
    </div>
    <div v-else class="h-full flex items-center justify-center text-gray-500 text-sm">
      No profit data available
    </div>
  </div>
</template>

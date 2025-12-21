<script setup lang="ts">
import { computed } from 'vue'
import { useBotStore } from '@/stores/botStore'

const botStore = useBotStore()

const chartData = computed(() => {
  return botStore.dailyStats.map((d, i) => ({
    date: d.date,
    profit: d.profit_abs || 0,
    cumulative: botStore.dailyStats.slice(0, i + 1).reduce((sum, s) => sum + (s.profit_abs || 0), 0)
  }))
})

const maxProfit = computed(() => {
  const cumulative = chartData.value.map(d => d.cumulative)
  return Math.max(...cumulative, 1)
})
</script>

<template>
  <div class="h-48">
    <div v-if="chartData.length > 0" class="h-full flex items-end gap-1">
      <div 
        v-for="(d, i) in chartData.slice(-14)" 
        :key="i"
        class="flex-1 flex flex-col justify-end"
      >
        <div 
          class="rounded-t transition-all duration-300"
          :class="d.profit >= 0 ? 'bg-success' : 'bg-danger'"
          :style="{ height: `${Math.abs(d.profit) / maxProfit * 100}%`, minHeight: '4px' }"
        ></div>
        <div class="text-[10px] text-gray-500 text-center mt-1 truncate">
          {{ d.date.slice(5) }}
        </div>
      </div>
    </div>
    <div v-else class="h-full flex items-center justify-center text-gray-500 text-sm">
      No profit data available
    </div>
  </div>
</template>

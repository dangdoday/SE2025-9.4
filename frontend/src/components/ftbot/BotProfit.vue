<script setup lang="ts">
import { computed } from 'vue'
import { useBotStore } from '@/stores/botStore'

const botStore = useBotStore()

const profitClass = computed(() => {
  const profit = botStore.totalProfit
  if (profit > 0) return 'text-success'
  if (profit < 0) return 'text-danger'
  return 'text-white'
})

const todayProfit = computed(() => {
  if (!botStore.dailyStats || botStore.dailyStats.length === 0) return 0
  
  const today = new Date().toISOString().split('T')[0]
  const todayStat = botStore.dailyStats.find((d: any) => d.date === today)
  return todayStat ? todayStat.abs_profit : 0
})

const weekProfit = computed(() => {
  if (!botStore.dailyStats || botStore.dailyStats.length === 0) return 0
  
  // Calculate profit for current ISO week or just last 7 days? 
  // "This Week" usually implies the current week (Mon-Sun).
  // But for simple "Recent performance", last 7 days is often used.
  // Let's use last 7 days for consistency with typical dashboard view.
  // Actually, 'dailyStats' is a list of days. I'll just sum the last 7 entries IF they are within 7 days.
  // Better: Filter by date >= 7 days ago.
  
  const sevenDaysAgo = new Date()
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
  const cutoff = sevenDaysAgo.toISOString().split('T')[0]
  
  return botStore.dailyStats
    .filter((d: any) => d.date >= cutoff)
    .reduce((sum: number, d: any) => sum + d.abs_profit, 0)
})

function formatProfit(value: number) {
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}`
}

function getProfitColor(value: number) {
  if (value > 0) return 'text-success'
  if (value < 0) return 'text-danger'
  return 'text-gray-400' // or default color
}
</script>

<template>
  <div class="card">
    <div class="card-header">
      <span>📈 Profit</span>
      <button @click="botStore.fetchProfit()" class="text-xs text-gray-500 hover:text-primary">
        🔄
      </button>
    </div>

    <div class="mb-4">
      <div class="text-3xl font-bold" :class="profitClass">
        {{ botStore.totalProfit >= 0 ? '+' : '' }}{{ botStore.totalProfit.toFixed(2) }}
      </div>
      <div class="text-sm text-gray-500">USDT Total Profit</div>
    </div>

    <div class="space-y-2 text-sm">
      <div class="flex justify-between py-1 border-b border-dark-100">
        <span class="text-gray-500">Today</span>
        <span :class="getProfitColor(todayProfit)">{{ formatProfit(todayProfit) }}</span>
      </div>
      <div class="flex justify-between py-1 border-b border-dark-100">
        <span class="text-gray-500">Last 7 Days</span>
        <span :class="getProfitColor(weekProfit)">{{ formatProfit(weekProfit) }}</span>
      </div>
      <div class="flex justify-between py-1 border-b border-dark-100">
        <span class="text-gray-500">Win Rate</span>
        <span class="text-primary">{{ botStore.winRate }}%</span>
      </div>
      <div class="flex justify-between py-1">
        <span class="text-gray-500">Closed Trades</span>
        <span class="text-white">{{ botStore.profit?.closed_trade_count || 0 }}</span>
      </div>
    </div>
  </div>
</template>

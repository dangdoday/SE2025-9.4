<script setup lang="ts">
import { onMounted, onUnmounted, onActivated, computed, ref } from 'vue'
import { useBotStore } from '@/stores/botStore'
import { botApi } from '@/api/api'
import BotStatus from '@/components/ftbot/BotStatus.vue'
import BotBalance from '@/components/ftbot/BotBalance.vue'
import BotProfit from '@/components/ftbot/BotProfit.vue'
import TradeList from '@/components/ftbot/TradeList.vue'
import PeriodBreakdown from '@/components/ftbot/PeriodBreakdown.vue'

const botStore = useBotStore()
const isRefreshing = ref(false)
let refreshInterval: number | null = null

async function refresh() {
  if (isRefreshing.value) return
  isRefreshing.value = true
  try {
    await botStore.refreshAll()
  } catch (e) {
    console.error('Refresh error:', e)
  } finally {
    isRefreshing.value = false
  }
}

function startAutoRefresh() {
  if (!refreshInterval) {
    refreshInterval = window.setInterval(refresh, 10000)
  }
}

function stopAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

onMounted(() => {
  refresh()
  startAutoRefresh()
})

// Called when component is activated from keep-alive cache
onActivated(() => {
  refresh()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})

const profitClass = computed(() => {
  const profit = botStore.totalProfit
  if (profit > 0) return 'text-success'
  if (profit < 0) return 'text-danger'
  return 'text-white'
})
</script>

<template>
  <div class="space-y-6 fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div>
        <h1 class="text-2xl font-bold text-white">Dashboard</h1>
        <p class="text-gray-500 text-sm mt-1">Live Trading on Binance Spot</p>
      </div>
      <div class="flex gap-2">
        <button @click="botStore.refreshAll()" :disabled="isRefreshing" class="btn btn-outline">
          🔄 Refresh
        </button>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Total Balance -->
      <div class="card">
        <div class="flex items-center justify-between mb-2">
          <span class="text-gray-500 text-sm">Total Balance</span>
          <span class="text-primary">💰</span>
        </div>
        <div class="stat-value text-primary">
          {{ botStore.totalBalance.toFixed(2) }}
        </div>
        <div class="text-xs text-gray-500 mt-1">USDT</div>
      </div>

      <!-- Total Profit -->
      <div class="card">
        <div class="flex items-center justify-between mb-2">
          <span class="text-gray-500 text-sm">Total Profit</span>
          <span class="text-success">📈</span>
        </div>
        <div class="stat-value" :class="profitClass">
          {{ botStore.totalProfit >= 0 ? '+' : '' }}{{ botStore.totalProfit.toFixed(2) }}
        </div>
        <div class="text-xs text-gray-500 mt-1">USDT</div>
      </div>

      <!-- Win Rate -->
      <div class="card">
        <div class="flex items-center justify-between mb-2">
          <span class="text-gray-500 text-sm">Win Rate</span>
          <span class="text-success">🎯</span>
        </div>
        <div class="stat-value text-success">
          {{ botStore.winRate }}%
        </div>
        <div class="text-xs text-gray-500 mt-1">of closed trades</div>
      </div>

      <!-- Open Trades -->
      <div class="card">
        <div class="flex items-center justify-between mb-2">
          <span class="text-gray-500 text-sm">Open Trades</span>
          <span class="text-primary">📊</span>
        </div>
        <div class="stat-value text-white">
          {{ botStore.openTradeCount }}
        </div>
        <div class="text-xs text-gray-500 mt-1">active positions</div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left Column - Charts -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Profit Over Time -->
        <div class="card">
          <div class="card-header">
            <span>📈 Profit Over Time</span>
          </div>
          <PeriodBreakdown />
        </div>

        <!-- Open Trades -->
        <div class="card">
          <div class="card-header">
            <span>💹 Open Trades</span>
            <span class="badge badge-warning">{{ botStore.openTradeCount }}</span>
          </div>
          <TradeList :trades="botStore.openTrades" :is-open="true" />
        </div>
      </div>

      <!-- Right Column - Status & Info -->
      <div class="space-y-6">
        <!-- Bot Status -->
        <BotStatus />

        <!-- Balance -->
        <BotBalance />

        <!-- Quick Profit -->
        <BotProfit />
      </div>
    </div>

    <!-- Recent Closed Trades -->
    <div class="card">
      <div class="card-header">
        <span>📋 Recent Closed Trades</span>
        <router-link to="/trade" class="text-primary text-sm hover:underline">
          View All →
        </router-link>
      </div>
      <TradeList :trades="botStore.closedTrades.slice(0, 10)" :is-open="false" />
    </div>
  </div>
</template>

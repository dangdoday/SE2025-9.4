<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useBotStore } from '@/stores/botStore'
import { botApi } from '@/api/api'
import CumProfitChart from '@/components/charts/CumProfitChart.vue'

const botStore = useBotStore()

// Form state
const strategy = ref('RSI_EMA')
const timeframe = ref('4h')
const startDate = ref('2023-01-01')
const endDate = ref('2025-01-01')
const isRunning = ref(false)
const progress = ref(0)
const results = ref<any>(null)

const strategies = ref<string[]>([])
const timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']

onMounted(async () => {
  await botStore.fetchStrategies()
  strategies.value = botStore.strategies
})

async function runBacktest() {
  isRunning.value = true
  progress.value = 0
  results.value = null

  try {
    const config = {
      strategy: strategy.value,
      timeframe: timeframe.value,
      timerange: `${startDate.value.replace(/-/g, '')}-${endDate.value.replace(/-/g, '')}`
    }

    // Start backtest
    await botApi.backtest(config)

    // Poll for results
    const pollInterval = setInterval(async () => {
      try {
        const res = await botApi.backtestStatus()
        progress.value = res.data.progress || 0
        
        if (res.data.status === 'ended') {
          clearInterval(pollInterval)
          results.value = res.data
          isRunning.value = false
        }
      } catch (e) {
        clearInterval(pollInterval)
        isRunning.value = false
      }
    }, 1000)

  } catch (error) {
    console.error('Backtest failed:', error)
    isRunning.value = false
  }
}

async function abortBacktest() {
  try {
    await botApi.backtestAbort()
    isRunning.value = false
    progress.value = 0
  } catch (error) {
    console.error('Failed to abort:', error)
  }
}
</script>

<template>
  <div class="space-y-6 fade-in">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-white">Backtesting</h1>
      <p class="text-gray-500 text-sm">Test your strategy with historical data</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Configuration Panel -->
      <div class="card">
        <div class="card-header">
          <span>⚙️ Configuration</span>
        </div>

        <div class="space-y-4">
          <!-- Strategy -->
          <div>
            <label class="label">Strategy</label>
            <select v-model="strategy" class="input">
              <option v-for="s in strategies" :key="s" :value="s">{{ s }}</option>
              <option value="RSI_EMA">RSI_EMA</option>
            </select>
          </div>

          <!-- Timeframe -->
          <div>
            <label class="label">Timeframe</label>
            <select v-model="timeframe" class="input">
              <option v-for="tf in timeframes" :key="tf" :value="tf">{{ tf }}</option>
            </select>
          </div>

          <!-- Date Range -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Start Date</label>
              <input v-model="startDate" type="date" class="input" />
            </div>
            <div>
              <label class="label">End Date</label>
              <input v-model="endDate" type="date" class="input" />
            </div>
          </div>

          <!-- Progress -->
          <div v-if="isRunning" class="pt-4">
            <div class="flex justify-between text-sm mb-2">
              <span class="text-gray-400">Progress</span>
              <span class="text-primary">{{ Math.round(progress * 100) }}%</span>
            </div>
            <div class="w-full h-2 bg-dark-100 rounded-full overflow-hidden">
              <div 
                class="h-full bg-primary transition-all duration-300"
                :style="{ width: `${progress * 100}%` }"
              ></div>
            </div>
          </div>

          <!-- Buttons -->
          <div class="pt-4 flex gap-3">
            <button 
              v-if="!isRunning"
              @click="runBacktest" 
              class="btn btn-primary flex-1"
            >
              🚀 Run Backtest
            </button>
            <button 
              v-else
              @click="abortBacktest" 
              class="btn btn-danger flex-1"
            >
              ⏹️ Abort
            </button>
          </div>
        </div>
      </div>

      <!-- Results Panel -->
      <div class="lg:col-span-2 space-y-4">
        <!-- Results Summary -->
        <div v-if="results" class="card">
          <div class="card-header">
            <span>📊 Results Summary</span>
          </div>
          
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div class="stat-label">Total Profit</div>
              <div class="stat-value stat-positive">
                +{{ (results.profit_total_abs || 0).toFixed(2) }} USDT
              </div>
            </div>
            <div>
              <div class="stat-label">Win Rate</div>
              <div class="stat-value text-success">
                {{ ((results.wins || 0) / (results.total_trades || 1) * 100).toFixed(1) }}%
              </div>
            </div>
            <div>
              <div class="stat-label">Total Trades</div>
              <div class="stat-value text-white">
                {{ results.total_trades || 0 }}
              </div>
            </div>
            <div>
              <div class="stat-label">Max Drawdown</div>
              <div class="stat-value stat-negative">
                {{ (results.max_drawdown_abs || 0).toFixed(2) }}%
              </div>
            </div>
          </div>
        </div>

        <!-- Chart -->
        <div class="card">
          <div class="card-header">
            <span>📈 Equity Curve</span>
          </div>
          <div class="h-80">
            <CumProfitChart v-if="results" :data="results" />
            <div v-else class="h-full flex items-center justify-center text-gray-500">
              Run a backtest to see results
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

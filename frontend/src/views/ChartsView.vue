<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useBotStore } from '@/stores/botStore'
import CandleChartContainer from '@/components/charts/CandleChartContainer.vue'

const route = useRoute()
const botStore = useBotStore()

// Get pair from URL query if provided
const initialPair = (route.query.pair as string) || 'BTC/USDT'
const selectedPair = ref(initialPair)
const selectedTimeframe = ref('4h')

const timeframes = ['1m', '5m', '15m', '1h', '4h', '1d', '1w']

// Default pairs list (fallback when API is not available)
const defaultPairs = [
  'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
  'ADA/USDT', 'AVAX/USDT', 'DOGE/USDT', 'DOT/USDT', 'LINK/USDT',
  'ATOM/USDT', 'NEAR/USDT', 'OP/USDT', 'ARB/USDT', 'SUI/USDT',
  'SEI/USDT', 'INJ/USDT', 'PEPE/USDT', 'SHIB/USDT', 'FLOKI/USDT',
  'APT/USDT', 'TIA/USDT', 'FET/USDT', 'IMX/USDT', 'GRT/USDT',
  'FIL/USDT', 'RUNE/USDT', 'TAO/USDT', 'WIF/USDT', 'BONK/USDT',
  'MINA/USDT', 'ZK/USDT', 'JUP/USDT', 'PYTH/USDT', 'ONDO/USDT',
  'MANTA/USDT', 'AEVO/USDT', 'DYM/USDT', 'SAGA/USDT', 'XAI/USDT',
  'TRB/USDT', 'EGLD/USDT'
]

// Get pairs - try from API, fallback to default
const pairs = ref<string[]>(defaultPairs)

async function loadPairs() {
  let loadedPairs: string[] = []

  try {
    const res = await axios.get('/binance-proxy/api/v3/ticker/price')
    if (Array.isArray(res.data)) {
      const list = res.data
        .map((item: any) => item?.symbol)
        .filter((symbol: string) => typeof symbol === 'string' && symbol.endsWith('USDT'))
        .map((symbol: string) => `${symbol.slice(0, -4)}/USDT`)
      if (list.length > 0) {
        loadedPairs = Array.from(new Set(list))
      }
    }
  } catch (error) {
    console.warn('Failed to load Binance price list, trying exchangeInfo')
  }

  if (loadedPairs.length === 0) {
    try {
      const res = await axios.get('/binance-proxy/api/v3/exchangeInfo')
      const symbols = res.data?.symbols || []
      const list = symbols
        .filter((s: any) => s.status === 'TRADING' && s.isSpotTradingAllowed && s.quoteAsset === 'USDT')
        .map((s: any) => `${s.baseAsset}/${s.quoteAsset}`)
      if (list.length > 0) {
        loadedPairs = list
      }
    } catch (error) {
      console.warn('Failed to load Binance exchangeInfo, falling back to whitelist')
    }
  }

  if (loadedPairs.length > 0) {
    pairs.value = loadedPairs.sort()
  } else {
    try {
      await botStore.fetchWhitelist()
      if (botStore.whitelist && botStore.whitelist.length > 0) {
        pairs.value = botStore.whitelist
      } else {
        pairs.value = defaultPairs
      }
    } catch (error) {
      console.log('Using default pairs list')
      pairs.value = defaultPairs
    }
  }

  if (pairs.value.length > 0 && !pairs.value.includes(selectedPair.value)) {
    selectedPair.value = pairs.value[0]
  }
}

// Get all trades (open + closed) for chart markers
const allTrades = computed(() => {
  return [...botStore.openTrades, ...botStore.closedTrades]
})

onMounted(() => {
  loadPairs()
  // Load trades for chart markers
  botStore.fetchTrades()
})
</script>

<template>
  <div class="space-y-6 fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div>
        <h1 class="text-2xl font-bold text-white">📊 Charts</h1>
        <p class="text-gray-500 text-sm">Xem biểu đồ giá và chỉ báo kỹ thuật</p>
      </div>
      
      <!-- Controls -->
      <div class="flex items-center gap-3">
        <select v-model="selectedPair" class="input !w-72">
          <option v-for="pair in pairs" :key="pair" :value="pair">{{ pair }}</option>
        </select>
        <select v-model="selectedTimeframe" class="input !w-32">
          <option v-for="tf in timeframes" :key="tf" :value="tf">{{ tf }}</option>
        </select>
        <button @click="loadPairs" class="btn btn-outline text-sm">
          🔄
        </button>
      </div>
    </div>

    <!-- Info -->
    <div class="flex items-center gap-4 text-sm text-gray-400">
      <span class="text-primary font-medium">{{ selectedPair }}</span>
      <span>⏱️ {{ selectedTimeframe }}</span>
      <span>{{ pairs.length }} cặp tiền</span>
    </div>

    <!-- Chart -->
    <div class="card" style="height: calc(100vh - 260px); min-height: 500px;">
      <CandleChartContainer 
        :pair="selectedPair" 
        :timeframe="selectedTimeframe"
        :trades="allTrades"
      />
    </div>
  </div>
</template>

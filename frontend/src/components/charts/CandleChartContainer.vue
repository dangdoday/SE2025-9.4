<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

interface Trade {
  trade_id: number
  pair: string
  is_open: boolean
  open_date: string
  close_date?: string
  open_rate: number
  close_rate?: number
  profit_abs?: number
}

const props = defineProps<{
  pair: string
  timeframe: string
  trades?: Trade[]
}>()

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null
const isLoading = ref(false)
const isLoadingMore = ref(false)
const error = ref('')
const currentPrice = ref(0)
const priceChange = ref(0)
const candleCount = ref(0)

let ws: WebSocket | null = null
let refreshInterval: number | null = null
let candleData: any[] = []

// Binance timeframe mapping
function getBinanceInterval(tf: string): string {
  const mapping: Record<string, string> = {
    '1m': '1m', '3m': '3m', '5m': '5m', '15m': '15m', '30m': '30m',
    '1h': '1h', '2h': '2h', '4h': '4h', '6h': '6h', '8h': '8h', '12h': '12h',
    '1d': '1d', '3d': '3d', '1w': '1w', '1M': '1M'
  }
  return mapping[tf] || '4h'
}

// Fetch data from Binance public API - max 1000 candles per request
async function fetchFromBinance(pair: string, timeframe: string, limit = 1000, endTime?: number) {
  const symbol = pair.replace('/', '')
  const interval = getBinanceInterval(timeframe)
  let url = `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`
  if (endTime) {
    url += `&endTime=${endTime}`
  }
  
  const res = await axios.get(url)
  // Binance klines format: [openTime, open, high, low, close, volume, closeTime, ...]
  return res.data.map((k: any) => ({
    time: k[0],
    open: parseFloat(k[1]),
    high: parseFloat(k[2]),
    low: parseFloat(k[3]),
    close: parseFloat(k[4]),
    volume: parseFloat(k[5])
  }))
}

// Connect to Binance WebSocket for real-time updates
function connectWebSocket() {
  if (ws) {
    ws.close()
  }
  
  const symbol = props.pair.replace('/', '').toLowerCase()
  const interval = getBinanceInterval(props.timeframe)
  const wsUrl = `wss://stream.binance.com:9443/ws/${symbol}@kline_${interval}`
  
  ws = new WebSocket(wsUrl)
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.k) {
        const kline = data.k
        const newCandle = {
          time: kline.t,
          open: parseFloat(kline.o),
          high: parseFloat(kline.h),
          low: parseFloat(kline.l),
          close: parseFloat(kline.c),
          volume: parseFloat(kline.v)
        }
        
        // Update current price
        currentPrice.value = newCandle.close
        
        // Update or add the latest candle
        if (candleData.length > 0) {
          const lastCandle = candleData[candleData.length - 1]
          if (lastCandle.time === newCandle.time) {
            // Update existing candle
            candleData[candleData.length - 1] = newCandle
          } else {
            // New candle - just add, don't remove old ones
            candleData.push(newCandle)
          }
          
          // Calculate price change from first candle
          if (candleData.length > 0) {
            const firstOpen = candleData[0].open
            priceChange.value = ((newCandle.close - firstOpen) / firstOpen) * 100
          }
          
          updateChart()
        }
      }
    } catch (e) {
      console.error('WebSocket parse error:', e)
    }
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
  
  ws.onclose = () => {
    // Reconnect after 5 seconds
    setTimeout(() => {
      if (props.pair && props.timeframe) {
        connectWebSocket()
      }
    }, 5000)
  }
}

async function loadData() {
  if (!props.pair || !props.timeframe) return
  
  isLoading.value = true
  error.value = ''
  
  try {
    candleData = await fetchFromBinance(props.pair, props.timeframe)
    candleCount.value = candleData.length
    
    if (candleData.length > 0) {
      currentPrice.value = candleData[candleData.length - 1].close
      const firstOpen = candleData[0].open
      priceChange.value = ((currentPrice.value - firstOpen) / firstOpen) * 100
    }
    
    updateChart()
    
    // Connect WebSocket for real-time updates
    connectWebSocket()
    
  } catch (err: any) {
    console.error('Failed to load candles:', err)
    error.value = 'Không thể tải dữ liệu'
  } finally {
    isLoading.value = false
  }
}

// Load more historical data
async function loadMoreHistory() {
  if (isLoadingMore.value || candleData.length === 0) return
  
  isLoadingMore.value = true
  
  try {
    const oldestCandle = candleData[0]
    const endTime = oldestCandle.time - 1
    
    const olderData = await fetchFromBinance(props.pair, props.timeframe, 1000, endTime)
    
    if (olderData.length > 0) {
      // Prepend older data
      candleData = [...olderData, ...candleData]
      candleCount.value = candleData.length
      
      // Calculate new price change
      const firstOpen = candleData[0].open
      priceChange.value = ((currentPrice.value - firstOpen) / firstOpen) * 100
      
      updateChart()
    }
  } catch (err) {
    console.error('Failed to load more history:', err)
  } finally {
    isLoadingMore.value = false
  }
}

function updateChart() {
  if (!chartRef.value || candleData.length === 0) return
  
  if (!chart) {
    chart = echarts.init(chartRef.value, 'dark')
  }

  // Format dates
  const dates = candleData.map((d: any) => {
    const date = new Date(d.time)
    return date.toLocaleString('vi-VN', { 
      day: '2-digit', 
      month: '2-digit', 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  })
  
  // ECharts candlestick format: [open, close, low, high]
  const ohlc = candleData.map((d: any) => [d.open, d.close, d.low, d.high])
  const volumes = candleData.map((d: any) => d.volume)
  
  // Generate trade markers for current pair
  const pairTrades = (props.trades || []).filter(t => t.pair === props.pair)
  
  // Find candle index by trade time
  function findCandleIndex(tradeDate: string): number {
    const tradeTime = new Date(tradeDate).getTime()
    for (let i = 0; i < candleData.length; i++) {
      const candleTime = candleData[i].time
      const nextCandleTime = candleData[i + 1]?.time || Infinity
      if (tradeTime >= candleTime && tradeTime < nextCandleTime) {
        return i
      }
    }
    return -1
  }
  
  // Build mark points for buy (green arrow up) and sell (red arrow down)
  const markPoints: any[] = []
  const markLines: any[] = []
  
  pairTrades.forEach(trade => {
    const entryIdx = findCandleIndex(trade.open_date)
    
    if (entryIdx >= 0) {
      // Buy marker - green arrow pointing up
      markPoints.push({
        name: `Buy #${trade.trade_id}`,
        coord: [entryIdx, trade.open_rate],
        value: `Buy\n$${trade.open_rate.toFixed(2)}`,
        symbol: 'arrow',
        symbolSize: 15,
        symbolRotate: 0,
        itemStyle: { color: '#0ECB81' },
        label: {
          show: true,
          position: 'bottom',
          fontSize: 9,
          color: '#0ECB81',
          formatter: 'B'
        }
      })
      
      // If trade is closed, add sell marker and connecting line
      if (!trade.is_open && trade.close_date && trade.close_rate) {
        const exitIdx = findCandleIndex(trade.close_date)
        
        if (exitIdx >= 0) {
          // Sell marker - red arrow pointing down
          const isProfit = (trade.profit_abs || 0) >= 0
          markPoints.push({
            name: `Sell #${trade.trade_id}`,
            coord: [exitIdx, trade.close_rate],
            value: `Sell\n$${trade.close_rate.toFixed(2)}`,
            symbol: 'arrow',
            symbolSize: 15,
            symbolRotate: 180,
            itemStyle: { color: '#F6465D' },
            label: {
              show: true,
              position: 'top',
              fontSize: 9,
              color: '#F6465D',
              formatter: 'S'
            }
          })
          
          // Connecting dashed line
          markLines.push({
            lineStyle: {
              type: 'dashed',
              color: isProfit ? '#0ECB8180' : '#F6465D80',
              width: 1
            },
            data: [
              { coord: [entryIdx, trade.open_rate] },
              { coord: [exitIdx, trade.close_rate] }
            ]
          })
        }
      }
    }
  })

  const option = {
    backgroundColor: 'transparent',
    animation: false,
    title: {
      text: `${props.pair}`,
      subtext: `$${currentPrice.value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} (${priceChange.value >= 0 ? '+' : ''}${priceChange.value.toFixed(2)}%)`,
      left: 10,
      top: 5,
      textStyle: { color: '#F0B90B', fontSize: 16 },
      subtextStyle: { 
        color: priceChange.value >= 0 ? '#0ECB81' : '#F6465D', 
        fontSize: 14,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: '#1E2329',
      borderColor: '#2B3139',
      textStyle: { color: '#EAECEF' },
      formatter: (params: any) => {
        if (!params || params.length === 0) return ''
        const candle = params.find((p: any) => p.seriesType === 'candlestick')
        if (!candle || !candle.data) return ''
        
        // ECharts candlestick data format varies - check array length
        // If length is 5, first element is dataIndex, rest is [open, close, low, high]
        // If length is 4, it's just [open, close, low, high]
        const rawData = candle.data
        let open: number, close: number, low: number, high: number
        
        if (Array.isArray(rawData)) {
          if (rawData.length >= 5) {
            // First element is index, skip it
            [, open, close, low, high] = rawData
          } else if (rawData.length === 4) {
            [open, close, low, high] = rawData
          } else {
            return ''
          }
        } else {
          return ''
        }
        
        const change = ((close - open) / open * 100).toFixed(2)
        const color = close >= open ? '#0ECB81' : '#F6465D'
        return `
          <div style="font-size:12px">
            <div style="margin-bottom:4px"><b>${candle.name}</b></div>
            <div>Open: $${Number(open).toLocaleString(undefined, {maximumFractionDigits: 8})}</div>
            <div>High: $${Number(high).toLocaleString(undefined, {maximumFractionDigits: 8})}</div>
            <div>Low: $${Number(low).toLocaleString(undefined, {maximumFractionDigits: 8})}</div>
            <div>Close: $${Number(close).toLocaleString(undefined, {maximumFractionDigits: 8})}</div>
            <div style="color:${color}">Change: ${change}%</div>
          </div>
        `
      }
    },
    grid: [
      { left: 80, right: 20, top: 60, height: '50%' },
      { left: 80, right: 20, top: '72%', height: '18%' }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        axisLine: { lineStyle: { color: '#2B3139' } },
        axisLabel: { color: '#848E9C', fontSize: 9, rotate: 30 },
        gridIndex: 0
      },
      {
        type: 'category',
        data: dates,
        axisLine: { lineStyle: { color: '#2B3139' } },
        axisLabel: { show: false },
        gridIndex: 1
      }
    ],
    yAxis: [
      {
        scale: true,
        axisLine: { lineStyle: { color: '#2B3139' } },
        axisLabel: { 
          color: '#848E9C',
          formatter: (val: number) => {
            if (val >= 1000) return (val / 1000).toFixed(1) + 'K'
            if (val >= 1) return val.toLocaleString()
            return val.toPrecision(4)
          }
        },
        splitLine: { lineStyle: { color: '#2B3139' } },
        gridIndex: 0
      },
      {
        scale: true,
        axisLine: { lineStyle: { color: '#2B3139' } },
        axisLabel: { show: false },
        splitLine: { show: false },
        gridIndex: 1
      }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 60, end: 100 },
      { show: true, xAxisIndex: [0, 1], type: 'slider', bottom: 5, height: 20 }
    ],
    series: [
      {
        name: props.pair,
        type: 'candlestick',
        data: ohlc,
        xAxisIndex: 0,
        yAxisIndex: 0,
        itemStyle: {
          color: '#0ECB81',
          color0: '#F6465D',
          borderColor: '#0ECB81',
          borderColor0: '#F6465D'
        },
        markPoint: {
          data: markPoints,
          animation: false
        },
        markLine: {
          symbol: 'none',
          data: markLines,
          animation: false,
          silent: true
        }
      },
      {
        name: 'Volume',
        type: 'bar',
        data: volumes,
        xAxisIndex: 1,
        yAxisIndex: 1,
        itemStyle: {
          color: (params: any) => {
            const idx = params.dataIndex
            if (idx < ohlc.length) {
              const [open, close] = ohlc[idx]
              return close >= open ? '#0ECB8160' : '#F6465D60'
            }
            return '#2B3139'
          }
        }
      }
    ]
  }

  chart.setOption(option, true)
  
  // Listen for zoom/scroll to left edge to auto-load more history
  chart.off('dataZoom')
  chart.on('dataZoom', (params: any) => {
    // Check if zoomed/scrolled to the very beginning
    if (params.start !== undefined && params.start < 5) {
      loadMoreHistory()
    }
  })
}

function cleanup() {
  if (ws) {
    ws.close()
    ws = null
  }
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', () => chart?.resize())
})

onUnmounted(() => {
  cleanup()
})

watch(() => [props.pair, props.timeframe], () => {
  cleanup()
  loadData()
})
</script>

<template>
  <div class="relative w-full h-full min-h-[400px]">
    <!-- Header controls -->
    <div class="absolute top-2 right-2 z-20 flex items-center gap-3 text-xs">
      <span v-if="isLoadingMore" class="text-primary flex items-center gap-1">
        ⏳ Đang tải...
      </span>
      <span class="text-gray-500">{{ candleCount.toLocaleString() }} nến</span>
      <span class="flex items-center gap-1">
        <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
        LIVE
      </span>
    </div>
    
    <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-dark-300/80 z-10">
      <div class="flex items-center gap-2 text-primary">
        <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
        </svg>
        <span>Đang tải...</span>
      </div>
    </div>
    <div v-if="error && !isLoading" class="absolute inset-0 flex items-center justify-center bg-dark-300/50 z-10">
      <div class="text-center">
        <div class="text-danger mb-2">{{ error }}</div>
        <button @click="loadData" class="text-primary hover:underline text-sm">Thử lại</button>
      </div>
    </div>
    <div ref="chartRef" class="w-full h-full"></div>
  </div>
</template>

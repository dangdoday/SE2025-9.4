<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  data?: any
}>()

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

function initChart() {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value, 'dark')
  updateChart()
}

function updateChart() {
  if (!chart || !props.data) return

  // Generate sample cumulative profit data
  const dates = []
  const profits = []
  let cumulative = 0
  
  for (let i = 0; i < 30; i++) {
    const date = new Date()
    date.setDate(date.getDate() - (30 - i))
    dates.push(date.toLocaleDateString())
    cumulative += (Math.random() - 0.3) * 10
    profits.push(cumulative)
  }

  const option = {
    backgroundColor: 'transparent',
    grid: {
      left: 50,
      right: 20,
      top: 20,
      bottom: 40
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1E2329',
      borderColor: '#2B3139',
      textStyle: { color: '#EAECEF' }
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#2B3139' } },
      axisLabel: { color: '#848E9C', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#2B3139' } },
      axisLabel: { color: '#848E9C' },
      splitLine: { lineStyle: { color: '#2B3139' } }
    },
    series: [{
      type: 'line',
      data: profits,
      smooth: true,
      lineStyle: { color: '#F0B90B', width: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(240, 185, 11, 0.3)' },
          { offset: 1, color: 'rgba(240, 185, 11, 0)' }
        ])
      },
      itemStyle: { color: '#F0B90B' }
    }]
  }

  chart.setOption(option)
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => chart?.resize())
})

watch(() => props.data, updateChart, { deep: true })
</script>

<template>
  <div ref="chartRef" class="w-full h-full min-h-[300px]"></div>
</template>

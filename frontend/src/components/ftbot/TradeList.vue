<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBotStore } from '@/stores/botStore'
import type { Trade } from '@/stores/botStore'
import { isAdminUser } from '@/utils/auth'

const props = defineProps<{
  trades: Trade[]
  isOpen?: boolean
  showActions?: boolean
}>()

const router = useRouter()
const botStore = useBotStore()
const isAdmin = computed(() => isAdminUser())

function formatDate(date: string) {
  return new Date(date).toLocaleString()
}

function formatProfit(trade: Trade) {
  const profit = trade.profit_abs || 0
  return profit >= 0 ? `+${profit.toFixed(2)}` : profit.toFixed(2)
}

function profitClass(trade: Trade) {
  const profit = trade.profit_abs || 0
  return profit >= 0 ? 'text-success' : 'text-danger'
}

async function handleForceExit(tradeId: number) {
  if (confirm('Are you sure you want to exit this trade?')) {
    try {
      await botStore.forceExit(tradeId.toString())
    } catch (err: any) {
      console.error('Failed to force exit:', err)
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to exit trade'
      alert(`Error: ${errorMsg}`)
    }
  }
}

// Navigate to chart with selected pair
function goToChart(pair: string) {
  router.push({ path: '/graph', query: { pair } })
}
</script>

<template>
  <div class="overflow-x-auto">
    <table v-if="trades.length > 0" class="table">
      <thead>
        <tr>
          <th>Pair</th>
          <th>Open Date</th>
          <th>Rate</th>
          <th>Amount</th>
          <th>Profit</th>
          <th v-if="!isOpen">Exit Reason</th>
          <th v-if="isOpen && showActions && isAdmin">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr 
          v-for="trade in trades" 
          :key="trade.trade_id"
          @click="goToChart(trade.pair)"
          class="cursor-pointer hover:bg-dark-100 transition-colors"
        >
          <td>
            <div class="flex items-center gap-2">
              <span class="font-medium text-primary">{{ trade.pair }}</span>
              <span class="text-xs text-gray-500 hover:text-primary" title="Xem chart">📈</span>
            </div>
          </td>
          <td class="text-gray-400 text-sm">
            {{ formatDate(trade.open_date) }}
          </td>
          <td class="text-white">
            {{ trade.open_rate.toFixed(4) }}
          </td>
          <td class="text-white">
            {{ trade.stake_amount.toFixed(2) }} USDT
          </td>
          <td :class="profitClass(trade)">
            {{ formatProfit(trade) }} USDT
          </td>
          <td v-if="!isOpen" class="text-gray-400 text-sm">
            {{ trade.exit_reason || '-' }}
          </td>
          <td v-if="isOpen && showActions && isAdmin">
            <button 
              @click.stop="handleForceExit(trade.trade_id)"
              class="text-xs btn btn-danger py-1 px-2"
            >
              Exit
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else class="text-center py-8 text-gray-500">
      No trades found
    </div>
  </div>
</template>

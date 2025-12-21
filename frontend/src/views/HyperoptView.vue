<script setup lang="ts">
import { ref } from 'vue'

// Form state
const strategy = ref('RSI_EMA')
const isRunning = ref(false)
const results = ref<any[]>([])

// Hyperopt parameters
const hyperoptConfig = ref({
  epochs: 100,
  spaces: ['buy', 'sell', 'roi', 'stoploss'],
  loss: 'SharpeHyperOptLoss',
  minTrades: 10
})

const lossOptions = [
  'ShortTradeDurHyperOptLoss',
  'OnlyProfitHyperOptLoss',
  'SharpeHyperOptLoss',
  'SortinoHyperOptLoss',
  'MaxDrawDownHyperOptLoss'
]

function runHyperopt() {
  isRunning.value = true
  // Simulate hyperopt running
  setTimeout(() => {
    results.value = [
      { epoch: 1, trades: 42, profit: 15.4, sharpe: 1.2, drawdown: 8.5 },
      { epoch: 2, trades: 38, profit: 18.2, sharpe: 1.4, drawdown: 7.2 },
      { epoch: 3, trades: 45, profit: 22.1, sharpe: 1.6, drawdown: 6.8 },
      { epoch: 4, trades: 41, profit: 25.8, sharpe: 1.8, drawdown: 5.4 },
      { epoch: 5, trades: 39, profit: 28.3, sharpe: 2.1, drawdown: 4.9 }
    ]
    isRunning.value = false
  }, 2000)
}
</script>

<template>
  <div class="space-y-6 fade-in">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-white">Hyperopt</h1>
      <p class="text-gray-500 text-sm">Optimize your strategy parameters</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Configuration -->
      <div class="card">
        <div class="card-header">
          <span>⚡ Configuration</span>
        </div>

        <div class="space-y-4">
          <!-- Strategy -->
          <div>
            <label class="label">Strategy</label>
            <select v-model="strategy" class="input">
              <option value="RSI_EMA">RSI_EMA</option>
            </select>
          </div>

          <!-- Epochs -->
          <div>
            <label class="label">Epochs</label>
            <input v-model.number="hyperoptConfig.epochs" type="number" class="input" />
          </div>

          <!-- Loss Function -->
          <div>
            <label class="label">Loss Function</label>
            <select v-model="hyperoptConfig.loss" class="input">
              <option v-for="loss in lossOptions" :key="loss" :value="loss">{{ loss }}</option>
            </select>
          </div>

          <!-- Spaces -->
          <div>
            <label class="label">Optimization Spaces</label>
            <div class="grid grid-cols-2 gap-2 mt-2">
              <label class="flex items-center gap-2 text-sm text-gray-400">
                <input type="checkbox" value="buy" v-model="hyperoptConfig.spaces" class="rounded" />
                Buy
              </label>
              <label class="flex items-center gap-2 text-sm text-gray-400">
                <input type="checkbox" value="sell" v-model="hyperoptConfig.spaces" class="rounded" />
                Sell
              </label>
              <label class="flex items-center gap-2 text-sm text-gray-400">
                <input type="checkbox" value="roi" v-model="hyperoptConfig.spaces" class="rounded" />
                ROI
              </label>
              <label class="flex items-center gap-2 text-sm text-gray-400">
                <input type="checkbox" value="stoploss" v-model="hyperoptConfig.spaces" class="rounded" />
                Stoploss
              </label>
            </div>
          </div>

          <!-- Button -->
          <button 
            @click="runHyperopt" 
            class="btn btn-primary w-full mt-4"
            :disabled="isRunning"
          >
            {{ isRunning ? '🔄 Running...' : '🚀 Start Hyperopt' }}
          </button>
        </div>
      </div>

      <!-- Results -->
      <div class="lg:col-span-2 card">
        <div class="card-header">
          <span>📊 Optimization Results</span>
        </div>

        <div v-if="results.length > 0" class="overflow-x-auto">
          <table class="table">
            <thead>
              <tr>
                <th>Epoch</th>
                <th>Trades</th>
                <th>Profit %</th>
                <th>Sharpe</th>
                <th>Drawdown %</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in results" :key="r.epoch">
                <td>{{ r.epoch }}</td>
                <td>{{ r.trades }}</td>
                <td class="text-success">+{{ r.profit.toFixed(2) }}%</td>
                <td>{{ r.sharpe.toFixed(2) }}</td>
                <td class="text-danger">-{{ r.drawdown.toFixed(2) }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-12 text-gray-500">
          Run hyperopt to see results
        </div>
      </div>
    </div>
  </div>
</template>

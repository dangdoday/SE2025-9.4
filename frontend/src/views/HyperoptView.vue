<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useBotStore } from '@/stores/ftbotwrapper';

const botStore = useBotStore();

// Hyperopt configuration
const strategy = ref('RSI_EMA');
const timeframe = ref('4h');
const timerange = ref('20230101-20251201');
const epochs = ref(2000);
const hyperoptLoss = ref('SharpeHyperOptLoss');
const spaces = ref<string[]>(['buy', 'sell']);
const minTrades = ref(20);
const jobs = ref(8);

// State
const isRunning = ref(false);
const currentEpoch = ref(0);
const bestResult = ref<any>(null);
const hyperoptResults = ref<Array<{
  total_profit: number;
  win_rate: number;
  total_trades: number;
  sharpe: number;
  max_drawdown: number;
}>>([]);
const logs = ref<string[]>([]);
const pollInterval = ref<number | null>(null);

// Available options
const lossOptions = [
  { label: 'Sharpe Ratio', value: 'SharpeHyperOptLoss' },
  { label: 'Sortino Ratio', value: 'SortinoHyperOptLoss' },
  { label: 'Calmar Ratio', value: 'CalmarHyperOptLoss' },
  { label: 'Max Drawdown', value: 'MaxDrawDownHyperOptLoss' },
  { label: 'Profit', value: 'OnlyProfitHyperOptLoss' },
];

const spaceOptions = [
  { label: 'Buy Signal', value: 'buy' },
  { label: 'Sell Signal', value: 'sell' },
  { label: 'ROI', value: 'roi' },
  { label: 'Stoploss', value: 'stoploss' },
  { label: 'Trailing', value: 'trailing' },
];

const timeframeOptions = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d'];

// Computed
const progress = computed(() => {
  if (epochs.value === 0) return 0;
  return Math.min((currentEpoch.value / epochs.value) * 100, 100);
});

const isFormValid = computed(() => {
  return strategy.value && timeframe.value && timerange.value && epochs.value > 0 && spaces.value.length > 0;
});

// Methods
const startHyperopt = async () => {
  if (!isFormValid.value) return;

  isRunning.value = true;
  currentEpoch.value = 0;
  logs.value = [];
  logs.value.push(`🚀 Bắt đầu Hyperopt: ${strategy.value}`);
  logs.value.push(`⏱️ Timeframe: ${timeframe.value} | Epochs: ${epochs.value}`);
  logs.value.push(`📊 Loss Function: ${hyperoptLoss.value}`);
  logs.value.push(`🎯 Spaces: ${spaces.value.join(', ')}`);
  logs.value.push('---');

  try {
    // Mock hyperopt start - replace with actual API call when backend is ready
    logs.value.push('✅ Hyperopt đang chạy...');
    logs.value.push('⚙️ Đang tối ưu hóa parameters...');
    startPolling();
  } catch (error: any) {
    logs.value.push(`❌ Lỗi: ${error.message}`);
    isRunning.value = false;
  }
};

const stopHyperopt = async () => {
  try {
    // Mock stop hyperopt
    logs.value.push('⏹️ Đã dừng Hyperopt');
    isRunning.value = false;
    stopPolling();
  } catch (error: any) {
    logs.value.push(`❌ Lỗi khi dừng: ${error.message}`);
  }
};

const startPolling = () => {
  pollInterval.value = window.setInterval(async () => {
    try {
      // Mock polling - simulate progress
      if (currentEpoch.value < epochs.value) {
        currentEpoch.value += Math.floor(Math.random() * 10) + 1;
        
        if (currentEpoch.value >= epochs.value) {
          currentEpoch.value = epochs.value;
          
          // Mock best result
          bestResult.value = {
            total_profit: 74.3,
            win_rate: 0.734,
            total_trades: 150,
            sharpe: 2.45,
            params: {
              buy_rsi: 35,
              sell_rsi: 70,
              ema_short: 12,
              ema_long: 26,
            }
          };
          
          isRunning.value = false;
          logs.value.push('✅ Hyperopt hoàn thành!');
          stopPolling();
          loadResults();
        }
      }
    } catch (error) {
      console.error('Polling error:', error);
    }
  }, 2000);
};

const stopPolling = () => {
  if (pollInterval.value) {
    clearInterval(pollInterval.value);
    pollInterval.value = null;
  }
};

const loadResults = async () => {
  try {
    // Mock results - top 10 best combinations
    const mockResults: Array<{
      total_profit: number;
      win_rate: number;
      total_trades: number;
      sharpe: number;
      max_drawdown: number;
    }> = [];
    for (let i = 0; i < 10; i++) {
      mockResults.push({
        total_profit: 74.3 - (i * 2.5),
        win_rate: 0.734 - (i * 0.02),
        total_trades: 150 - (i * 5),
        sharpe: 2.45 - (i * 0.15),
        max_drawdown: -12.5 - (i * 1.2),
      });
    }
    hyperoptResults.value = mockResults;
    logs.value.push(`📊 Đã tải ${mockResults.length} kết quả`);
  } catch (error: any) {
    logs.value.push(`❌ Không thể tải kết quả: ${error.message}`);
  }
};

const applyBestParams = async () => {
  if (!bestResult.value) return;

  try {
    // Mock apply params
    logs.value.push('✅ Đã áp dụng parameters tối ưu vào strategy');
    logs.value.push(`📝 Buy RSI: ${bestResult.value.params.buy_rsi}`);
    logs.value.push(`📝 Sell RSI: ${bestResult.value.params.sell_rsi}`);
    logs.value.push(`📝 EMA Short: ${bestResult.value.params.ema_short}`);
    logs.value.push(`📝 EMA Long: ${bestResult.value.params.ema_long}`);
    alert('Parameters đã được cập nhật! Hãy chạy backtest để kiểm tra.');
  } catch (error: any) {
    logs.value.push(`❌ Lỗi khi áp dụng params: ${error.message}`);
  }
};

// Lifecycle
onMounted(() => {
  // Load saved settings if any
  loadResults();
});

onBeforeUnmount(() => {
  stopPolling();
});
</script>

<template>
  <div class="hyperopt-view p-6 max-w-7xl mx-auto">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Hyperopt - Tối ưu hóa chiến lược</h1>
      <div class="text-sm text-gray-500">
        <span class="material-symbols-outlined align-middle">science</span>
        Tìm parameters tối ưu cho strategy
      </div>
    </div>

    <!-- Warning Box -->
    <div class="bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 p-4 mb-6">
      <div class="flex items-center">
        <span class="material-symbols-outlined text-yellow-600 mr-2">warning</span>
        <div>
          <p class="font-semibold text-yellow-800 dark:text-yellow-200">Lưu ý quan trọng</p>
          <ul class="text-sm text-yellow-700 dark:text-yellow-300 mt-2 list-disc ml-5">
            <li>Hyperopt có thể chạy rất lâu (vài giờ đến vài ngày)</li>
            <li>Số epochs càng cao thì kết quả càng tốt nhưng thời gian càng lâu</li>
            <li>Nên bắt đầu với epochs thấp (200-500) để test</li>
            <li>Backtest kết quả trước khi áp dụng vào live trading</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left Panel - Configuration -->
      <div class="lg:col-span-1">
        <div class="bg-white dark:bg-surface-dark rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-bold mb-4 flex items-center">
            <span class="material-symbols-outlined mr-2">settings</span>
            Cấu hình
          </h2>

          <div class="space-y-4">
            <!-- Strategy -->
            <div>
              <label class="block text-sm font-medium mb-2">Strategy</label>
              <input
                v-model="strategy"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-surface-dark"
                placeholder="RSI_EMA"
                :disabled="isRunning"
              />
            </div>

            <!-- Timeframe -->
            <div>
              <label class="block text-sm font-medium mb-2">Timeframe</label>
              <select
                v-model="timeframe"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-surface-dark"
                :disabled="isRunning"
              >
                <option v-for="tf in timeframeOptions" :key="tf" :value="tf">{{ tf }}</option>
              </select>
            </div>

            <!-- Timerange -->
            <div>
              <label class="block text-sm font-medium mb-2">Timerange</label>
              <input
                v-model="timerange"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-surface-dark"
                placeholder="20230101-20251201"
                :disabled="isRunning"
              />
              <p class="text-xs text-gray-500 mt-1">Format: YYYYMMDD-YYYYMMDD</p>
            </div>

            <!-- Epochs -->
            <div>
              <label class="block text-sm font-medium mb-2">Số Epochs</label>
              <input
                v-model.number="epochs"
                type="number"
                min="10"
                max="100000"
                step="100"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-surface-dark font-mono"
                :disabled="isRunning"
              />
              <p class="text-xs text-gray-500 mt-1">Khuyến nghị: 500-2000 epochs</p>
            </div>

            <!-- Loss Function -->
            <div>
              <label class="block text-sm font-medium mb-2">Loss Function</label>
              <select
                v-model="hyperoptLoss"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-surface-dark"
                :disabled="isRunning"
              >
                <option v-for="loss in lossOptions" :key="loss.value" :value="loss.value">
                  {{ loss.label }}
                </option>
              </select>
            </div>

            <!-- Spaces -->
            <div>
              <label class="block text-sm font-medium mb-2">Optimization Spaces</label>
              <div class="space-y-2">
                <label
                  v-for="space in spaceOptions"
                  :key="space.value"
                  class="flex items-center cursor-pointer"
                >
                  <input
                    v-model="spaces"
                    type="checkbox"
                    :value="space.value"
                    class="mr-2"
                    :disabled="isRunning"
                  />
                  <span class="text-sm">{{ space.label }}</span>
                </label>
              </div>
            </div>

            <!-- Advanced Options -->
            <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs font-medium mb-1">Min Trades</label>
                  <input
                    v-model.number="minTrades"
                    type="number"
                    min="1"
                    class="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-surface-dark"
                    :disabled="isRunning"
                  />
                </div>
                <div>
                  <label class="block text-xs font-medium mb-1">Parallel Jobs</label>
                  <input
                    v-model.number="jobs"
                    type="number"
                    min="1"
                    max="16"
                    class="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-surface-dark"
                    :disabled="isRunning"
                  />
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="pt-4 space-y-2">
              <button
                v-if="!isRunning"
                @click="startHyperopt"
                :disabled="!isFormValid"
                class="w-full px-4 py-3 bg-primary-500 text-black font-bold rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                <span class="material-symbols-outlined mr-2">play_arrow</span>
                Bắt đầu Hyperopt
              </button>
              <button
                v-else
                @click="stopHyperopt"
                class="w-full px-4 py-3 bg-red-500 text-white font-bold rounded-lg hover:bg-red-600 flex items-center justify-center"
              >
                <span class="material-symbols-outlined mr-2">stop</span>
                Dừng Hyperopt
              </button>

              <button
                v-if="bestResult"
                @click="applyBestParams"
                :disabled="isRunning"
                class="w-full px-4 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center justify-center"
              >
                <span class="material-symbols-outlined mr-2">check_circle</span>
                Áp dụng Best Params
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel - Results & Logs -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Progress -->
        <div
          v-if="isRunning || currentEpoch > 0"
          class="bg-white dark:bg-surface-dark rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <h2 class="text-xl font-bold mb-4">Tiến trình</h2>
          <div class="space-y-3">
            <div class="flex justify-between text-sm">
              <span>Epoch: {{ currentEpoch }} / {{ epochs }}</span>
              <span class="font-mono">{{ progress.toFixed(1) }}%</span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
              <div
                class="bg-primary-500 h-full transition-all duration-300 flex items-center justify-center text-xs font-bold text-black"
                :style="{ width: `${progress}%` }"
              >
                <span v-if="progress > 10">{{ progress.toFixed(0) }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Best Result -->
        <div
          v-if="bestResult"
          class="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg border-2 border-green-500 p-6"
        >
          <h2 class="text-xl font-bold mb-4 flex items-center text-green-700 dark:text-green-300">
            <span class="material-symbols-outlined mr-2">emoji_events</span>
            Best Result
          </h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center">
              <p class="text-sm text-gray-600 dark:text-gray-400">Total Profit</p>
              <p class="text-2xl font-mono font-bold text-green-600">
                {{ bestResult.total_profit?.toFixed(2) }}%
              </p>
            </div>
            <div class="text-center">
              <p class="text-sm text-gray-600 dark:text-gray-400">Win Rate</p>
              <p class="text-2xl font-mono font-bold">
                {{ (bestResult.win_rate * 100)?.toFixed(1) }}%
              </p>
            </div>
            <div class="text-center">
              <p class="text-sm text-gray-600 dark:text-gray-400">Trades</p>
              <p class="text-2xl font-mono font-bold">{{ bestResult.total_trades }}</p>
            </div>
            <div class="text-center">
              <p class="text-sm text-gray-600 dark:text-gray-400">Sharpe Ratio</p>
              <p class="text-2xl font-mono font-bold">{{ bestResult.sharpe?.toFixed(2) }}</p>
            </div>
          </div>
          <div class="mt-4 p-3 bg-white/50 dark:bg-black/20 rounded">
            <p class="text-sm font-semibold mb-2">Parameters:</p>
            <pre class="text-xs overflow-auto">{{ JSON.stringify(bestResult.params, null, 2) }}</pre>
          </div>
        </div>

        <!-- Top 10 Results -->
        <div
          v-if="hyperoptResults.length > 0"
          class="bg-white dark:bg-surface-dark rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <h2 class="text-xl font-bold mb-4">Top 10 Kết quả</h2>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="border-b border-gray-200 dark:border-gray-700">
                <tr class="text-left">
                  <th class="pb-2">#</th>
                  <th class="pb-2">Profit %</th>
                  <th class="pb-2">Win Rate</th>
                  <th class="pb-2">Trades</th>
                  <th class="pb-2">Sharpe</th>
                  <th class="pb-2">Drawdown</th>
                </tr>
              </thead>
              <tbody class="font-mono">
                <tr
                  v-for="(result, index) in hyperoptResults"
                  :key="index"
                  class="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50"
                >
                  <td class="py-2">{{ index + 1 }}</td>
                  <td class="py-2 font-bold" :class="result.total_profit > 0 ? 'text-profit' : 'text-loss'">
                    {{ result.total_profit?.toFixed(2) }}%
                  </td>
                  <td class="py-2">{{ (result.win_rate * 100)?.toFixed(1) }}%</td>
                  <td class="py-2">{{ result.total_trades }}</td>
                  <td class="py-2">{{ result.sharpe?.toFixed(2) }}</td>
                  <td class="py-2 text-loss">{{ result.max_drawdown?.toFixed(2) }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Logs -->
        <div class="bg-white dark:bg-surface-dark rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-bold mb-4 flex items-center">
            <span class="material-symbols-outlined mr-2">terminal</span>
            Logs
          </h2>
          <div
            class="bg-gray-900 text-green-400 font-mono text-sm p-4 rounded h-80 overflow-y-auto"
          >
            <div v-for="(log, index) in logs" :key="index" class="mb-1">{{ log }}</div>
            <div v-if="logs.length === 0" class="text-gray-500">Chưa có logs...</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

/* Custom scrollbar for logs */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #1a1a1a;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #4a5568;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #718096;
}
</style>

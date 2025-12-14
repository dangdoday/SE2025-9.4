<template>
  <div class="api-settings-page p-6 max-w-5xl mx-auto">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold flex items-center">
        <span class="material-symbols-outlined text-primary-500 mr-3 text-4xl">key</span>
        Cấu hình API Keys
      </h1>
    </div>
    
    <div class="warning-box bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 p-5 mb-6 rounded-lg">
      <h3 class="text-lg font-bold text-yellow-800 dark:text-yellow-200 flex items-center mb-3">
        <span class="material-symbols-outlined mr-2">warning</span>
        Quan trọng - Bảo mật API Keys
      </h3>
      <ul class="space-y-2 text-yellow-700 dark:text-yellow-300">
        <li class="flex items-start">
          <span class="material-symbols-outlined text-sm mr-2 mt-0.5">check_circle</span>
          <span>Không chia sẻ API keys với bất kỳ ai</span>
        </li>
        <li class="flex items-start">
          <span class="material-symbols-outlined text-sm mr-2 mt-0.5">check_circle</span>
          <span>Chỉ bật quyền "Enable Reading" cho demo</span>
        </li>
        <li class="flex items-start">
          <span class="material-symbols-outlined text-sm mr-2 mt-0.5">check_circle</span>
          <span>Bật "Enable Spot Trading" chỉ khi chạy live</span>
        </li>
        <li class="flex items-start">
          <span class="material-symbols-outlined text-sm mr-2 mt-0.5">cancel</span>
          <span class="font-bold">KHÔNG BAO GIỜ bật "Enable Withdrawals"</span>
        </li>
      </ul>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left Panel - Form -->
      <div class="lg:col-span-2">
        <div class="form-section bg-white dark:bg-surface-dark rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-xl font-bold mb-6 flex items-center">
            <img src="https://bin.bnbstatic.com/static/images/common/favicon.ico" class="w-6 h-6 mr-2" alt="Binance" />
            Binance API Configuration
          </h2>
          
          <div class="space-y-5">
            <div class="form-group">
              <label class="block text-sm font-semibold mb-2">API Key:</label>
              <div class="relative">
                <input 
                  v-model="apiKey" 
                  :type="showApiKey ? 'text' : 'password'"
                  placeholder="Nhập Binance API Key"
                  class="input-field w-full px-4 py-3 pr-24 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-surface-dark font-mono text-sm"
                />
                <button @click="showApiKey = !showApiKey" class="btn-toggle absolute right-2 top-2 px-3 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-xs font-medium transition-colors">
                  <span class="material-symbols-outlined text-sm">{{ showApiKey ? 'visibility_off' : 'visibility' }}</span>
                </button>
              </div>
            </div>

            <div class="form-group">
              <label class="block text-sm font-semibold mb-2">API Secret:</label>
              <div class="relative">
                <input 
                  v-model="apiSecret" 
                  :type="showApiSecret ? 'text' : 'password'"
                  placeholder="Nhập Binance API Secret"
                  class="input-field w-full px-4 py-3 pr-24 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-surface-dark font-mono text-sm"
                />
                <button @click="showApiSecret = !showApiSecret" class="btn-toggle absolute right-2 top-2 px-3 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-xs font-medium transition-colors">
                  <span class="material-symbols-outlined text-sm">{{ showApiSecret ? 'visibility_off' : 'visibility' }}</span>
                </button>
              </div>
            </div>

            <div class="form-group">
              <label class="block text-sm font-semibold mb-2">Trading Mode:</label>
              <div class="flex gap-4">
                <label class="flex-1 cursor-pointer">
                  <input type="radio" :value="true" v-model="dryRun" class="sr-only peer" />
                  <div class="p-4 border-2 border-gray-300 dark:border-gray-600 rounded-lg peer-checked:border-primary-500 peer-checked:bg-primary-50 dark:peer-checked:bg-primary-900/20 transition-all">
                    <div class="flex items-center justify-between mb-2">
                      <span class="font-bold">Dry Run</span>
                      <span class="material-symbols-outlined text-green-600">verified_user</span>
                    </div>
                    <p class="text-xs text-gray-600 dark:text-gray-400">Giả lập - An toàn</p>
                  </div>
                </label>
                <label class="flex-1 cursor-pointer">
                  <input type="radio" :value="false" v-model="dryRun" class="sr-only peer" />
                  <div class="p-4 border-2 border-gray-300 dark:border-gray-600 rounded-lg peer-checked:border-red-500 peer-checked:bg-red-50 dark:peer-checked:bg-red-900/20 transition-all">
                    <div class="flex items-center justify-between mb-2">
                      <span class="font-bold">Live Trading</span>
                      <span class="material-symbols-outlined text-red-600">warning</span>
                    </div>
                    <p class="text-xs text-gray-600 dark:text-gray-400">Thật - Cẩn thận!</p>
                  </div>
                </label>
              </div>
            </div>

            <div v-if="dryRun" class="form-group bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
              <label class="block text-sm font-semibold mb-2">Dry Run Wallet (USDT):</label>
              <input 
                v-model.number="dryRunWallet" 
                type="number"
                min="100"
                step="100"
                class="input-field w-full px-4 py-3 border border-blue-300 dark:border-blue-700 rounded-lg bg-white dark:bg-surface-dark font-mono text-lg font-bold"
              />
              <p class="text-xs text-blue-600 dark:text-blue-400 mt-2">Số tiền ảo để test chiến lược</p>
            </div>

            <div class="button-group flex gap-3 pt-4">
              <button @click="testConnection" class="btn btn-test flex-1 px-6 py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center" :disabled="!isValid || loading">
                <span class="material-symbols-outlined mr-2">{{ loading ? 'progress_activity' : 'lan' }}</span>
                {{ loading ? 'Đang kiểm tra...' : 'Test Connection' }}
              </button>
              
              <button @click="saveConfig" class="btn btn-save flex-1 px-6 py-3 bg-primary-500 text-black font-bold rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center" :disabled="!isValid || loading">
                <span class="material-symbols-outlined mr-2">save</span>
                Lưu cấu hình
              </button>
            </div>

            <div v-if="testResult" class="result-box mt-4 p-4 rounded-lg border-2" :class="testResult.success ? 'bg-green-50 dark:bg-green-900/20 border-green-500' : 'bg-red-50 dark:bg-red-900/20 border-red-500'">
              <h3 class="font-bold text-lg mb-2 flex items-center" :class="testResult.success ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'">
                <span class="material-symbols-outlined mr-2">{{ testResult.success ? 'check_circle' : 'error' }}</span>
                {{ testResult.success ? 'Kết nối thành công!' : 'Kết nối thất bại' }}
              </h3>
              <p class="text-sm mb-3" :class="testResult.success ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">{{ testResult.message }}</p>
              <div v-if="testResult.accountInfo" class="bg-white/50 dark:bg-black/20 p-3 rounded space-y-1 text-sm">
                <p><strong>Email:</strong> {{ testResult.accountInfo.email || 'N/A' }}</p>
                <p><strong>Balance:</strong> <span class="font-mono font-bold text-profit">{{ testResult.accountInfo.balance }} USDT</span></p>
                <p><strong>Can Trade:</strong> <span :class="testResult.accountInfo.canTrade ? 'text-profit' : 'text-loss'">{{ testResult.accountInfo.canTrade ? 'Yes ✓' : 'No ✗' }}</span></p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel - Help -->
      <div class="lg:col-span-1">
        <div class="help-section bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6 sticky top-6">
          <h2 class="text-lg font-bold mb-4 flex items-center">
            <span class="material-symbols-outlined mr-2 text-primary-500">help</span>
            Hướng dẫn
          </h2>
          <ol class="space-y-3 text-sm">
            <li class="flex items-start">
              <span class="flex-shrink-0 w-6 h-6 bg-primary-500 text-black rounded-full flex items-center justify-center font-bold mr-2 mt-0.5 text-xs">1</span>
              <span>Đăng nhập <a href="https://www.binance.com" target="_blank" class="text-primary-600 dark:text-primary-400 hover:underline font-semibold">Binance.com</a></span>
            </li>
            <li class="flex items-start">
              <span class="flex-shrink-0 w-6 h-6 bg-primary-500 text-black rounded-full flex items-center justify-center font-bold mr-2 mt-0.5 text-xs">2</span>
              <span>Vào <strong>Account → API Management</strong></span>
            </li>
            <li class="flex items-start">
              <span class="flex-shrink-0 w-6 h-6 bg-primary-500 text-black rounded-full flex items-center justify-center font-bold mr-2 mt-0.5 text-xs">3</span>
              <span>Click <strong>Create API</strong></span>
            </li>
            <li class="flex items-start">
              <span class="flex-shrink-0 w-6 h-6 bg-primary-500 text-black rounded-full flex items-center justify-center font-bold mr-2 mt-0.5 text-xs">4</span>
              <span>Đặt tên (vd: "Trading Bot")</span>
            </li>
            <li class="flex items-start">
              <span class="flex-shrink-0 w-6 h-6 bg-primary-500 text-black rounded-full flex items-center justify-center font-bold mr-2 mt-0.5 text-xs">5</span>
              <div class="space-y-1">
                <strong class="block">Phân quyền:</strong>
                <ul class="ml-4 space-y-1">
                  <li class="flex items-center text-green-600 dark:text-green-400"><span class="material-symbols-outlined text-xs mr-1">check</span> Enable Reading</li>
                  <li class="flex items-center text-green-600 dark:text-green-400"><span class="material-symbols-outlined text-xs mr-1">check</span> Enable Spot Trading</li>
                  <li class="flex items-center text-red-600 dark:text-red-400"><span class="material-symbols-outlined text-xs mr-1">close</span> Enable Withdrawals</li>
                </ul>
              </div>
            </li>
            <li class="flex items-start">
              <span class="flex-shrink-0 w-6 h-6 bg-primary-500 text-black rounded-full flex items-center justify-center font-bold mr-2 mt-0.5 text-xs">6</span>
              <span>Copy API Key và Secret</span>
            </li>
            <li class="flex items-start">
              <span class="flex-shrink-0 w-6 h-6 bg-primary-500 text-black rounded-full flex items-center justify-center font-bold mr-2 mt-0.5 text-xs">7</span>
              <span>Dán vào form và test</span>
            </li>
          </ol>

          <div class="mt-6 p-3 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-800">
            <p class="text-xs text-center font-semibold text-primary-700 dark:text-primary-300">
              <span class="material-symbols-outlined text-sm align-middle mr-1">info</span>
              Luôn bắt đầu với Dry Run để test
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useBotStore } from '@/stores/ftbotwrapper';

const botStore = useBotStore();

// Form data
const apiKey = ref('');
const apiSecret = ref('');
const dryRun = ref(true);
const dryRunWallet = ref(1000);

// UI state
const showApiKey = ref(false);
const showApiSecret = ref(false);
const loading = ref(false);
const testResult = ref<any>(null);

// Validation
const isValid = computed(() => {
  return apiKey.value.length > 0 && apiSecret.value.length > 0;
});

// Test API connection
const testConnection = async () => {
  loading.value = true;
  testResult.value = null;

  try {
    // Simulate API test - Replace with actual API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    testResult.value = {
      success: true,
      message: 'Kết nối Binance API thành công!',
      accountInfo: {
        email: 'user@example.com',
        balance: '1000.00',
        canTrade: true
      }
    };
  } catch (error: any) {
    testResult.value = {
      success: false,
      message: error.message || 'Lỗi kết nối'
    };
  } finally {
    loading.value = false;
  }
};

// Save configuration
const saveConfig = async () => {
  loading.value = true;

  try {
    // Save config logic here
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    testResult.value = {
      success: true,
      message: '✅ Cấu hình đã được lưu thành công!'
    };

    // Reload after 2 seconds
    setTimeout(() => {
      window.location.reload();
    }, 2000);
  } catch (error: any) {
    testResult.value = {
      success: false,
      message: error.message || 'Lỗi khi lưu cấu hình'
    };
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-icon {
  animation: spin 1s linear infinite;
}
</style>

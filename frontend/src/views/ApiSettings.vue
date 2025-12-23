<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useSettingsStore } from '@/stores/settingsStore'
import { useBotStore } from '@/stores/botStore'
import { botApi } from '@/api/api'
import { getUsernameFromToken, isAdminUser } from '@/utils/auth'

const router = useRouter()
const settingsStore = useSettingsStore()
const botStore = useBotStore()

interface ApiProfile {
  id: string
  name: string
  api_key: string
  secret_key: string
  trading_mode: 'spot' | 'futures'
  margin_mode?: 'isolated' | 'cross'
  is_testnet: boolean
  copy_enabled: boolean
  allocation_pct: number
}

// Binance API Keys
const binanceApiKey = ref('')
const binanceSecretKey = ref('')
const profileName = ref('')
const tradingMode = ref<'spot' | 'futures'>('spot') // Always spot
const marginMode = ref<'isolated' | 'cross'>('isolated')
const showSecret = ref(false)
const isLoading = ref(false)
const message = ref('')
const messageType = ref<'success' | 'error'>('success')
const savedApiKey = ref('')
const copyEnabled = ref(false)
const allocationPct = ref(0)

// Profiles state
const profiles = ref<ApiProfile[]>([])
const currentUsername = ref('')
const isAdmin = computed(() => isAdminUser())

// Load profiles from backend
async function loadProfiles() {
  try {
    const res = await botApi.getProfiles()
    const list = res.data.profiles as ApiProfile[]
    profiles.value = list.map((profile) => ({
      ...profile,
      copy_enabled: profile.copy_enabled ?? false,
      allocation_pct: profile.allocation_pct ?? 0
    }))
  } catch (error) {
    console.error('Failed to load profiles:', error)
    profiles.value = []
  }
}

// Check for legacy localStorage and import them to backend
// Check for legacy localStorage and import them to backend
async function checkAndImportLegacy() {
  // Security: Only allow auto-import for the main admin
  // This prevents shared browsers from leaking Admin keys to new users
  if (currentUsername.value !== 'admin') {
      // PROACTIVELY CLEAR LEGACY KEYS
      // If a non-admin user logs in on a shared browser, we must wipe the admin's cached keys
      // to prevents confusion or accidental leakage.
      if (localStorage.getItem('binance_api_key')) {
          console.warn('Clearing legacy API keys from shared browser storage for security.')
          localStorage.removeItem('binance_api_key')
          localStorage.removeItem('binance_secret_key')
          localStorage.removeItem('binance_trading_mode')
      }
      return
  }

  const legacyKey = localStorage.getItem('binance_api_key')
  const legacySecret = localStorage.getItem('binance_secret_key')
  
  if (legacyKey && legacySecret) {
      const exists = profiles.value.some(p => p.api_key === legacyKey)
      if (!exists) {
           const id = crypto.randomUUID()
           const name = 'Imported Account'
           const trading_mode = (localStorage.getItem('binance_trading_mode') as any) || 'spot'
           
           try {
               await botApi.saveProfile({
                  id,
                  name,
                  api_key: legacyKey,
                  secret_key: legacySecret,
                  trading_mode,
                  is_testnet: false,
                  copy_enabled: false,
                  allocation_pct: 0
               })
               
               // After importing, reload
               await loadProfiles()
               
               // Clear legacy
               localStorage.removeItem('binance_api_key')
               localStorage.removeItem('binance_secret_key')
           } catch (e) {
               console.error('Failed to auto-import legacy profile:', e)
           }
      }
  }
}

onMounted(async () => {
  currentUsername.value = getUsernameFromToken()
  await loadProfiles()
  await checkAndImportLegacy()

  try {
    const res = await botApi.showConfig()
    if (res.data.trading_mode) {
      tradingMode.value = res.data.trading_mode
    }
    if (isAdmin.value && res.data.exchange?.key) {
       savedApiKey.value = res.data.exchange.key
    }
  } catch (error) {
    // Ignore error
  }
})

function normalizeAllocation(value: number) {
  if (!Number.isFinite(value)) {
    return 0
  }
  return Math.min(100, Math.max(0, value))
}

async function saveProfileChanges(profile: ApiProfile) {
  const allocation = normalizeAllocation(profile.allocation_pct)
  const payload = {
    ...profile,
    allocation_pct: allocation
  }
  profile.allocation_pct = allocation
  try {
    await botApi.saveProfile(payload)
    showMessage('Profile updated.', 'success')
  } catch (e: any) {
    showMessage(e.message || 'Failed to update profile', 'error')
  }
}

async function saveBinanceConfig() {
  isLoading.value = true
  message.value = ''
  
  try {
    if (!binanceApiKey.value || !binanceSecretKey.value) {
      showMessage('Vui lòng nhập cả API Key và Secret Key', 'error')
      return
    }

    const finalName = profileName.value.trim() || `Account ${profiles.value.length + 1}`
    const existingIndex = profiles.value.findIndex(p => p.api_key === binanceApiKey.value)
    
    const id = existingIndex >= 0 ? profiles.value[existingIndex].id : crypto.randomUUID()
    
    const profilePayload = {
      id,
      name: finalName,
      api_key: binanceApiKey.value,
      secret_key: binanceSecretKey.value,
      trading_mode: tradingMode.value,
      margin_mode: marginMode.value,
      is_testnet: false,
      copy_enabled: copyEnabled.value,
      allocation_pct: normalizeAllocation(allocationPct.value)
    }

    // 1. Save to backend profiles
    await botApi.saveProfile(profilePayload)
    await loadProfiles()
    
    if (isAdmin.value) {
      // 2. Activate profile (admin only)
      const dbUrl = `sqlite:///tradesv3_${id}.sqlite`

      await botApi.setExchangeConfig(
        binanceApiKey.value,
        binanceSecretKey.value,
        false,
        tradingMode.value,
        marginMode.value,
        dbUrl
      )

      await botApi.saveExchangeConfig(
        binanceApiKey.value,
        binanceSecretKey.value,
        false,
        tradingMode.value,
        false
      )

      try {
        await botApi.reloadConfig()
        await new Promise(resolve => setTimeout(resolve, 2000))
        await botStore.refreshAll()
      } catch (reloadError) {
        console.warn('Backend reload failed:', reloadError)
      }
    }
    
    const successMessage = isAdmin.value
      ? `✅ Đã lưu profile "${finalName}" và kích hoạt thành công!`
      : `✅ Đã lưu profile "${finalName}". Bạn có thể bật copy trading.`
    showMessage(successMessage, 'success')
    savedApiKey.value = binanceApiKey.value
    profileName.value = ''
    binanceApiKey.value = ''
    binanceSecretKey.value = ''
    copyEnabled.value = false
    allocationPct.value = 0
  } catch (e: any) {
    showMessage(e.message || 'Lỗi khi lưu cấu hình Binance', 'error')
  } finally {
    isLoading.value = false
  }
}

async function switchToProfile(profile: ApiProfile) {
  if (!isAdmin.value) {
    showMessage('Chỉ admin mới được chuyển tài khoản bot.', 'error')
    return
  }
  if (confirm(`Bạn có chắc muốn chuyển sang tài khoản "${profile.name}"? Bot sẽ reload lại.`)) {
    isLoading.value = true
    try {
        const dbUrl = `sqlite:///tradesv3_${profile.id}.sqlite`
        
        await botApi.setExchangeConfig(
          profile.api_key,
          profile.secret_key,
          false, 
          profile.trading_mode,
          profile.margin_mode || 'isolated',
          dbUrl
        )
        
        await botApi.saveExchangeConfig(
          profile.api_key,
          profile.secret_key,
          false,
          profile.trading_mode,
          false
        )

        try {
          await botApi.reloadConfig()
          await new Promise(resolve => setTimeout(resolve, 2000))
          await botStore.refreshAll()
        } catch (reloadError) {
           console.warn('Backend reload failed:', reloadError)
        }

        savedApiKey.value = profile.api_key
        showMessage(`✅ Đã chuyển sang "${profile.name}"!`, 'success')

    } catch (e: any) {
        showMessage(e.message || 'Lỗi khi chuyển profile', 'error')
    } finally {
        isLoading.value = false
    }
  }
}

async function deleteProfile(id: string) {
  if (confirm('Xóa tài khoản này?')) {
    try {
      await botApi.deleteProfile(id)
      await loadProfiles()
      showMessage('Tài khoản đã bị xóa!', 'success')
    } catch (e: any) {
      showMessage('Không thể xóa tài khoản', 'error')
    }
  }
}

function clearBinanceConfig() {
  binanceApiKey.value = ''
  binanceSecretKey.value = ''
  profileName.value = ''
  copyEnabled.value = false
  allocationPct.value = 0
  showMessage('Đã xóa trắng form', 'success')
}

function showMessage(msg: string, type: 'success' | 'error') {
  message.value = msg
  messageType.value = type
  setTimeout(() => { message.value = '' }, 5000)
}

function maskKey(key: string) {
  if (!key || key.length < 8) return '****'
  return `${key.substring(0, 4)}...${key.substring(key.length - 4)}`
}

</script>

<template>
  <div class="space-y-6 fade-in max-w-xl pb-20">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-white">API Settings</h1>
      <p class="text-gray-500 text-sm">Quản lý nhiều tài khoản Binance</p>
    </div>

    <!-- Message -->
    <div v-if="message" 
      class="p-3 rounded-lg"
      :class="messageType === 'success' ? 'bg-success/20 text-success' : 'bg-danger/20 text-danger'"
    >
      {{ message }}
    </div>

    <!-- Form Configuration -->
    <div class="card">
      <div class="card-header">
        <span>🔗 Cấu hình mới / Cập nhật</span>
      </div>
      
      <!-- Live Trading Notice -->
      <div class="mb-6 p-4 rounded-xl border bg-warning/5 border-warning/20">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full flex items-center justify-center text-xl bg-warning/20">
             ⚠️
          </div>
          <div>
            <h3 class="font-bold text-white text-sm">Lưu ý: Auto Live Trading</h3>
            <p class="text-xs text-gray-400 mt-0.5">
              Lưu cấu hình sẽ tự động kích hoạt chế độ Live Trading cho tài khoản này.
            </p>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <!-- Profile Name -->
        <div>
          <label class="label">Tên gợi nhớ (Ví dụ: Tài khoản chính)</label>
          <input 
            v-model="profileName" 
            type="text" 
            class="input" 
            placeholder="Nhập tên tài khoản... (Để trống để tự tạo)"
          />
        </div>

        <!-- API Key -->
        <div>
          <label class="label">Binance API Key</label>
          <input 
            v-model="binanceApiKey" 
            type="text" 
            class="input font-mono text-sm" 
            placeholder="Nhập API Key từ Binance"
            autocomplete="off"
          />
        </div>

        <!-- Secret Key -->
        <div>
          <label class="label">Secret Key</label>
          <div class="relative">
            <input 
              v-model="binanceSecretKey" 
              :type="showSecret ? 'text' : 'password'" 
              class="input font-mono text-sm pr-12" 
              placeholder="Nhập Secret Key"
              autocomplete="new-password"
            />
            <button 
              type="button"
              @click="showSecret = !showSecret"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
            >
              {{ showSecret ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm font-medium text-white">Copy trading</div>
              <p class="text-xs text-gray-500">Mirror master trades from this bot</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="copyEnabled" class="sr-only peer">
              <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>
          <div>
            <label class="label">Allocation %</label>
            <input
              v-model.number="allocationPct"
              type="number"
              class="input"
              min="0"
              max="100"
              step="0.1"
              :disabled="!copyEnabled"
              placeholder="0"
            />
          </div>
        </div>

        <!-- Buttons -->
        <div class="space-y-3 pt-4 border-t border-dark-100">
          <button @click="saveBinanceConfig" :disabled="isLoading" class="btn btn-primary w-full">
            {{ isLoading ? '⏳ Đang xử lý...' : (isAdmin ? '💾 Lưu & Kích hoạt' : '💾 Lưu profile') }}
          </button>
          <button @click="clearBinanceConfig" class="btn btn-outline w-full">
            🗑️ Xóa form
          </button>
        </div>
      </div>
    </div>

    <!-- Saved Profiles List -->
    <div class="space-y-4">
      <h2 class="text-lg font-bold text-white flex items-center gap-2">
        📂 Danh sách tài khoản
        <span class="text-xs font-normal text-gray-500">({{ profiles.length }})</span>
      </h2>

      <div v-if="profiles.length === 0" class="text-center py-8 bg-dark-100 rounded-xl border border-dashed border-dark-50">
        <p class="text-gray-500">Chưa có tài khoản nào được lưu</p>
      </div>

      <div v-else class="grid gap-3">
        <div 
          v-for="profile in profiles" 
          :key="profile.id"
          class="card hover:border-primary/50 transition-colors group"
          :class="{ 'border-primary ring-1 ring-primary/20': profile.api_key === savedApiKey }"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full flex items-center justify-center text-lg"
                :class="profile.api_key === savedApiKey ? 'bg-primary text-dark-300' : 'bg-dark-100 text-gray-400'"
              >
                {{ profile.api_key === savedApiKey ? '🚀' : '👤' }}
              </div>
              <div>
                <h3 class="font-bold text-white" :class="{'text-primary': profile.api_key === savedApiKey}">
                  {{ profile.name }}
                </h3>
                <div class="flex items-center gap-2 text-xs text-gray-400 font-mono">
                  <span>{{ maskKey(profile.api_key) }}</span>
                  <span v-if="isAdmin && profile.api_key === savedApiKey" class="px-1.5 py-0.5 rounded bg-success/20 text-success font-sans font-bold text-[10px]">ACTIVE</span>
                </div>
              </div>
            </div>

            <div class="flex items-center gap-2 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
               <button 
                @click.stop="deleteProfile(profile.id)"
                class="p-2 text-gray-500 hover:text-danger hover:bg-danger/10 rounded-lg transition-colors"
                title="Xóa tài khoản này"
              >
                🗑️
              </button>
              <button 
                v-if="isAdmin"
                @click="switchToProfile(profile)"
                class="btn btn-sm"
                :class="profile.api_key === savedApiKey ? 'btn-success' : 'btn-outline'"
              >
                {{ profile.api_key === savedApiKey ? 'Đang dùng' : 'Chuyển sang' }}
              </button>
            </div>
          </div>
          <div class="mt-4 grid gap-3 sm:grid-cols-2">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-xs font-medium text-white">Copy trading</div>
                <p class="text-[10px] text-gray-500">Mirror master trades</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  v-model="profile.copy_enabled"
                  class="sr-only peer"
                  @change="saveProfileChanges(profile)"
                >
                <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>
            <div>
              <label class="label text-xs">Allocation %</label>
              <input
                v-model.number="profile.allocation_pct"
                type="number"
                class="input"
                min="0"
                max="100"
                step="0.1"
                :disabled="!profile.copy_enabled"
                placeholder="0"
                @change="saveProfileChanges(profile)"
                @blur="saveProfileChanges(profile)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Back Button -->
    <router-link to="/settings" class="btn btn-outline w-full block text-center">
      ← Quay lại Settings
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBotStore } from '@/stores/botStore'
import { useSettingsStore } from '@/stores/settingsStore'
import { botApi } from '@/api/api'

const router = useRouter()
const botStore = useBotStore()
const settingsStore = useSettingsStore()

// Bot connection
const apiUrl = ref('http://localhost:8080')
const username = ref('binancebot')
const password = ref('')

const isLoading = ref(false)
const error = ref('')
const showPassword = ref(false)
const isRegister = ref(false) // Toggle Login/Register

// Handle Form Submit
async function handleSubmit() {
  if (isRegister.value) {
    await handleRegister()
  } else {
    await handleLogin()
  }
}

// Register
async function handleRegister() {
  if (isLoading.value) return
  if (!username.value || !password.value) {
    error.value = 'Vui lòng nhập đầy đủ thông tin'
    return
  }
  
  isLoading.value = true
  error.value = ''
  
  try {
    const res = await botApi.registerUser(username.value, password.value)
    if (res.data.status === 'success') {
      alert(`Tạo tài khoản ${res.data.username} thành công! Vui lòng đăng nhập.`)
      isRegister.value = false // Switch back to login
    }
  } catch (e: any) {
    console.error('Register error:', e)
    error.value = e.response?.data?.detail || 'Tạo tài khoản thất bại.'
  } finally {
    isLoading.value = false
  }
}

// Login: handle authentication
async function handleLogin() {
  if (isLoading.value) return
  
  if (!username.value || !password.value) {
    error.value = 'Vui lòng nhập đầy đủ thông tin'
    return
  }

  isLoading.value = true
  error.value = ''
  
  try {
    console.log('Attempting login for:', username.value)
    settingsStore.setApiUrl(apiUrl.value)
    
    // IMPORTANT: Ensure clean state before new login
    botStore.disconnect()
    
    const success = await botStore.login(username.value, password.value, false)
    
    if (success) {
      console.log('Login successful, redirecting...')
      await router.push('/dashboard')
    } else {
      error.value = 'Đăng nhập thất bại. Vui lòng kiểm tra lại tài khoản.'
    }
  } catch (e: any) {
    console.error('Login error:', e)
    error.value = e.message || 'Đăng nhập thất bại. Kiểm tra lại thông tin.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  // Check if already logged in (using store state directly)
  if (botStore.isConnected) {
    router.push('/dashboard')
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center">
    <div class="w-full max-w-md">
      <!-- Logo & Title -->
      <div class="text-center mb-8">
        <div class="w-20 h-20 rounded-2xl bg-primary mx-auto mb-4 flex items-center justify-center shadow-lg shadow-primary/20">
          <span class="text-4xl font-bold text-dark-300">B</span>
        </div>
        <h1 class="text-3xl font-bold text-white mb-2">BinanceBot</h1>
        <p class="text-gray-500">Automated Crypto Trading System</p>
      </div>

      <!-- Login Card -->
      <div class="card fade-in">
        <div class="p-4 rounded-lg bg-danger/10 border border-danger/20 mb-6">
          <div class="flex items-center gap-3">
            <span class="text-2xl">💰</span>
            <div>
              <p class="text-danger font-medium">Live Trading & Simulation</p>
              <p class="text-xs text-gray-400">Kết nối trực tiếp đến tài khoản Binance của bạn.</p>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mb-4 p-3 rounded-lg bg-danger/10 border border-danger/20">
          <p class="text-sm text-danger">❌ {{ error }}</p>
        </div>

        <!-- Login form -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Username -->
          <div>
            <label class="label">Tài khoản</label>
            <input 
              v-model="username"
              type="text" 
              class="input"
              placeholder="binancebot"
              autocomplete="username"
            />
          </div>
          
          <!-- Password -->
          <div>
            <label class="label">Mật khẩu</label>
            <div class="relative">
              <input 
                v-model="password"
                :type="showPassword ? 'text' : 'password'" 
                class="input pr-12"
                placeholder="Nhập mật khẩu"
                autocomplete="current-password"
              />
              <button 
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
              >
                {{ showPassword ? '🙈' : '👁️' }}
              </button>
            </div>
          </div>
          
          <!-- Submit Button -->
          <button 
            type="submit" 
            :disabled="isLoading"
            class="btn w-full py-3 text-lg font-semibold"
            :class="isRegister ? 'btn-primary' : 'btn-success'"
          >
            <span v-if="isLoading">⏳ Đang xử lý...</span>
            <span v-else>{{ isRegister ? '✨ Đăng ký tài khoản' : '🚀 Bắt đầu giao dịch' }}</span>
          </button>
          
          <!-- Toggle Register -->
          <div class="text-center mt-4">
             <button type="button" @click="isRegister = !isRegister" class="text-sm text-primary hover:text-primary-hover hover:underline">
               {{ isRegister ? 'Đã có tài khoản? Đăng nhập ngay' : 'Chưa có tài khoản? Đăng ký mới' }}
             </button>
          </div>

          <p class="text-center text-gray-500 text-xs mt-4" v-if="!isRegister">
            Cấu hình API keys và chế độ Dry Run tại Settings → API Settings
          </p>
        </form>

        <!-- Footer -->
        <div class="mt-6 pt-6 border-t border-dark-100">
          <p class="text-xs text-gray-500 text-center">
            BinanceBot v2.0 • RSI-EMA Strategy
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

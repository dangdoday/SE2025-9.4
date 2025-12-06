<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useBotStore } from '@/stores/ftbotwrapper';
import { useLoginInfo } from '@/composables/loginInfo';
import type { BotDescriptor, AuthPayload } from '@/types';

const router = useRouter();
const botStore = useBotStore();

const isLogin = ref(true);
const loading = ref(false);
const errorMessage = ref('');

// Login form
const loginUsername = ref('');
const loginPassword = ref('');

// Register form
const registerUsername = ref('');
const registerPassword = ref('');
const registerConfirmPassword = ref('');

const handleLogin = async () => {
  if (!loginUsername.value || !loginPassword.value) {
    errorMessage.value = 'Vui lòng điền đầy đủ thông tin';
    return;
  }

  loading.value = true;
  errorMessage.value = '';

  try {
    // Mock login for demo - simulate successful authentication
    const botId = `bot-${Date.now()}`;
    const authUrl = 'http://127.0.0.1:8080';
    
    // Initialize login info in storage (mock authentication)
    const { login } = useLoginInfo(botId);
    const mockAuth: AuthPayload = {
      botName: loginUsername.value || 'BinanceBot',
      url: authUrl,
      username: loginUsername.value,
      password: loginPassword.value,
    };
    
    // Mock login - store fake tokens
    await login(mockAuth).catch(() => {
      // If real API fails, manually set mock login info
      const loginInfoStore = useLoginInfo(botId);
      const mockStorage = {
        botName: mockAuth.botName,
        apiUrl: authUrl,
        username: mockAuth.username,
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token',
        autoRefresh: false,
      };
      // Manually set in storage
      localStorage.setItem('ftAuthLoginInfo', JSON.stringify({
        ...JSON.parse(localStorage.getItem('ftAuthLoginInfo') || '{}'),
        [botId]: mockStorage,
      }));
    });
    
    const botDescriptor: BotDescriptor = {
      botName: loginUsername.value || 'BinanceBot',
      botId,
      botUrl: authUrl,
      sortId: Object.keys(botStore.availableBots).length + 1,
    };
    
    // Add bot to store
    botStore.addBot(botDescriptor);
    botStore.selectBot(botId);

    router.push('/dashboard');
  } catch (error: any) {
    errorMessage.value = error.message || 'Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.';
  } finally {
    loading.value = false;
  }
};

const handleRegister = async () => {
  if (!registerUsername.value || !registerPassword.value || !registerConfirmPassword.value) {
    errorMessage.value = 'Vui lòng điền đầy đủ thông tin';
    return;
  }

  if (registerPassword.value !== registerConfirmPassword.value) {
    errorMessage.value = 'Mật khẩu xác nhận không khớp';
    return;
  }

  if (registerPassword.value.length < 6) {
    errorMessage.value = 'Mật khẩu phải có ít nhất 6 ký tự';
    return;
  }

  loading.value = true;
  errorMessage.value = '';

  try {
    // Mock registration for demo - simulate successful account creation
    const botId = `bot-${Date.now()}`;
    const authUrl = 'http://127.0.0.1:8080';
    
    // Initialize login info in storage (mock authentication)
    const { login } = useLoginInfo(botId);
    const mockAuth: AuthPayload = {
      botName: registerUsername.value,
      url: authUrl,
      username: registerUsername.value,
      password: registerPassword.value,
    };
    
    // Mock login - store fake tokens
    await login(mockAuth).catch(() => {
      // If real API fails, manually set mock login info
      const mockStorage = {
        botName: mockAuth.botName,
        apiUrl: authUrl,
        username: mockAuth.username,
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token',
        autoRefresh: false,
      };
      // Manually set in storage
      localStorage.setItem('ftAuthLoginInfo', JSON.stringify({
        ...JSON.parse(localStorage.getItem('ftAuthLoginInfo') || '{}'),
        [botId]: mockStorage,
      }));
    });
    
    const botDescriptor: BotDescriptor = {
      botName: registerUsername.value,
      botId,
      botUrl: authUrl,
      sortId: Object.keys(botStore.availableBots).length + 1,
    };
    
    // Add bot to store
    botStore.addBot(botDescriptor);
    botStore.selectBot(botId);

    router.push('/dashboard');
  } catch (error: any) {
    errorMessage.value = error.message || 'Đăng ký thất bại. Vui lòng thử lại.';
  } finally {
    loading.value = false;
  }
};


</script>

<template>
  <div class="min-h-[calc(100vh-120px)] flex items-center justify-center p-6">
    <div class="w-full max-w-md">
      <!-- Logo & Title -->
      <div class="text-center mb-8">
        <div class="flex justify-center mb-4">
          <div class="h-20 w-20 flex items-center justify-center rounded-2xl bg-primary-500 text-black shadow-lg">
            <svg fill="none" viewBox="0 0 48 48" class="w-12 h-12" xmlns="http://www.w3.org/2000/svg">
              <path clip-rule="evenodd" d="M39.475 21.6262C40.358 21.4363 40.6863 21.5589 40.7581 21.5934C40.7876 21.655 40.8547 21.857 40.8082 22.3336C40.7408 23.0255 40.4502 24.0046 39.8572 25.2301C38.6799 27.6631 36.5085 30.6631 33.5858 33.5858C30.6631 36.5085 27.6632 38.6799 25.2301 39.8572C24.0046 40.4502 23.0255 40.7407 22.3336 40.8082C21.8571 40.8547 21.6551 40.7875 21.5934 40.7581C21.5589 40.6863 21.4363 40.358 21.6262 39.475C21.8562 38.4054 22.4689 36.9657 23.5038 35.2817C24.7575 33.2417 26.5497 30.9744 28.7621 28.762C30.9744 26.5497 33.2417 24.7574 35.2817 23.5037C36.9657 22.4689 38.4054 21.8562 39.475 21.6262ZM4.41189 29.2403L18.7597 43.5881C19.8813 44.7097 21.4027 44.9179 22.7217 44.7893C24.0585 44.659 25.5148 44.1631 26.9723 43.4579C29.9052 42.0387 33.2618 39.5667 36.4142 36.4142C39.5667 33.2618 42.0387 29.9052 43.4579 26.9723C44.1631 25.5148 44.659 24.0585 44.7893 22.7217C44.9179 21.4027 44.7097 19.8813 43.5881 18.7597L29.2403 4.41187C27.8527 3.02428 25.8765 3.02573 24.2861 3.36776C22.6081 3.72863 20.7334 4.58419 18.8396 5.74801C16.4978 7.18716 13.9881 9.18353 11.5858 11.5858C9.18354 13.988 7.18717 16.4978 5.74802 18.8396C4.58421 20.7334 3.72865 22.6081 3.36778 24.2861C3.02574 25.8765 3.02429 27.8527 4.41189 29.2403Z" fill="currentColor" fill-rule="evenodd"></path>
            </svg>
          </div>
        </div>
        <h1 class="text-3xl font-bold mb-2">BinanceBot</h1>
        <p class="text-gray-500 dark:text-gray-400">Automated Trading System</p>
      </div>

      <!-- Login/Register Card -->
      <div class="bg-white dark:bg-surface-dark rounded-xl border border-gray-200 dark:border-gray-700 shadow-xl p-8">
        <!-- Tab Switcher -->
        <div class="flex gap-2 mb-6 bg-gray-100 dark:bg-gray-800 p-1 rounded-lg">
          <button
            @click="isLogin = true"
            :class="isLogin ? 'bg-primary-500 text-black font-bold' : 'text-gray-600 dark:text-gray-400'"
            class="flex-1 py-2 px-4 rounded-lg transition-all duration-200"
          >
            Đăng nhập
          </button>
          <button
            @click="isLogin = false"
            :class="!isLogin ? 'bg-primary-500 text-black font-bold' : 'text-gray-600 dark:text-gray-400'"
            class="flex-1 py-2 px-4 rounded-lg transition-all duration-200"
          >
            Đăng ký
          </button>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p class="text-sm text-red-600 dark:text-red-400 flex items-center">
            <span class="material-symbols-outlined text-sm mr-2">error</span>
            {{ errorMessage }}
          </p>
        </div>

        <!-- Login Form -->
        <form v-if="isLogin" @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">Username</label>
            <input
              v-model="loginUsername"
              type="text"
              placeholder="Nhập username"
              class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">Password</label>
            <input
              v-model="loginPassword"
              type="password"
              placeholder="Nhập mật khẩu"
              class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
              required
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-primary-500 hover:bg-primary-600 text-black font-bold rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <span v-if="loading" class="material-symbols-outlined animate-spin mr-2">progress_activity</span>
            {{ loading ? 'Đang đăng nhập...' : 'Đăng nhập' }}
          </button>
        </form>

        <!-- Register Form -->
        <form v-else @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">Username</label>
            <input
              v-model="registerUsername"
              type="text"
              placeholder="Nhập username"
              class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">Password</label>
            <input
              v-model="registerPassword"
              type="password"
              placeholder="Nhập mật khẩu (tối thiểu 6 ký tự)"
              class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
              required
              minlength="6"
            />
          </div>

          <div>
            <label class="block text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">Xác nhận Password</label>
            <input
              v-model="registerConfirmPassword"
              type="password"
              placeholder="Nhập lại mật khẩu"
              class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
              required
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-primary-500 hover:bg-primary-600 text-black font-bold rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <span v-if="loading" class="material-symbols-outlined animate-spin mr-2">progress_activity</span>
            {{ loading ? 'Đang đăng ký...' : 'Đăng ký' }}
          </button>
        </form>

        <!-- Quick Setup Info -->
        <div class="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <p class="text-xs text-blue-800 dark:text-blue-300 mb-2 font-semibold flex items-center">
            <span class="material-symbols-outlined text-sm mr-2">info</span>
            Hướng dẫn nhanh
          </p>
          <ul class="text-xs text-blue-700 dark:text-blue-400 space-y-1 ml-6 list-disc">
            <li>Khởi động bot: <code class="bg-blue-100 dark:bg-blue-950 px-1 py-0.5 rounded">binancebot trade --config config.json</code></li>
            <li>URL mặc định: <code class="bg-blue-100 dark:bg-blue-950 px-1 py-0.5 rounded">http://127.0.0.1:8080</code></li>
            <li>Username/Password được cấu hình trong config file</li>
          </ul>
        </div>
      </div>

      <!-- Footer -->
      <p class="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
        Powered by <span class="text-primary-500 font-semibold">BinanceBot</span> Trading System
      </p>
    </div>
  </div>
</template>

<style scoped>
.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

code {
  font-family: 'Fira Code', monospace;
}
</style>
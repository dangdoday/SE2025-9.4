<script setup lang="ts">
import { ref } from 'vue'
import { useSettingsStore } from '@/stores/settingsStore'
import { useBotStore } from '@/stores/botStore'

const settingsStore = useSettingsStore()
const botStore = useBotStore()

const refreshInterval = ref(settingsStore.refreshInterval / 1000)
const confirmDialogs = ref(true)
const showProfit = ref(true)

function saveSettings() {
  settingsStore.setRefreshInterval(refreshInterval.value * 1000)
  // Show toast or notification
}


const authUsername = ref('')
const authPassword = ref('')
const isAuthLoading = ref(false)
const authMessage = ref({ text: '', type: '' })

async function updateAuth() {
  if (!authUsername.value || !authPassword.value) {
    authMessage.value = { text: 'Please enter both username and password', type: 'error' }
    return
  }

  try {
    isAuthLoading.value = true
    authMessage.value = { text: '', type: '' }
    await botStore.updateAccount({
      username: authUsername.value,
      password: authPassword.value
    })
    authMessage.value = { text: 'Authentication updated! Restart backend to apply.', type: 'success' }
  } catch (e: any) {
    authMessage.value = { text: e.message || 'Failed to update authentication', type: 'error' }
  } finally {
    isAuthLoading.value = false
  }
}
</script>

<template>
  <div class="space-y-6 fade-in max-w-3xl">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-white">Settings</h1>
      <p class="text-gray-500 text-sm">Configure your trading bot preferences</p>
    </div>

    <!-- General Settings -->
    <div class="card">
      <div class="card-header">
        <span>⚙️ General Settings</span>
      </div>

      <div class="space-y-6">
        <!-- Refresh Interval -->
        <div>
          <label class="label">Auto Refresh Interval (seconds)</label>
          <input v-model.number="refreshInterval" type="number" class="input w-32" min="1" max="60" />
          <p class="text-xs text-gray-500 mt-1">How often to refresh data from the bot</p>
        </div>

        <!-- Confirm Dialogs -->
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm font-medium text-white">Confirm Dialogs</div>
            <p class="text-xs text-gray-500">Show confirmation before force exit</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="confirmDialogs" class="sr-only peer">
            <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
          </label>
        </div>

        <!-- Show Profit in Title -->
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm font-medium text-white">Show Open Trades in Title</div>
            <p class="text-xs text-gray-500">Display trade count in browser tab</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="showProfit" class="sr-only peer">
            <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
          </label>
        </div>
      </div>
    </div>

    <!-- Account Security -->
    <div class="card">
      <div class="card-header">
        <span>🔒 Account Security</span>
      </div>

      <div class="space-y-4">
        <p class="text-xs text-gray-500">Update your bot login credentials. These are saved to your config file.</p>
        
        <div v-if="authMessage.text" :class="`p-3 rounded-lg text-xs ${authMessage.type === 'success' ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'}`">
          {{ authMessage.text }}
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">New Username</label>
            <input v-model="authUsername" type="text" class="input" placeholder="Enter new username" />
          </div>
          <div>
            <label class="label">New Password</label>
            <input v-model="authPassword" type="password" class="input" placeholder="Enter new password" />
          </div>
        </div>

        <button @click="updateAuth" class="btn btn-outline w-full" :disabled="isAuthLoading">
          {{ isAuthLoading ? 'Updating...' : 'Update Credentials' }}
        </button>
      </div>
    </div>

    <!-- Bot Info -->
    <div class="card">
      <div class="card-header">
        <span>🤖 Bot Information</span>
      </div>

      <div class="space-y-4">
        <div class="flex justify-between py-2 border-b border-dark-100">
          <span class="text-gray-500">Strategy</span>
          <span class="text-white font-medium">{{ botStore.botState?.strategy || 'RSI_EMA' }}</span>
        </div>
        <div class="flex justify-between py-2 border-b border-dark-100">
          <span class="text-gray-500">Trading Mode</span>
          <span class="text-white font-medium">{{ botStore.botState?.trading_mode || 'Spot' }}</span>
        </div>
        <div class="flex justify-between py-2 border-b border-dark-100">
          <span class="text-gray-500">Dry Run</span>
          <span :class="botStore.botState?.dry_run ? 'text-warning' : 'text-success'">
            {{ botStore.botState?.dry_run ? 'Yes' : 'No' }}
          </span>
        </div>
        <div class="flex justify-between py-2">
          <span class="text-gray-500">Max Open Trades</span>
          <span class="text-white font-medium">{{ botStore.botState?.max_open_trades || 3 }}</span>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="card">
      <div class="card-header">
        <span>🔧 Actions</span>
      </div>

      <div class="space-y-3">
        <button @click="saveSettings" class="btn btn-primary w-full">
          💾 Save Settings
        </button>

        <router-link to="/settings/api" class="btn btn-outline w-full block text-center">
          🔑 API Settings
        </router-link>
      </div>
    </div>
  </div>
</template>

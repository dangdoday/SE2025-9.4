<script setup lang="ts">
import { ref } from 'vue'
import { useBotStore } from '@/stores/botStore'

const emit = defineEmits(['close'])
const botStore = useBotStore()

const pair = ref('')
const price = ref<number | undefined>()
const stakeAmount = ref<number | undefined>()
const isLoading = ref(false)
const error = ref('')

async function handleSubmit() {
  if (!pair.value) {
    error.value = 'Please select a pair'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    await botStore.forceEntry(pair.value, price.value, stakeAmount.value)
    emit('close')
  } catch (e: any) {
    error.value = e.message || 'Failed to create trade'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="space-y-4">
    <!-- Error -->
    <div v-if="error" class="p-3 rounded-lg bg-danger/10 border border-danger/20">
      <p class="text-sm text-danger">{{ error }}</p>
    </div>

    <!-- Pair -->
    <div>
      <label class="label">Trading Pair</label>
      <select v-model="pair" class="input">
        <option value="">Select pair...</option>
        <option v-for="p in botStore.whitelist" :key="p" :value="p">{{ p }}</option>
      </select>
    </div>

    <!-- Price (Optional) -->
    <div>
      <label class="label">Price (Optional)</label>
      <input 
        v-model.number="price" 
        type="number" 
        class="input" 
        placeholder="Market price if empty"
        step="0.00000001"
      />
    </div>

    <!-- Stake Amount (Optional) -->
    <div>
      <div class="flex justify-between items-center mb-1">
        <label class="label mb-0">Stake Amount</label>
        <span class="text-xs font-medium text-primary">{{ botStore.stakeCurrency }}</span>
      </div>
      <input 
        v-model.number="stakeAmount" 
        type="number" 
        class="input" 
        :placeholder="`Bot default: ${botStore.botState?.stake_amount || 30}`"
        step="0.01"
      />
      <p class="text-[11px] text-gray-400 mt-1 leading-tight">
        * Enter amount in {{ botStore.stakeCurrency }} (e.g. 10 or 50). 
        Binance usually requires at least 5-10 {{ botStore.stakeCurrency }} per trade.
      </p>
    </div>

    <!-- Buttons -->
    <div class="flex gap-3 pt-4">
      <button 
        @click="handleSubmit" 
        class="btn btn-primary flex-1"
        :disabled="isLoading"
      >
        {{ isLoading ? 'Creating...' : '✓ Create Trade' }}
      </button>
      <button @click="emit('close')" class="btn btn-outline">
        Cancel
      </button>
    </div>
  </div>
</template>

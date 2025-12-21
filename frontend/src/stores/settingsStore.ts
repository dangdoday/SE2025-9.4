import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export type ConnectionMode = 'bot' | 'binance' | 'none'
export type TradingMode = 'spot' | 'futures'
export type MarginMode = 'isolated' | 'cross'

export const useSettingsStore = defineStore('settings', () => {
    // Connection Mode
    const connectionMode = ref<ConnectionMode>(
        (localStorage.getItem('connection_mode') as ConnectionMode) || 'none'
    )

    // API Settings
    const apiUrl = ref(localStorage.getItem('api_url') || 'http://localhost:8080')
    const username = ref(localStorage.getItem('username') || '')
    const token = ref(localStorage.getItem('bot_token') || '')

    // Binance Settings
    const binanceApiKey = ref(localStorage.getItem('binance_api_key') || '')
    const binanceSecretKey = ref(localStorage.getItem('binance_secret_key') || '')
    const tradingMode = ref<TradingMode>(
        (localStorage.getItem('trading_mode') as TradingMode) || 'spot'
    )
    const marginMode = ref<MarginMode>(
        (localStorage.getItem('margin_mode') as MarginMode) || 'isolated'
    )

    // UI Settings
    const darkMode = ref(true)
    const sidebarCollapsed = ref(false)
    const refreshInterval = ref(5000)

    // Computed
    const isConnectedToBot = computed(() => !!token.value)
    const isConnected = computed(() => !!token.value)
    const modeLabel = computed(() => {
        if (!token.value) return 'Disconnected'
        if (tradingMode.value === 'futures') {
            return `⚡ Binance Futures`
        }
        return `📊 Binance Spot`
    })

    // Actions
    function setConnectionMode(mode: ConnectionMode) {
        connectionMode.value = mode
        localStorage.setItem('connection_mode', mode)
    }

    function setApiUrl(url: string) {
        apiUrl.value = url
        localStorage.setItem('api_url', url)
    }

    function setCredentials(user: string, authToken: string) {
        username.value = user
        token.value = authToken
        localStorage.setItem('username', user)
        localStorage.setItem('bot_token', authToken)
    }

    function clearCredentials() {
        username.value = ''
        token.value = ''
        localStorage.removeItem('username')
        localStorage.removeItem('bot_token')
        setConnectionMode('none')
    }

    function setBinanceCredentials(
        apiKey: string,
        secretKey: string,
        tMode: TradingMode = 'spot',
        mMode: MarginMode = 'isolated'
    ) {
        binanceApiKey.value = apiKey
        binanceSecretKey.value = secretKey
        tradingMode.value = tMode
        marginMode.value = mMode
        localStorage.setItem('binance_api_key', apiKey)
        localStorage.setItem('binance_secret_key', secretKey)
        localStorage.setItem('trading_mode', tMode)
        localStorage.setItem('margin_mode', mMode)
        setConnectionMode('binance')
    }

    function clearBinanceCredentials() {
        binanceApiKey.value = ''
        binanceSecretKey.value = ''
        tradingMode.value = 'spot'
        marginMode.value = 'isolated'
        localStorage.removeItem('binance_api_key')
        localStorage.removeItem('binance_secret_key')
        localStorage.removeItem('trading_mode')
        localStorage.removeItem('margin_mode')
        if (connectionMode.value === 'binance') {
            setConnectionMode('none')
        }
    }

    function toggleSidebar() {
        sidebarCollapsed.value = !sidebarCollapsed.value
    }

    function setRefreshInterval(interval: number) {
        refreshInterval.value = interval
    }

    return {
        // State
        connectionMode,
        apiUrl,
        username,
        token,
        binanceApiKey,
        binanceSecretKey,
        tradingMode,
        marginMode,
        darkMode,
        sidebarCollapsed,
        refreshInterval,
        // Computed
        isConnectedToBot,
        isConnected,
        modeLabel,
        // Actions
        setConnectionMode,
        setApiUrl,
        setCredentials,
        clearCredentials,
        setBinanceCredentials,
        clearBinanceCredentials,
        toggleSidebar,
        setRefreshInterval
    }
})

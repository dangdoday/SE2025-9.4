import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { botApi } from '@/api/api'
import { useSettingsStore } from './settingsStore'

export interface Trade {
    trade_id: number
    pair: string
    is_open: boolean
    open_date: string
    close_date?: string
    open_rate: number
    close_rate?: number
    stake_amount: number
    profit_abs?: number
    profit_ratio?: number
    exit_reason?: string
}

export interface Balance {
    currency: string
    free: number
    used: number
    balance: number
    est_stake: number
}

export interface BotState {
    state: string
    running: boolean
    dry_run: boolean
    max_open_trades: number
    stake_currency: string
    stake_amount: number
    trading_mode: string
    strategy?: string
    bot_name?: string
    version?: string
}

export const useBotStore = defineStore('bot', () => {
    // State
    const isConnected = ref(false)
    const isLoading = ref(false)
    const botState = ref<BotState | null>(null)
    const balance = ref<Balance[]>([])
    const totalBalance = ref(0)
    const profit = ref<any>(null)
    const openTrades = ref<Trade[]>([])
    const closedTrades = ref<Trade[]>([])
    const dailyStats = ref<any[]>([])
    const performance = ref<any[]>([])
    const whitelist = ref<string[]>([])
    const blacklist = ref<string[]>([])
    const strategies = ref<string[]>([])
    const logs = ref<any[]>([])
    const version = ref('')

    // Computed
    const openTradeCount = computed(() => openTrades.value.length)
    const totalProfit = computed(() => profit.value?.profit_all_coin || 0)
    const winRate = computed(() => {
        if (!profit.value) return 0
        const wins = profit.value.winning_trades || 0
        const total = profit.value.closed_trade_count || 0
        return total > 0 ? (wins / total * 100).toFixed(1) : 0
    })
    const isBotRunning = computed(() => botState.value?.state === 'running')
    const stakeCurrency = computed(() => botState.value?.stake_currency || 'USDT')

    // Actions
    async function login(username: string, password: string, setAsBotMode: boolean = false) {
        const settingsStore = useSettingsStore()

        try {
            isLoading.value = true
            console.log('BotStore: Initiating login for', username)
            const res = await botApi.login(username, password)

            if (res.data && res.data.access_token) {
                console.log('BotStore: Login successful, token received')
                isConnected.value = true

                // Save credentials to settings store and localStorage
                settingsStore.setCredentials(username, res.data.access_token)
                sessionStorage.setItem('bot_token', res.data.access_token)
                if (res.data.refresh_token) {
                    sessionStorage.setItem('bot_refresh_token', res.data.refresh_token)
                }

                // Only set as 'bot' mode if explicitly requested (Local Bot login)
                if (setAsBotMode) {
                    settingsStore.setConnectionMode('bot')
                }

                // Start refreshing data in the background
                // Note: We don't await this to keep login fast, but it runs in background
                refreshAll().catch(err => console.warn('Initial refresh failed:', err))

                return true
            }
            console.warn('BotStore: Login failed, no access token in response')
            return false
        } catch (error: any) {
            console.error('BotStore: Login exception:', error)
            isConnected.value = false
            const errorMessage = error.response?.data?.detail || error.message || 'Login failed'
            throw new Error(errorMessage)
        } finally {
            isLoading.value = false
        }
    }

    async function connect() {
        try {
            isLoading.value = true
            await botApi.ping()
            isConnected.value = true
            // Refresh in background
            refreshAll()
        } catch (error) {
            isConnected.value = false
            throw error
        } finally {
            isLoading.value = false
        }
    }

    function disconnect() {
        isConnected.value = false
        sessionStorage.removeItem('bot_token')
        sessionStorage.removeItem('bot_refresh_token')
        botState.value = null
        balance.value = []
        totalBalance.value = 0
        profit.value = null
        openTrades.value = []
        closedTrades.value = []
    }

    async function refreshAll() {
        // Use Promise.allSettled to prevent one failing API from blocking all
        await Promise.allSettled([
            fetchStatus(),
            fetchBalance(),
            fetchProfit(),
            fetchTrades(),
            fetchWhitelist(),
            fetchDailyStats()
        ])
    }

    async function fetchStatus() {
        try {
            const res = await botApi.showConfig()
            botState.value = {
                state: res.data.state,
                running: res.data.state === 'running',
                dry_run: res.data.dry_run,
                max_open_trades: res.data.max_open_trades,
                stake_currency: res.data.stake_currency,
                stake_amount: parseFloat(res.data.stake_amount),
                trading_mode: res.data.trading_mode,
                strategy: res.data.strategy,
                bot_name: res.data.bot_name,
                version: res.data.version
            }
            version.value = res.data.version
        } catch (error) {
            console.error('Failed to fetch status:', error)
        }
    }

    async function fetchBalance() {
        try {
            const res = await botApi.balance()
            balance.value = res.data.currencies || []
            totalBalance.value = res.data.total || 0
        } catch (error) {
            console.error('Failed to fetch balance:', error)
            // Clear data on error (e.g., 403) to prevent showing stale data
            balance.value = []
            totalBalance.value = 0
        }
    }

    async function fetchProfit() {
        try {
            const res = await botApi.profit()
            profit.value = res.data
        } catch (error) {
            console.error('Failed to fetch profit:', error)
            profit.value = null
        }
    }

    async function fetchTrades() {
        try {
            // Get open trades from /status endpoint (live open positions)
            const statusRes = await botApi.status()
            if (Array.isArray(statusRes.data)) {
                openTrades.value = statusRes.data
            }

            // Get closed trades from /trades endpoint
            const res = await botApi.trades(500)
            const trades = res.data.trades || []
            closedTrades.value = trades.filter((t: Trade) => !t.is_open).slice(0, 100)
        } catch (error) {
            console.error('Failed to fetch trades:', error)
            openTrades.value = []
            closedTrades.value = []
        }
    }

    async function fetchDailyStats() {
        try {
            const res = await botApi.daily(30)
            dailyStats.value = res.data.data || []
        } catch (error) {
            console.error('Failed to fetch daily stats:', error)
            dailyStats.value = []
        }
    }

    async function fetchWhitelist() {
        try {
            const res = await botApi.whitelist()
            whitelist.value = res.data.whitelist || []
        } catch (error) {
            console.error('Failed to fetch whitelist:', error)
        }
    }

    async function fetchBlacklist() {
        try {
            const res = await botApi.blacklist()
            blacklist.value = res.data.blacklist || []
        } catch (error) {
            console.error('Failed to fetch blacklist:', error)
        }
    }

    async function fetchPerformance() {
        try {
            const res = await botApi.performance()
            performance.value = res.data
        } catch (error) {
            console.error('Failed to fetch performance:', error)
        }
    }

    async function fetchStrategies() {
        try {
            const res = await botApi.strategies()
            strategies.value = res.data.strategies || []
        } catch (error) {
            console.error('Failed to fetch strategies:', error)
        }
    }

    async function fetchLogs() {
        try {
            const res = await botApi.logs(100)
            logs.value = res.data.logs || []
        } catch (error) {
            console.error('Failed to fetch logs:', error)
        }
    }

    async function startBot() {
        try {
            await botApi.start()
            await fetchStatus()
        } catch (error) {
            console.error('Failed to start bot:', error)
            throw error
        }
    }

    async function stopBot() {
        try {
            await botApi.stop()
            await fetchStatus()
        } catch (error) {
            console.error('Failed to stop bot:', error)
            throw error
        }
    }

    async function forceEntry(pair: string, price?: number, stakeAmount?: number) {
        try {
            const res = await botApi.forceEntry(pair, price, stakeAmount)
            await fetchTrades()
            return res.data
        } catch (error) {
            console.error('Failed to force entry:', error)
            throw error
        }
    }

    async function forceExit(tradeId: string) {
        try {
            const res = await botApi.forceExit(tradeId)
            await fetchTrades()
            return res.data
        } catch (error) {
            console.error('Failed to force exit:', error)
            throw error
        }
    }

    async function updateAccount(payload: any) {
        try {
            const res = await botApi.saveAuthConfig(payload.username, payload.password)
            return res.data
        } catch (error) {
            console.error('Failed to update account:', error)
            throw error
        }
    }

    // Check if already logged in on startup
    function checkAuth() {
        const token = sessionStorage.getItem('bot_token')
        if (token) {
            isConnected.value = true
            refreshAll().catch(() => {
                // Token expired
                disconnect()
            })
        }
    }

    return {
        // State
        isConnected,
        isLoading,
        botState,
        balance,
        totalBalance,
        profit,
        openTrades,
        closedTrades,
        dailyStats,
        performance,
        whitelist,
        blacklist,
        strategies,
        logs,
        version,
        // Computed
        openTradeCount,
        totalProfit,
        winRate,
        isBotRunning,
        stakeCurrency,
        // Actions
        login,
        connect,
        disconnect,
        checkAuth,
        refreshAll,
        fetchStatus,
        fetchBalance,
        fetchProfit,
        fetchTrades,
        fetchDailyStats,
        fetchWhitelist,
        fetchBlacklist,
        fetchPerformance,
        fetchStrategies,
        fetchLogs,
        startBot,
        stopBot,
        forceEntry,
        forceExit,
        updateAccount
    }
})

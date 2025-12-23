import axios from 'axios'
import { useSettingsStore } from '@/stores/settingsStore'

// Get the settings store (will be initialized when used)
let settingsStore: ReturnType<typeof useSettingsStore> | null = null

function getSettingsStore() {
    if (!settingsStore) {
        settingsStore = useSettingsStore()
    }
    return settingsStore
}

// Create axios instance with dynamic base URL
const api = axios.create({
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// Request interceptor - add auth token and dynamic base URL
api.interceptors.request.use(
    (config) => {
        const settings = getSettingsStore()

        // Set base URL from settings
        const baseUrl = settings.apiUrl || 'http://localhost:8080'
        config.baseURL = `${baseUrl}/api/v1`

        // Add auth token only if not already set (e.g. for refresh calls)
        const token = sessionStorage.getItem('bot_token')
        if (token && !config.headers.Authorization) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        // Handle 401 - redirect to login
        if (error.response?.status === 401) {
            console.warn('API 401 Unauthorized:', error.config?.url)

            // Try to refresh token first if we have a refresh token
            const refreshToken = sessionStorage.getItem('bot_refresh_token')
            if (refreshToken && !error.config._retry && !error.config.url?.includes('/token/login')) {
                error.config._retry = true
                try {
                    const refreshResponse = await api.post('/token/refresh', null, {
                        headers: {
                            'Authorization': `Bearer ${refreshToken}`
                        }
                    })
                    if (refreshResponse.data.access_token) {
                        sessionStorage.setItem('bot_token', refreshResponse.data.access_token)
                        // Retry the original request with new token
                        error.config.headers['Authorization'] = `Bearer ${refreshResponse.data.access_token}`
                        return api.request(error.config)
                    }
                } catch (refreshError) {
                    console.warn('Refresh token failed')
                }
            }

            // Clear invalid tokens
            sessionStorage.removeItem('bot_token')
            sessionStorage.removeItem('bot_refresh_token')

            // If we're already on home/login page, don't redirect (just let the component handle the error)
            const isAtLogin = window.location.pathname === '/' || window.location.pathname === '/login'
            if (!isAtLogin) {
                console.warn('Unauthorized on non-login page, redirecting to login...')
                window.location.href = '/'
            }
        }
        console.error('API Error:', error.response?.data || error.message)
        return Promise.reject(error)
    }
)

// API functions
export const botApi = {
    // Auth - Backend uses HTTP Basic Auth for login
    login: async (username: string, password: string) => {
        // We now support both JSON body and HTTP Basic Auth.
        // Let's use JSON body as it's more standard for APIs.
        const response = await api.post('/token/login', {
            username: username,
            password: password
        })

        // Save tokens if present
        if (response.data.access_token) {
            sessionStorage.setItem('bot_token', response.data.access_token)
        }
        if (response.data.refresh_token) {
            sessionStorage.setItem('bot_refresh_token', response.data.refresh_token)
        }

        return response
    },

    // Bot status
    ping: () => api.get('/ping'),
    version: () => api.get('/version'),
    status: () => api.get('/status'),
    showConfig: () => api.get('/show_config'),

    // Bot control
    start: () => api.post('/start'),
    stop: () => api.post('/stop'),
    pause: () => api.post('/pause'),
    reloadConfig: () => api.post('/reload_config'),

    // Balance & Profit
    balance: () => api.get('/balance'),
    profit: () => api.get('/profit'),
    profitAll: () => api.get('/profit_all'),
    stats: () => api.get('/stats'),
    daily: (days = 7) => api.get(`/daily?timescale=${days}`),
    weekly: (weeks = 4) => api.get(`/weekly?timescale=${weeks}`),
    monthly: (months = 3) => api.get(`/monthly?timescale=${months}`),

    // Trades
    trades: (limit = 500, offset = 0) => api.get(`/trades?limit=${limit}&offset=${offset}`),
    trade: (id: number) => api.get(`/trade/${id}`),
    deleteTrade: (id: number) => api.delete(`/trades/${id}`),
    count: () => api.get('/count'),
    reloadOpenTrades: () => api.post('/trades/reload'),

    // Force entry/exit
    forceEntry: (pair: string, price?: number, stakeAmount?: number) =>
        api.post('/forceenter', { pair, price, stakeamount: stakeAmount }),
    forceExit: (tradeId: string, ordertype?: string) =>
        api.post('/forceexit', { tradeid: tradeId, ordertype }),

    // Performance
    performance: () => api.get('/performance'),
    entries: (pair?: string) => api.get('/entries', { params: { pair } }),
    exits: (pair?: string) => api.get('/exits', { params: { pair } }),

    // Pairs
    whitelist: () => api.get('/whitelist'),
    blacklist: () => api.get('/blacklist'),
    addBlacklist: (pairs: string[]) => api.post('/blacklist', { blacklist: pairs }),
    deleteBlacklist: (pairs: string[]) => api.delete('/blacklist', { params: { pairs_to_delete: pairs } }),

    // Locks
    locks: () => api.get('/locks'),
    deleteLock: (id: number) => api.delete(`/locks/${id}`),

    // Strategies
    strategies: () => api.get('/strategies'),
    strategy: (name: string) => api.get(`/strategy/${name}`),

    // Backtest
    backtest: (config: any) => api.post('/backtest', config),
    backtestStatus: () => api.get('/backtest'),
    backtestAbort: () => api.delete('/backtest'),
    backtestHistory: () => api.get('/backtest/history'),
    deleteBacktestHistory: (id: string) => api.delete(`/backtest/history/${id}`),

    // Logs
    logs: (limit = 50) => api.get(`/logs?limit=${limit}`),

    // Candles
    pairCandles: (pair: string, timeframe: string, limit = 500) =>
        api.get('/pair_candles', { params: { pair, timeframe, limit } }),

    // Available pairs
    availablePairs: (timeframe?: string) =>
        api.get('/available_pairs', { params: { timeframe } }),

    // Exchanges
    exchanges: () => api.get('/exchanges'),

    // System
    sysinfo: () => api.get('/sysinfo'),
    health: () => api.get('/health'),

    // Exchange configuration - for Binance Direct mode (Spot/Futures)
    setExchangeConfig: (
        apiKey: string,
        secretKey: string,
        testnet: boolean = false,
        tradingMode: 'spot' | 'futures' = 'spot',
        marginMode?: 'isolated' | 'cross',
        dbUrl?: string
    ) =>
        api.post('/set_exchange_config', {
            api_key: apiKey,
            secret_key: secretKey,
            testnet,
            trading_mode: tradingMode,
            margin_mode: marginMode,
            db_url: dbUrl
        }),

    // Toggle dry run mode without requiring API keys


    // Save exchange config to file (persists after restart)
    saveExchangeConfig: async (apiKey: string, apiSecret: string, sandbox: boolean = true, tradingMode: string = 'spot', dryRun: boolean = true) => {
        // Persist config to file on disk
        return api.post('/config/save_exchange', {
            api_key: apiKey,
            api_secret: apiSecret,
            sandbox,
            dry_run: dryRun,
            trading_mode: tradingMode
        });
    },

    // Save auth config to file (persists after restart)
    saveAuthConfig: async (username: string, password: string) => {
        return api.post('/config/save_auth', {
            username,
            password
        });
    },

    // Register new user
    registerUser: async (username: string, password: string) => {
        return api.post('/register', {
            username,
            password
        });
    },

    // Profiles (Backend Storage)
    getProfiles: () => api.get('/profiles'),
    saveProfile: (profile: any) => api.post('/profiles', profile),
    deleteProfile: (id: string) => api.delete(`/profiles/${id}`)
}

export default api

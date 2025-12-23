# Codebase Overview (Detailed)

This document describes the structure, core modules, and runtime flows of the
project in D:\CNPM\SE2025-9.4. It focuses on how the bot works, how the UI
connects, and how copy trading is implemented.

Important: config/config.json contains sensitive API keys and passwords.
This document intentionally does not include any secrets or concrete values.

## 1) High level architecture

- Backend: Python, freqtrade-based engine (folder: backend/binancebot).
- Frontend: Vue 3 + Vite + Pinia (folder: frontend).
- API: FastAPI endpoints exposed by backend, consumed by frontend.
- Storage: SQLite for trades, plus JSON files for copy-trade state.
- Deployment: Dockerfile + docker-compose.yml (Linux), run_bot scripts (Windows).

Runtime flow:
1. Backend starts via `python -m binancebot trade --config config/config.json`.
2. Bot loads config + strategy, connects to exchange via ccxt, starts the loop.
3. API server exposes endpoints for UI and management.
4. Frontend calls API endpoints for status, trades, settings, etc.
5. Copy trading mirrors master orders to enabled follower profiles.

## 2) Repository layout

- backend/                 Python trading engine (freqtrade-based).
- frontend/                Vue 3 UI (Vite build).
- config/                  Main config.json (keys, exchange, strategy).
- data/                    SQLite DB files (tradesv3.sqlite*).
- user_data/               Strategies and strategy parameters.
- run_bot/                 Windows install/start/stop scripts.
- deploy/                  systemd service template.
- scripts/                 Helper scripts (post_deploy, checks).
- docs/                    Deployment docs + this file.
- Dockerfile, docker-compose.yml

## 3) Backend (Python)

Entry point:
- backend/binancebot/__main__.py -> binancebot/main.py
- main.py uses CLI commands and starts trading with subcommand `trade`.

Key modules:
- backend/binancebot/commands/            CLI and subcommands.
- backend/binancebot/exchange/            Exchange abstraction on top of ccxt.
- backend/binancebot/rpc/                 RPC and API server logic.
- backend/binancebot/strategy/            Strategy interface and helpers.
- backend/binancebot/persistence/         SQLAlchemy models (Trade, Order, etc).
- backend/binancebot/data/                Data history, analysis helpers.
- backend/binancebot/loggers/             Logging setup and log level configs.
- backend/binancebot/misc.py              Utility helpers.

### 3.1 API server (FastAPI)

Location:
- backend/binancebot/rpc/api_server/

Important files:
- api_v1.py
  - Core endpoints: /status, /trades, /trade/{id}, /balance, /profit, /whitelist
  - Bot control: /start, /stop, /pause, /reload_config (admin-only).
  - Force actions: /forceenter, /forceexit (admin-only).
  - Logs: /logs (admin-only).
  - Exchange config switch: /set_exchange_config (admin-only).
  - Ownership checks: check_api_ownership (for user data restrictions).
- api_config.py
  - Profile storage: /profiles GET/POST/DELETE.
  - Save exchange keys: /config/save_exchange.
  - Save auth: /config/save_auth.
  - Profiles include copy_enabled + allocation_pct for copy trading.
- api_auth.py
  - JWT tokens include identity: { u, admin }.
  - verify_auth uses pbkdf2_sha256 hashing.
  - token_login and token_refresh set admin flag in the token payload.
- deps.py
  - Provides get_config/get_api_config and RPC dependencies.

Admin rules:
- Primary admin is api_server.username in config.json.
- Admin can start/stop bot, force entry/exit, reload config, and view logs.

### 3.2 Copy trading (multi-account)

Location:
- backend/binancebot/copy_trading.py

Summary:
- Reads profiles from config.json (api_server.profiles).
- Uses copy_enabled + allocation_pct per profile.
- Skips master account by comparing active_profile_id and exchange key.
- Spot only (futures are skipped for now).
- Uses market orders for entries/exits.
- Uses allocation_pct of free quote balance to compute stake.
- Tracks copied entries in data/copy_trades.json to close correctly on exit.

Integration:
- backend/binancebot/binancebot.py
  - mirror_entry called after Trade.commit in execute_entry.
  - mirror_exit called after trade exit (non-sub-trade).

Limitations:
- Spot only.
- Uses market orders.
- Allocation is based on free quote balance at entry time.

### 3.3 Strategy (trade logic)

Active strategy:
- user_data/strategies/RSI_EMA.py

Key points:
- Indicators: RSI (14), EMA of RSI (9), WMA of RSI (45), ATR.
- Entry: RSI crosses above EMA with downtrend expansion.
- Exit: RSI crosses below EMA with uptrend expansion.
- Risk control: stoploss, trailing stop, minimal ROI table.
- Dynamic stake: uses Kelly + risk per trade.

Hyperopt parameters:
- user_data/strategies/RSI_EMA.json
- Contains tuned values for buy/sell/roi/stoploss/trailing.

Timeframe:
- Strategy file uses timeframe "4h".
- Config can also specify timeframe; strategy setting is authoritative.

### 3.4 Storage

- data/tradesv3.sqlite*         Main SQLite DB for trades.
- data/tradesv3.dryrun.sqlite   Dry-run DB.
- data/copy_trades.json         Copy-trading entry tracking.

## 4) Frontend (Vue 3)

Location:
- frontend/

Key structure:
- frontend/src/views/
  - DashboardView.vue
  - TradingView.vue
  - ChartsView.vue
  - SettingsView.vue
  - ApiSettings.vue
  - LogView.vue (admin only in nav)
- frontend/src/components/
  - ftbot/BotControls.vue (admin-only controls)
  - ftbot/TradeList.vue (admin-only exit actions)
  - ftbot/ForceEntryForm.vue (admin-only)
- frontend/src/stores/
  - botStore.ts: handles bot state, trades, balance, logs
- frontend/src/api/api.ts
  - Axios wrapper for /api/v1 endpoints.
- frontend/src/utils/auth.ts
  - Parses token for username and admin flag.

UI permissions:
- Start/Stop/Force Entry/Exit: only admin sees these controls.
- Logs: menu item visible only for admin.
- Copy trading toggle per profile is available to each user.

## 5) Configuration (config/config.json)

Do not commit real keys or passwords.
Key sections:
- exchange: name, key/secret, ccxt_config, pair_whitelist.
- api_server: listen/port, jwt_secret_key, username/password, users, profiles.
- strategy: active strategy name and strategy_path.
- trading_mode, stake_currency, max_open_trades, ROI, stoploss.

Profiles:
- api_server.profiles is the admin profile list.
- api_server.users contains user entries, each can have profiles.
- Each profile supports copy_enabled + allocation_pct for copy trading.

## 6) Deployment

Docker:
- Dockerfile builds backend + frontend and packages UI into backend.
- docker-compose.yml runs single container with config and data volumes.

Systemd:
- deploy/binancebot.service template for Linux deployments.

Windows:
- run_bot/INSTALL.bat installs Python + Node dependencies.
- run_bot/START_BOT.bat starts backend + frontend dev server.
- run_bot/STOP_BOT.bat stops local processes.

Scripts:
- scripts/post_deploy.sh: venv setup + restart service.
- scripts/check_drift.py / check_limits.py: basic checks.

## 7) Observability

- Admin can view /logs in UI (LogView).
- Server logs via docker: `docker logs -f se2025-94-binancebot-1`.
- API logs contain ownership checks and bot heartbeat.

## 8) Security notes

- config/config.json contains API keys and hashed passwords.
- Keep config.json outside git or encrypted if possible.
- JWT secret key should be private and unique.
- Admin-only endpoints are enforced in backend.

## 9) Custom changes in this codebase (non-stock freqtrade)

- Copy trading manager (backend/binancebot/copy_trading.py).
- Profile management and copy flags in api_config.py + api_schemas.py.
- Active profile tracking in set_exchange_config.
- Trade reload endpoint (/trades/reload) for open trade sync.
- Admin-only UI controls and LogView route.
- Auth tokens include admin flag to drive UI gating.

If you need deeper per-module documentation, list the specific areas
(example: exchange order flow, strategy signals, websocket messages).

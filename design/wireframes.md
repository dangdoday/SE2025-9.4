# Wireframe Specifications - Crypto Trading Bot

## 📊 Dashboard Screen

### Layout Structure
```
┌─────────────────────────────────────────────────────────────┐
│ Header (80px)                                                │
│ [Logo] Crypto Trading Bot        [Balance] [Profile] [⚙]   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ Trading Chart Area (60% height)                             │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ [BTCUSDT] [1m][5m][15m][1h][4h][1d]          $45,234 │  │
│ │                                                         │  │
│ │          📈 Candlestick Chart                          │  │
│ │              + SMA Lines                               │  │
│ │                                                         │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                               │
├──────────────────────┬────────────────────────────────────────┤
│ Control Panel (40%)  │ Trading Stats (60%)                    │
│                      │                                        │
│ ┌──────────────────┐ │ ┌────────────────────────────────────┐ │
│ │ Bot Status       │ │ │ Account Balance                    │ │
│ │ ● Active         │ │ │ USDT: 10,000                       │ │
│ │                  │ │ │ BTC: 0.5                           │ │
│ │ [START] [STOP]   │ │ └────────────────────────────────────┘ │
│ └──────────────────┘ │                                        │
│                      │ ┌────────────────────────────────────┐ │
│ ┌──────────────────┐ │ │ Today's Performance                │ │
│ │ Strategy         │ │ │ PnL: +$234.56 (+2.3%)             │ │
│ │ SMA Crossover ▼  │ │ │ Win Rate: 65%                      │ │
│ └──────────────────┘ │ │ Total Trades: 15                   │ │
│                      │ └────────────────────────────────────┘ │
│ ┌──────────────────┐ │                                        │
│ │ Risk Management  │ │ Recent Trades (Table)                 │
│ │ Max Loss: $500   │ │ Time | Type | Price | Qty | PnL      │
│ │ Position: 10%    │ │ ───────────────────────────────────── │
│ └──────────────────┘ │ 14:30 | SELL | 45,234 | 0.1 | +$12   │
│                      │ 14:15 | BUY  | 45,100 | 0.1 | -       │
└──────────────────────┴────────────────────────────────────────┘
```

### Components Detail

#### 1. Header
- **Height:** 80px
- **Background:** `#1E2329`
- **Elements:**
  - Logo + Title (Left)
  - Balance Display (Center-Right)
  - Profile Icon (Right)
  - Settings Icon (Right)

#### 2. Chart Container
- **Height:** 60vh
- **Background:** `#0B0E11`
- **Features:**
  - Symbol selector dropdown
  - Timeframe buttons (1m, 5m, 15m, 1h, 4h, 1d)
  - Current price display (large, right side)
  - Candlestick chart with volume
  - SMA lines (Fast: Yellow, Slow: Blue)

#### 3. Control Panel (Left Sidebar)
- **Width:** 320px
- **Background:** `#1E2329`
- **Sections:**
  
  **3.1 Bot Status Card**
  - Status indicator (Dot + Text)
  - Colors: Green (Active), Red (Stopped), Yellow (Paused)
  - START button (Green, `#0ECB81`)
  - STOP button (Red, `#F6465D`)
  
  **3.2 Strategy Selector**
  - Dropdown menu
  - Options: SMA Crossover, RSI, MACD, Manual
  
  **3.3 Risk Management**
  - Max Daily Loss input
  - Position Size slider
  - Max Open Positions input

#### 4. Stats & Trading Panel (Right Main Area)
- **Background:** `#0B0E11`
  
  **4.1 Account Balance Card**
  - USDT Balance
  - BTC Balance
  - Total Value in USD
  
  **4.2 Performance Card**
  - Today's PnL (with % change)
  - Win Rate (with progress bar)
  - Total Trades count
  - Chart icon for visualization
  
  **4.3 Recent Trades Table**
  - Columns: Time, Type (BUY/SELL), Price, Quantity, PnL
  - Color coding: Green (profit), Red (loss)
  - Scrollable, max 10 rows visible
  - "View All" button at bottom

---

## 🎛️ Trading Control Screen

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Trading Control Center                                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ ┌─────────────────────────┐  ┌─────────────────────────┐   │
│ │ Strategy Configuration   │  │ Current Settings        │   │
│ │                          │  │                         │   │
│ │ Type: SMA Crossover      │  │ Fast SMA: 7             │   │
│ │                          │  │ Slow SMA: 25            │   │
│ │ Fast Period: [  7  ]     │  │ Timeframe: 1h           │   │
│ │ Slow Period: [ 25  ]     │  │                         │   │
│ │ Timeframe:   [1h ▼]      │  │ Status: ● Ready         │   │
│ │                          │  │                         │   │
│ │ [SAVE CONFIG]            │  │ [START TRADING]         │   │
│ └─────────────────────────┘  └─────────────────────────┘   │
│                                                               │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ Risk Management Settings                              │   │
│ │                                                         │   │
│ │ Max Daily Loss:         [ $500   ]                    │   │
│ │ Position Size (%):      [======|   ] 10%              │   │
│ │ Max Open Positions:     [ 3      ]                    │   │
│ │ Stop Loss (%):          [ 2.0    ]                    │   │
│ │ Take Profit (%):        [ 3.0    ]                    │   │
│ │                                                         │   │
│ │ □ Enable notifications                                 │   │
│ │ □ Auto-restart on daily reset                         │   │
│ │                                                         │   │
│ │ [APPLY SETTINGS]                                       │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                               │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ Trading Log (Real-time)                               │   │
│ │ ───────────────────────────────────────────────────── │   │
│ │ [14:35:23] Bot started                                │   │
│ │ [14:35:25] SMA calculated: Fast=45234, Slow=45100     │   │
│ │ [14:35:26] BUY signal detected                        │   │
│ │ [14:35:27] Order placed: BUY 0.1 BTC @ 45234          │   │
│ │ [14:35:28] Order filled: BUY 0.1 BTC @ 45234          │   │
│ │ ...                                                     │   │
│ └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📜 Trade History Screen

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Trade History                                  [Export CSV]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ Filters: [All Types ▼] [Last 7 Days ▼] [All Status ▼] [🔍] │
│                                                               │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ Date/Time  │ Type │ Symbol   │ Price  │ Qty │ PnL    │   │
│ ├─────────────────────────────────────────────────────────   │
│ │ 2025-10-28 │ SELL │ BTCUSDT  │ 45,234 │ 0.1 │ +$124  │   │
│ │ 14:30:15   │      │          │        │     │        │   │
│ ├─────────────────────────────────────────────────────────   │
│ │ 2025-10-28 │ BUY  │ BTCUSDT  │ 45,100 │ 0.1 │ -      │   │
│ │ 14:15:42   │      │          │        │     │        │   │
│ ├─────────────────────────────────────────────────────────   │
│ │ 2025-10-28 │ SELL │ BTCUSDT  │ 45,050 │ 0.1 │ -$50   │   │
│ │ 13:45:23   │      │          │        │     │        │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                               │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ Summary Statistics                                    │   │
│ │                                                         │   │
│ │ Total Trades: 150                                      │   │
│ │ Winning Trades: 98 (65%)                               │   │
│ │ Losing Trades: 52 (35%)                                │   │
│ │ Total Profit: +$1,234.56                               │   │
│ │ Average Win: +$24.50                                   │   │
│ │ Average Loss: -$15.30                                  │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                               │
│                    [ < ] Page 1 of 15 [ > ]                  │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Settings Screen

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Settings                                                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ Tabs: [API Config] [Bot Settings] [Notifications] [Theme]   │
│                                                               │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ API Configuration                                     │   │
│ │                                                         │   │
│ │ Binance API Key:                                       │   │
│ │ [ *********************************** ]                │   │
│ │                                                         │   │
│ │ Binance Secret Key:                                    │   │
│ │ [ *********************************** ]                │   │
│ │                                                         │   │
│ │ Environment:  ◉ Testnet  ○ Mainnet (⚠️ Use testnet!)  │   │
│ │                                                         │   │
│ │ [TEST CONNECTION]  [SAVE]                              │   │
│ │                                                         │   │
│ │ Status: ✅ Connected to Binance Testnet                │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                               │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ Default Trading Parameters                            │   │
│ │                                                         │   │
│ │ Default Symbol:        [ BTCUSDT ▼ ]                  │   │
│ │ Default Timeframe:     [ 1h ▼      ]                  │   │
│ │ Auto-start on launch:  □                               │   │
│ │ Enable paper trading:  ☑                               │   │
│ │                                                         │   │
│ │ [RESET TO DEFAULTS]  [SAVE]                            │   │
│ └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Component Specifications

### Buttons

**Primary Button (START/BUY)**
- Background: `#0ECB81`
- Text: White `#FFFFFF`
- Border-radius: 8px
- Height: 40px
- Font-weight: 600
- Hover: Lighter shade `#3DD598`

**Danger Button (STOP/SELL)**
- Background: `#F6465D`
- Text: White `#FFFFFF`
- Border-radius: 8px
- Height: 40px
- Font-weight: 600
- Hover: Darker shade `#D93A4D`

**Secondary Button**
- Background: Transparent
- Border: 1px solid `#2B2F36`
- Text: `#EAECEF`
- Border-radius: 8px
- Height: 40px
- Hover: Background `#2B2F36`

### Cards

**Default Card**
- Background: `#1E2329`
- Border-radius: 12px
- Padding: 24px
- Box-shadow: `0 2px 8px rgba(0, 0, 0, 0.15)`

### Input Fields

**Text Input**
- Background: `#0B0E11`
- Border: 1px solid `#2B2F36`
- Border-radius: 8px
- Height: 40px
- Padding: 0 16px
- Text color: `#EAECEF`
- Focus: Border `#F0B90B`

### Status Indicators

**Active (Green):** ● `#0ECB81`
**Stopped (Red):** ● `#F6465D`
**Paused (Yellow):** ● `#F0B90B`

---

## 📐 Spacing Guidelines

- Component spacing: 24px
- Section spacing: 32px
- Element padding: 16px
- Icon size: 24x24px
- Button height: 40px
- Input height: 40px

---

## 🔤 Typography Usage

- **H1 (32px):** Page titles
- **H2 (24px):** Section headers
- **H3 (20px):** Card titles
- **Body (16px):** Regular text, labels
- **Caption (14px):** Helper text, table content
- **Small (12px):** Timestamps, minor labels

---

## 📱 Responsive Breakpoints

### Desktop (1024px+)
- Full layout as shown
- Chart: 60% height
- Sidebar: 320px fixed

### Tablet (768px - 1023px)
- Stack control panel below chart
- Chart: 50% height
- Full-width components

### Mobile (320px - 767px)
- Single column layout
- Chart: 40vh height
- Bottom navigation tabs
- Collapsible sections

---

## 🎯 Interactive States

### Hover
- Slight brightness increase
- Smooth transition (0.2s)

### Active/Pressed
- Slight scale down (0.98)
- Darker shade

### Disabled
- Opacity: 0.5
- Cursor: not-allowed

### Loading
- Spinner overlay
- Disabled interactions
- Subtle pulse animation

---

## 📊 Data Visualization

### Chart
- Library: Chart.js / Lightweight Charts
- Type: Candlestick
- SMA Lines: 2px solid
- Grid: `#2B2F36`
- Tooltip: Dark theme

### Progress Bars
- Height: 8px
- Background: `#2B2F36`
- Fill: `#0ECB81` (success) or `#F6465D` (danger)
- Border-radius: 4px

---

## Notes
- Tất cả màu sắc lấy từ `design-tokens.json`
- Font chính: Inter (import từ Google Fonts)
- Icons: Sử dụng Lucide React hoặc Heroicons
- Animations: Smooth, subtle (< 300ms)

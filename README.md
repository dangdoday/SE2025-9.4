# 🤖 BinanceBot - Crypto Trading Bot

Bot giao dịch tiền điện tử tự động trên sàn Binance với giao diện web hiện đại.

## 📋 Tính năng

- **Giao dịch Spot** - Mua/bán tiền điện tử trực tiếp
- **Chiến lược RSI-EMA** - Tín hiệu giao dịch dựa trên chỉ báo kỹ thuật
- **Multi-User** - Hỗ trợ nhiều tài khoản với dữ liệu cách ly
- **Live Chart** - Biểu đồ nến real-time từ Binance
- **Dashboard** - Theo dõi balance, profit, trades
- **Dry Run** - Chế độ mô phỏng không dùng tiền thật

## 🛠️ Yêu cầu hệ thống

1. **Python 3.10+**
   - Download: https://www.python.org/downloads/
   - ⚠️ Tick chọn "Add Python to PATH" khi cài đặt

2. **Node.js 18+**
   - Download: https://nodejs.org/

3. **Git** (tùy chọn)
   - Download: https://git-scm.com/

## 📦 Cấu trúc thư mục

```
SE2025-9.4/
├── backend/          # Python FastAPI server
├── frontend/         # Vue.js web UI
├── config/           # Configuration files
│   └── config.json   # Main config (API keys, settings)
├── data/             # Database files
├── docs/             # Documentation
├── scripts/          # Utility scripts
├── user_data/        # Strategies, logs
└── run_bot/          # Start/Stop scripts
```

## 🚀 Cài đặt & Chạy

### Bước 1: Cài đặt dependencies

```bash
# Backend (Python)
cd backend
pip install -r ../requirements.txt

# Frontend (Node.js)
cd frontend
npm install
```

### Bước 2: Cấu hình

Chỉnh sửa file `config/config.json`:

```json
{
  "exchange": {
    "key": "YOUR_BINANCE_API_KEY",
    "secret": "YOUR_BINANCE_SECRET_KEY"
  },
  "api_server": {
    "username": "admin",
    "password": "your_password"
  },
  "dry_run": true
}
```

### Bước 3: Chạy Bot

- **Windows**: Chạy `run_bot/START_BOT.bat`
- **Linux/Mac**: 
  ```bash
  # Terminal 1 - Backend
  cd backend && python -m binancebot trade
  
  # Terminal 2 - Frontend
  cd frontend && npm run dev
  ```

### Bước 4: Truy cập

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **Đăng nhập**: username `admin`, password trong config

## 🔐 Bảo mật

- ⚠️ **KHÔNG** chia sẻ `config.json` vì chứa API keys
- Sử dụng **Dry Run** (`"dry_run": true`) để test trước
- Tạo API key trên Binance với quyền giới hạn (chỉ Trade, không Withdraw)

## 🛑 Dừng Bot

- **Windows**: Chạy `run_bot/STOP_BOT.bat`
- **Linux/Mac**: `Ctrl+C` trong terminal

## 🐛 Xử lý lỗi thường gặp

### Bot không kết nối được Binance
- Kiểm tra API key/secret đúng chưa
- Kiểm tra kết nối internet
- Binance có thể bị chặn IP (dùng VPN)

### Dashboard trống
- Đợi Bot sync dữ liệu (vài giây)
- Kiểm tra tài khoản có balance không
- Xem log trong Console (F12)

### Không có tiền để trade
- Bật `"dry_run": true` trong config
- Đặt `"dry_run_wallet": 1000` để có tiền mô phỏng

## 👨‍💻 Tech Stack

- **Backend**: Python + FastAPI + SQLAlchemy
- **Frontend**: Vue 3 + TypeScript + Vite + ECharts
- **Database**: SQLite
- **Trading**: CCXT (Binance API)

## 📄 License

MIT License - SE2025-9.4 Team

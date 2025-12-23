# Báo cáo đồ án SE2025-9.4 (Goals and Objectives)

Tài liệu này trình bày báo cáo đồ án theo định dạng Goals and Objectives,
viết chi tiết về toàn bộ dự án: mục tiêu, kiến trúc, chức năng, triển khai,
phân quyền, lưu trữ dữ liệu, giám sát và hướng phát triển.

## Goals

1) Xây dựng hệ thống bot giao dịch tiền mã hóa tự động có giao diện web dễ sử dụng.
2) Hỗ trợ mô hình copy trading nhiều tài khoản với một bot trung tâm.
3) Phân quyền rõ ràng giữa admin và user để vận hành an toàn.
4) Dễ triển khai trên Windows và Linux (Docker/systemd).
5) Có khả năng mở rộng để thêm audit log (blockchain) và chiến lược mới.

## Objectives

### 1) Mục tiêu chức năng (Functional Objectives)

1.1 Bot giao dịch tự động
- Nạp cấu hình và chiến lược giao dịch từ `config/config.json`.
- Phân tích dữ liệu nến theo timeframe cấu hình.
- Phát hiện tín hiệu vào/ra lệnh và đặt lệnh qua ccxt.
- Lưu lịch sử lệnh và trạng thái giao dịch vào SQLite.

1.2 Copy trading (một bot trung tâm)
- Bot trung tâm sinh lệnh và mirror sang các profile đang bật copy.
- Mỗi profile có `copy_enabled` và `allocation_pct`.
- Điều chỉnh khối lượng lệnh theo % vốn của từng tài khoản.
- Theo dõi entry/exit để đóng lệnh chính xác.

1.3 Giao diện web
- Hiển thị trạng thái bot, danh sách lệnh, thống kê lợi nhuận.
- Quản lý API key và profile.
- Bật/tắt copy trading cho từng profile.
- Xem logs theo quyền admin.

### 2) Mục tiêu kiến trúc (Architecture Objectives)

2.1 Backend (Python/FastAPI)
- Trading engine dựa trên core freqtrade.
- API server cung cấp `/status`, `/trades`, `/balance`, `/profit`, `/whitelist`, `/logs`.
- Các endpoint điều khiển bot chỉ cho admin: `/start`, `/stop`, `/pause`, `/reload_config`.
- Endpoint force action chỉ cho admin: `/forceenter`, `/forceexit`.

2.2 Frontend (Vue 3)
- Pinia quản lý state.
- Axios gọi API `/api/v1`.
- Phân quyền UI dựa trên token admin.

2.3 Lưu trữ và dữ liệu
- SQLite lưu trades (`data/tradesv3.sqlite*`).
- JSON lưu trạng thái copy trading (`data/copy_trades.json`).

### 3) Mục tiêu triển khai (Deployment Objectives)

3.1 Windows
- `run_bot/INSTALL.bat`: cài phụ thuộc Python/Node.
- `run_bot/START_BOT.bat`: chạy backend + frontend.
- `run_bot/STOP_BOT.bat`: dừng tiến trình.

3.2 Linux/Server
- Dockerfile và `docker-compose.yml` chạy container.
- `deploy/binancebot.service` là template systemd.
- `scripts/post_deploy.sh` hỗ trợ khởi tạo venv và restart service.

### 4) Mục tiêu bảo mật và phân quyền

4.1 Admin
- Start/Stop bot trung tâm.
- Force entry/exit.
- Xem logs hệ thống.

4.2 User thường
- Quản lý profile cá nhân.
- Bật/tắt copy trading và cấu hình tỷ lệ vốn.

4.3 Bảo mật cấu hình
- Mật khẩu lưu dạng hash pbkdf2_sha256.
- Không công khai API key trong tài liệu.

## Nội dung chi tiết dự án

### 1) Kiến trúc tổng quan

- Backend: Python + FastAPI (API server) + trading engine.
- Frontend: Vue 3 + Vite + Pinia.
- DB: SQLite.

Luồng chính:
1) Bot đọc config -> nạp chiến lược -> kết nối exchange.
2) Bot phân tích nến -> phát tín hiệu vào/ra.
3) Bot đặt lệnh -> lưu Trade vào DB.
4) Copy trading mirror lệnh sang profile đang bật.
5) UI hiển thị trade, chart, logs.

### 2) Cấu trúc thư mục chính

- `backend/`: mã nguồn backend và engine giao dịch.
- `frontend/`: giao diện web.
- `config/`: cấu hình hệ thống (config.json).
- `data/`: SQLite và state runtime.
- `user_data/`: chiến lược và tham số chiến lược.
- `run_bot/`: script chạy trên Windows.
- `deploy/`: systemd service.
- `scripts/`: script hỗ trợ.
- `docs/`: tài liệu.

### 3) Chiến lược giao dịch

Strategy hiện dùng: `RSI_EMA`
- Indicator: RSI(14), EMA RSI(9), WMA RSI(45), ATR.
- Entry: RSI cắt lên EMA trong downtrend expansion.
- Exit: RSI cắt xuống EMA trong uptrend expansion.
- Có stoploss, trailing stop, ROI table.

File liên quan:
- `user_data/strategies/RSI_EMA.py`
- `user_data/strategies/RSI_EMA.json` (tham số hyperopt)

### 4) Copy trading

- Mirror lệnh từ bot trung tâm sang follower.
- Tính stake theo `allocation_pct` của từng profile.
- Theo dõi entry/exit qua `data/copy_trades.json`.
- Hiện hỗ trợ spot và market order.

### 5) Quan sát và vận hành

- Admin xem logs qua trang Logs trong UI.
- Có thể xem log container: `docker logs -f se2025-94-binancebot-1`.
- Bot có heartbeat để xác nhận trạng thái chạy.

### 6) Kết quả đạt được

- Bot giao dịch tự động hoạt động ổn định.
- UI quản lý và theo dõi được trạng thái, lệnh, biểu đồ.
- Copy trading chạy được nhiều tài khoản với một bot trung tâm.
- Hệ thống triển khai trên server Linux bằng Docker.

### 7) Hạn chế hiện tại

- Copy trading chỉ hỗ trợ spot.
- Audit log on-chain chưa triển khai.
- Chưa có báo cáo hiệu suất theo từng profile.

### 8) Hướng phát triển

- Ghi hash lệnh lên blockchain (Merkle root + tx log).
- Thêm chế độ futures cho copy trading.
- Bổ sung báo cáo hiệu suất chi tiết theo từng tài khoản.
- Tối ưu UI/UX và phân quyền sâu hơn.

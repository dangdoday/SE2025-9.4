# Cấu trúc thư mục chính dự án

Dưới đây là các thư mục chính trong dự án và mục đích của từng thư mục.

## Thư mục cấp cao

- backend/  
  Chứa mã nguồn backend (Python) của bot trading và API.

- frontend/  
  Chứa mã nguồn giao diện web (Vue 3).

- config/  
  Chứa các file cấu hình (config.json, cấu hình exchange, API server).

- data/  
  Lưu cơ sở dữ liệu SQLite và dữ liệu runtime (tradesv3*.sqlite, v.v.).

- user_data/  
  Chứa chiến lược giao dịch (strategies) và cấu hình chiến lược.

- run_bot/  
  Script cài đặt/chạy/tắt bot trên Windows (INSTALL.bat, START_BOT.bat, STOP_BOT.bat).

- deploy/  
  File mẫu systemd service cho Linux.

- scripts/  
  Script hỗ trợ triển khai và kiểm tra.

- docs/  
  Tài liệu dự án (deploy, codebase, v.v.).

## File quan trọng ở root

- Dockerfile  
  Build image cho backend + frontend (UI được đóng gói vào backend).

- docker-compose.yml  
  Chạy container với volumes config/data.

- requirements.txt  
  Danh sách thư viện Python.

- pyproject.toml  
  Cấu hình Python tooling.

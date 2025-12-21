# Hướng Dẫn CI/CD và Deployment

## 📋 Mục Lục
1. [Chuẩn bị](#chuẩn-bị)
2. [Cấu hình GitHub Secrets](#cấu-hình-github-secrets)
3. [Deploy lên Server](#deploy-lên-server)
4. [Chạy Local với Docker](#chạy-local-với-docker)
5. [Quản lý và Troubleshooting](#quản-lý-và-troubleshooting)

---

## 🚀 Chuẩn Bị

### Yêu cầu hệ thống
- **Git** đã cài đặt
- **Docker** và **Docker Compose** đã cài đặt
- **SSH access** đến server (nếu deploy lên server)
- **GitHub account** với quyền push code

### Cài đặt Docker
**Windows:**
- Tải Docker Desktop: https://www.docker.com/products/docker-desktop
- Cài đặt và khởi động Docker Desktop

**Linux (Ubuntu/Debian):**
```bash
# Cài đặt Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Cài đặt Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Thêm user vào group docker
sudo usermod -aG docker $USER
```

---

## 🔑 Cấu Hình GitHub Secrets

### 1. Truy cập GitHub Repository Settings
- Vào repository: https://github.com/dangdoday/SE2025-9.4
- Click vào **Settings** > **Secrets and variables** > **Actions**

### 2. Thêm các Secrets sau:

#### Cho Docker Hub (optional - nếu dùng Docker Hub):
- **DOCKER_USERNAME**: Username Docker Hub của bạn
- **DOCKER_PASSWORD**: Password hoặc Access Token của Docker Hub

#### Cho Server Deployment:
- **SERVER_HOST**: IP address hoặc domain của server (VD: `192.168.1.100`)
- **SERVER_USER**: Username SSH (VD: `ubuntu`, `root`)
- **SSH_PRIVATE_KEY**: Private SSH key để kết nối server

**Cách tạo SSH key:**
```bash
# Trên máy local
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Copy public key lên server
ssh-copy-id user@server_ip

# Copy private key để paste vào GitHub Secret
cat ~/.ssh/id_rsa
```

---

## 🌐 Deploy Lên Server

### Bước 1: Chuẩn bị Server

**Kết nối SSH vào server:**
```bash
ssh user@your_server_ip
```

**Cài đặt Docker trên server** (nếu chưa có):
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**Tạo thư mục project:**
```bash
sudo mkdir -p /opt/binancebot
sudo chown $USER:$USER /opt/binancebot
cd /opt/binancebot
```

**Clone repository:**
```bash
git clone https://github.com/dangdoday/SE2025-9.4.git .
```

**Cấu hình file config:**
```bash
# Copy và chỉnh sửa config
cp config/config.json.example config/config.json
nano config/config.json  # Điền API keys của Binance
```

### Bước 2: Deploy lần đầu

**Linux:**
```bash
chmod +x deploy.sh
./deploy.sh production
```

**Windows (trên server Windows):**
```cmd
deploy.bat
```

### Bước 3: Kiểm tra deployment

```bash
# Xem trạng thái containers
docker-compose ps

# Xem logs
docker-compose logs -f

# Kiểm tra backend
curl http://localhost:8080/api/v1/health

# Kiểm tra frontend
curl http://localhost:80
```

---

## 💻 Chạy Local Với Docker

### Cách 1: Sử dụng Docker Compose (Recommended)

```bash
# Build và start tất cả services
docker-compose up -d --build

# Xem logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Cách 2: Build từng service riêng

**Backend:**
```bash
# Build image
docker build -t binancebot-backend .

# Run container
docker run -d \
  --name binancebot-backend \
  -p 8080:8080 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/user_data:/app/user_data \
  binancebot-backend
```

**Frontend:**
```bash
cd frontend

# Build image
docker build -f Dockerfile.frontend -t binancebot-frontend .

# Run container
docker run -d \
  --name binancebot-frontend \
  -p 80:80 \
  binancebot-frontend
```

### Truy cập ứng dụng:
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8080/api/v1
- **API Docs**: http://localhost:8080/api/v1/docs

---

## 📊 CI/CD Workflow

### Quy trình tự động:

1. **Push code lên GitHub**
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

2. **GitHub Actions tự động chạy:**
   - ✅ Test backend
   - ✅ Build và test frontend
   - ✅ Build Docker images
   - ✅ Push images lên Docker Hub
   - ✅ Deploy lên server

3. **Xem tiến trình:**
   - Vào: https://github.com/dangdoday/SE2025-9.4/actions
   - Click vào workflow đang chạy để xem logs

---

## 🛠 Quản Lý và Troubleshooting

### Các lệnh hữu ích:

**Xem logs:**
```bash
# Xem tất cả logs
docker-compose logs -f

# Xem logs của một service
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Restart services:**
```bash
# Restart tất cả
docker-compose restart

# Restart một service
docker-compose restart backend
```

**Update code mới:**
```bash
# Trên server
cd /opt/binancebot
git pull origin main
docker-compose up -d --build
```

**Xóa và rebuild hoàn toàn:**
```bash
docker-compose down -v  # Xóa cả volumes
docker-compose up -d --build --force-recreate
```

**Kiểm tra tài nguyên:**
```bash
# Xem CPU, RAM usage
docker stats

# Xem disk usage
docker system df
```

**Clean up:**
```bash
# Xóa containers không dùng
docker container prune -f

# Xóa images không dùng
docker image prune -a -f

# Xóa tất cả (cẩn thận!)
docker system prune -a -f
```

### Troubleshooting thường gặp:

**1. Port đã được sử dụng:**
```bash
# Tìm process đang dùng port
lsof -i :8080  # Linux/Mac
netstat -ano | findstr :8080  # Windows

# Kill process hoặc đổi port trong docker-compose.yml
```

**2. Container không start:**
```bash
# Xem logs chi tiết
docker-compose logs backend

# Kiểm tra config
docker-compose config
```

**3. Không connect được database:**
```bash
# Kiểm tra network
docker network ls
docker network inspect binancebot_binancebot-network

# Restart tất cả services
docker-compose restart
```

**4. Out of memory:**
```bash
# Tăng memory limit trong docker-compose.yml
services:
  backend:
    mem_limit: 2g
    mem_reservation: 1g
```

**5. SSL/HTTPS issues:**
```bash
# Cài đặt Let's Encrypt (trên server Linux)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 🔒 Bảo Mật

### Checklist bảo mật:
- ✅ Không commit file config chứa API keys
- ✅ Sử dụng .gitignore cho sensitive files
- ✅ Cấu hình firewall trên server
- ✅ Sử dụng HTTPS cho production
- ✅ Backup định kỳ database và config
- ✅ Giới hạn quyền truy cập SSH
- ✅ Cập nhật Docker images thường xuyên

### Files không nên commit:
```
config/config.json        # Chứa API keys
config/login.json         # Chứa credentials
.env                      # Environment variables
*.log                     # Log files
user_data/              # User data và databases
```

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra logs: `docker-compose logs -f`
2. Xem GitHub Actions logs: https://github.com/dangdoday/SE2025-9.4/actions
3. Kiểm tra file config
4. Đảm bảo Docker đang chạy
5. Kiểm tra network connectivity

---

## 📝 Notes

- Backup config và database trước khi deploy
- Test trên môi trường dev trước khi push lên production
- Monitor logs sau mỗi lần deploy
- Giữ Docker images được update thường xuyên

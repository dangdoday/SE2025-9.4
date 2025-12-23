# Linux Deploy (CI/CD)

This repo can be deployed on a Linux server with systemd and a GitHub Actions workflow.
The workflow builds the frontend, syncs the repo to the server, installs Python deps, and restarts the service.

## 1) Server prerequisites

- Python 3.11+ with venv support
- Node.js 18+ (only needed if you plan to build on the server)
- Git, rsync, and systemd

Example packages (Ubuntu):

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev git rsync
```

If you use TA-Lib features, install the native library on the server.

## 2) Clone and configure on the server

```bash
sudo mkdir -p /opt/binancebot
sudo chown -R $USER:$USER /opt/binancebot
git clone <YOUR_REPO_URL> /opt/binancebot
cd /opt/binancebot
```

Create the runtime config outside the repo:

```bash
sudo mkdir -p /etc/binancebot
sudo cp config/config.json.example /etc/binancebot/config.json
sudo nano /etc/binancebot/config.json
```

Important config tips:

- Set `api_server.listen_ip_address` to `127.0.0.1` if using a reverse proxy.
- Set `api_server.listen_ip_address` to `0.0.0.0` if you want direct remote access.
- Update `api_server.CORS_origins` to match your frontend URL.

## 3) Install the systemd service

Copy and edit the service file to match your paths and user:

```bash
sudo cp deploy/binancebot.service /etc/systemd/system/binancebot.service
sudo nano /etc/systemd/system/binancebot.service
```

Then enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now binancebot
```

## 4) GitHub Actions secrets

Add these secrets in your GitHub repo settings:

- `SSH_HOST` - server IP or domain
- `SSH_USER` - SSH username (should have access to `DEPLOY_PATH`)
- `SSH_KEY` - private key for SSH
- `SSH_PORT` - SSH port (usually `22`)
- `DEPLOY_PATH` - server path (example: `/opt/binancebot`)

Optional environment variables for `scripts/post_deploy.sh`:

- `SERVICE_NAME` - systemd service name (default `binancebot`)
- `SYSTEMD_MODE` - `system` or `user` (default `system`)
- `PYTHON_BIN` - python binary (default `python3.11`)

## 5) First deploy

Push to `main`, or run the GitHub Actions workflow manually.
The workflow will:

1. Build the frontend.
2. Copy the UI bundle to `backend/binancebot/rpc/api_server/ui/installed`.
3. Rsync the repo to `DEPLOY_PATH` (excluding `data/` and `config/config.json`).
4. Run `scripts/post_deploy.sh` to install Python deps and restart the service.

## 6) Logs and health checks

```bash
sudo systemctl status binancebot
journalctl -u binancebot -f
```

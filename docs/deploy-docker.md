# Docker Deploy

This setup builds the UI inside Docker and serves it from the backend on port 8080.

## 1) Server prerequisites

- Docker + Docker Compose (plugin)
- Git

Example (Ubuntu):

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git
sudo systemctl enable --now docker
```

## 2) Clone repo on server

```bash
sudo mkdir -p /opt/binancebot
sudo chown -R $USER:$USER /opt/binancebot
git clone <YOUR_REPO_URL> /opt/binancebot
cd /opt/binancebot
```

## 3) Prepare config

Create the runtime config on the server (keep secrets out of Git):

```bash
mkdir -p config
cp config/config.json.example config/config.json
nano config/config.json
```

Set `api_server.listen_ip_address` to `0.0.0.0` so the container can bind externally.
Update `api_server.CORS_origins` to your frontend URL if needed.

## 4) Run with Docker Compose

```bash
docker compose up -d --build
```

Access: `http://<server-ip>:8080`

## 5) GitHub Actions (optional)

If you want CI/CD via GitHub Actions, add these secrets:

- `SSH_HOST`
- `SSH_USER`
- `SSH_KEY`
- `SSH_PORT`
- `DEPLOY_PATH` (example: `/opt/binancebot`)

Then use `.github/workflows/deploy-docker.yml`.

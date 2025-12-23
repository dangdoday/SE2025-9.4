# syntax=docker/dockerfile:1

FROM node:18-alpine AS ui-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY backend ./backend
COPY user_data ./user_data
COPY config ./config
COPY --from=ui-build /app/frontend/dist /app/backend/binancebot/rpc/api_server/ui/installed
RUN printf "%s" "docker" > /app/backend/binancebot/rpc/api_server/ui/installed/.uiversion

ENV PYTHONPATH=/app/backend
EXPOSE 8080

CMD ["python", "-m", "binancebot", "trade", "--config", "/config/config.json"]

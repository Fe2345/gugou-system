#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

# --- 加载 .env ---
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

DJANGO_PORT="${DJANGO_PORT:-8001}"

echo "========================================"
echo "  谷子交易系统 — 后端启动"
echo "========================================"
echo "  数据库: ${DB_HOST:-127.0.0.1}:${DB_PORT:-3306}/${DB_NAME:-gugou}"
echo "  Redis:  ${REDIS_HOST:-127.0.0.1}:${REDIS_PORT:-6379} (USE_REDIS=${USE_REDIS:-false})"
echo "  Django: http://127.0.0.1:${DJANGO_PORT}"
echo "========================================"

cd gugou_backend

# --- 检查虚拟环境 ---
if [ ! -d .venv ]; then
  echo ">> 创建虚拟环境..."
  uv sync
fi

# --- 数据库迁移 ---
echo ">> 执行数据库迁移..."
uv run python manage.py migrate --noinput

echo ""
echo ">> 启动 Django 开发服务器 (0.0.0.0:${DJANGO_PORT})..."
exec uv run python manage.py runserver "0.0.0.0:${DJANGO_PORT}"

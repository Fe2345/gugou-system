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

VITE_PORT="${VITE_PORT:-3000}"
BACKEND_URL="${VITE_BACKEND_URL:-http://127.0.0.1:8001}"

echo "========================================"
echo "  谷子交易系统 — 前端启动"
echo "========================================"
echo "  Vite:    http://127.0.0.1:${VITE_PORT}"
echo "  Proxy:   /api -> ${BACKEND_URL}"
echo "========================================"

cd frontend

# --- 安装依赖 ---
if [ ! -d node_modules ]; then
  echo ">> 安装依赖..."
  npm install
fi

echo ""
echo ">> 启动 Vite 开发服务器..."
exec npm run dev

#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
Set-Location $ProjectDir

# --- 加载 .env ---
$EnvFile = Join-Path $ProjectDir '.env'
if (Test-Path $EnvFile) {
  Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)=(.*)') {
      $name = $matches[1].Trim()
      $value = $matches[2].Trim()
      Set-Item -Path "env:$name" -Value $value
    }
  }
}

$DJANGO_PORT = $env:DJANGO_PORT ?? '8001'

Write-Host "========================================"
Write-Host "  谷子交易系统 — 后端启动"
Write-Host "========================================"
Write-Host "  数据库: $($env:DB_HOST ?? '127.0.0.1'):$($env:DB_PORT ?? '3306')/$($env:DB_NAME ?? 'gugou')"
Write-Host "  Redis:  $($env:REDIS_HOST ?? '127.0.0.1'):$($env:REDIS_PORT ?? '6379') (USE_REDIS=$($env:USE_REDIS ?? 'false'))"
Write-Host "  Django: http://127.0.0.1:${DJANGO_PORT}"
Write-Host "========================================"

Set-Location (Join-Path $ProjectDir 'gugou_backend')

# --- 检查虚拟环境 ---
if (-not (Test-Path '.venv')) {
  Write-Host ">> 创建虚拟环境..."
  uv sync
}

# --- 数据库迁移 ---
Write-Host ">> 执行数据库迁移..."
uv run python manage.py migrate --noinput

Write-Host "`n>> 启动 Django 开发服务器 (0.0.0.0:${DJANGO_PORT})..."
uv run python manage.py runserver "0.0.0.0:${DJANGO_PORT}"

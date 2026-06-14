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

$VITE_PORT = $env:VITE_PORT ?? '3000'
$BACKEND_URL = $env:VITE_BACKEND_URL ?? 'http://127.0.0.1:8001'

Write-Host "========================================"
Write-Host "  谷子交易系统 — 前端启动"
Write-Host "========================================"
Write-Host "  Vite:    http://127.0.0.1:${VITE_PORT}"
Write-Host "  Proxy:   /api -> ${BACKEND_URL}"
Write-Host "========================================"

Set-Location (Join-Path $ProjectDir 'frontend')

# --- 安装依赖 ---
if (-not (Test-Path 'node_modules')) {
  Write-Host ">> 安装依赖..."
  npm install
}

Write-Host "`n>> 启动 Vite 开发服务器..."
npm run dev

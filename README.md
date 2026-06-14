# 谷购系统 / 谷子交易系统

面向二次元谷子（Goods）商品、资产和交易场景的全栈项目。包含 Vue 3 前端、Django REST Framework 后端，以及商品、资产、市场、订单、换物、拼团、价格、信用和地区数据等模块。

## 技术栈

### 前端

- Vue 3 + TypeScript + Vite
- Vue Router + Pinia
- Axios + Element Plus

### 后端

- Python 3.12+ / Django 6 / Django REST Framework
- Simple JWT 认证
- MariaDB / MySQL 数据库
- Redis 缓存

## 项目结构

```text
gugou-system/
  frontend/                 前端项目
    src/
      api/                  接口封装
      layouts/              布局组件
      router/               路由配置
      stores/               Pinia 状态
      types/                TypeScript 类型
      utils/                工具函数
      views/user/           用户端页面
      views/admin/          管理端页面

  gugou_backend/            Django 后端项目
    apps/
      accounts/             用户与认证
      addresses/            地区数据
      products/             商品库
      assets/               用户资产
      market/               市场挂单
      orders/               订单
      exchanges/            换物
      teams/                拼团
      pricing/              价格记录
      credits/              信用记录
      operations/           后台运营
      common/               通用响应、权限、编号

  scripts/                  启动脚本
    backend.sh              后端启动
    frontend.sh             前端启动
    gugou_data_replace.sql  数据替换脚本

  docker-compose.yml        MariaDB + Redis 容器编排
  docs/                     项目文档
```

## 快速开始

完整安装步骤请参考 [INSTALL.md](./INSTALL.md)。

```sh
# 1. 安装依赖（前后端）
cd frontend && npm install
cd ../gugou_backend && uv sync

# 2. 配置环境变量
cp .env.example .env   # 填写实际数据库、Redis 等配置

# 3. 启动数据库（Docker）
docker compose up -d

# 4. 迁移 + 导入数据
cd gugou_backend && uv run python manage.py migrate
mysql -h127.0.0.1 -uroot -p gugou < scripts/gugou_data_replace.sql

# 5. 启动
./scripts/backend.sh   # 后端 → http://127.0.0.1:8001
./scripts/frontend.sh  # 前端 → http://127.0.0.1:3000
```

## 常用命令

```sh
# 后端检查
cd gugou_backend
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py test

# 前端构建
cd frontend
npm run build
```

## 接口前缀

| 前缀 | 说明 |
|------|------|
| `/api/auth/` | 登录、注册、刷新 Token |
| `/api/user/` | 用户信息 |
| `/api/products/` | 商品库 |
| `/api/assets/` | 用户资产 |
| `/api/market/` | 市场挂单 |
| `/api/orders/` | 订单 |
| `/api/exchanges/` | 换物 |
| `/api/teams/` | 拼团 |
| `/api/pricing/` | 价格 |
| `/api/credits/` | 信用 |
| `/api/operations/` | 后台运营 |
| `/api/divisions/` | 地区数据 |

## 协作注意

- 开发前阅读 [AGENTS.md](./AGENTS.md)。
- 不要直接在 `dev` 或 `main` 分支开发。
- `.env`、`.venv`、`node_modules`、`__pycache__` 不提交。
- 修改模型后必须生成并执行 Django 迁移。

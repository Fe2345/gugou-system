# 谷购系统

谷购系统是一个面向二次元谷子商品、资产和交易场景的前后端项目。当前最新版包含 Vue 3 前端、Django REST Framework 后端，以及商品、资产、市场、订单、换物、拼团、价格、信用和地区数据等模块。

## 技术栈

### 前端

- Vue 3
- TypeScript
- Vite
- Vue Router
- Pinia
- Axios

### 后端

- Python 3.12+
- Django 6
- Django REST Framework
- Simple JWT
- MySQL 或 MariaDB
- Redis

## 项目结构

```text
gugou-system/
  frontend/                 前端项目
    src/
      api/                  前端接口封装
      layouts/              布局组件
      router/               路由配置
      stores/               Pinia 状态
      types/                TypeScript 类型
      utils/                请求、校验、格式化等工具
      views/
        user/               用户端页面
        admin/              管理端页面

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
      common/               通用响应、权限、编号等
    config/                 Django 配置

  docs/                     项目文档和数据脚本
```

## 环境配置

本地真实配置写入 `.env`，不要提交到 Git。配置模板见 `.env.example`。

常用配置项：

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_PORT=8001

DB_NAME=change-me
DB_USER=change-me
DB_PASSWORD=change-me
DB_HOST=127.0.0.1
DB_PORT=3306

USE_REDIS=true
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

VITE_HOST=0.0.0.0
VITE_PORT=3000
VITE_API_BASE_URL=/api
VITE_BACKEND_URL=http://127.0.0.1:8001
```

如果本地后端运行在其他端口，需要同步调整 `DJANGO_PORT` 和 `VITE_BACKEND_URL`。

## 安装依赖

### 后端

```sh
cd gugou_backend
uv sync
```

如果不使用 `uv`，也可以在虚拟环境中按 `pyproject.toml` 安装依赖。

### 前端

```sh
cd frontend
npm install
```

## 数据库迁移

确认 `.env` 中数据库配置正确后执行：

```sh
cd gugou_backend
uv run python manage.py migrate
```

检查是否存在未生成迁移：

```sh
cd gugou_backend
uv run python manage.py makemigrations --check --dry-run
```

## 数据填充

商品种子数据位于：

```text
gugou_backend/seed_products.json
```

商品图片建议放在：

```text
frontend/public/images/products/
```

通过管理命令导入商品、图片、价格和示例资产：

```sh
cd gugou_backend
uv run python manage.py seed_data
```

给伙伴手动导入商品数据时，可以参考：

```text
docs/seed_products.sql
```

地区数据来源于 `data.sqlite`，迁移后会写入后端地区表。注意：当前仓库中 `data.sqlite` 是二进制文件，如出现 Git 冲突，不要直接用文本编辑器打开或手动合并。

## 启动项目

### 后端

```sh
./backend.sh
```

或手动启动：

```sh
cd gugou_backend
uv run python manage.py runserver 0.0.0.0:8001
```

### 前端

```sh
./frontend.sh
```

或手动启动：

```sh
cd frontend
npm run dev
```

默认访问地址：

```text
前端：http://127.0.0.1:3000
后端：http://127.0.0.1:8001
```

## 常用检查命令

后端：

```sh
cd gugou_backend
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py test
```

前端：

```sh
cd frontend
npm run build
```

## 当前接口约定

前端统一通过 `frontend/src/utils/request.ts` 请求接口，默认 `baseURL` 为 `/api`，开发环境由 Vite proxy 转发到 `VITE_BACKEND_URL`。

主要后端接口前缀：

```text
/api/auth/          登录、注册、刷新 Token
/api/user/          用户信息
/api/products/      商品库
/api/assets/        用户资产
/api/market/        市场挂单
/api/orders/        订单
/api/exchanges/     换物
/api/teams/         拼团
/api/pricing/       价格
/api/credits/       信用
/api/operations/    后台运营
/api/divisions/     地区数据
```

## 协作注意事项

- 开发前先阅读并遵守 `AGENTS.md`。
- 不要直接在 `dev` 或 `main` 分支开发。
- `.env`、`.venv`、`node_modules`、缓存文件和真实密钥不要提交。
- 不要提交 `gugou_backend/.seq_cache`。
- 出现冲突时先确认冲突来源，尤其是 `data.sqlite` 这类二进制文件。
- 修改模型后必须生成并执行 Django 迁移。

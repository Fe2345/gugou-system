# 安装说明

## 环境要求

- Python >= 3.12
- Node.js >= 20.19
- MariaDB / MySQL（可用 Docker 启动）
- Redis

---

## 1. 进入项目

```sh
cd gugou-system
```

## 2. 安装前端依赖

```sh
cd frontend
npm install
```

## 3. 安装后端依赖

推荐使用 `uv`（项目已提供 `uv.lock`）：

```sh
cd gugou_backend
uv sync
```

或使用 pip：

```sh
cd gugou_backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 4. 配置环境变量

```sh
cp .env.example .env
```

根据实际环境修改 `.env` 中的配置：

| 变量 | 说明 | 示例值 |
|------|------|--------|
| `DJANGO_SECRET_KEY` | Django 密钥 | `change-me`（自行生成） |
| `DJANGO_DEBUG` | 调试模式 | `True` |
| `DJANGO_PORT` | 后端端口 | `8001` |
| `DB_NAME` | 数据库名 | `gugou` |
| `DB_USER` | 数据库用户 | `root` |
| `DB_PASSWORD` | 数据库密码 | `root123` |
| `DB_HOST` | 数据库主机 | `127.0.0.1` |
| `DB_PORT` | 数据库端口 | `3306` |
| `USE_REDIS` | 是否启用 Redis | `true` |
| `REDIS_HOST` | Redis 主机 | `127.0.0.1` |
| `REDIS_PORT` | Redis 端口 | `6379` |
| `VITE_PORT` | 前端端口 | `3000` |
| `VITE_BACKEND_URL` | 后端代理地址 | `http://127.0.0.1:8001` |

## 5. 启动数据库

项目提供 Docker Compose 一键启动 MariaDB 和 Redis：

```sh
docker compose up -d
```

也可使用本地已安装的 MariaDB/MySQL，确保创建好数据库：

```sql
CREATE DATABASE IF NOT EXISTS gugou CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 6. 执行数据库迁移

```sh
cd gugou_backend
uv run python manage.py migrate
```

## 7. 导入数据

```sh
mysql -h127.0.0.1 -P3306 -uroot -p gugou < scripts/data.sql
```

或通过 Docker 容器导入：

```sh
docker exec -i mariadb mysql -uroot -proot123 gugou < scripts/gugou_data_replace.sql
```

## 8. 启动系统

### 后端

```sh
./scripts/backend.sh
```

PowerShell：

```powershell
./scripts/backend.ps1
```

后端默认运行在 `http://127.0.0.1:8001`。

### 前端

```sh
./scripts/frontend.sh
```

PowerShell：

```powershell
./scripts/frontend.ps1
```

前端默认运行在 `http://127.0.0.1:3000`。

两个启动脚本会自动加载 `.env` 配置、检查依赖，并在首次启动时执行迁移。

---

## 验证

- 前端：浏览器访问 `http://127.0.0.1:3000`
- 后端 API：`http://127.0.0.1:8001/api/products/?page=1&page_size=10`

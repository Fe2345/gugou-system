# CLAUDE.md

本文档用于约定 Claude Code 或其他代码 Agent 在本项目中的协作规范。  
所有 Agent 在执行任务前，必须先阅读并遵守本文档。  
本文档优先级高于 Agent 的默认开发习惯。

最后更新日期：2026-05-23

---

## 1. 项目协作总原则

本项目为多人协作项目，Agent 的主要职责是根据明确任务完成局部修改，而不是擅自重构整个项目。

Agent 必须遵守以下原则：

1. 先理解现有代码，再进行修改。
2. 只修改与当前任务直接相关的文件。
3. 不得破坏已有功能、接口字段、数据库结构和运行方式。
4. 不得直接在 `dev` 或 `main` 分支提交代码。
5. 不得写死任何依赖具体运行环境的配置。
6. 不得提交密钥、密码、本地路径、缓存文件和虚拟环境文件。
7. 修改完成后，必须说明改动内容、测试情况和未解决问题。
8. 不得声称已经完成未实际执行的测试或命令。

---

## 2. 正式开始任务前的检查要求

在开始任何代码修改前，必须先检查当前 Git 状态和当前分支与远程 `dev` 分支的差距。

必须执行或等价执行以下检查：

```bash
git status
git branch --show-current
git fetch origin
git rev-list --left-right --count HEAD...origin/dev
````

检查结果处理规则：

1. 如果当前存在未提交修改，必须先确认这些修改是否属于当前任务。
2. 如果当前分支不是基于最新 `origin/dev`，不得直接开始开发。
3. 如果当前在 `dev` 或 `main` 分支，不得直接修改并提交。
4. 如果发现本地代码落后于 `origin/dev`，应先基于最新 `origin/dev` 创建新任务分支。
5. 如果存在冲突风险，应在最终说明中明确指出。

禁止在未检查 Git 状态的情况下直接修改代码。

---

## 3. 分支协作规范

所有新任务必须从最新的 `origin/dev` 创建新的 feature 或 fix 分支。

推荐流程：

```bash
git fetch origin
git checkout dev
git pull origin dev
git checkout -b feature/task-name
```

或直接从远程 `dev` 创建：

```bash
git fetch origin
git checkout -b feature/task-name origin/dev
```

分支命名规范：

```text
feature/user-auth
feature/product-api
feature/order-module
feature/admin-review
fix/login-error
fix/order-status-bug
docs/api-description
refactor/module-name
```

分支使用规则：

1. 禁止直接在 `dev` 分支开发。
2. 禁止直接在 `main` 分支开发。
3. 一个任务对应一个独立分支。
4. 分支名称应能表达任务内容。
5. 不得把多个无关任务混在同一个分支中。
6. 不得使用 `git push --force`，除非项目负责人明确要求。
7. 不得擅自合并 `dev` 或 `main`。
8. 不得擅自删除远程分支。

---

## 4. 提交规范

提交前必须检查改动范围：

```bash
git status
git diff
```

提交信息应简洁说明本次改动内容。

推荐格式：

```text
feat: add user address api
fix: correct order status transition
docs: update backend interface description
refactor: simplify product query logic
test: add order module tests
chore: update dependencies
```

提交规则：

1. 每次提交只包含同一类相关改动。
2. 不得把格式化、重构、业务修改混在同一个提交中。
3. 不得提交无关文件。
4. 不得提交 `.env`、`.venv`、`node_modules`、缓存文件、日志文件。
5. 不得提交本机 IDE 配置，除非项目已经明确纳入版本管理。
6. 不得提交包含真实密码、密钥、数据库连接信息的文件。

---

## 5. 环境变量与敏感配置规范

所有依赖具体运行环境的配置必须通过环境变量读取，不允许写死在代码中。

注意：
真实配置应写入 `.env` 文件，而不是 `.venv`。
`.venv` 是 Python 虚拟环境目录，不用于保存项目配置。

必须通过环境变量管理的内容包括但不限于：

1. 数据库名称。
2. 数据库用户名。
3. 数据库密码。
4. 数据库主机。
5. 数据库端口。
6. Django `SECRET_KEY`。
7. Django `DEBUG`。
8. Redis 地址和端口。
9. 第三方 API Key。
10. 文件上传路径。
11. 前后端服务地址。
12. 邮箱服务账号和授权码。
13. OSS、COS、S3 等对象存储配置。
14. 支付、短信、登录认证等外部服务配置。

项目应维护以下文件：

```text
.env              本地真实配置，不提交 Git
.env.example      配置模板，可以提交 Git
.gitignore        必须忽略 .env 和 .venv
```

`.env.example` 可以包含配置项名称，但不得包含真实密码、真实密钥和个人路径。

示例：

```env
DEBUG=True
SECRET_KEY=change-me

DB_NAME=project_db
DB_USER=root
DB_PASSWORD=change-me
DB_HOST=127.0.0.1
DB_PORT=3306

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

禁止出现以下写法：

```python
PASSWORD = "123456"
HOST = "localhost"
SECRET_KEY = "real-secret-key"
UPLOAD_PATH = "C:\\Users\\xxx\\Desktop\\upload"
```

推荐从环境变量读取：

```python
import os

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
```

---

## 6. `.gitignore` 规范

项目必须忽略本地环境、缓存、日志和敏感配置文件。

推荐包含：

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.sqlite3

# Virtual environment
.venv/
venv/
env/

# Environment variables
.env
.env.local
.env.*.local

# Django
staticfiles/
media/
*.log

# Node
node_modules/
dist/
.cache/

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db
```

Agent 不得移除上述忽略规则。

---

## 7. 代码修改边界

Agent 修改代码前，必须先阅读相关模块文件、路由、模型、序列化器、接口调用方式和已有命名风格。

修改边界规则：

1. 只允许修改与当前任务直接相关的文件。
2. 不允许为了完成小任务而重构整个模块。
3. 不允许删除已有接口。
4. 不允许删除已有字段。
5. 不允许删除已有测试。
6. 不允许修改与当前任务无关的业务逻辑。
7. 不允许擅自改变项目目录结构。
8. 不允许擅自更换技术栈。
9. 不允许擅自引入大型依赖。
10. 不允许在未说明原因的情况下进行大范围格式化。

如果确实需要修改公共模块，必须在最终说明中明确说明：

1. 修改了哪个公共模块。
2. 为什么必须修改。
3. 影响了哪些业务模块。
4. 是否需要其他成员同步调整。

---

## 8. 后端接口设计规范

后端接口必须保持统一、稳定、可预测。

推荐统一响应格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

推荐错误响应格式：

```json
{
  "code": 400,
  "message": "参数错误",
  "data": null
}
```

推荐分页响应格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "count": 100,
    "page": 1,
    "page_size": 10,
    "results": []
  }
}
```

接口设计规则：

1. 接口路径应语义清晰。
2. 请求方法必须符合语义。
3. 查询数据使用 `GET`。
4. 新增数据使用 `POST`。
5. 整体更新使用 `PUT`。
6. 局部更新使用 `PATCH`。
7. 删除数据使用 `DELETE`。
8. 接口返回字段应保持稳定。
9. 不得随意修改已经被前端使用的字段名。
10. 不得随意修改已经被前端使用的接口路径。
11. 不得在同一项目中混用多种字段命名风格。
12. 新增接口必须说明请求参数、返回字段和错误情况。

如果接口变更会影响前端，必须在最终说明中明确写出：

```text
影响前端的接口变更：
1. 接口路径：
2. 请求方法：
3. 新增字段：
4. 删除字段：
5. 字段含义变化：
6. 前端需要同步修改的位置：
```

---

## 9. 前端协作规范

如果任务涉及前端，Agent 必须遵守现有前端项目结构和组件风格。

前端修改规则：

1. 不得擅自更换前端框架。
2. 不得擅自更换 UI 组件库。
3. 不得擅自修改全局路由结构。
4. 不得擅自修改全局状态管理方式。
5. 不得在多个页面重复编写相同接口请求逻辑。
6. 不得把后端接口地址写死在组件中。
7. 应通过统一请求封装调用接口。
8. 新增页面应遵守已有目录结构。
9. 新增组件应命名清晰，职责单一。
10. 不得在组件中直接写大量复杂业务逻辑。

环境相关的前端配置也必须放入环境变量文件，例如：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

禁止在前端代码中写死：

```javascript
const baseUrl = "http://127.0.0.1:8000"
```

---

## 10. Django Model 与数据库迁移规范

如果项目后端使用 Django，必须遵守本节规范。

模型设计规则：

1. 新增或修改 Model 后，必须生成迁移文件。
2. 不得随意删除已经存在的迁移文件。
3. 不得擅自修改已经被其他成员使用的迁移历史。
4. 不得随意重命名数据库表。
5. 不得随意重命名数据库字段。
6. 重要字段必须设置合理的类型、长度、默认值和约束。
7. 金额、积分、库存、订单状态等字段必须明确类型和取值范围。
8. 时间字段应区分创建时间、更新时间和业务时间。
9. 外键关系必须明确删除策略。
10. 涉及唯一性的字段必须设置唯一约束或联合唯一约束。

推荐字段规范：

```python
created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
```

迁移检查命令：

```bash
python manage.py makemigrations --check --dry-run
python manage.py makemigrations
python manage.py migrate
```

如果新增了迁移文件，最终说明中必须写明：

```text
是否新增迁移文件：是
迁移文件路径：
迁移原因：
是否已执行 migrate：
```

---

## 11. 权限与安全规范

所有涉及用户数据、订单数据、资产数据、商家数据和后台管理的数据接口，都必须进行权限校验。

基本规则：

1. 需要登录的接口必须校验用户身份。
2. 普通用户接口必须校验当前用户身份。
3. 商家接口必须校验商家身份。
4. 管理员接口必须校验管理员身份。
5. 涉及用户个人信息的数据必须校验数据归属。
6. 涉及订单、地址、资产、收藏、交易的数据必须校验数据归属。
7. 后端不得直接信任前端传入的 `user_id`。
8. 后端应优先从当前登录态中获取用户身份。
9. 不得把密码、密钥、Token 明文返回给前端。
10. 不得在日志中打印密码、Token、密钥和完整个人敏感信息。

禁止写法：

```python
user_id = request.data.get("user_id")
order = Order.objects.get(user_id=user_id)
```

推荐逻辑：

```python
user = request.user
order = Order.objects.get(user=user)
```

涉及角色的接口必须明确区分：

```text
普通用户
商家用户
管理员
超级管理员
```

## 12. 依赖管理规范

新增依赖前必须判断是否确有必要。

Python 项目依赖规则：

1. 新增 Python 第三方库后，必须更新依赖文件。
2. 不得在代码中使用未声明的第三方库。
3. 不得引入与项目技术栈冲突的依赖。
4. 不得引入体积过大但用途很小的依赖。
5. 优先使用标准库、Django、Django REST Framework 已有能力。

常见依赖文件：

```text
requirements.txt
pyproject.toml
Pipfile
```

前端项目依赖规则：

1. 新增 npm 依赖后，必须更新 `package.json` 和锁文件。
2. 不得随意删除已有依赖。
3. 不得同时混用多个包管理器的锁文件。
4. 如果项目使用 `npm`，不得新增 `yarn.lock` 或 `pnpm-lock.yaml`。
5. 如果项目使用 `pnpm`，不得新增 `package-lock.json`。

---

## 14. 日志与异常处理规范

异常处理必须清晰，不得吞掉错误。

禁止写法：

```python
try:
    do_something()
except Exception:
    pass
```

推荐写法：

```python
try:
    do_something()
except SpecificException as e:
    logger.exception("操作失败")
    return error_response("操作失败")
```

日志规则：

1. 关键业务操作应记录必要日志。
2. 异常应记录上下文信息。
3. 不得记录密码、密钥、Token。
4. 不得记录完整身份证号、手机号等敏感信息。
5. 不得把调试用 `print` 长期保留在正式代码中。
6. 不得把临时调试日志作为业务日志。

---

## 15. 测试与运行检查规范

修改代码后，必须尽量执行与任务相关的检查命令。

后端推荐检查：

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

前端推荐检查：

```bash
npm install
npm run lint
npm run build
```

或根据项目实际包管理器执行：

```bash
pnpm install
pnpm lint
pnpm build
```

测试说明规则：

1. 实际执行过的命令，必须写入最终说明。
2. 未执行的命令，不得声称已经执行。
3. 如果测试失败，必须说明失败原因。
4. 如果无法运行测试，必须说明原因。
5. 如果只做了静态检查，也必须如实说明。
6. 不得用主观判断代替测试结果。

最终说明中的测试部分应使用以下格式：

```text
测试情况：
1. 已执行：
   - python manage.py check
   - python manage.py test
2. 结果：
   - 通过
3. 未执行：
   - npm run build
4. 未执行原因：
   - 当前任务未涉及前端，且本地未安装前端依赖
```

---

## 16. 文档维护规范

如果修改涉及接口、模型、配置、部署或运行方式，必须同步更新相关文档。

需要同步更新文档的情况：

1. 新增接口。
2. 修改接口路径。
3. 修改请求参数。
4. 修改返回字段。
5. 修改数据库模型。
6. 新增环境变量。
7. 新增依赖。
8. 修改启动方式。
9. 修改权限规则。
10. 修改业务状态流转。

文档可包括：

```text
README.md
CLAUDE.md
.env.example
接口文档
数据库设计文档
前后端协作说明
部署说明
```

---

## 17. 文件与目录操作规范

Agent 不得随意创建、删除或移动文件。

允许创建的文件：

1. 当前任务明确要求的新模块文件。
2. 当前任务需要的测试文件。
3. 当前任务需要的迁移文件。
4. 当前任务需要的文档文件。
5. 当前任务需要的配置模板文件。

禁止行为：

1. 删除整个目录。
2. 重命名核心目录。
3. 移动大量文件。
4. 创建无意义的临时文件。
5. 提交本地缓存文件。
6. 提交运行日志文件。
7. 提交编译产物。
8. 提交虚拟环境目录。
9. 提交依赖安装目录。

---

## 18. 代码风格规范

Agent 应遵守项目已有代码风格，不得把个人风格强加到项目中。

通用规则：

1. 命名应清晰表达业务含义。
2. 函数职责应单一。
3. 不写过长函数。
4. 不写重复逻辑。
5. 不写无意义注释。
6. 不保留无用代码。
7. 不保留被注释掉的大段旧代码。
8. 不使用含糊命名，例如 `data1`、`temp2`、`aaa`。
9. 不为了追求简短而牺牲可读性。
10. 不为了局部方便破坏整体结构。

注释规则：

1. 复杂业务逻辑需要注释。
2. 权限判断需要注释。
3. 状态流转需要注释。
4. 事务操作需要注释。
5. 简单赋值不需要注释。
6. 注释必须解释原因，而不是重复代码表面含义。

---

## 19. Agent 不得执行的高风险操作

除非用户明确要求，否则 Agent 不得执行以下操作：

```bash
rm -rf
git reset --hard
git clean -fd
git push --force
git rebase dev
git merge main
git checkout -- .
drop database
truncate table
delete from
```

也不得擅自进行：

1. 删除数据库。
2. 清空数据表。
3. 删除迁移文件。
4. 重建项目。
5. 修改 Git 历史。
6. 删除他人代码。
7. 覆盖他人分支。
8. 修改生产配置。
9. 上传真实密钥。
10. 暴露用户隐私数据。

如果任务确实需要高风险操作，必须先说明风险、影响范围和替代方案，并等待项目负责人确认。

---

## 20. 任务完成后的交付说明格式

每次完成任务后，Agent 必须按照以下格式输出说明。

```text
任务完成说明：

一、修改内容
1. 修改文件：
   - 文件路径：
   - 修改内容：
2. 新增文件：
   - 文件路径：
   - 文件作用：

二、接口变化
1. 是否新增接口：
2. 是否修改接口：
3. 是否影响前端：
4. 需要前端同步的内容：

三、数据库变化
1. 是否修改 Model：
2. 是否新增迁移文件：
3. 是否已执行迁移：
4. 是否影响已有数据：

四、环境变量变化
1. 是否新增环境变量：
2. 是否更新 .env.example：
3. 新增配置项说明：

五、依赖变化
1. 是否新增依赖：
2. 是否更新依赖文件：
3. 新增依赖用途：

六、测试情况
1. 已执行命令：
2. 测试结果：
3. 未执行命令：
4. 未执行原因：

七、注意事项
1. 仍需人工确认的问题：
2. 潜在影响：
3. 后续建议：
```

禁止只回复：

```text
已完成
已修复
可以了
没有问题
```

---

## 21. 适用于本项目的优先级规则

当任务指令、现有代码和本文档发生冲突时，按以下优先级处理：

```text
用户当前明确指令
项目已有代码和接口约定
CLAUDE.md 协作规范
Agent 默认行为
```

如果用户要求与安全规范、分支规范、敏感配置规范冲突，Agent 不得直接执行，应说明冲突点并给出安全做法。

---

## 22. 最重要的硬性要求

以下要求必须严格遵守：

1. 开始任务前必须检查 Git 状态和与 `origin/dev` 的差距。
2. 新任务必须从最新 `origin/dev` 创建新分支。
3. 禁止直接在 `dev` 或 `main` 分支开发和提交。
4. 环境相关配置必须写入 `.env` 并通过环境变量读取。
5. `.env`、`.venv`、真实密钥、真实密码不得提交。
6. Agent 只能修改当前任务相关文件。
7. 不得擅自重构无关模块。
8. 不得随意修改已约定接口字段。
9. 涉及订单、库存、资产、积分、交易状态的操作必须考虑事务一致性。
10. 修改完成后必须说明改了什么、测了什么、还有什么风险。
11. 不得声称执行了未实际执行的测试。
12. 不得用本地写死路径、写死端口、写死账号密码来完成任务。
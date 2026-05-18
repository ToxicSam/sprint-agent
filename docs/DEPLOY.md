# Sprint Agent v2.0 - 部署指南

> 本文档涵盖开发环境搭建、生产部署、Docker 部署、静态托管部署及常见问题排查。
>
> 版本: v2.0 | 适用技术栈: React 19 + TypeScript + Vite / Python + FastAPI + SQLite / Docker

---

## 目录

1. [前置条件](#1-前置条件)
2. [开发环境搭建](#2-开发环境搭建)
3. [生产环境部署](#3-生产环境部署)
4. [Docker 部署（推荐）](#4-docker-部署推荐)
5. [静态托管部署](#5-静态托管部署)
6. [后端独立部署方案](#6-后端独立部署方案)
7. [从 v1.0 迁移数据](#7-从-v10-迁移数据)
8. [环境变量参考表](#8-环境变量参考表)
9. [安全建议](#9-安全建议)
10. [常见问题排查](#10-常见问题排查)
11. [FAQ](#11-faq)

---

## 1. 前置条件

在部署 Sprint Agent v2.0 之前，请确保系统已安装以下依赖：

| 依赖项 | 最低版本 | 推荐版本 | 验证命令 |
|--------|---------|---------|---------|
| Node.js | 20.0.0 | 20.x LTS | `node --version` |
| npm | 10.0.0 | 10.x | `npm --version` |
| Python | 3.12.0 | 3.12.x | `python --version` |
| pip | 24.0 | 最新版 | `pip --version` |
| Docker | 24.0.0 | 最新版 | `docker --version` |
| Docker Compose | 2.20.0 | 最新版 | `docker compose version` |
| Git | 2.40.0 | 最新版 | `git --version` |

> **注意**：Python 3.11 及以下版本未经过充分测试，建议使用 Python 3.12 以避免兼容性问题。

### 操作系统兼容性

- **Linux**: Ubuntu 22.04+、Debian 12+、CentOS Stream 9+（推荐）
- **macOS**: macOS 13+（Ventura 或更新版本）
- **Windows**: Windows 11 + WSL2（推荐）或 Windows Server 2022

---

## 2. 开发环境搭建

### 2.1 克隆代码仓库

```bash
git clone https://github.com/ToxicSam/sprint-agent.git
cd sprint-agent
```

仓库结构说明：

```
sprint-agent/
├── frontend/          # React 19 + TypeScript + Vite 前端
│   ├── src/
│   ├── public/
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── backend/           # Python + FastAPI + SQLite 后端
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── data/
│       └── init.json  # 初始化数据（Zero-Mock 核心）
├── docker-compose.yml # 全栈 Docker 编排
└── README.md
```

### 2.2 安装前端依赖

```bash
cd frontend
npm install
```

安装过程预计需要 1-3 分钟（取决于网络环境）。若遇到依赖安装缓慢，可配置 npm 镜像：

```bash
# 国内用户建议配置淘宝镜像
npm config set registry https://registry.npmmirror.com
npm install
```

### 2.3 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

`requirements.txt` 核心依赖包括：

```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
python-multipart>=0.0.12
```

### 2.4 启动后端开发服务器

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

启动后访问 http://localhost:8000/docs 可查看自动生成的 API 文档（Swagger UI）。

常用启动参数说明：

| 参数 | 说明 | 示例值 |
|------|------|--------|
| `--reload` | 代码变更自动重载（仅开发） | - |
| `--port` | 监听端口 | `8000` |
| `--host` | 监听地址 | `0.0.0.0` |
| `--workers` | 工作进程数（生产） | `4` |

### 2.5 启动前端开发服务器

在另一个终端窗口中：

```bash
cd frontend
npm run dev
```

默认启动在 http://localhost:5173（Vite 默认端口）。

### 2.6 访问应用

| 服务 | 开发地址 | 说明 |
|------|---------|------|
| 前端页面 | http://localhost:5173 | Vite 开发服务器 |
| 后端 API | http://localhost:8000 | FastAPI 服务 |
| API 文档 | http://localhost:8000/docs | Swagger UI |
| API 红文档 | http://localhost:8000/redoc | ReDoc 格式 |

首次启动时，后端会自动检测 SQLite 数据库是否为空。若为空，则读取 `backend/data/init.json` 初始化数据。此过程通常在 1 秒内完成。

---

## 3. 生产环境部署

### 3.1 构建前端生产包

```bash
cd frontend
npm install
npm run build
```

构建产物输出到 `frontend/dist/` 目录，包含以下文件：

```
frontend/dist/
├── index.html          # 入口 HTML
├── assets/
│   ├── index-xxx.js    # 打包后的 JS
│   ├── index-xxx.css   # 打包后的 CSS
│   └── ...             # 其他静态资源
└── ...
```

### 3.2 配置 API 基础地址

前端通过环境变量获取后端 API 地址：

```typescript
// 前端代码中的 API 地址配置
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

生产环境需要设置 `VITE_API_URL`：

```bash
# 方式一：构建时注入
VITE_API_URL=https://api.yourdomain.com npm run build

# 方式二：.env 文件（推荐）
# 在 frontend/.env.production 中写入：
# VITE_API_URL=https://api.yourdomain.com
```

> **重要**：以 `VITE_` 开头的环境变量才会被 Vite 暴露到前端代码中。

### 3.3 启动后端生产服务

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

或使用 Gunicorn + Uvicorn（见第 6 节）。

### 3.4 CORS 配置

开发环境后端已配置 `allow_origins=["*"]`。生产环境应限制来源：

```python
# backend/main.py 中的 CORS 配置（生产环境应修改）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "https://app.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 4. Docker 部署（推荐）

### 4.1 全栈 Docker Compose 部署

项目根目录已提供 `docker-compose.yml`：

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/data:/app/data
    environment:
      - ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
```

### 4.2 一键启动

```bash
cd sprint-agent
docker compose up -d
```

启动后访问：
- 前端：http://localhost:3000
- 后端 API：http://localhost:8000

### 4.3 查看日志

```bash
# 查看所有服务日志
docker compose logs -f

# 查看后端日志
docker compose logs -f backend

# 查看前端日志
docker compose logs -f frontend
```

### 4.4 数据持久化

SQLite 数据库和 `init.json` 通过卷挂载实现持久化：

```yaml
volumes:
  - ./backend/data:/app/data
```

`backend/data/` 目录包含：
- `init.json` — 初始化数据文件
- `sprint_agent.db` — SQLite 数据库文件（首次启动后自动生成）

**备份建议**：定期备份 `backend/data/` 目录：

```bash
# 手动备份
cp -r backend/data backup/data-$(date +%Y%m%d)

# 自动备份（加入 crontab）
# 每天凌晨 2 点备份
0 2 * * * cd /path/to/sprint-agent && cp -r backend/data backup/data-$(date +\%Y\%m\%d)
```

### 4.5 停止与重启

```bash
# 停止服务
docker compose down

# 停止并删除数据卷（谨慎操作）
docker compose down -v

# 重启服务
docker compose restart

# 重建镜像并启动
docker compose up -d --build
```

### 4.6 生产环境 Docker 调优

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "127.0.0.1:8000:8000"  # 仅本地访问，配合 Nginx 反向代理
    volumes:
      - sprint_data:/app/data
    environment:
      - ENV=production
      - WORKERS=4
    restart: always
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 128M

  frontend:
    build:
      context: ./frontend
      args:
        - VITE_API_URL=/api
    ports:
      - "127.0.0.1:3000:80"
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: always

volumes:
  sprint_data:
```

---

## 5. 静态托管部署

### 5.1 构建静态文件

```bash
cd frontend
npm install
VITE_API_URL=https://api.yourdomain.com npm run build
```

构建产物位于 `frontend/dist/`，可直接部署到任何静态文件托管服务。

### 5.2 GitHub Pages 部署

```bash
# 安装 gh-pages
cd frontend
npm install -D gh-pages

# 在 package.json 中添加：
# "homepage": "https://yourname.github.io/sprint-agent",
# "scripts": { "deploy": "gh-pages -d dist" }

# 构建并部署
npm run build
npm run deploy
```

### 5.3 Vercel 部署

```bash
# 安装 Vercel CLI
npm install -g vercel

# 部署（项目根目录）
cd frontend
vercel --prod

# 或在 Vercel 面板中连接 GitHub 仓库自动部署
```

配置 API 代理（`vercel.json`）：

```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://api.yourdomain.com/api/:path*" }
  ]
}
```

### 5.4 Netlify 部署

```bash
# 安装 Netlify CLI
npm install -g netlify-cli

# 部署
cd frontend
netlify deploy --prod --dir=dist
```

配置代理重定向（`netlify.toml`）：

```toml
[[redirects]]
  from = "/api/*"
  to = "https://api.yourdomain.com/api/:splat"
  status = 200
  force = true
```

### 5.5 API 代理说明

静态托管前端需要代理 API 请求到后端服务。推荐方案：

| 托管平台 | 代理方式 | 配置文件 |
|---------|---------|---------|
| GitHub Pages | 不支持代理 | 需使用完整 API URL |
| Vercel | `vercel.json` rewrites | `vercel.json` |
| Netlify | `_redirects` 或 `netlify.toml` | `netlify.toml` |
| Nginx | `proxy_pass` | `nginx.conf` |
| Cloudflare Pages | `_redirects` | `_redirects` |

---

## 6. 后端独立部署方案

### 6.1 直接 Python 部署

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6.2 Gunicorn + Uvicorn（推荐生产方案）

```bash
cd backend
source venv/bin/activate
pip install gunicorn

# 启动（使用 Uvicorn worker）
gunicorn main:app -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-connections 1000 \
  --max-requests 10000 \
  --max-requests-jitter 1000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

### 6.3 Systemd 服务（Linux 服务器）

创建服务文件 `/etc/systemd/system/sprint-agent.service`：

```ini
[Unit]
Description=Sprint Agent Backend
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/sprint-agent/backend
Environment=PATH=/opt/sprint-agent/backend/venv/bin
Environment=ENV=production
Environment=PYTHONPATH=/opt/sprint-agent/backend
ExecStart=/opt/sprint-agent/backend/venv/bin/gunicorn main:app \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --access-logfile /var/log/sprint-agent/access.log \
    --error-logfile /var/log/sprint-agent/error.log
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启用并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable sprint-agent
sudo systemctl start sprint-agent
sudo systemctl status sprint-agent
```

查看日志：

```bash
sudo journalctl -u sprint-agent -f
```

### 6.4 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## 7. 从 v1.0 迁移数据

### 7.1 数据格式转换

v1.0 的 JSON 格式需转换为 v2.0 的 `init.json` 格式。主要变化：

| 变更项 | v1.0 | v2.0 |
|--------|------|------|
| 文件结构 | 多个独立 JSON 文件 | 单个 `init.json` |
| Sprint ID | 使用数字或简单字符串 | `spr-xxx` 格式 |
| Member ID | 使用数字或简单字符串 | `mem-xxx` 格式 |
| Task ID | 使用数字或简单字符串 | `task-xxx` 格式 |
| 任务状态 | `pending`, `doing`, `completed` | `todo`, `progress`, `done`, `paused` |

### 7.2 转换脚本

```bash
# 使用 Python 脚本转换
python scripts/migrate_v1_to_v2.py --input ./v1-data/ --output ./backend/data/init.json
```

### 7.3 导入方式

转换后的数据可通过以下方式导入：

**方式一：启动自动导入**
将 `init.json` 放入 `backend/data/` 目录，删除旧的 `.db` 文件，重启后端服务。

**方式二：设置页拖拽导入**
进入应用设置页，将 JSON 文件拖拽到导入区域。

**方式三：API 导入**

```bash
curl -X POST http://localhost:8000/api/import \
  -H "Content-Type: multipart/form-data" \
  -F "file=@init.json"
```

**方式四：重置导入**

```bash
curl -X POST http://localhost:8000/api/reset
```

---

## 8. 环境变量参考表

### 前端环境变量

| 变量名 | 默认值 | 说明 | 必需 |
|--------|--------|------|------|
| `VITE_API_URL` | `http://localhost:8000` | 后端 API 基础地址 | 否 |
| `VITE_APP_TITLE` | `Sprint Agent` | 应用标题 | 否 |

> 注意：前端变量必须以 `VITE_` 开头才能被 Vite 识别。

### 后端环境变量

| 变量名 | 默认值 | 说明 | 必需 |
|--------|--------|------|------|
| `ENV` | `development` | 运行环境 | 否 |
| `DATABASE_URL` | `./data/sprint_agent.db` | SQLite 数据库路径 | 否 |
| `INIT_DATA_PATH` | `./data/init.json` | 初始化数据文件路径 | 否 |
| `CORS_ORIGINS` | `*` | CORS 允许来源（逗号分隔） | 否 |
| `WORKERS` | `1` | Uvicorn 工作进程数 | 否 |
| `PORT` | `8000` | 监听端口 | 否 |
| `HOST` | `0.0.0.0` | 监听地址 | 否 |

---

## 9. 安全建议

### 9.1 生产环境必做事项

1. **修改 CORS 配置**：将 `allow_origins=["*"]` 改为具体的域名白名单
2. **启用 HTTPS**：使用 Let's Encrypt 或其他证书服务
3. **设置防火墙**：仅开放 80/443 端口，后端不直接暴露公网
4. **定期备份**：配置自动备份 `backend/data/` 目录
5. **更新依赖**：定期运行 `npm audit` 和 `pip audit` 检查安全漏洞

### 9.2 网络安全

```bash
# UFW 防火墙配置示例（Ubuntu）
sudo ufw default deny incoming
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 9.3 数据安全

- 数据库文件权限设置为 `640`
- init.json 中不应包含敏感信息（密码、密钥等）
- 定期清理旧备份文件

---

## 10. 常见问题排查

### 10.1 前端构建失败

**问题**：`npm run build` 报错，提示类型错误

**解决方案**：

```bash
# 1. 清除缓存重新安装
rm -rf node_modules package-lock.json
npm install
npm run build

# 2. 检查 TypeScript 版本
npx tsc --version  # 应 >= 5.6

# 3. 检查 Node 版本
node --version  # 应 >= 20.0
```

### 10.2 后端启动失败

**问题**：`uvicorn` 命令未找到或端口被占用

**解决方案**：

```bash
# 1. 确认 uvicorn 已安装
pip install uvicorn[standard]

# 2. 检查端口占用
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# 3. 更换端口启动
python -m uvicorn main:app --port 8001
```

### 10.3 前端无法连接后端

**问题**：浏览器控制台报 CORS 错误或连接被拒绝

**解决方案**：

```bash
# 1. 确认后端已启动
curl http://localhost:8000/health

# 2. 检查前端环境变量是否设置正确
echo $VITE_API_URL  # 应指向正确的后端地址

# 3. 确认 CORS 配置包含前端地址
# 修改 backend/main.py 中的 allow_origins
```

### 10.4 数据库未初始化

**问题**：页面显示空白或报错 "No data found"

**解决方案**：

```bash
# 1. 确认 init.json 文件存在
ls backend/data/init.json

# 2. 删除旧数据库触发重新初始化
rm backend/data/sprint_agent.db
# 重启后端服务

# 3. 检查 init.json 格式是否正确
python -c "import json; json.load(open('backend/data/init.json'))"
```

### 10.5 Docker 容器启动失败

**问题**：`docker compose up` 后容器立即退出

**解决方案**：

```bash
# 1. 查看具体错误
docker compose logs backend

# 2. 检查 Dockerfile 语法
docker build ./backend

# 3. 确认端口未被占用
# 修改 docker-compose.yml 中的端口映射
```

### 10.6 前端白屏

**问题**：部署后页面空白，控制台报错

**解决方案**：

```bash
# 1. 检查构建产物
ls frontend/dist/index.html
ls frontend/dist/assets/

# 2. 检查 API 地址配置
grep VITE_API_URL frontend/.env.production

# 3. 查看浏览器控制台网络请求是否成功
# F12 -> Network 面板
```

---

## 11. FAQ

### Q1: 是否必须使用 Docker 部署？

**A**: 不是必须的。Docker 部署是推荐方案，但您也可以选择直接部署 Python 后端 + Nginx 静态文件服务。Docker 的优势在于环境一致性和一键启动。

### Q2: 如何更新到最新版本？

**A**:

```bash
git pull origin main
docker compose down
docker compose up -d --build
```

### Q3: 如何修改默认端口？

**A**: 修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8080:80"    # 前端改为 8080
  - "9000:8000"  # 后端改为 9000
```

同时更新前端的环境变量 `VITE_API_URL`。

### Q4: 支持多用户协作吗？

**A**: v2.0 的数据模型已预留多用户字段（`members` 表），但当前版本为单用户模式。后续版本将添加认证和权限管理。

### Q5: 数据存储在哪里？

**A**: 默认存储在 `backend/data/sprint_agent.db`（SQLite 文件）。通过 Docker 卷挂载持久化。

### Q6: 如何重置所有数据？

**A**: 三种方式：
1. 删除 `backend/data/sprint_agent.db` 并重启服务
2. 调用 API：`POST /api/reset`
3. 设置页点击"重置数据"按钮

### Q7: 能否使用 PostgreSQL/MySQL 替代 SQLite？

**A**: 当前版本仅支持 SQLite。后续版本计划支持 PostgreSQL 和 MySQL，届时只需修改数据库连接配置即可。

### Q8: 前端是否可以在没有后端的情况下运行？

**A**: 不可以。Sprint Agent v2.0 遵循 Zero-Mock 原则，前端代码中没有任何模拟数据逻辑，所有数据均通过 API 从后端获取。这是设计上的刻意选择。

### Q9: 如何自定义初始化数据？

**A**: 编辑 `backend/data/init.json` 文件，按 DATA_FORMAT.md 中的格式规范填写数据，然后重启服务或调用 `/api/reset`。

### Q10: 生产环境推荐的服务器配置？

**A**: 最低配置：2 vCPU / 2GB RAM / 20GB SSD。推荐配置：4 vCPU / 4GB RAM / 40GB SSD。本项目资源占用极低，单核 1GB 也能流畅运行。

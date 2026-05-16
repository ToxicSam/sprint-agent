# Sprint Agent 部署指南

## 🚀 三种部署方式

### 方式一：一键脚本部署（推荐，5 分钟）

#### 前置要求

- Docker 20.10+
- Docker Compose 2.0+

#### 部署步骤

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/sprint-agent.git
cd sprint-agent

# 2. 执行部署脚本
./scripts/deploy.sh
```

脚本会自动完成：
- 检查 Docker 环境
- 初始化数据目录结构
- 可选：引导创建 Sprint 或导入现有数据
- 构建 Docker 镜像
- 启动服务
- 等待健康检查通过

访问 http://localhost:8080 开始使用。

#### 部署脚本交互流程

```
🚀 Sprint Agent 一键部署脚本
==============================

🔍 检查依赖...
✅ docker 已安装
✅ docker-compose 已安装

📁 数据目录: ./data

📝 未检测到 Sprint 数据，需要初始化

请选择操作:
  1) 创建新 Sprint
  2) 从现有 JSON 文件导入
  3) 稍后手动配置

请选择 [1/2/3]: 1
Sprint 名称 (如: 5.12-5.23): 5.12-5.23
开始日期 (YYYY-MM-DD): 2026-05-12
结束日期 (YYYY-MM-DD): 2026-05-23
工作日数 [10]: 10

✅ 配置已创建，Sprint 将在启动后通过 API 创建

🏗️ 构建 Docker 镜像...
▶️ 启动服务...

✅ Sprint Agent 已启动！

📊 看板地址: http://localhost:8080
📡 API 地址: http://localhost:8080/api
❤️  健康检查: http://localhost:8080/api/health
```

---

### 方式二：Docker Compose 部署

适合已熟悉 Docker 的用户，更灵活可控。

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/sprint-agent.git
cd sprint-agent

# 2. 创建数据目录
mkdir -p data/{active,sprints,story_pool,retro,assessments}

# 3. 复制现有数据（可选）
cp /path/to/your/active_sprint.json data/active/

# 4. 启动服务
docker-compose up -d

# 5. 查看日志
docker-compose logs -f

# 6. 停止服务
docker-compose down
```

#### Docker Compose 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| 端口映射 | 宿主机:容器 | `8080:8080` |
| 数据卷 | 持久化数据 | `./data:/app/data` |
| 前端热更新 | 开发模式 | `./web:/app/web` |
| 重启策略 | 容器崩溃自动重启 | `unless-stopped` |
| 健康检查 | 每 30s 检查 | 3 次重试 |

#### 自定义端口

编辑 `docker-compose.yml`：

```yaml
services:
  sprint-agent:
    ports:
      - "3000:8080"  # 改为 3000 端口
```

---

### 方式三：源码部署

适合开发环境或需要定制化的场景。

#### 前置要求

- Python 3.12+
- pip

#### 部署步骤

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/sprint-agent.git
cd sprint-agent

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 创建数据目录
mkdir -p data/{active,sprints,story_pool,retro,assessments}

# 5. 启动 API 服务
python -m api.server

# 6. 访问看板
# 前端是静态文件，可以用任意 HTTP 服务器托管
# 方式 A: Python 内置服务器
cd web && python -m http.server 3000
# 方式 B: 直接访问（API 和前端同端口）
# 访问 http://localhost:8080
```

---

## 🔧 运维命令

### Docker 环境

```bash
# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 更新镜像后重建
docker-compose up -d --build

# 进入容器调试
docker-compose exec sprint-agent bash

# 查看数据文件
docker-compose exec sprint-agent ls -la /app/data

# 备份数据
cp -r data data-backup-$(date +%Y%m%d)

# 完全清理
docker-compose down -v
```

### 源码环境

```bash
# 启动服务
python -m api.server

# 指定端口
python -m api.server --port 9000

# 开发模式（热重载）
uvicorn api.server:app --reload --port 8080
```

---

## ☁️ 云服务部署

### 阿里云/腾讯云/华为云

1. 购买云服务器（推荐 2C4G）
2. 安装 Docker（参考官方文档）
3. 按「方式二」部署
4. 配置安全组开放 8080 端口
5. （可选）配置域名 + Nginx 反向代理

### 使用 Nginx 反向代理 + HTTPS

```nginx
server {
    listen 80;
    server_name sprint.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name sprint.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 使用 Cloudflare Tunnel（免费 HTTPS）

```bash
# 1. 安装 cloudflared
# 2. 登录 Cloudflare
cloudflared tunnel login

# 3. 创建隧道
cloudflared tunnel create sprint-agent

# 4. 配置路由
cloudflared tunnel route dns sprint-agent sprint.yourdomain.com

# 5. 启动隧道
cloudflared tunnel run sprint-agent
```

---

## 📦 数据迁移

### 从旧版本迁移

Sprint Agent 使用 JSON 文件存储，迁移非常简单：

```bash
# 1. 备份旧数据
cp -r /old/path/data ./data

# 2. 重新部署（会自动读取现有数据）
./scripts/deploy.sh
```

### 导出数据

```bash
# 打包整个数据目录
tar czvf sprint-data-$(date +%Y%m%d).tar.gz data/

# 或只导出当前 Sprint
cp data/active/active_sprint.json sprint-export.json
```

### 导入数据

```bash
# 解包到数据目录
tar xzvf sprint-data-20260516.tar.gz

# 或复制单个文件
cp sprint-export.json data/active/active_sprint.json
```

---

## 🔒 安全建议

1. **不要暴露到公网** — 如果没有认证，建议只在内网或 VPN 使用
2. **定期备份** — 数据在 `data/` 目录，建议每日备份
3. **使用 HTTPS** — 生产环境务必配置 SSL
4. **防火墙** — 只开放必要的端口

---

## 🆘 故障排查

### 服务启动失败

```bash
# 检查日志
docker-compose logs

# 检查端口占用
lsof -i :8080

# 检查数据目录权限
ls -la data/
```

### 看板无法加载数据

1. 检查 API 是否运行：`curl http://localhost:8080/api/health`
2. 检查浏览器控制台是否有 CORS 错误
3. 检查 data/active/active_sprint.json 是否存在

### 数据丢失

Sprint Agent 有自动备份机制，备份文件在 `data/active/` 目录下：

```bash
# 列出所有备份
ls -lt data/active/*.bak.*

# 恢复最新备份
cp data/active/active_sprint.bak.20260516120000 data/active/active_sprint.json
```

---

## 📞 获取帮助

- 查看日志：`docker-compose logs -f`
- 提交 Issue：[GitHub Issues](https://github.com/yourusername/sprint-agent/issues)
- 查看文档：[完整文档](docs/)

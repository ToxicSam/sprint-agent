# Sprint Agent v2.0 - 发布指南

> 本文档指导如何将 Sprint Agent v2.0 代码发布到 GitHub、创建版本 Release、部署前端页面及发布 Docker 镜像。
>
> 版本: v2.0

---

## 目录

1. [GitHub 仓库设置](#1-github-仓库设置)
2. [推送代码到 GitHub](#2-推送代码到-github)
3. [创建版本 Release](#3-创建版本-release)
4. [GitHub Pages 部署](#4-github-pages-部署)
5. [Docker 镜像发布](#5-docker-镜像发布)
6. [发布说明模板](#6-发布说明模板)
7. [版本号规则](#7-版本号规则)
8. [标签与变更日志](#8-标签与变更日志)

---

## 1. GitHub 仓库设置

### 1.1 创建仓库

访问 https://github.com/new 创建新仓库：

```
仓库名称: sprint-agent
可见性: Public（或 Private）
初始化: 不勾选 README（已有本地代码）
```

### 1.2 关联本地仓库

```bash
# 进入项目根目录
cd sprint-agent

# 初始化 Git（若尚未初始化）
git init

# 添加远程仓库
git remote add origin https://github.com/ToxicSam/sprint-agent.git

# 验证远程仓库
git remote -v
```

### 1.3 配置 .gitignore

确保以下文件不被提交：

```
# frontend/.gitignore
node_modules/
dist/
.env
.env.local
*.log

# backend/.gitignore
__pycache__/
*.pyc
*.pyo
.venv/
venv/
*.db
*.sqlite3
.env

# 根目录 .gitignore
.DS_Store
*.swp
*.swo
.idea/
.vscode/
```

---

## 2. 推送代码到 GitHub

### 2.1 首次推送

```bash
# 添加所有文件
git add .

# 提交初始版本
git commit -m "feat: Sprint Agent v2.0 初始版本

- React 19 + TypeScript + Vite 前端
- Python + FastAPI + SQLite 后端
- Zero-Mock 数据架构
- Docker Compose 全栈部署
- 设置页支持 JSON/CSV/Markdown 导入导出"

# 推送到 main 分支
git branch -M main
git push -u origin main
```

### 2.2 后续更新推送

```bash
# 日常开发推送流程
git add .
git commit -m "type: 简短描述"
git push origin main
```

提交信息规范：

| 前缀 | 含义 | 示例 |
|------|------|------|
| `feat:` | 新功能 | `feat: 添加任务筛选功能` |
| `fix:` | 修复 Bug | `fix: 修复日期解析错误` |
| `docs:` | 文档更新 | `docs: 更新部署指南` |
| `refactor:` | 代码重构 | `refactor: 优化查询性能` |
| `chore:` | 杂项维护 | `chore: 更新依赖版本` |

---

## 3. 创建版本 Release

### 3.1 使用 GitHub CLI（推荐）

```bash
# 安装 GitHub CLI
# macOS: brew install gh
# Ubuntu: sudo apt install gh
# Windows: winget install --id GitHub.cli

# 登录
gitHub auth login

# 创建标签
git tag -a v2.0.0 -m "Sprint Agent v2.0.0 正式发布"
git push origin v2.0.0

# 创建 Release（使用说明模板）
gitHub release create v2.0.0 \
  --title "Sprint Agent v2.0.0" \
  --notes-file RELEASE_NOTES.md \
  --target main
```

### 3.2 使用 GitHub 网页

1. 访问仓库页面 -> 右侧 **Releases** 区域 -> **Create a new release**
2. 点击 **Choose a tag** -> 输入 `v2.0.0` -> **Create new tag**
3. 目标分支选择 `main`
4. Release title 填入 `Sprint Agent v2.0.0`
5. 在描述框中粘贴发布说明（见第 6 节模板）
6. 点击 **Publish release**

### 3.3 预发布版本

```bash
# 创建预发布版本
git tag -a v2.1.0-beta.1 -m "v2.1.0 Beta 1"
git push origin v2.1.0-beta.1

gitHub release create v2.1.0-beta.1 \
  --title "Sprint Agent v2.1.0 Beta 1" \
  --notes "预发布版本，请勿用于生产环境。" \
  --prerelease \
  --target main
```

---

## 4. GitHub Pages 部署

### 4.1 配置 GitHub Pages

1. 进入仓库 **Settings** -> **Pages**
2. **Source** 选择 **GitHub Actions**

### 4.2 创建工作流

创建 `.github/workflows/deploy-pages.yml`：

```yaml
name: Deploy Frontend to GitHub Pages

on:
  push:
    branches: [main]
    tags: ['v*']

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci

      - name: Build
        working-directory: ./frontend
        run: |
          echo "VITE_API_URL=${{ secrets.API_URL }}" >> .env.production
          npm run build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./frontend/dist

      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v4
```

### 4.3 配置 API 地址

在仓库 **Settings** -> **Secrets and variables** -> **Actions** 中添加：

```
Name: API_URL
Value: https://your-backend-api-domain.com
```

### 4.4 验证部署

推送代码后，在 **Actions** 标签页查看部署状态。部署完成后访问：

```
https://toxicsam.github.io/sprint-agent
```

前端线上演示地址：https://kq22uxqu5dioc.ok.kimi.link

---

## 5. Docker 镜像发布

### 5.1 构建本地镜像

```bash
# 构建后端镜像
cd backend
docker build -t toxicsam/sprint-agent-backend:v2.0.0 .
docker build -t toxicsam/sprint-agent-backend:latest .

# 构建前端镜像
cd ../frontend
docker build -t toxicsam/sprint-agent-frontend:v2.0.0 .
docker build -t toxicsam/sprint-agent-frontend:latest .
```

### 5.2 推送到 Docker Hub

```bash
# 登录
docker login

# 推送后端镜像
docker push toxicsam/sprint-agent-backend:v2.0.0
docker push toxicsam/sprint-agent-backend:latest

# 推送前端镜像
docker push toxicsam/sprint-agent-frontend:v2.0.0
docker push toxicsam/sprint-agent-frontend:latest
```

### 5.3 推送到 GitHub Container Registry

```bash
# 登录 GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u ToxicSam --password-stdin

# 打标签并推送
docker tag toxicsam/sprint-agent-backend:v2.0.0 \
  ghcr.io/toxicsam/sprint-agent-backend:v2.0.0
docker push ghcr.io/toxicsam/sprint-agent-backend:v2.0.0
```

### 5.4 使用发布镜像

```bash
# docker-compose.yml 中使用发布镜像
services:
  backend:
    image: toxicsam/sprint-agent-backend:v2.0.0
    # ...
  frontend:
    image: toxicsam/sprint-agent-frontend:v2.0.0
    # ...
```

---

## 6. 发布说明模板

创建 `RELEASE_NOTES.md` 模板文件：

```markdown
## Sprint Agent v{VERSION}

发布日期: {DATE}

### 新增功能

- 功能描述 1
- 功能描述 2

### 改进优化

- 优化描述 1
- 优化描述 2

### 问题修复

- 修复描述 1
- 修复描述 2

### 技术栈

- 前端: React {REACT_VERSION} + TypeScript + Vite
- 后端: Python {PYTHON_VERSION} + FastAPI + SQLite
- 部署: Docker Compose

### 升级说明

```bash
docker compose pull
docker compose up -d
```

### 完整变更日志

查看 [CHANGELOG.md](CHANGELOG.md)
```

---

## 7. 版本号规则

采用 **语义化版本控制 2.0.0**（SemVer）：

```
格式: MAJOR.MINOR.PATCH

MAJOR — 主版本号：不兼容的 API 变更
MINOR — 次版本号：向下兼容的功能新增
PATCH — 修订号：向下兼容的问题修复
```

版本示例：

| 版本 | 含义 | 场景 |
|------|------|------|
| `2.0.0` | 正式发布 | v2.0 首个稳定版本 |
| `2.1.0` | 功能更新 | 新增导出功能 |
| `2.1.1` | 问题修复 | 修复导出 CSV 编码问题 |
| `2.2.0-beta.1` | 预发布 | v2.2.0 第一个测试版 |

---

## 8. 标签与变更日志

### 8.1 创建标签

```bash
# 创建带注释的标签
git tag -a v2.0.0 -m "Sprint Agent v2.0.0 正式发布"

# 推送标签到远程
git push origin v2.0.0

# 推送所有标签
git push origin --tags
```

### 8.2 维护 CHANGELOG.md

每次发布前更新 `CHANGELOG.md`：

```markdown
# 变更日志

所有版本变更记录。

格式基于 [Keep a Changelog](https://keepachangelog.com/)。

## [2.0.0] - 2025-05-15

### Added
- Zero-Mock 数据架构
- 设置页数据导入导出
- Docker Compose 全栈部署
- GitHub Actions 自动部署

### Changed
- 升级至 React 19
- 升级至 Python 3.12

### Fixed
- 日期时区解析问题
- 大数据量导出超时

## [1.0.0] - 2025-03-01

### Added
- 初始版本发布
- 基础看板功能
- 每日站会记录
```

### 8.3 版本发布检查清单

发布前确认以下事项：

- [ ] 代码已通过全部测试
- [ ] 版本号已更新（package.json, main.py 等）
- [ ] CHANGELOG.md 已更新
- [ ] 文档已同步更新
- [ ] init.json 示例数据已验证
- [ ] Docker 镜像构建成功
- [ ] GitHub Actions 工作流通过
- [ ] 标签已创建并推送
- [ ] Release 说明已撰写
- [ ] Docker 镜像已推送

# Sprint Agent

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/fastapi-0.104+-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/docker-ready-blue.svg" alt="Docker">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License">
</p>

**Sprint Agent** 是一个团队敏捷迭代自动化管理系统，承载 Planning → Daily Standup → Retro → 半年自评全流程，内嵌 Interview/Grill 机制主动挖掘事迹。

## ✨ 核心特性

- **🎯 Trello 风格看板** — 拖拽式任务管理，实时状态更新
- **📊 全流程覆盖** — Sprint 规划、日报、回顾、自评一站式
- **🤖 Interview/Grill** — 自动追问机制，主动挖掘团队事迹
- **📡 REST API** — 完整的 API 接口，支持外部集成
- **🐳 一键部署** — Docker + docker-compose，5 分钟启动
- **💾 数据持久化** — JSON 文件存储，自动备份，随时可迁移

## 🚀 快速开始

### 方式一：Docker 一键部署（推荐）

```bash
# 克隆仓库
git clone https://github.com/yourusername/sprint-agent.git
cd sprint-agent

# 一键部署
./scripts/deploy.sh
```

访问 http://localhost:8080 即可使用看板。

### 方式二：手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/sprint-agent.git
cd sprint-agent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python -m api.server
```

### 方式三：Docker Compose

```bash
docker-compose up -d
```

## 📖 详细文档

- [部署指南](docs/DEPLOY.md) — Docker、源码、云服务部署
- [使用手册](docs/USAGE.md) — CLI 命令、API 接口、看板操作
- [架构说明](docs/ARCHITECTURE.md) — 系统设计、数据模型、扩展开发

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 后端 API | FastAPI + Python 3.12 |
| 前端看板 | Vanilla JS + HTML5 Drag & Drop |
| 数据存储 | JSON 文件 + 自动备份 |
| 容器化 | Docker + docker-compose |
| 部署 | 一键 Shell 脚本 |

## 📁 项目结构

```
sprint-agent/
├── api/                  # FastAPI 服务
│   ├── server.py         # API 入口
│   └── agent_api.py      # 业务 API 层
├── web/                  # 前端看板
│   └── index.html        # Trello 风格看板
├── models/               # 数据模型
│   ├── sprint.py
│   ├── task.py
│   ├── member.py
│   └── ...
├── engines/              # 业务引擎
│   ├── planning_engine.py
│   ├── standup_engine.py
│   ├── retro_engine.py
│   └── ...
├── parsers/              # 命令解析
│   ├── command_parser.py
│   └── nlp_engine.py
├── storage/              # 持久化
│   └── persistence_manager.py
├── data/                 # 数据目录（运行时生成）
│   ├── active/
│   ├── sprints/
│   ├── story_pool/
│   ├── retro/
│   └── assessments/
├── scripts/              # 部署脚本
│   └── deploy.sh
├── docs/                 # 文档
│   ├── DEPLOY.md
│   ├── USAGE.md
│   └── ARCHITECTURE.md
├── requirements.txt      # Python 依赖
├── docker-compose.yml    # Docker Compose 配置
├── Dockerfile            # Docker 镜像定义
└── README.md             # 本文件
```

## 🖼️ 界面预览

### Trello 风格看板

- **四列看板**：📋 未开始 → 🏃 进行中 → ✅ 已完成 → ⏸️ 挂起
- **拖拽移动**：卡片直接拖到别的列，自动更新状态
- **新建任务**：点击「➕ 新建任务」按钮
- **卡片详情**：点击卡片查看进度、日报记录、阻塞信息

### 统计栏

- 成员数、任务数、完成数
- 预估/投入工时、阻塞数、完成率

## 📡 API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sprint` | 获取当前 Sprint |
| GET | `/api/board` | 获取看板数据 |
| POST | `/api/sprint` | 创建 Sprint |
| POST | `/api/members` | 添加成员 |
| POST | `/api/tasks` | 添加任务 |
| PATCH | `/api/tasks/{id}/status` | 更新任务状态 |
| POST | `/api/daily-log` | 添加日报 |
| GET | `/api/dashboard` | 团队看板文本 |
| POST | `/api/retro` | 生成 Retro 报告 |
| POST | `/api/assessment` | 生成自评表 |

完整 API 文档启动后访问：http://localhost:8080/docs

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 License

MIT License

---

<p align="center">
  Made with ❤️ for Agile Teams
</p>

# Sprint Agent v2.0 — 系统架构文档

> 版本：v2.0  
> 日期：2025-07-31  
> 状态：正式发布  
> 作者：Sprint Agent Team

---

## 目录

1. [系统架构概览](#1-系统架构概览)
2. [技术栈](#2-技术栈)
3. [前端架构](#3-前端架构)
4. [后端架构](#4-后端架构)
5. [数据流设计](#5-数据流设计)
6. [安全设计](#6-安全设计)
7. [性能优化](#7-性能优化)
8. [扩展点](#8-扩展点)

---

## 1. 系统架构概览

### 1.1 整体架构图

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           Sprint Agent v2.0                              │
├──────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────┐    ┌────────────────────────────────┐  │
│  │        前端 (Frontend)        │    │        后端 (Backend)           │  │
│  │   React 19 + TypeScript      │    │    Python + FastAPI             │  │
│  │   Vite + Tailwind + shadcn   │◄──►│    SQLAlchemy 2.0 + SQLite      │  │
│  │                              │    │                                │  │
│  │  ┌────────┐ ┌──────────┐    │    │  ┌────────┐  ┌──────────────┐ │  │
│  │  │ Layout │ │  Pages   │    │    │  │ Router │  │  API Layer   │ │  │
│  │  │ Shell  │ │Dashboard │    │    │  │        │  │  (Routers)   │ │  │
│  │  │        │ │Planning  │    │    │  │ /sprint│  │              │ │  │
│  │  │ TopNav │ │Standup   │    │    │  │ /tasks │  │ /api/sprint  │ │  │
│  │  │Sidebar │ │Retro     │    │    │  │ /retro │  │ /api/tasks   │ │  │
│  │  │AgentP. │ │Settings  │    │    │  │ /agent │  │ /api/members │ │  │
│  │  │BottomB.│ │Login     │    │    │  │ ...    │  │ /api/standup │ │  │
│  │  └────────┘ └──────────┘    │    │  └────────┘  │ /api/retro   │ │  │
│  │         │                    │    │              │ /api/agent   │ │  │
│  │         ▼                    │    │              │ /api/settings│ │  │
│  │  ┌──────────────────┐        │    │  ┌────────┐  └──────────────┘ │  │
│  │  │   Zustand Store   │        │    │  │Service │                  │  │
│  │  │                  │        │    │  │ Layer  │                  │  │
│  │  │  useSprintStore  │        │    │  │        │  ┌────────────┐  │  │
│  │  │  useTaskStore    │        │    │  │ Sprint │  │ Zero-Mock  │  │  │
│  │  │  useMemberStore  │        │    │  │ Task   │  │   Import   │  │  │
│  │  │  useStandupStore │        │    │  │ Member │  │            │  │  │
│  │  │  useRetroStore   │        │    │  │ Standup│  │ init.json  │  │  │
│  │  │  useUIStore      │        │    │  │ Retro  │  │  ────────► │  │  │
│  │  │  useAgentStore   │        │    │  │ Agent  │  │  SQLite    │  │  │
│  │  └──────────────────┘        │    │  └────────┘  └────────────┘  │  │
│  │         │                    │    │              │                │  │
│  │         ▼                    │    │              ▼                │  │
│  │  ┌──────────────────┐        │    │  ┌──────────────────────┐      │  │
│  │  │    API Client     │        │    │  │  Data Access Layer   │      │  │
│  │  │                   │        │    │  │  (SQLAlchemy ORM)    │      │  │
│  │  │  fetch wrapper    │◄───────┼────┼──│  Models + Sessions   │      │  │
│  │  │  domain clients   │        │    │  └──────────────────────┘      │  │
│  │  └──────────────────┘        │    │              │                  │  │
│  └──────────────────────────────┘    │              ▼                  │  │
│                                       │  ┌──────────────────────┐       │  │
│                                       │  │    SQLite Database    │       │  │
│                                       │  │                       │       │  │
│                                       │  │ Sprint│Member│Task    │       │  │
│                                       │  │ DailyLog│Retro│Rating │       │  │
│                                       │  │ AgentMsg│Config        │       │  │
│                                       │  └──────────────────────┘       │  │
│                                       └───────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

### 1.2 部署架构

```
┌─────────────┐      HTTP/REST      ┌──────────────────┐
│   Browser   │ ◄────────────────►  │  FastAPI Server  │
│  (SPA)      │   (Fetch API)       │   Uvicorn        │
│             │                     │                  │
│ HashRouter  │                     │  - API Routers   │
│ manages     │                     │  - Service Layer │
│ all routes  │                     │  - ORM Models    │
│             │                     │  - SQLite file   │
└─────────────┘                     └──────────────────┘
```

---

## 2. 技术栈

### 2.1 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 19.x | UI 框架 |
| TypeScript | 5.6+ | 类型系统 |
| Vite | 6.x | 构建工具与开发服务器 |
| Tailwind CSS | 3.4+ | 原子化 CSS 样式 |
| shadcn/ui | latest | UI 组件基础库 |
| @dnd-kit | 6.x | 拖拽交互（看板） |
| TanStack Table | 8.x | 表格组件（Standup 批量编辑） |
| Zustand | 4.x | 状态管理 |
| Lucide React | latest | 图标库 |
| date-fns | 3.x | 日期工具函数 |
| react-hook-form | 7.x | 表单处理 |
| zod | 3.x | 运行时数据校验 |

### 2.2 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.12+ | 运行环境 |
| FastAPI | 0.115+ | Web 框架 |
| SQLAlchemy | 2.0+ | ORM 数据访问层 |
| Pydantic | v2 | 数据模型与校验 |
| SQLite | 3.40+ | 嵌入式数据库 |
| Uvicorn | 0.34+ | ASGI 服务器 |
| python-multipart | latest | 文件上传处理 |
| email-validator | latest | 邮箱格式校验 |

---

## 3. 前端架构

### 3.1 组件层级树

```
App.tsx (HashRouter)
│
├── Layout.tsx                          # 主布局壳
│   ├── TopNav.tsx                      # 顶部导航栏 (48px)
│   │   ├── SprintSelector.tsx          # Sprint 下拉选择
│   │   ├── PageTitle.tsx               # 当前页面标题
│   │   └── UserMenu.tsx                # 用户菜单（头像/设置/退出）
│   │
│   ├── Sidebar.tsx                     # 可折叠侧边栏 (52px→200px)
│   │   ├── SidebarToggle.tsx           # 展开/收起按钮
│   │   ├── NavItem[]                   # 导航项列表
│   │   │   ├── NavItem (Dashboard)     # / 首页
│   │   │   ├── NavItem (Planning)      # /planning 规划
│   │   │   ├── NavItem (Standup)       # /standup 站会
│   │   │   ├── NavItem (Retro)         # /retro 回顾
│   │   │   └── NavItem (Settings)      # /settings 设置
│   │   └── ThemeToggle.tsx             # 亮色/暗色切换
│   │
│   ├── MainContent.tsx                 # 主内容区域 (flex-1)
│   │   ├── DashboardPage.tsx           # 看板页面
│   │   │   ├── SprintHeader.tsx        # Sprint 信息头
│   │   │   ├── KanbanBoard.tsx         # 四列看板容器
│   │   │   │   ├── KanbanColumn.tsx    # 单列 (todo/progress/done/paused)
│   │   │   │   │   ├── SortableContext  # dnd-kit 排序上下文
│   │   │   │   │   ├── TaskCard.tsx    # 任务卡片 (Sortable)
│   │   │   │   │   └── InlineTaskCreator.tsx  # 行内新建任务
│   │   │   │   └── DragOverlay.tsx     # 拖拽浮层
│   │   │   ├── TaskDetailSlideOver.tsx # 任务详情滑出面板
│   │   │   └── BurndownMiniChart.tsx   # 迷你燃尽图
│   │   │
│   │   ├── PlanningPage.tsx            # 规划页面
│   │   │   ├── SprintForm.tsx          # Sprint 基本信息表单
│   │   │   ├── MemberTable.tsx         # 团队成员表格 (inline 编辑)
│   │   │   ├── TemplateSelector.tsx    # Sprint 模板预设
│   │   │   └── CapacitySummary.tsx     # 容量汇总卡片
│   │   │
│   │   ├── StandupPage.tsx             # 站会页面
│   │   │   ├── TabNavigation.tsx       # 成员标签切换
│   │   │   ├── StandupTable.tsx        # TanStack Table 批量编辑
│   │   │   ├── YesterdayFillButton.tsx # "填充昨日" 按钮
│   │   │   └── SubmitToolbar.tsx       # 提交工具栏 (Ctrl+Enter)
│   │   │
│   │   ├── RetroPage.tsx               # 回顾页面
│   │   │   ├── RatingSection.tsx       # 四维度评分区
│   │   │   │   └── RatingCard.tsx      # 单维度评分卡片 (1-5星)
│   │   │   ├── FeedbackTabs.tsx        # 三标签反馈 (liked/disliked/action)
│   │   │   │   └── FeedbackList.tsx    # 反馈列表
│   │   │   ├── TemplateSelector.tsx    # 回顾模板选择器
│   │   │   └── SummaryPanel.tsx        # 自动生成的总结面板
│   │   │
│   │   ├── SettingsPage.tsx            # 设置页面
│   │   │   ├── GeneralSettings.tsx     # 通用设置 Tab
│   │   │   ├── TeamSettings.tsx        # 团队设置 Tab
│   │   │   ├── DataSettings.tsx        # 数据导入/导出 Tab
│   │   │   ├── AgentSettings.tsx       # 智能体设置 Tab
│   │   │   └── AppearanceSettings.tsx  # 外观设置 Tab
│   │   │
│   │   └── LoginPage.tsx               # 登录页面
│   │
│   ├── AgentPanel.tsx                  # 智能体面板 (320px, docked)
│   │   ├── ChatMessageList.tsx         # 消息历史列表
│   │   ├── ChatInput.tsx               # 输入框 (支持 / 命令)
│   │   ├── SlashCommandMenu.tsx        # 斜杠命令补全菜单
│   │   ├── QuickActionBar.tsx          # 快捷操作按钮栏
│   │   └── TypingIndicator.tsx         # 输入中指示器
│   │
│   └── BottomBar.tsx                   # 底部状态栏 (32px)
│       ├── SprintStatusBadge.tsx       # Sprint 状态徽章
│       ├── LastSyncIndicator.tsx       # 上次同步时间
│       └── AgentQuickToggle.tsx        # 快速打开 Agent 面板
│
└── Global overlays (Toast, Confirm Dialog, etc.)
```

### 3.2 状态管理 (Zustand Store 结构)

```typescript
// Store 分层设计 — 每个业务域独立 Store

┌────────────────────────────────────────────────────────────────┐
│                    useUIStore（UI 状态）                         │
├────────────────────────────────────────────────────────────────┤
│  state: {                                                      │
│    sidebarCollapsed: boolean;       // 侧边栏折叠状态            │
│    agentPanelOpen: boolean;         // Agent 面板开关            │
│    theme: 'light' | 'dark';         // 当前主题                  │
│    activePage: string;              // 当前页面标识              │
│    toasts: Toast[];                 // 全局 Toast 队列           │
│    slideOver: { open, content } | null;  // 滑出面板状态        │
│  }                                                              │
│  actions:                                                       │
│    toggleSidebar(), toggleAgentPanel(), setTheme(),            │
│    addToast(), removeToast(), openSlideOver(), closeSlideOver() │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                   useSprintStore（Sprint 状态）                  │
├────────────────────────────────────────────────────────────────┤
│  state: {                                                      │
│    sprints: Sprint[];               // 所有 Sprint 列表          │
│    activeSprintId: number | null;   // 当前激活 Sprint           │
│    activeSprint: Sprint | null;     // 当前 Sprint 详情          │
│    stats: SprintStats | null;       // Sprint 统计数据           │
│    loading: boolean;                // 加载状态                  │
│  }                                                              │
│  actions:                                                       │
│    fetchSprints(), createSprint(), updateSprint(),             │
│    deleteSprint(), setActiveSprint(), fetchStats()             │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                    useTaskStore（任务状态）                       │
├────────────────────────────────────────────────────────────────┤
│  state: {                                                      │
│    tasks: Task[];                   // 当前 Sprint 的任务列表    │
│    taskMap: Map<number, Task>;      // ID → Task 快速索引       │
│    columns: {                                                   │
│      todo: Task[]; progress: Task[]; done: Task[]; paused: Task[] │
│    };                                                           │
│    draggingTaskId: number | null;   // 正在拖拽的任务 ID         │
│  }                                                              │
│  actions:                                                       │
│    fetchTasks(), createTask(), updateTask(), deleteTask(),     │
│    moveTask(), bulkUpdateTasks(), reorderTasks()               │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                   useMemberStore（成员状态）                      │
├────────────────────────────────────────────────────────────────┤
│  state: {                                                      │
│    members: Member[];               // 所有团队成员              │
│    memberMap: Map<number, Member>;  // ID → Member 快速索引    │
│  }                                                              │
│  actions: fetchMembers(), createMember(), updateMember(),      │
│           deleteMember()                                        │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                   useStandupStore（站会状态）                     │
├────────────────────────────────────────────────────────────────┤
│  state: {                                                      │
│    dailyLogs: DailyLog[];           // 当日日志列表              │
│    yesterdayLogs: DailyLog[];       // 昨日日志（填充用）        │
│    activeMemberTab: number;         // 当前编辑的成员 Tab        │
│    unsavedChanges: boolean;         // 未保存变更标记            │
│  }                                                              │
│  actions: fetchLogs(), submitLog(), submitBatch(),             │
│           fillFromYesterday(), setActiveTab()                   │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                    useRetroStore（回顾状态）                      │
├────────────────────────────────────────────────────────────────┤
│  state: {                                                      │
│    items: RetroItem[];              // 反馈条目列表              │
│    ratings: RetroRating[];          // 四维度评分                │
│    activeCategory: 'liked'|'disliked'|'action';                  │
│    report: RetroReport | null;      // 自动生成的回顾报告        │
│  }                                                              │
│  actions: fetchItems(), addItem(), voteItem(),                 │
│           submitRatings(), generateReport()                     │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                   useAgentStore（智能体状态）                      │
├────────────────────────────────────────────────────────────────┤
│  state: {                                                      │
│    messages: AgentMessage[];        // 对话历史                  │
│    isTyping: boolean;               // 是否正在输入              │
│    context: AgentContext | null;    // 当前上下文                │
│    suggestedActions: string[];      // 建议操作列表              │
│  }                                                              │
│  actions: sendMessage(), executeAction(), fetchHistory(),      │
│           fetchContext(), clearChat()                           │
└────────────────────────────────────────────────────────────────┘
```

### 3.3 路由设计 (HashRouter)

```typescript
// HashRouter 路由表 — 所有路由为客户端路由，无需服务端配置

┌──────────────┬────────────────────┬──────────────┬──────────────────────────┐
│    路径       │      页面组件       │     名称      │        说明              │
├──────────────┼────────────────────┼──────────────┼──────────────────────────┤
│      /       │ DashboardPage      │ 看板          │ 四列 Kanban + 拖拽        │
│  /planning   │ PlanningPage       │ 规划          │ Sprint 表单 + 成员管理    │
│  /standup    │ StandupPage        │ 站会          │ 批量编辑日报              │
│  /retro      │ RetroPage          │ 回顾          │ 评分 + 反馈 + 报告        │
│  /settings   │ SettingsPage       │ 设置          │ 5 Tab 配置页面            │
│  /login      │ LoginPage          │ 登录          │ 用户认证入口              │
└──────────────┴────────────────────┴──────────────┴──────────────────────────┘

// 路由守卫：未登录自动重定向至 /login
// 激活路由的导航项在 Sidebar 中高亮显示
```

### 3.4 API 层设计

```
┌──────────────────────────────────────────────────────────────────┐
│                      API Layer                                    │
├──────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               client.ts (Fetch 封装)                      │   │
│  │                                                          │   │
│  │  baseUrl: '/api'                                         │   │
│  │  headers: { 'Content-Type': 'application/json' }        │   │
│  │                                                          │   │
│  │  request<T>(method, path, body?)                         │   │
│  │    → fetch(baseUrl + path, { method, body })            │   │
│  │    → if !ok: throw ApiError(status, message)             │   │
│  │    → return response.json() as T                         │   │
│  │                                                          │   │
│  │  get<T>(path)     → request('GET', path)                │   │
│  │  post<T>(path, b) → request('POST', path, b)            │   │
│  │  put<T>(path, b)  → request('PUT', path, b)             │   │
│  │  del<T>(path)     → request('DELETE', path)             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                    │
│           ┌──────────────────┼──────────────────┐                 │
│           ▼                  ▼                  ▼                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │  sprintApi   │ │   taskApi    │ │  memberApi   │              │
│  │              │ │              │ │              │              │
│  │ getAll()     │ │ getAll(q?)   │ │ getAll()     │              │
│  │ create(d)    │ │ create(d)    │ │ create(d)    │              │
│  │ getById(id)  │ │ update(id,d) │ │ update(id,d) │              │
│  │ getStats(id) │ │ remove(id)   │ │ remove(id)   │              │
│  └──────────────┘ │ move(id,d)   │ └──────────────┘              │
│                   │ bulk(d)      │                                │
│                   └──────────────┘                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │  standupApi  │ │   retroApi   │ │  agentApi    │              │
│  │              │ │              │ │              │              │
│  │ getAll()     │ │ getItems()   │ │ sendMsg(d)   │              │
│  │ create(d)    │ │ addItem(d)   │ │ getHistory() │              │
│  │ batch(d)     │ │ vote(id)     │ │ execute(d)   │              │
│  │ yesterday()  │ │ rate(d)      │ │ getContext() │              │
│  │              │ │ getReport(id)│ │              │              │
│  └──────────────┘ └──────────────┘ └──────────────┘              │
│  ┌──────────────┐                                                │
│  │ settingsApi  │                                                │
│  │ getAll()     │                                                │
│  │ update(d)    │                                                │
│  │ import(f)    │                                                │
│  │ export()     │                                                │
│  │ reset()      │                                                │
│  └──────────────┘                                                │
└──────────────────────────────────────────────────────────────────┘
```

### 3.5 主题系统

```
┌──────────────────────────────────────────────────────────────────┐
│                     主题系统架构                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Tailwind CSS 暗黑模式: class 策略                               │
│   ────────────────────────────────────────                       │
│   tailwind.config.js: darkMode: 'class'                          │
│                                                                  │
│   html.dark → 全局暗黑模式切换                                    │
│                                                                  │
│   CSS Variables 定义:                                            │
│   :root {                                                        │
│     --background: 0 0% 100%;          /* 亮色背景 */              │
│     --foreground: 240 10% 3.9%;       /* 亮色文字 */              │
│     --card: 0 0% 100%;                                           │
│     --primary: 240 5.9% 10%;                                     │
│     ...                                                          │
│   }                                                              │
│   .dark {                                                        │
│     --background: 240 10% 3.9%;       /* 暗色背景 */              │
│     --foreground: 0 0% 98%;           /* 暗色文字 */              │
│     --card: 240 10% 3.9%;                                        │
│     --primary: 0 0% 98%;                                         │
│     ...                                                          │
│   }                                                              │
│                                                                  │
│   shadcn/ui 组件自动适配 CSS Variables                            │
│                                                                  │
│   主题持久化: Zustand persist 中间件 → localStorage               │
│   初始化: 读取 localStorage → 设置 html class                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. 后端架构

### 4.1 分层架构图

```
┌──────────────────────────────────────────────────────────────────┐
│                      后端分层架构                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    Presentation Layer                       │  │
│  │                   (API 路由层 / Routers)                    │  │
│  │                                                            │  │
│  │  sprint.py  │  tasks.py  │  members.py  │  standup.py     │  │
│  │  retro.py   │  agent.py  │  settings.py                   │  │
│  │                                                            │  │
│  │  - 请求参数解析 (Query/Path/Body)                          │  │
│  │  - 输入校验 (Pydantic schemas)                             │  │
│  │  - 响应格式化                                              │  │
│  │  - HTTP 状态码管理                                         │  │
│  └────────────────────────┬───────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    Service Layer                            │  │
│  │                   (业务逻辑层 / Services)                   │  │
│  │                                                            │  │
│  │  SprintService  │  TaskService  │  MemberService          │  │
│  │  StandupService │  RetroService │  AgentService           │  │
│  │  SettingsService                                              │  │
│  │                                                            │  │
│  │  - 核心业务规则处理                                         │  │
│  │  - 多实体事务编排                                           │  │
│  │  - 数据统计计算 (burndown, velocity)                        │  │
│  │  - Agent 上下文组装                                         │  │
│  └────────────────────────┬───────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    Data Access Layer                        │  │
│  │                   (数据访问层 / ORM)                        │  │
│  │                                                            │  │
│  │              SQLAlchemy 2.0 (Declarative Base)              │  │
│  │                                                            │  │
│  │  - Model 定义 (8 张表)                                     │  │
│  │  - CRUD 基础操作                                           │  │
│  │  - 关系映射 (relationships)                                │  │
│  │  - Session 管理                                            │  │
│  └────────────────────────┬───────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    Storage Layer                            │  │
│  │                   (存储层 / SQLite)                         │  │
│  │                                                            │  │
│  │              SQLite 文件数据库 (.db)                        │  │
│  │                                                            │  │
│  │  - 零配置部署                                              │  │
│  │  - 单文件迁移                                              │  │
│  │  - 足够支撑团队协作规模                                    │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 数据库 Schema (8 张表)

```sql
-- =============================================
-- Sprint 表 — Sprint 基本信息
-- =============================================
CREATE TABLE sprint (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(100) NOT NULL,          -- Sprint 名称
    goal            TEXT,                            -- Sprint 目标
    start_date      DATE NOT NULL,                   -- 开始日期
    end_date        DATE NOT NULL,                   -- 结束日期
    status          VARCHAR(20) DEFAULT 'active'     -- 状态: active/closed/draft
);

-- =============================================
-- Member 表 — 团队成员
-- =============================================
CREATE TABLE member (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(100) NOT NULL,          -- 成员姓名
    role            VARCHAR(20) NOT NULL,           -- 角色: sm/dev/qa/po
    capacity        FLOAT DEFAULT 1.0,              -- 容量系数 (0.0-1.0)
    avatar          VARCHAR(255)                    -- 头像 URL
);

-- =============================================
-- Task 表 — 任务卡片
-- =============================================
CREATE TABLE task (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sprint_id       INTEGER NOT NULL REFERENCES sprint(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,          -- 任务标题
    assignee_id     INTEGER REFERENCES member(id),  -- 负责人
    status          VARCHAR(20) DEFAULT 'todo',     -- 状态: todo/progress/done/paused
    priority        INTEGER DEFAULT 5,              -- 优先级 1-10
    story_points    INTEGER DEFAULT 0,              -- 故事点
    blocked_by      INTEGER REFERENCES task(id),    -- 被哪个任务阻塞
    description     TEXT                            -- 详细描述
);

-- =============================================
-- DailyLog 表 — 每日站会记录
-- =============================================
CREATE TABLE daily_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sprint_id       INTEGER NOT NULL REFERENCES sprint(id) ON DELETE CASCADE,
    member_id       INTEGER NOT NULL REFERENCES member(id) ON DELETE CASCADE,
    date            DATE NOT NULL,                   -- 记录日期
    completed       TEXT,                            -- 昨日完成内容
    planned         TEXT,                            -- 今日计划
    blockers        TEXT,                            -- 遇到的阻塞
    hours_spent     FLOAT DEFAULT 0.0                -- 昨日投入工时
);

-- =============================================
-- Retro 表 — 回顾反馈条目
-- =============================================
CREATE TABLE retro (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sprint_id       INTEGER NOT NULL REFERENCES sprint(id) ON DELETE CASCADE,
    category        VARCHAR(20) NOT NULL,           -- 类别: liked/disliked/action
    item            TEXT NOT NULL,                   -- 反馈内容
    votes           INTEGER DEFAULT 0                -- 投票数
);

-- =============================================
-- RetroRating 表 — 回顾维度评分
-- =============================================
CREATE TABLE retro_rating (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sprint_id       INTEGER NOT NULL REFERENCES sprint(id) ON DELETE CASCADE,
    dimension       VARCHAR(20) NOT NULL,           -- 维度: velocity/quality/teamwork/process
    score           INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5)  -- 评分 1-5
);

-- =============================================
-- AgentMessage 表 — 智能体对话记录
-- =============================================
CREATE TABLE agent_message (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    role            VARCHAR(20) NOT NULL,           -- 角色: user/agent/system
    content         TEXT NOT NULL,                   -- 消息内容
    context         TEXT,                            -- 上下文 JSON (entities, page)
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP  -- 创建时间
);

-- =============================================
-- Config 表 — 系统配置键值对
-- =============================================
CREATE TABLE config (
    key             VARCHAR(100) PRIMARY KEY,       -- 配置键
    value           TEXT                            -- 配置值 (JSON 字符串)
);
```

### 4.3 实体关系图 (ERD)

```
┌──────────┐       ┌──────────┐       ┌──────────┐
│  Sprint  │◄──────┤   Task   │       │  Member  │
│          │ 1:N   │          │ N:1   │          │
│ id (PK)  │       │ id (PK)  │──────►│ id (PK)  │
│ name     │       │ sprint_id│       │ name     │
│ goal     │       │ assignee├───────┤ role     │
│ status   │       │ status   │       │ capacity │
└─────┬────┘       └────┬─────┘       └────┬─────┘
      │                 │                  │
      │ N:1             │ 1:1 (self-ref)   │
      │                 │ blocked_by       │
      ▼                 ▼                  │
┌──────────┐       ┌──────────┐            │
│ DailyLog │       │  Task    │            │
│          │       │ (self)   │            │
│ id (PK)  │       └──────────┘            │
│ sprint_id│                               │
│ member_id├───────────────────────────────┘
└──────────┘

┌──────────┐       ┌────────────┐
│  Sprint  │◄──────┤   Retro    │
│          │ 1:N   │            │
└──────────┘       │ id (PK)    │
                   │ category   │
                   │ item/votes │
                   └────────────┘

┌──────────┐       ┌────────────┐
│  Sprint  │◄──────┤RetroRating │
│          │ 1:N   │            │
└──────────┘       │ dimension  │
                   │ score 1-5  │
                   └────────────┘

┌────────────────┐    ┌──────────┐
│  AgentMessage  │    │  Config  │
│                │    │          │
│ id (PK)        │    │ key (PK) │
│ role/content   │    │ value    │
│ context (JSON) │    └──────────┘
│ created_at     │
└────────────────┘
```

### 4.4 API 路由结构

```
/api
│
├── /sprint
│   ├── GET    /                  → 获取所有 Sprint 列表
│   ├── POST   /                  → 创建新 Sprint
│   └── GET    /{id}/stats        → 获取 Sprint 统计数据 (burndown/velocity)
│
├── /tasks
│   ├── GET    /                  → 获取任务列表 (支持 sprint_id 过滤)
│   ├── POST   /                  → 创建任务
│   ├── PUT    /{id}              → 更新任务
│   ├── DELETE /{id}              → 删除任务
│   ├── POST   /{id}/move         → 移动任务状态/排序
│   └── POST   /bulk              → 批量操作任务
│
├── /members
│   ├── GET    /                  → 获取所有成员
│   ├── POST   /                  → 创建成员
│   ├── PUT    /{id}              → 更新成员
│   └── DELETE /{id}              → 删除成员
│
├── /standup
│   ├── GET    /                  → 获取当日日报列表
│   ├── POST   /                  → 提交日报
│   ├── POST   /batch             → 批量提交日报
│   └── GET    /yesterday         → 获取昨日日报 (填充用)
│
├── /retro
│   ├── GET    /                  → 获取回顾反馈条目
│   ├── POST   /                  → 添加反馈条目
│   ├── POST   /vote              → 投票
│   ├── POST   /rate              → 提交维度评分
│   └── GET    /{id}/report       → 获取自动生成的回顾报告
│
├── /agent
│   ├── POST   /message           → 发送消息给智能体
│   ├── GET    /history           → 获取对话历史
│   ├── POST   /action            → 执行智能体操作
│   └── GET    /context           → 获取当前上下文快照
│
└── /settings
    ├── GET    /                  → 获取所有配置项
    ├── PUT    /                  → 更新配置项
    ├── POST   /import            → 导入数据 (JSON 文件)
    ├── GET    /export            → 导出数据
    ├── POST   /reset             → 重置数据库
    └── GET    /health            → 健康检查
```

### 4.5 Zero-Mock 数据导入机制

```
┌──────────────────────────────────────────────────────────────────┐
│                    Zero-Mock 数据导入机制                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  后端启动流程:                                                    │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────────────┐  │
│  │  启动    │───►│ 检查 DB  │───►│ 表是否为空?              │  │
│  │  Uvicorn │    │  存在?   │    │                          │  │
│  └──────────┘    └──────────┘    └────────────┬─────────────┘  │
│                                                │                │
│                               ┌─ 是 ───────────┘                │
│                               ▼                                 │
│                     ┌──────────────────┐                        │
│                     │  读取 init.json  │                        │
│                     │  (数据目录)      │                        │
│                     └────────┬─────────┘                        │
│                              │                                  │
│                              ▼                                  │
│                     ┌──────────────────┐                        │
│                     │  解析 JSON 数据  │                        │
│                     │  按表顺序插入    │                        │
│                     │  Sprint → Member │                        │
│                     │  → Task → Config │                        │
│                     └──────────────────┘                        │
│                              │                                  │
│                               ── 否 ──► 跳过导入，正常启动       │
│                                                                  │
│  ─────────────────────────────────────────────────────────────   │
│                                                                  │
│  init.json 结构:                                                  │
│  {                                                               │
│    "sprints": [...],     # 预置 Sprint 数据                     │
│    "members": [...],     # 预置团队成员                          │
│    "tasks": [...],       # 预置任务 (可选)                       │
│    "config": {...}       # 默认配置项                            │
│  }                                                               │
│                                                                  │
│  核心原则:                                                        │
│  1. init.json 是正式数据文件，不是 mock                          │
│  2. 前端代码中绝不包含任何 mock 数据                              │
│  3. 前端所有数据必须通过 API 获取                                 │
│  4. 导入仅在空库时执行一次，不会覆盖已有数据                      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 5. 数据流设计

### 5.1 Sprint 创建流程

```
用户操作: Planning 页面填写 Sprint 表单
    │
    ▼
┌──────────────────────┐
│  SprintForm.tsx      │
│  (react-hook-form)   │
│  + zod 校验          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐    校验失败     ┌──────────────┐
│  zod schema 校验      │──────────────►│  显示错误提示  │
│  (name, date range)  │               └──────────────┘
└──────────┬───────────┘
           │ 校验通过
           ▼
┌──────────────────────┐
│  useSprintStore.     │
│  createSprint(data)  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  sprintApi.create()  │
│  POST /api/sprint    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Backend:            │
│  SprintRouter POST   │
│  → SprintService     │
│  → SQLAlchemy insert │
│  → commit()          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐    失败     ┌──────────────────┐
│  返回 201 + Sprint   │───────────►│ 显示 Toast 错误   │
│  对象                │            └──────────────────┘
└──────────┬───────────┘
           │ 成功
           ▼
┌──────────────────────┐
│  Store 更新本地列表  │
│  sprints.push(new)   │
│  activeSprint = new  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Toast 提示创建成功   │
│  自动导航至 Dashboard │
└──────────────────────┘
```

### 5.2 任务生命周期流程

```
┌──────────────────────────────────────────────────────────────────┐
│                    任务生命周期状态机                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  创建                        拖拽                 完成           │
│  ┌─────┐    ┌──────┐    ┌───────┐    ┌──────┐    ┌─────┐      │
│  │新建 │───►│ todo │───►│progress│───►│ done │    │归档 │      │
│  │任务 │    │ 待办 │    │ 进行中 │    │ 完成 │───►│     │      │
│  └─────┘    └──┬───┘    └───┬───┘    └──┬───┘    └─────┘      │
│                │             │            │                      │
│                │             │            │                      │
│                ▼             ▼            │                      │
│             ┌──────┐    ┌──────┐         │                      │
│             │paused│◄───┘paused│◄────────┘                      │
│             │ 暂停 │    │ 暂停 │                                 │
│             └──┬───┘    └──────┘                                 │
│                │                                                  │
│                └────────────────────────────────► 恢复至原状态      │
│                                                                  │
│  创建: InlineTaskCreator → POST /api/tasks                      │
│  拖拽: @dnd-kit → moveTask() → POST /api/tasks/{id}/move        │
│  暂停: TaskCard 菜单 → PUT /api/tasks/{id}                      │
│  编辑: TaskDetailSlideOver → PUT /api/tasks/{id}                │
│  删除: TaskCard 菜单 → DELETE /api/tasks/{id}                   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 5.3 站会提交流程

```
用户操作: Standup 页面
    │
    ├── 切换成员 Tab (TabNavigation)
    │       → useStandupStore.setActiveTab(memberId)
    │
    ├── 填写表格字段 (TanStack Table 单元格编辑)
    │       → 实时更新 local state
    │       → unsavedChanges = true
    │
    ├── 点击 "Fill from Yesterday"
    │       → GET /api/standup/yesterday
    │       → 填充昨日 completed → 今日 planned
    │
    ├── 按 Ctrl+Enter 提交 (全局快捷键监听)
    │       │
    │       ▼
    │   ┌──────────────────────────┐
    │   │ useStandupStore.         │
    │   │ submitBatch(allLogs)     │
    │   └───────────┬──────────────┘
    │               │
    │               ▼
    │   ┌──────────────────────────┐
    │   │ standupApi.batch(logs)   │
    │   │ POST /api/standup/batch  │
    │   └───────────┬──────────────┘
    │               │
    │               ▼
    │   ┌──────────────────────────┐
    │   │ Backend:                 │
    │   │ 遍历 logs → upsert       │
    │   │ 存在则更新，不存在则插入 │
    │   │ 单事务提交               │
    │   └───────────┬──────────────┘
    │               │
    │               ▼
    │   ┌──────────────────────────┐
    │   │ 返回更新后的日志列表     │
    │   │ unsavedChanges = false   │
    │   │ Toast: "提交成功"        │
    │   └──────────────────────────┘
    │
    └── 自动保存草稿 (debounce 3s)
            → localStorage 缓存
            → 页面刷新后恢复
```

### 5.4 智能体交互流程

```
用户操作: AgentPanel 中输入消息
    │
    ├── 以 "/" 开头 → 触发斜杠命令补全
    │       ├── /plan    → 发送规划上下文
    │       ├── /standup → 发送站会上下文
    │       └── /retro   → 发送回顾上下文
    │
    └── 普通消息
            │
            ▼
    ┌──────────────────────────┐
    │ ChatInput.tsx            │
    │ → useAgentStore.         │
    │   sendMessage(content)   │
    │ → 乐观更新 UI (显示消息) │
    └───────────┬──────────────┘
                │
                ▼
    ┌──────────────────────────┐
    │ agentApi.sendMsg()       │
    │ POST /api/agent/message  │
    │ 附带上下文:              │
    │ { entities, activePage } │
    └───────────┬──────────────┘
                │
                ▼
    ┌──────────────────────────┐
    │ Backend: AgentService    │
    │ 1. 解析用户意图          │
    │ 2. 查询相关实体数据      │
    │ 3. 组装上下文            │
    │ 4. 生成响应/操作         │
    └───────────┬──────────────┘
                │
                ▼
    ┌──────────────────────────┐
    │ 返回: {                  │
    │   message: AgentMessage, │
    │   actions?: QuickAction[]│
    │   navigateTo?: string    │
    │ }                        │
    └───────────┬──────────────┘
                │
                ▼
    ┌──────────────────────────┐
    │ Store 更新:              │
    │ messages.push(response)  │
    │ isTyping = false         │
    │ suggestedActions = ...   │
    │                          │
    │ 若 navigateTo 存在:      │
    │ → router.navigate(...)   │
    └──────────────────────────┘
```

---

## 6. 安全设计

### 6.1 安全策略概览

| 层面 | 策略 | 实现方式 |
|------|------|----------|
| 输入校验 | 所有请求参数校验 | Pydantic v2 schemas |
| SQL 注入 | ORM 参数化查询 | SQLAlchemy 2.0 自动转义 |
| XSS 防护 | 输出编码 | React 自动转义 + DOMPurify |
| CSRF | 同域部署 | 前后端同源，无需额外 Token |
| 文件上传 | 格式/大小限制 | python-multipart 校验 |
| 数据导出 | 权限控制 | 仅已登录用户可导出 |

### 6.2 输入校验层

```python
# Pydantic v2 Schema 示例 — Task 创建请求
class TaskCreate(BaseModel):
    sprint_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=255)
    assignee_id: int | None = Field(default=None, gt=0)
    status: Literal['todo', 'progress', 'done', 'paused'] = 'todo'
    priority: int = Field(default=5, ge=1, le=10)
    story_points: int = Field(default=0, ge=0)
    description: str = ''

    # 自定义校验
    @model_validator(mode='after')
    def validate_dates(self):
        if self.blocked_by and self.blocked_by == self.id:
            raise ValueError('任务不能阻塞自身')
        return self
```

---

## 7. 性能优化

### 7.1 前端性能

| 策略 | 实现 | 效果 |
|------|------|------|
| 组件懒加载 | React.lazy + Suspense | 首屏 < 200KB |
| 虚拟列表 | TanStack Table 虚拟滚动 | 1000+ 行无卡顿 |
| 拖拽优化 | @dnd-kit 虚拟化 | 大量卡片流畅拖拽 |
| 状态拆分 | 多 Zustand Store | 减少不必要重渲染 |
| 防抖节流 | 搜索/自动保存 debounce | 减少 API 调用 |
| CSS 按需 | Tailwind purge | 生产 CSS < 10KB |
| 资源缓存 | Vite 产物 hash | 长期缓存 JS/CSS |

### 7.2 后端性能

| 策略 | 实现 | 效果 |
|------|------|------|
| 连接池 | SQLAlchemy connection pool | 复用数据库连接 |
| 查询优化 | selectinload / lazy load | 减少 N+1 查询 |
| 响应压缩 | FastAPI GZipMiddleware | 减少传输体积 |
| 分页查询 | LIMIT/OFFSET 默认分页 | 大数据集不溢出 |
| 异步处理 | async/await 全链路 | 高并发低延迟 |

### 7.3 关键性能指标

```
首屏加载:     < 1.5s  (Lighthouse Performance > 90)
交互响应:     < 100ms (拖拽操作 60fps)
API 响应:     < 50ms  (P95，本地 SQLite)
表格渲染:     < 200ms (100 行数据)
```

---

## 8. 扩展点

### 8.1 扩展点设计

| 扩展点 | 当前实现 | 可扩展方向 |
|--------|----------|------------|
| 认证方式 | 本地登录 | OAuth2 / SSO / LDAP |
| 数据库 | SQLite | PostgreSQL / MySQL (切换方言) |
| Agent 后端 | 规则驱动 | LLM API (OpenAI/Claude) |
| 数据导出 | JSON | CSV / Excel / Jira XML |
| 通知机制 | 无 | WebSocket 实时推送 |
| 看板视图 | 四列固定 | 自定义列 / 泳道视图 |
| 图表 | 迷你图 | ECharts 详细报表 |
| 部署方式 | 单机 | Docker / K8s / Serverless |

### 8.2 Agent 扩展架构

```
当前: AgentService (规则驱动)
       │
       └─► 关键词匹配 → 预定义响应模板
       └─► 上下文查询 → 返回结构化数据

扩展: LLM Adapter 模式
       │
       ├─► OpenAIAdapter    → GPT-4 / GPT-3.5
       ├─► ClaudeAdapter    → Anthropic Claude
       ├─► LocalAdapter     → 本地 LLM (Ollama)
       └─► RulesAdapter     → 当前规则引擎 (默认)

配置方式: Config 表设置 agent.provider = 'openai'
```

### 8.3 插件化 Sprint 模板

```
TemplateSelector 支持自定义模板:

内置模板:
├── 标准 2 周 Sprint
├── Kanban 流程
├── 冲刺 + 发布
└── 维护迭代

自定义模板 (存储于 Config 表):
├── 用户可创建/编辑
├── JSON 格式定义预设字段
└── 支持导入/导出
```

---

*文档结束 — Sprint Agent v2.0 系统架构文档*

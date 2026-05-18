# Sprint Agent v2.0 — 前端架构文档

> 版本：v2.0  
> 日期：2025-07-31  
> 状态：正式发布

---

## 目录

1. [技术栈与版本](#1-技术栈与版本)
2. [项目结构](#2-项目结构)
3. [组件架构](#3-组件架构)
4. [状态管理](#4-状态管理)
5. [类型系统](#5-类型系统)
6. [API 层](#6-api-层)
7. [快捷操作设计](#7-快捷操作设计)
8. [主题系统](#8-主题系统)
9. [响应式设计](#9-响应式设计)
10. [构建配置](#10-构建配置)

---

## 1. 技术栈与版本

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 19.x | UI 框架，函数组件 + Hooks |
| TypeScript | 5.6+ | 静态类型系统 |
| Vite | 6.x | 构建工具与开发服务器 |
| Tailwind CSS | 3.4+ | 原子化 CSS 工具类 |
| shadcn/ui | latest | 无头 UI 组件基础库 |
| @dnd-kit/core | 6.x | 拖拽交互基础设施 |
| @dnd-kit/sortable | 6.x | 可排序拖拽封装 |
| TanStack Table | 8.x | 高性能表格 |
| Zustand | 4.x | 轻量级状态管理 |
| Lucide React | latest | 图标库 |
| date-fns | 3.x | 日期处理工具 |
| react-hook-form | 7.x | 表单状态管理 |
| zod | 3.x | 运行时 schema 校验 |

---

## 2. 项目结构

```
sprint-agent-v2/frontend/
├── public/
│   └── favicon.ico
│
├── src/
│   ├── main.tsx                    # 应用入口 (createRoot)
│   ├── App.tsx                     # 根组件 (HashRouter)
│   ├── index.css                   # 全局样式 + Tailwind directives
│   │
│   ├── components/
│   │   ├── layout/                 # 布局组件
│   │   │   ├── Layout.tsx          # 主布局壳 (Nav+Sidebar+Main+Agent+Bottom)
│   │   │   ├── TopNav.tsx          # 顶部导航栏
│   │   │   ├── Sidebar.tsx         # 可折叠侧边栏
│   │   │   ├── AgentPanel.tsx      # 智能体面板 (320px)
│   │   │   ├── BottomBar.tsx       # 底部状态栏
│   │   │   └── NavItem.tsx         # 导航项
│   │   │
│   │   ├── dashboard/              # 看板页面组件
│   │   │   ├── SprintHeader.tsx
│   │   │   ├── KanbanBoard.tsx
│   │   │   ├── KanbanColumn.tsx
│   │   │   ├── TaskCard.tsx
│   │   │   ├── InlineTaskCreator.tsx
│   │   │   └── TaskDetailSlideOver.tsx
│   │   │
│   │   ├── planning/               # 规划页面组件
│   │   │   ├── SprintForm.tsx
│   │   │   ├── MemberTable.tsx
│   │   │   ├── TemplateSelector.tsx
│   │   │   └── CapacitySummary.tsx
│   │   │
│   │   ├── standup/                # 站会页面组件
│   │   │   ├── TabNavigation.tsx
│   │   │   ├── StandupTable.tsx
│   │   │   ├── YesterdayFillButton.tsx
│   │   │   └── SubmitToolbar.tsx
│   │   │
│   │   ├── retro/                  # 回顾页面组件
│   │   │   ├── RatingSection.tsx
│   │   │   ├── RatingCard.tsx
│   │   │   ├── FeedbackTabs.tsx
│   │   │   ├── FeedbackList.tsx
│   │   │   └── SummaryPanel.tsx
│   │   │
│   │   ├── settings/               # 设置页面组件
│   │   │   ├── GeneralSettings.tsx
│   │   │   ├── TeamSettings.tsx
│   │   │   ├── DataSettings.tsx
│   │   │   ├── AgentSettings.tsx
│   │   │   └── AppearanceSettings.tsx
│   │   │
│   │   ├── agent/                  # 智能体组件
│   │   │   ├── ChatMessageList.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── SlashCommandMenu.tsx
│   │   │   ├── QuickActionBar.tsx
│   │   │   └── TypingIndicator.tsx
│   │   │
│   │   └── ui/                     # shadcn/ui 组件
│   │       ├── button.tsx
│   │       ├── input.tsx
│   │       ├── dialog.tsx
│   │       ├── select.tsx
│   │       ├── tabs.tsx
│   │       ├── table.tsx
│   │       ├── card.tsx
│   │       ├── badge.tsx
│   │       ├── toast.tsx
│   │       ├── slide-over.tsx
│   │       └── ...
│   │
│   ├── pages/                      # 页面级组件
│   │   ├── DashboardPage.tsx
│   │   ├── PlanningPage.tsx
│   │   ├── StandupPage.tsx
│   │   ├── RetroPage.tsx
│   │   ├── SettingsPage.tsx
│   │   └── LoginPage.tsx
│   │
│   ├── stores/                     # Zustand 状态管理
│   │   ├── useUIStore.ts
│   │   ├── useSprintStore.ts
│   │   ├── useTaskStore.ts
│   │   ├── useMemberStore.ts
│   │   ├── useStandupStore.ts
│   │   ├── useRetroStore.ts
│   │   └── useAgentStore.ts
│   │
│   ├── api/                        # API 客户端
│   │   ├── client.ts               # fetch 封装
│   │   ├── sprintApi.ts
│   │   ├── taskApi.ts
│   │   ├── memberApi.ts
│   │   ├── standupApi.ts
│   │   ├── retroApi.ts
│   │   ├── agentApi.ts
│   │   └── settingsApi.ts
│   │
│   ├── types/                      # TypeScript 类型定义
│   │   └── index.ts
│   │
│   ├── hooks/                      # 自定义 Hooks
│   │   ├── useAuth.ts
│   │   ├── useShortcut.ts
│   │   └── useToast.ts
│   │
│   └── lib/                        # 工具函数
│       └── utils.ts                # cn() 等辅助函数
│
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
└── package.json
```

---

## 3. 组件架构

### 3.1 布局壳 (Layout Shell)

```
┌────────────────────────────────────────────────────┐
│ TopNav (48px fixed)                                │
│ [Logo] [Sprint 选择器] [页面标题]         [用户菜单] │
├──────────┬───────────────────────────┬─────────────┤
│          │                           │             │
│ Sidebar  │                           │ AgentPanel  │
│ (52px    │                           │ (320px      │
│  →200px) │      MainContent          │  docked)    │
│  [ ]     │      (flex: 1)            │             │
│  [D] 看板 │                           │ [Chat]      │
│  [P] 规划 │      页面内容区域          │ [Input]     │
│  [S] 站会 │                           │ [Quick]     │
│  [R] 回顾 │                           │             │
│  [C] 设置 │                           │             │
│  [T] 主题 │                           │             │
│          │                           │             │
├──────────┴───────────────────────────┴─────────────┤
│ BottomBar (32px) [状态] [同步时间] [Agent 切换]     │
└────────────────────────────────────────────────────┘

- 总高度: 100vh
- 内容区: calc(100vh - 48px - 32px)
- 侧边栏折叠态: 52px; 展开态: 200px
- AgentPanel: 固定 320px，可折叠
```

### 3.2 页面组件

| 页面 | 核心组件 | 布局特点 |
|------|----------|----------|
| Dashboard | KanbanBoard (4列) | 全宽，横向滚动，卡片网格 |
| Planning | 两栏 (60%/40%) | 左侧表单，右侧成员表格 |
| Standup | 全宽表格 | Tab 导航 + TanStack Table |
| Retro | 上下结构 | 上部评分卡，下部反馈区 |
| Settings | 侧边 Tab | 左侧设置导航，右侧内容 |
| Login | 居中卡片 | 简单居中表单 |

### 3.3 共享组件

#### TaskCard — 看板任务卡片

```typescript
interface TaskCardProps {
  task: Task;                     // 任务数据
  isDragging?: boolean;           // 拖拽中状态
  onEdit: (task: Task) => void;   // 编辑回调
  onDelete: (id: number) => void; // 删除回调
  onClick: (task: Task) => void;  // 点击打开详情
}

// 使用 @dnd-kit/sortable 的 useSortable hook
// 拖拽手柄: 卡片左侧 grip 图标
// 拖拽浮层: DragOverlay 渲染独立副本
```

#### InlineTaskCreator — 行内创建任务

```typescript
interface InlineTaskCreatorProps {
  sprintId: number;
  defaultStatus: TaskStatus;      // 默认状态（列决定）
  onCreated: (task: Task) => void; // 创建成功回调
}

// 行为: 点击 "+" → 展开输入框 → 输入标题 → Enter/失去焦点 → 提交
// 输入框: autoFocus，Enter 提交，Escape 取消
// 提交后: 清空输入框，保持展开状态（方便连续创建）
```

#### SprintHeader — Sprint 信息头

```typescript
interface SprintHeaderProps {
  sprint: Sprint;
  stats: SprintStats | null;      // 燃尽/进度统计
}

// 展示: Sprint 名称、目标、起止日期、进度条、剩余天数
```

#### SlideOver — 滑出详情面板

```typescript
interface SlideOverProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

// 从右侧滑出，宽度 480px，覆盖主内容区
// 背景遮罩点击关闭
```

---

## 4. 状态管理

### 4.1 Zustand Store 结构

#### useUIStore — UI 状态

```typescript
interface UIState {
  sidebarCollapsed: boolean;
  agentPanelOpen: boolean;
  theme: 'light' | 'dark';
  activePage: string;
  toasts: Toast[];
  slideOver: { open: boolean; content: ReactNode; title: string } | null;

  toggleSidebar: () => void;
  toggleAgentPanel: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setActivePage: (page: string) => void;
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  openSlideOver: (title: string, content: ReactNode) => void;
  closeSlideOver: () => void;
}
```

#### useTaskStore — 任务状态

```typescript
interface TaskState {
  tasks: Task[];
  taskMap: Map<number, Task>;
  columns: Record<TaskStatus, Task[]>;
  draggingTaskId: number | null;
  loading: boolean;

  fetchTasks: (sprintId: number) => Promise<void>;
  createTask: (data: TaskCreate) => Promise<Task>;
  updateTask: (id: number, data: Partial<Task>) => Promise<void>;
  deleteTask: (id: number) => Promise<void>;
  moveTask: (id: number, status: TaskStatus, index?: number) => Promise<void>;
  setDraggingTaskId: (id: number | null) => void;
  _recomputeColumns: () => void;        // 内部：重新分组
}

// columns 派生: 从 tasks 数组按 status 分组计算
// taskMap 派生: 从 tasks 数组构建 Map 索引
```

#### useStandupStore — 站会状态

```typescript
interface StandupState {
  dailyLogs: DailyLog[];
  yesterdayLogs: DailyLog[];
  activeMemberTab: number;
  unsavedChanges: boolean;

  fetchLogs: (sprintId: number, date: string) => Promise<void>;
  fetchYesterdayLogs: (sprintId: number) => Promise<void>;
  submitLog: (log: DailyLogCreate) => Promise<void>;
  submitBatch: (logs: DailyLogCreate[]) => Promise<void>;
  fillFromYesterday: () => void;        // 将昨日 completed → 今日 planned
  updateLocalLog: (memberId: number, field: string, value: string) => void;
  setActiveTab: (memberId: number) => void;
}
```

#### useAgentStore — 智能体状态

```typescript
interface AgentState {
  messages: AgentMessage[];
  isTyping: boolean;
  context: AgentContext | null;
  suggestedActions: QuickAction[];

  sendMessage: (content: string) => Promise<void>;
  executeAction: (actionId: string) => Promise<void>;
  fetchHistory: () => Promise<void>;
  fetchContext: () => Promise<void>;
  clearChat: () => void;
}
```

### 4.2 Persist 中间件 (主题持久化)

```typescript
// useUIStore.ts — 主题持久化配置
import { persist } from 'zustand/middleware';

export const useUIStore = create<UIState>()(
  persist(
    (set, get) => ({
      theme: 'light',
      sidebarCollapsed: false,
      // ... 其他状态
      setTheme: (theme) => {
        set({ theme });
        document.documentElement.classList.toggle('dark', theme === 'dark');
      },
    }),
    {
      name: 'sprint-agent-ui',           // localStorage key
      partialize: (state) => ({          // 只持久化指定字段
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
);

// 初始化: App.tsx 中读取持久化值并应用
useEffect(() => {
  const { theme } = useUIStore.getState();
  document.documentElement.classList.toggle('dark', theme === 'dark');
}, []);
```

---

## 5. 类型系统

### 5.1 核心类型定义

```typescript
// ==================== 枚举类型 ====================

type SprintStatus = 'active' | 'closed' | 'draft';
type TaskStatus = 'todo' | 'progress' | 'done' | 'paused';
type MemberRole = 'sm' | 'dev' | 'qa' | 'po';
type RetroCategory = 'liked' | 'disliked' | 'action';
type RetroDimension = 'velocity' | 'quality' | 'teamwork' | 'process';
type AgentRole = 'user' | 'agent' | 'system';

// ==================== 实体类型 ====================

interface Sprint {
  id: number;
  name: string;
  goal: string | null;
  start_date: string;           // ISO date string
  end_date: string;
  status: SprintStatus;
}

interface Member {
  id: number;
  name: string;
  role: MemberRole;
  capacity: number;             // 0.0 ~ 1.0
  avatar: string | null;
}

interface Task {
  id: number;
  sprint_id: number;
  title: string;
  assignee_id: number | null;
  assignee?: Member;            // 关联对象（前端组装）
  status: TaskStatus;
  priority: number;             // 1 ~ 10
  story_points: number;
  blocked_by: number | null;
  description: string;
  created_at?: string;
}

interface DailyLog {
  id: number;
  sprint_id: number;
  member_id: number;
  member?: Member;              // 关联对象
  date: string;                 // ISO date
  completed: string;
  planned: string;
  blockers: string;
  hours_spent: number;
}

interface RetroItem {
  id: number;
  sprint_id: number;
  category: RetroCategory;
  item: string;
  votes: number;
  hasVoted?: boolean;           // 前端状态：当前用户是否已投票
}

interface RetroRating {
  id: number;
  sprint_id: number;
  dimension: RetroDimension;
  score: number;                // 1 ~ 5
}

interface AgentMessage {
  id: number;
  role: AgentRole;
  content: string;
  context: AgentContext | null;
  created_at: string;
}

interface Config {
  key: string;
  value: string;                // JSON string
}

// ==================== DTO 类型 ====================

interface TaskCreate {
  sprint_id: number;
  title: string;
  assignee_id?: number | null;
  status?: TaskStatus;
  priority?: number;
  story_points?: number;
  description?: string;
}

interface DailyLogCreate {
  sprint_id: number;
  member_id: number;
  date: string;
  completed: string;
  planned: string;
  blockers: string;
  hours_spent: number;
}

// ==================== 派生类型 ====================

interface SprintStats {
  sprint_id: number;
  total_points: number;
  completed_points: number;
  remaining_points: number;
  burndown: { date: string; remaining: number }[];
  velocity: number;             // 日均完成点数
  completion_rate: number;      // 完成率 0~1
}

interface AgentContext {
  page: string;
  entities: {
    sprint?: Sprint;
    tasks?: Task[];
    members?: Member[];
  };
}

interface QuickAction {
  id: string;
  label: string;
  action: string;
  icon?: string;
}
```

---

## 6. API 层

### 6.1 统一 Fetch 封装

```typescript
// src/api/client.ts

const BASE_URL = '/api';

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const options: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };

  if (body !== undefined) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      response.status,
      errorData.detail || errorData.message || `HTTP ${response.status}`,
      errorData
    );
  }

  // 204 No Content 直接返回
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const client = {
  get: <T>(path: string) => request<T>('GET', path),
  post: <T>(path: string, body?: unknown) => request<T>('POST', path, body),
  put: <T>(path: string, body?: unknown) => request<T>('PUT', path, body),
  del: <T>(path: string) => request<T>('DELETE', path),
};

export { ApiError };
```

### 6.2 各域 API 客户端

```typescript
// ==================== sprintApi.ts ====================
import { client } from './client';

export const sprintApi = {
  getAll: () => client.get<Sprint[]>('/sprint'),
  getById: (id: number) => client.get<Sprint>(`/sprint/${id}`),
  create: (data: SprintCreate) => client.post<Sprint>('/sprint', data),
  getStats: (id: number) => client.get<SprintStats>(`/sprint/${id}/stats`),
};

// ==================== taskApi.ts ====================
export const taskApi = {
  getAll: (sprintId: number) =>
    client.get<Task[]>(`/tasks?sprint_id=${sprintId}`),
  create: (data: TaskCreate) => client.post<Task>('/tasks', data),
  update: (id: number, data: Partial<Task>) =>
    client.put<Task>(`/tasks/${id}`, data),
  remove: (id: number) => client.del<void>(`/tasks/${id}`),
  move: (id: number, data: { status: TaskStatus; index?: number }) =>
    client.post<void>(`/tasks/${id}/move`, data),
  bulk: (data: TaskBulkOperation) => client.post<void>('/tasks/bulk', data),
};

// ==================== memberApi.ts ====================
export const memberApi = {
  getAll: () => client.get<Member[]>('/members'),
  create: (data: MemberCreate) => client.post<Member>('/members', data),
  update: (id: number, data: Partial<Member>) =>
    client.put<Member>(`/members/${id}`, data),
  remove: (id: number) => client.del<void>(`/members/${id}`),
};

// ==================== standupApi.ts ====================
export const standupApi = {
  getAll: (sprintId: number, date: string) =>
    client.get<DailyLog[]>(`/standup?sprint_id=${sprintId}&date=${date}`),
  create: (data: DailyLogCreate) => client.post<DailyLog>('/standup', data),
  batch: (logs: DailyLogCreate[]) => client.post<DailyLog[]>('/standup/batch', logs),
  yesterday: (sprintId: number) =>
    client.get<DailyLog[]>(`/standup/yesterday?sprint_id=${sprintId}`),
};

// ==================== retroApi.ts ====================
export const retroApi = {
  getItems: (sprintId: number) =>
    client.get<RetroItem[]>(`/retro?sprint_id=${sprintId}`),
  addItem: (data: RetroItemCreate) => client.post<RetroItem>('/retro', data),
  vote: (id: number) => client.post<void>(`/retro/vote`, { item_id: id }),
  rate: (data: RetroRating[]) => client.post<void>('/retro/rate', data),
  getReport: (sprintId: number) =>
    client.get<RetroReport>(`/retro/${sprintId}/report`),
};

// ==================== agentApi.ts ====================
export const agentApi = {
  sendMessage: (content: string, context: AgentContext) =>
    client.post<AgentResponse>('/agent/message', { content, context }),
  getHistory: () => client.get<AgentMessage[]>('/agent/history'),
  executeAction: (actionId: string, params?: unknown) =>
    client.post<void>('/agent/action', { action_id: actionId, params }),
  getContext: () => client.get<AgentContext>('/agent/context'),
};

// ==================== settingsApi.ts ====================
export const settingsApi = {
  getAll: () => client.get<Record<string, string>>('/settings'),
  update: (data: Record<string, string>) => client.put<void>('/settings', data),
  import: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return client.post<void>('/import', form);
  },
  export: () => client.get<Blob>('/export'),
  reset: () => client.post<void>('/reset'),
  health: () => client.get<{ status: string }>('/health'),
};
```

---

## 7. 快捷操作设计

### 7.1 行内任务创建流程

```
KanbanColumn 底部
    │
    ├── 常驻显示 "+ Add task" 按钮
    │
    └── 点击后:
            │
            ├── InlineTaskCreator 展开
            │   ├── 单行输入框 (autoFocus)
            │   ├── 占位文本: "输入任务标题..."
            │   │
            │   ├── Enter → 提交创建
            │   │   ├── 成功: 清空输入框，保持展开，Toast 提示
            │   │   └── 失败: 输入框红框提示，错误信息
            │   │
            │   ├── Escape → 取消，折叠回按钮
            │   └── 失去焦点 → 若为空则折叠，有内容则自动提交
            │
            └── 连续创建: 保持展开状态，方便批量输入
```

### 7.2 站会批量编辑导航

```
StandupPage 交互:
    │
    ├── TabNavigation (顶部横向成员标签)
    │   ├── 点击切换: 切换当前编辑的成员
    │   ├── 未保存标记: Tab 右上角红点指示
    │   └── 左右箭头: 键盘 ← → 切换成员
    │
    ├── TanStack Table (全宽可编辑表格)
    │   ├── 单元格点击 → 切换为编辑态 (input/textarea)
    │   ├── Tab 键 → 跳到下一个单元格
    │   ├── Shift+Tab → 跳到上一个单元格
    │   └── 行级别: completed / planned / blockers / hours_spent
    │
    ├── "Fill from Yesterday" 按钮
    │   └── 点击 → 查询昨日日志 → 将 completed 内容填入 planned
    │
    └── 提交: Ctrl+Enter (全局监听)
        └── 提交成功后: 清除所有未保存标记
```

### 7.3 回顾快速评分

```
RetroPage → RatingSection:
    │
    └── 4 张 RatingCard 横向排列
        │
        ├── 每张卡片: dimension 名称 + 5 星评分
        ├── 鼠标悬停: 星星高亮预览
        ├── 点击星星: 设置分数 (1-5)
        ├── 再次点击同星: 取消评分
        └── 视觉反馈: 选中的星星 filled，未选中 outline

    评分提交: 4 个维度全部评分后，自动 POST /api/retro/rate
```

### 7.4 键盘快捷键表

| 快捷键 | 作用域 | 功能 |
|--------|--------|------|
| `Ctrl + Enter` | Standup 页面 | 批量提交日报 |
| `Ctrl + B` | 全局 | 切换侧边栏折叠 |
| `Ctrl + J` | 全局 | 切换 Agent 面板 |
| `Escape` | 全局 | 关闭 SlideOver / AgentPanel |
| `Tab` | Standup 表格 | 切换到下一个编辑单元格 |
| `Shift + Tab` | Standup 表格 | 切换到上一个编辑单元格 |
| `Enter` | InlineTaskCreator | 提交创建任务 |
| `Escape` | InlineTaskCreator | 取消创建，折叠输入框 |
| `/` | AgentPanel 输入框 | 触发斜杠命令菜单 |
| `↑ / ↓` | 斜杠命令菜单 | 选择命令项 |
| `Enter` | 斜杠命令菜单 | 确认选中命令 |

---

## 8. 主题系统

### 8.1 主题架构

```
Tailwind CSS 暗黑模式: class 策略

tailwind.config.js:
  darkMode: 'class'

切换方式:
  html.dark → 全局暗黑模式

实现:
  useUIStore.setTheme('dark')
  → document.documentElement.classList.add('dark')
  → localStorage 持久化

CSS Variables (shadcn/ui 默认):
  :root {
    --background: 0 0% 100%;
    --foreground: 240 10% 3.9%;
    --card: 0 0% 100%;
    --card-foreground: 240 10% 3.9%;
    --primary: 240 5.9% 10%;
    --primary-foreground: 0 0% 98%;
    --border: 240 5.9% 90%;
    --ring: 240 5.9% 10%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 240 10% 3.9%;
    --foreground: 0 0% 98%;
    --card: 240 10% 3.9%;
    --card-foreground: 0 0% 98%;
    --primary: 0 0% 98%;
    --primary-foreground: 240 5.9% 10%;
    --border: 240 3.7% 15.9%;
    --ring: 240 4.9% 83.9%;
  }

所有 shadcn/ui 组件使用 hsl(var(--xxx)) 引用变量
自定义组件使用 Tailwind 的 dark: 前缀
```

### 8.2 主题切换组件

```tsx
// ThemeToggle.tsx — 放置在 Sidebar 底部
function ThemeToggle() {
  const { theme, setTheme } = useUIStore();

  return (
    <button
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
      className="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-accent transition-colors"
      aria-label="切换主题"
    >
      {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
      <span className="hidden group-data-[expanded=true]:inline">
        {theme === 'light' ? '暗色模式' : '亮色模式'}
      </span>
    </button>
  );
}
```

---

## 9. 响应式设计

### 9.1 断点策略

| 断点 | 宽度 | 布局调整 |
|------|------|----------|
| sm | 640px | 基础移动端适配 |
| md | 768px | 平板: 侧边栏收缩，Agent 全宽浮层 |
| lg | 1024px | 小桌面: 显示完整侧边栏 |
| xl | 1280px | 标准桌面: 完整布局 |
| 2xl | 1536px | 大屏: 看板列更宽 |

### 9.2 响应式行为

```
< 768px (移动端):
  - 侧边栏: 完全隐藏，汉堡菜单触发 Drawer
  - AgentPanel: 全宽底部浮层 (Sheet)
  - 看板: 单列纵向堆叠，横向滑动切换列
  - 规划页: 单栏纵向堆叠
  - 底部栏: 简化显示

768px - 1024px (平板):
  - 侧边栏: 始终收缩 (52px)
  - AgentPanel: 280px 折叠面板
  - 看板: 横向滚动，卡片宽度自适应

>= 1024px (桌面):
  - 侧边栏: 可展开/收缩
  - AgentPanel: 320px docked 面板
  - 看板: 四列等分
  - 规划页: 双栏 60%/40%
```

---

## 10. 构建配置

### 10.1 Vite 配置

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',   // FastAPI 后端
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          // 代码分割策略
          vendor: ['react', 'react-dom'],
          dnd: ['@dnd-kit/core', '@dnd-kit/sortable', '@dnd-kit/utilities'],
          table: ['@tanstack/react-table'],
          utils: ['date-fns', 'zod', 'react-hook-form'],
        },
      },
    },
  },
});
```

### 10.2 Tailwind 配置

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};
```

### 10.3 TypeScript 配置

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 10.4 构建产物

```
dist/
├── assets/
│   ├── index-XXXXXX.js        # 主入口 (vendor + dnd + table 分离)
│   ├── vendor-XXXXXX.js       # React 等基础库
│   ├── dnd-XXXXXX.js          # 拖拽相关
│   ├── table-XXXXXX.js        # 表格相关
│   ├── utils-XXXXXX.js        # 工具库
│   └── index-XXXXXX.css       # 打包后的 Tailwind CSS
├── index.html
└── favicon.ico

预估体积:
  - 首屏 JS: < 200KB (gzip)
  - 总 JS: < 500KB (gzip)
  - CSS: < 15KB (gzip)
```

---

*文档结束 — Sprint Agent v2.0 前端架构文档*

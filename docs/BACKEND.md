# Sprint Agent v2.0 后端架构文档

## 1. 技术栈 (Tech Stack)

| 组件 | 技术选型 | 版本 |
|------|---------|------|
| 编程语言 | Python | 3.12+ |
| Web框架 | FastAPI | 最新稳定版 |
| ORM | SQLAlchemy | 2.0+ |
| 数据验证 | Pydantic | v2 |
| 数据库 | SQLite | 内置 |
| ASGI服务器 | Uvicorn | 最新稳定版 |

### 选型理由

- **FastAPI**: 原生支持异步、自动生成 OpenAPI 文档、依赖注入系统完善
- **SQLAlchemy 2.0**: 类型提示完整、声明式 ORM 语法简洁、支持异步会话
- **Pydantic v2**: 验证性能大幅提升、与 FastAPI 深度集成
- **SQLite**: 零配置部署、文件级数据持久化、WAL 模式支持并发读

---

## 2. 项目结构

```
sprint-agent-v2/
├── main.py                 # FastAPI 应用入口、生命周期管理
├── models.py               # SQLAlchemy ORM 模型定义（8 张表）
├── schemas.py              # Pydantic 数据验证与序列化模型
├── database.py             # 数据库引擎、会话工厂、依赖注入
├── routers/                # API 路由层（7 个路由器）
│   ├── sprint.py           # 迭代管理路由
│   ├── tasks.py            # 任务管理路由
│   ├── members.py          # 成员管理路由
│   ├── standup.py          # 每日站会路由
│   ├── retro.py            # 回顾会议路由
│   ├── agent.py            # 智能助手路由
│   └── settings.py         # 设置与数据管理路由
├── services/               # 业务逻辑层
│   └── agent_service.py    # 智能助手核心服务
├── data/                   # 初始数据
│   └── init.json           # 默认演示数据
├── static/                 # 静态资源
└── requirements.txt        # 依赖列表
```

---

## 3. 数据库设计

### 3.1 表结构概览

| 表名 | 中文说明 | 主键 |
|------|---------|------|
| sprints | 迭代 | id (Integer, PK) |
| members | 成员 | id (Integer, PK) |
| tasks | 任务 | id (Integer, PK) |
| daily_logs | 每日站会记录 | id (Integer, PK) |
| retros | 回顾项目 | id (Integer, PK) |
| retro_ratings | 回顾评分 | id (Integer, PK) |
| agent_messages | 助手对话记录 | id (Integer, PK) |
| configs | 系统配置 | key (String, PK) |

### 3.2 字段定义

#### sprints 表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, auto_increment | 迭代唯一标识 |
| name | String(255) | NOT NULL | 迭代名称 |
| goal | Text | nullable | 迭代目标 |
| start_date | Date | NOT NULL | 开始日期 |
| end_date | Date | NOT NULL | 结束日期 |
| status | String(50) | default "planning" | 状态 |
| created_at | DateTime | default now | 创建时间 |

#### members 表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, auto_increment | 成员唯一标识 |
| name | String(255) | NOT NULL | 成员姓名 |
| role | String(100) | NOT NULL | 角色 |
| capacity | Float | default 1.0 | 容量系数 |
| avatar | String(500) | nullable | 头像 URL |
| created_at | DateTime | default now | 创建时间 |

#### tasks 表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, auto_increment | 任务唯一标识 |
| title | String(500) | NOT NULL | 任务标题 |
| sprint_id | Integer | FK -> sprints.id | 所属迭代 |
| assignee_id | Integer | FK -> members.id, nullable | 负责人 |
| status | String(50) | default "todo" | 状态 |
| priority | String(50) | default "medium" | 优先级 |
| story_points | Integer | default 0 | 故事点 |
| blocked_by | Text | nullable | 阻塞原因 |
| description | Text | nullable | 描述 |
| created_at | DateTime | default now | 创建时间 |
| updated_at | DateTime | default now, onupdate | 更新时间 |

#### daily_logs 表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, auto_increment | 日志唯一标识 |
| sprint_id | Integer | FK -> sprints.id | 所属迭代 |
| member_id | Integer | FK -> members.id | 成员 |
| date | Date | NOT NULL | 日志日期 |
| completed | Text | nullable | 已完成工作 |
| planned | Text | nullable | 计划工作 |
| blockers | Text | nullable | 阻塞项 |
| hours_spent | Float | default 0 | 工时投入 |
| created_at | DateTime | default now | 创建时间 |

#### retros 表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, auto_increment | 回顾项唯一标识 |
| sprint_id | Integer | FK -> sprints.id | 所属迭代 |
| category | String(50) | NOT NULL | liked/disliked/action |
| item | Text | NOT NULL | 回顾内容 |
| votes | Integer | default 0 | 投票数 |
| created_at | DateTime | default now | 创建时间 |

#### retro_ratings 表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, auto_increment | 评分唯一标识 |
| sprint_id | Integer | FK -> sprints.id | 所属迭代 |
| dimension | String(100) | NOT NULL | 维度名称 |
| score | Integer | NOT NULL | 分数 (1-5) |
| created_at | DateTime | default now | 创建时间 |

#### agent_messages 表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, auto_increment | 消息唯一标识 |
| role | String(20) | NOT NULL | user/assistant |
| content | Text | NOT NULL | 消息内容 |
| context | Text | nullable | 上下文 JSON |
| created_at | DateTime | default now | 创建时间 |

#### configs 表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| key | String(255) | PK | 配置键 |
| value | Text | nullable | 配置值 |
| updated_at | DateTime | default now | 更新时间 |

### 3.3 实体关系图

```
+----------------+       +----------------+
|    sprints     |       |    members     |
+----------------+       +----------------+
| PK id          |       | PK id          |
| name           |       | name           |
| goal           |       | role           |
| start_date     |       | capacity       |
| end_date       |       | avatar         |
| status         |       | created_at     |
| created_at     |       +--------+-------+
+---+----+-------+                |
    |    |                        |
    | FK |                        | FK
    |    |            +-----------v-----------+
    |    |            |        tasks          |
    |    |            +-----------------------+
    |    +----------->| PK id                 |
    |                 | title                 |
    |                 | FK sprint_id          |
    |                 | FK assignee_id        |
    |                 | status                |
    |                 | priority              |
    |                 | story_points          |
    |                 | blocked_by            |
    |                 | description           |
    |                 | created_at            |
    |                 | updated_at            |
    |                 +-----------------------+
    |
    |    +------------+-----------+------------+
    |    |            |           |            |
    | FK |      FK    |     FK    |      FK    |
    |    v            v           v            v
    |  +-------------+ +---------+ +----------+ +------------------+
    |  |  daily_logs | | retros  | |retro_    | | agent_messages   |
    |  +-------------+ +---------+ |ratings   | +------------------+
    |  | PK id       | | PK id   | +---------+ | PK id            |
    |  | FK sprint_id| |FK sprint| | PK id   | | role             |
    |  | FK member_id| |category | |FK sprint| | content          |
    |  | date        | |item     | |dimension| | context          |
    |  | completed   | |votes    | |score    | | created_at       |
    |  | planned     | |created  | |created  | +------------------+
    |  | blockers    | +---------+ +---------+
    |  | hours_spent |
    |  | created_at  |
    |  +-------------+
    |
    |  +----------------+
    +->|     configs    |
       +----------------+
       | PK key         |
       | value          |
       | updated_at     |
       +----------------+
```

关系说明：
- `sprints` 1:N `tasks` — 一个迭代包含多个任务
- `members` 1:N `tasks` — 一个成员可负责多个任务
- `sprints` 1:N `daily_logs` — 一个迭代有多条站会记录
- `members` 1:N `daily_logs` — 一个成员有多条站会记录
- `sprints` 1:N `retros` — 一个迭代有多个回顾项
- `sprints` 1:N `retro_ratings` — 一个迭代有多维度评分
- `configs` 为独立配置表，无外部关联
- `agent_messages` 为独立对话记录表，无外部关联

---

## 4. API 层

### 4.1 路由组织

```
/api
├── /sprint        # SprintRouter    -> routers/sprint.py
├── /tasks         # TasksRouter     -> routers/tasks.py
├── /members       # MembersRouter   -> routers/members.py
├── /standup       # StandupRouter   -> routers/standup.py
├── /retro         # RetroRouter     -> routers/retro.py
├── /agent         # AgentRouter     -> routers/agent.py
├── /settings      # SettingsRouter  -> routers/settings.py
└── /health        # Health check    -> routers/settings.py
```

### 4.2 请求/响应流程

```
客户端请求
    |
    v
FastAPI Router (routers/*.py)
    |
    v
Pydantic Schema 验证 (schemas.py)
    |
    v
SQLAlchemy CRUD 操作 (models.py + database.py)
    |
    v
SQLite 数据库 (data.db)
    |
    v
Pydantic Schema 序列化
    |
    v
JSON 响应返回客户端
```

### 4.3 CORS 配置

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # 开发阶段允许所有来源
    allow_credentials=True,
    allow_methods=["*"],           # 允许所有 HTTP 方法
    allow_headers=["*"],           # 允许所有请求头
)
```

### 4.4 生命周期管理

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动阶段
    await init_database()          # 创建表结构
    await load_init_data()         # 空库时加载 data/init.json
    yield
    # 关闭阶段（资源清理）
```

---

## 5. 数据导入服务

### 5.1 零 Mock 原则

系统遵循 **Zero-Mock 原则**：当数据库为空时，自动从 `data/init.json` 加载真实演示数据，确保前端在首次启动后即可看到完整功能演示，无需任何手动配置。

### 5.2 init.json 结构

```json
{
  "sprints": [
    {
      "name": "Sprint 1",
      "goal": "完成核心功能",
      "start_date": "2024-01-01",
      "end_date": "2024-01-14",
      "status": "active"
    }
  ],
  "members": [
    {
      "name": "张三",
      "role": "后端开发",
      "capacity": 1.0,
      "avatar": "https://..."
    }
  ],
  "tasks": [
    {
      "title": "设计数据库",
      "sprint_id": 1,
      "assignee_id": 1,
      "status": "done",
      "priority": "high",
      "story_points": 5
    }
  ],
  "daily_logs": [...],
  "retros": [...],
  "retro_ratings": [...]
}
```

### 5.3 导入流程

```
[应用启动]
    |
    v
[检查数据库是否为空]
    |
    +-- 否 --> [跳过导入]
    |
    是
    |
    v
[读取 data/init.json]
    |
    v
[按依赖顺序导入]
    1. sprints     (无依赖)
    2. members     (无依赖)
    3. tasks       (依赖 sprints, members)
    4. daily_logs  (依赖 sprints, members)
    5. retros      (依赖 sprints)
    6. retro_ratings (依赖 sprints)
    |
    v
[提交事务]
    |
    v
[导入完成，服务就绪]
```

---

## 6. 智能助手服务 (Agent Service)

### 6.1 意图分类

| 意图 (Intent) | 描述 | 示例 |
|--------------|------|------|
| `plan_task` | 任务规划与拆分 | "帮我拆分用户注册功能" |
| `update_status` | 更新任务状态 | "把任务 #3 标记为完成" |
| `standup_log` | 记录站会内容 | "记录今天的工作" |
| `retro_score` | 回顾评分 | "给这次迭代打 4 分" |
| `general_chat` | 通用对话 | "你好，介绍一下功能" |
| `create_sprint` | 创建迭代 | "新建一个为期两周的迭代" |
| `add_member` | 添加成员 | "添加新成员李四" |
| `view_board` | 查看看板 | "显示当前迭代的任务" |

### 6.2 实体提取

通过正则表达式模式匹配提取关键实体：

| 实体类型 | 正则模式示例 | 提取结果 |
|---------|------------|---------|
| 任务 ID | `#(\d+)` 或 `任务\s*(\d+)` | `task_id: 3` |
| 成员姓名 | `分配给\s*(\S+)` | `assignee: "张三"` |
| 状态值 | `(?:标记为|设置为)\s*(\S+)` | `status: "done"` |
| 故事点 | `(\d+)\s*点` | `points: 5` |
| 日期 | `(\d{4}-\d{2}-\d{2})` | `date: "2024-01-15"` |
| 迭代名称 | `迭代\s*(\S+)` | `sprint: "Sprint 1"` |

### 6.3 上下文管理

```python
class AgentContext:
    current_page: str         # 当前所在页面
    sprint_id: int | None     # 当前选中的迭代
    selected_task: int | None # 当前选中的任务
    members: list[Member]     # 当前迭代成员列表
    tasks: list[Task]         # 当前迭代任务列表
```

上下文用于：
- 消除用户输入中的歧义（如 "这个任务" 指代当前选中的任务）
- 提供关联数据（如自动列出当前迭代的成员供选择）
- 构建个性化回复（如根据当前页面给出相关建议）

---

## 7. CRUD 操作概览

| 模块 | 创建 | 读取 | 更新 | 删除 | 特殊操作 |
|------|------|------|------|------|---------|
| Sprint | POST /api/sprint | GET /api/sprint, GET /api/sprint/{id} | PUT /api/sprint/{id} | DELETE /api/sprint/{id} | GET /api/sprint/{id}/stats |
| Task | POST /api/tasks | GET /api/tasks, GET /api/tasks/{id} | PUT /api/tasks/{id} | DELETE /api/tasks/{id} | POST /api/tasks/{id}/move, POST /api/tasks/bulk |
| Member | POST /api/members | GET /api/members, GET /api/members/{id} | PUT /api/members/{id} | DELETE /api/members/{id} | - |
| Standup | POST /api/standup | GET /api/standup, GET /api/standup/yesterday | POST /api/standup | - | POST /api/standup/batch |
| Retro | POST /api/retro | GET /api/retro/{sprint_id} | POST /api/retro/vote | - | POST /api/retro/rate, GET /api/retro/{sprint_id}/report |
| Agent | POST /api/agent/message | GET /api/agent/history | - | - | POST /api/agent/action, GET /api/agent/context |
| Settings | PUT /api/settings | GET /api/settings | - | - | POST /api/import, GET /api/export, POST /api/reset |

---

## 8. 错误处理

```python
from fastapi import HTTPException
```

| 错误场景 | HTTP 状态码 | 错误消息 |
|---------|-----------|---------|
| 资源不存在 | 404 | "Sprint not found" |
| 请求参数无效 | 422 | Pydantic 自动验证错误 |
| 外键约束冲突 | 409 | "Referenced resource does not exist" |
| 数据库操作失败 | 500 | "Internal server error" |

### 全局异常处理

```python
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc):
    return JSONResponse(
        status_code=409,
        content={"detail": "数据约束冲突，请检查关联资源是否存在"}
    )
```

---

## 9. 性能优化

### 9.1 SQLite WAL 模式

```python
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")  # 启用 WAL 模式
    cursor.close()
```

WAL 模式优势：
- 读操作不再阻塞写操作
- 写操作不再阻塞读操作
- 适合高并发读取场景

### 9.2 其他优化

| 优化项 | 说明 |
|--------|------|
| 异步会话 | 使用 `AsyncSession` 避免阻塞事件循环 |
| 延迟加载控制 | 显式 `selectinload` 避免 N+1 查询 |
| 索引 | 外键字段、常用查询字段自动创建索引 |
| 连接池 | 默认连接池复用数据库连接 |

---

## 10. 测试策略

### 10.1 测试层次

```
+--------------------------+
|    端到端测试 (E2E)       |  pytest + TestClient
|    验证完整请求链路        |
+--------------------------+
|    集成测试               |  数据库操作 + 路由
|    验证模块间协作          |
+--------------------------+
|    单元测试               |  AgentService 逻辑
|    验证核心算法            |  意图分类、实体提取
+--------------------------+
```

### 10.2 测试用例示例

```python
# 测试创建 Sprint
def test_create_sprint(client):
    response = client.post("/api/sprint", json={
        "name": "Sprint Test",
        "goal": "测试目标",
        "start_date": "2024-01-01",
        "end_date": "2024-01-14",
        "status": "active"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "Sprint Test"

# 测试意图分类
def test_agent_intent_classification():
    service = AgentService()
    result = service.classify_intent("把任务 #3 标记为完成")
    assert result.intent == "update_status"
    assert result.entities["task_id"] == 3
```

### 10.3 测试数据隔离

每个测试用例使用独立的数据库事务，测试结束后自动回滚，确保测试之间互不干扰。

---

## 附录：状态枚举值

### 任务状态 (Task Status)
- `todo` — 待办
- `progress` — 进行中
- `done` — 已完成
- `paused` — 已暂停

### 优先级 (Priority)
- `low` — 低
- `medium` — 中
- `high` — 高
- `urgent` — 紧急

### 迭代状态 (Sprint Status)
- `planning` — 规划中
- `active` — 进行中
- `completed` — 已完成
- `cancelled` — 已取消

### 回顾类别 (Retro Category)
- `liked` — 做得好的
- `disliked` — 需要改进的
- `action` — 行动项

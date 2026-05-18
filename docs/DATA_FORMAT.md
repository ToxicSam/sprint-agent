# Sprint Agent v2.0 - 数据格式规范

> 本文档定义 Sprint Agent v2.0 的完整数据格式规范，涵盖 init.json 结构、枚举类型、数据导入导出方法及校验规则。
>
> 版本: v2.0 | 适用技术栈: Python + FastAPI + SQLite

---

## 目录

1. [数据导入哲学（Zero-Mock 原则）](#1-数据导入哲学zero-mock-原则)
2. [init.json 完整规范](#2-initjson-完整规范)
3. [状态枚举定义](#3-状态枚举定义)
4. [完整示例 init.json](#4-完整示例-initjson)
5. [数据导入方法](#5-数据导入方法)
6. [数据导出方法](#6-数据导出方法)
7. [校验规则](#7-校验规则)
8. [从 v1.0 格式迁移](#8-从-v10-格式迁移)

---

## 1. 数据导入哲学（Zero-Mock 原则）

### 1.1 核心设计理念

Sprint Agent v2.0 采用 **Zero-Mock（零模拟）** 数据架构，确保所有数据流均为真实数据：

- **前端零模拟逻辑**：前端代码中不包含任何 mock 数据、模拟 API 或假数据生成逻辑。所有组件始终通过真实 API 调用获取数据。
- **init.json 作为正式初始化数据**：`backend/data/init.json` 是系统的正式初始化数据源，而非临时测试数据。后端启动时自动检测数据库状态，若为空则从该文件加载。
- **后端统一数据入口**：所有数据必须经过后端 API 层，由后端统一管理数据持久化和业务逻辑。
- **API 是唯一的通信桥梁**：前端与后端之间仅通过 REST API 通信，不存在任何直接文件读取或旁路数据通道。

### 1.2 数据流图

```
+------------------+     REST API      +-------------------+     SQLite    +--------------+
|   React 前端     |  <------------->  |   FastAPI 后端     |  <--------->  |  .db 文件    |
|  (零模拟逻辑)    |                   |  (数据管理中枢)    |               +--------------+
+------------------+                   +-------------------+                    |
         ^                                     ^                                 |
         |                                     |                                 |
    拖拽导入                            init.json 自动加载                        |
    (设置页)                            (启动时检测空数据库)                       |
                                              ^                                  |
                                              +----------------------------------+
```

### 1.3 设计优势

1. **一致性**：开发、测试、生产环境使用完全相同的数据流路径
2. **可验证性**：所有数据操作可通过 API 文档（Swagger UI）直接验证
3. **可迁移性**：通过 JSON 导入导出实现数据跨环境迁移
4. **可测试性**：API 层可独立测试，无需前端参与

---

## 2. init.json 完整规范

### 2.1 顶层结构

`init.json` 是一个 JSON 对象，包含 7 个顶级数组字段：

```json
{
  "sprints": [...],
  "members": [...],
  "tasks": [...],
  "daily_logs": [...],
  "retros": [...],
  "retro_ratings": [...],
  "agent_messages": [...]
}
```

| 字段名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `sprints` | `Sprint[]` | 是 | 迭代列表 |
| `members` | `Member[]` | 是 | 团队成员列表 |
| `tasks` | `Task[]` | 是 | 任务列表 |
| `daily_logs` | `DailyLog[]` | 否 | 每日站会记录 |
| `retros` | `Retro[]` | 否 | 回顾会议条目 |
| `retro_ratings` | `RetroRating[]` | 否 | 回顾维度评分 |
| `agent_messages` | `AgentMessage[]` | 否 | AI 助手对话历史 |

### 2.2 Sprint 对象

```json
{
  "id": "spr-001",
  "name": "Sprint 26.05",
  "goal": "完成用户管理模块和后端 API 优化",
  "start_date": "2025-05-01",
  "end_date": "2025-05-14",
  "status": "active"
}
```

| 字段名 | 类型 | 必需 | 约束 | 说明 |
|--------|------|------|------|------|
| `id` | `string` | 是 | 唯一，格式 `spr-xxx` | 迭代标识符 |
| `name` | `string` | 是 | 最长 100 字符 | 迭代名称 |
| `goal` | `string` | 否 | 最长 500 字符 | 迭代目标描述 |
| `start_date` | `string` | 是 | ISO 日期格式 `YYYY-MM-DD` | 开始日期 |
| `end_date` | `string` | 是 | ISO 日期格式 `YYYY-MM-DD` | 结束日期 |
| `status` | `SprintStatus` | 是 | 枚举值 | 迭代状态 |

### 2.3 Member 对象

```json
{
  "id": "mem-001",
  "name": "Sarah Chen",
  "role": "sm",
  "capacity": 4.0,
  "avatar": "SC"
}
```

| 字段名 | 类型 | 必需 | 约束 | 说明 |
|--------|------|------|------|------|
| `id` | `string` | 是 | 唯一，格式 `mem-xxx` | 成员标识符 |
| `name` | `string` | 是 | 最长 100 字符 | 成员姓名 |
| `role` | `MemberRole` | 是 | 枚举值 | 角色 |
| `capacity` | `number` | 否 | 范围 0.0 - 10.0 | 工作容量（人天/迭代） |
| `avatar` | `string` | 否 | 最长 10 字符 | 头像缩写 |

### 2.4 Task 对象

```json
{
  "id": "task-001",
  "sprint_id": "spr-001",
  "title": "实现用户登录 API",
  "status": "done",
  "priority": 10,
  "story_points": 5.0,
  "assignee_id": "mem-002"
}
```

| 字段名 | 类型 | 必需 | 约束 | 说明 |
|--------|------|------|------|------|
| `id` | `string` | 是 | 唯一，格式 `task-xxx` | 任务标识符 |
| `sprint_id` | `string` | 是 | 引用 `sprints.id` | 所属迭代 |
| `title` | `string` | 是 | 最长 200 字符 | 任务标题 |
| `status` | `TaskStatus` | 是 | 枚举值 | 任务状态 |
| `priority` | `number` | 否 | 范围 1 - 100 | 优先级（数值越大越优先） |
| `story_points` | `number` | 否 | 范围 0.0 - 100.0 | 故事点 |
| `assignee_id` | `string` | 否 | 引用 `members.id` | 负责人 |

### 2.5 DailyLog 对象

```json
{
  "sprint_id": "spr-001",
  "member_id": "mem-002",
  "date": "2025-05-02",
  "completed": "完成了登录 API 的单元测试",
  "planned": "开始开发注册功能",
  "hours_spent": 6.5
}
```

| 字段名 | 类型 | 必需 | 约束 | 说明 |
|--------|------|------|------|------|
| `sprint_id` | `string` | 是 | 引用 `sprints.id` | 所属迭代 |
| `member_id` | `string` | 是 | 引用 `members.id` | 提交人 |
| `date` | `string` | 是 | ISO 日期格式 `YYYY-MM-DD` | 记录日期 |
| `completed` | `string` | 是 | 最长 1000 字符 | 昨日完成 |
| `planned` | `string` | 是 | 最长 1000 字符 | 今日计划 |
| `hours_spent` | `number` | 否 | 范围 0.0 - 24.0 | 投入工时 |

### 2.6 Retro 对象

```json
{
  "sprint_id": "spr-001",
  "category": "liked",
  "item": "任务需求描述清晰",
  "votes": 2
}
```

| 字段名 | 类型 | 必需 | 约束 | 说明 |
|--------|------|------|------|------|
| `sprint_id` | `string` | 是 | 引用 `sprints.id` | 所属迭代 |
| `category` | `RetroCategory` | 是 | 枚举值 | 回顾类别 |
| `item` | `string` | 是 | 最长 500 字符 | 回顾条目内容 |
| `votes` | `number` | 否 | 范围 0 - 99 | 投票数 |

### 2.7 RetroRating 对象

```json
{
  "sprint_id": "spr-001",
  "dimension": "velocity",
  "score": 4
}
```

| 字段名 | 类型 | 必需 | 约束 | 说明 |
|--------|------|------|------|------|
| `sprint_id` | `string` | 是 | 引用 `sprints.id` | 所属迭代 |
| `dimension` | `RetroDimension` | 是 | 枚举值 | 评分维度 |
| `score` | `number` | 是 | 范围 1 - 5 | 评分分数 |

### 2.8 AgentMessage 对象

```json
{
  "role": "agent",
  "content": "你好！我是 Sprint Agent，你的敏捷开发助手。"
}
```

| 字段名 | 类型 | 必需 | 约束 | 说明 |
|--------|------|------|------|------|
| `role` | `string` | 是 | `agent` / `user` / `system` | 消息角色 |
| `content` | `string` | 是 | 最长 10000 字符 | 消息内容 |

---

## 3. 状态枚举定义

### 3.1 TaskStatus（任务状态）

| 枚举值 | 含义 | 说明 |
|--------|------|------|
| `todo` | 待办 | 尚未开始 |
| `progress` | 进行中 | 正在处理 |
| `done` | 已完成 | 已交付 |
| `paused` | 已暂停 | 暂时搁置 |

### 3.2 SprintStatus（迭代状态）

| 枚举值 | 含义 | 说明 |
|--------|------|------|
| `active` | 进行中 | 当前活跃迭代 |
| `completed` | 已完成 | 已正常结束 |
| `cancelled` | 已取消 | 提前终止 |

### 3.3 MemberRole（成员角色）

| 枚举值 | 含义 | 说明 |
|--------|------|------|
| `sm` | 敏捷教练 | Scrum Master |
| `dev` | 开发者 | Developer |
| `qa` | 测试工程师 | Quality Assurance |
| `po` | 产品负责人 | Product Owner |

### 3.4 RetroCategory（回顾类别）

| 枚举值 | 含义 | 说明 |
|--------|------|------|
| `liked` | 做得好的 | 继续保持的方面 |
| `disliked` | 做得不好的 | 需要改进的方面 |
| `action` | 行动计划 | 下一步改进措施 |

### 3.5 RetroDimension（回顾维度）

| 枚举值 | 含义 | 说明 |
|--------|------|------|
| `velocity` | 速率 | 交付速度 |
| `quality` | 质量 | 代码与交付质量 |
| `teamwork` | 协作 | 团队协作效率 |
| `process` | 流程 | 流程规范性 |

---

## 4. 完整示例 init.json

以下是一个最小化的完整 `init.json` 示例，包含所有 7 个数据实体：

```json
{
  "sprints": [
    {
      "id": "spr-001",
      "name": "Sprint 26.05",
      "goal": "完成用户管理模块开发",
      "start_date": "2025-05-01",
      "end_date": "2025-05-14",
      "status": "active"
    },
    {
      "id": "spr-002",
      "name": "Sprint 26.06",
      "goal": "优化后端性能与接口文档",
      "start_date": "2025-05-15",
      "end_date": "2025-05-28",
      "status": "active"
    }
  ],
  "members": [
    {
      "id": "mem-001",
      "name": "Sarah Chen",
      "role": "sm",
      "capacity": 4.0,
      "avatar": "SC"
    },
    {
      "id": "mem-002",
      "name": "Michael Wang",
      "role": "dev",
      "capacity": 6.5,
      "avatar": "MW"
    },
    {
      "id": "mem-003",
      "name": "Lisa Zhang",
      "role": "qa",
      "capacity": 5.0,
      "avatar": "LZ"
    },
    {
      "id": "mem-004",
      "name": "David Liu",
      "role": "po",
      "capacity": 3.0,
      "avatar": "DL"
    }
  ],
  "tasks": [
    {
      "id": "task-001",
      "sprint_id": "spr-001",
      "title": "实现用户登录 API",
      "status": "done",
      "priority": 10,
      "story_points": 5.0,
      "assignee_id": "mem-002"
    },
    {
      "id": "task-002",
      "sprint_id": "spr-001",
      "title": "编写登录模块单元测试",
      "status": "done",
      "priority": 9,
      "story_points": 3.0,
      "assignee_id": "mem-003"
    },
    {
      "id": "task-003",
      "sprint_id": "spr-001",
      "title": "实现用户注册页面",
      "status": "progress",
      "priority": 10,
      "story_points": 8.0,
      "assignee_id": "mem-002"
    },
    {
      "id": "task-004",
      "sprint_id": "spr-002",
      "title": "数据库查询性能优化",
      "status": "todo",
      "priority": 8,
      "story_points": 5.0,
      "assignee_id": "mem-002"
    }
  ],
  "daily_logs": [
    {
      "sprint_id": "spr-001",
      "member_id": "mem-002",
      "date": "2025-05-02",
      "completed": "完成了登录 API 的核心逻辑",
      "planned": "编写单元测试并修复边界情况",
      "hours_spent": 6.5
    },
    {
      "sprint_id": "spr-001",
      "member_id": "mem-003",
      "date": "2025-05-02",
      "completed": "编写了登录模块 80% 的测试用例",
      "planned": "完成剩余测试并提交测试报告",
      "hours_spent": 7.0
    }
  ],
  "retros": [
    {
      "sprint_id": "spr-001",
      "category": "liked",
      "item": "需求文档描述清晰，减少了沟通成本",
      "votes": 3
    },
    {
      "sprint_id": "spr-001",
      "category": "liked",
      "item": "每日站会时间控制在 15 分钟以内",
      "votes": 2
    },
    {
      "sprint_id": "spr-001",
      "category": "disliked",
      "item": "部分任务估时偏差较大",
      "votes": 2
    },
    {
      "sprint_id": "spr-001",
      "category": "action",
      "item": "引入故事点估算会议",
      "votes": 3
    }
  ],
  "retro_ratings": [
    {
      "sprint_id": "spr-001",
      "dimension": "velocity",
      "score": 4
    },
    {
      "sprint_id": "spr-001",
      "dimension": "quality",
      "score": 5
    },
    {
      "sprint_id": "spr-001",
      "dimension": "teamwork",
      "score": 4
    },
    {
      "sprint_id": "spr-001",
      "dimension": "process",
      "score": 3
    }
  ],
  "agent_messages": [
    {
      "role": "agent",
      "content": "你好！我是 Sprint Agent，你的敏捷开发助手。我可以帮你查看迭代进度、分析团队效率和生成回顾报告。"
    },
    {
      "role": "user",
      "content": "帮我查看当前 Sprint 的任务完成情况。"
    },
    {
      "role": "agent",
      "content": "当前 Sprint 26.05 共 3 个任务，已完成 2 个（66.7%），剩余 1 个进行中。故事点完成率 8/16（50%）。"
    }
  ]
}
```

---

## 5. 数据导入方法

### 5.1 启动自动导入（后端）

后端启动时的自动导入流程：

```
1. 后端启动
2. 检查 SQLite 数据库是否存在且包含数据
3. 若数据库为空：
   a. 读取 backend/data/init.json
   b. 解析 JSON 结构
   c. 按依赖顺序写入各表（sprints -> members -> tasks -> daily_logs -> retros -> retro_ratings -> agent_messages）
   d. 记录导入日志
4. 若数据库已有数据：
   a. 跳过自动导入
   b. 正常启动服务
```

触发重新导入的方法：删除数据库文件后重启服务。

```bash
rm backend/data/sprint_agent.db
python -m uvicorn main:app --reload --port 8000
```

### 5.2 设置页拖拽导入（前端）

操作步骤：

1. 打开应用，进入**设置**页面
2. 在"数据导入"区域，将 `init.json` 文件拖拽到上传区域
3. 系统自动解析并验证文件格式
4. 预览导入数据摘要（实体数量统计）
5. 确认导入后，数据通过 `POST /api/import` 提交至后端
6. 后端验证并写入数据库
7. 导入完成后自动刷新页面

支持格式：`.json` 文件

### 5.3 API POST /api/import

接口说明：

```
POST /api/import
Content-Type: multipart/form-data

参数:
  file: File (JSON 文件，必需)
```

调用示例：

```bash
curl -X POST http://localhost:8000/api/import \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/init.json"
```

返回示例：

```json
{
  "success": true,
  "imported": {
    "sprints": 2,
    "members": 4,
    "tasks": 4,
    "daily_logs": 2,
    "retros": 4,
    "retro_ratings": 4,
    "agent_messages": 3
  }
}
```

### 5.4 API POST /api/reset

接口说明：

```
POST /api/reset

功能: 清空当前数据库，重新从 backend/data/init.json 加载数据
```

调用示例：

```bash
curl -X POST http://localhost:8000/api/reset
```

返回示例：

```json
{
  "success": true,
  "message": "Database reset and reloaded from init.json",
  "data_source": "./data/init.json"
}
```

> **警告**：`/api/reset` 会清空所有现有数据，操作不可撤销。

---

## 6. 数据导出方法

### 6.1 设置页导出（前端）

操作步骤：

1. 打开应用，进入**设置**页面
2. 在"数据导出"区域选择导出格式
3. 点击导出按钮
4. 文件自动下载到本地

支持格式：

| 格式 | 文件扩展名 | 说明 |
|------|-----------|------|
| JSON | `.json` | 完整数据结构，可直接作为 init.json 使用 |
| CSV | `.csv` | 扁平化表格格式，适合 Excel 分析 |
| Markdown | `.md` | 人类可读的报告格式 |

### 6.2 API GET /api/export

接口说明：

```
GET /api/export?format=json

参数:
  format: string (可选，默认 json)
  可选值: json, csv, markdown
```

调用示例：

```bash
# 导出 JSON
curl http://localhost:8000/api/export?format=json -o sprint_data.json

# 导出 CSV
curl http://localhost:8000/api/export?format=csv -o sprint_data.csv

# 导出 Markdown
curl http://localhost:8000/api/export?format=markdown -o sprint_report.md
```

---

## 7. 校验规则

### 7.1 文件级校验

| 规则 | 说明 | 错误处理 |
|------|------|---------|
| 必须是有效 JSON | 文件能被标准 JSON 解析器解析 | 返回解析错误信息 |
| 必须包含 sprints 数组 | 顶层必须有 `sprints` 字段 | 返回缺少字段错误 |
| 必须包含 members 数组 | 顶层必须有 `members` 字段 | 返回缺少字段错误 |
| 必须包含 tasks 数组 | 顶层必须有 `tasks` 字段 | 返回缺少字段错误 |
| 可选字段可为空数组 | `daily_logs`, `retros`, `retro_ratings`, `agent_messages` 可为 `[]` | 允许通过 |

### 7.2 实体级校验

| 实体 | 校验规则 |
|------|---------|
| Sprint | `id` 唯一且非空；`start_date` <= `end_date`；`status` 为有效枚举值 |
| Member | `id` 唯一且非空；`name` 非空；`role` 为有效枚举值；`capacity` 在 0-10 范围内 |
| Task | `id` 唯一且非空；`sprint_id` 引用存在的 Sprint；`status` 为有效枚举值；`priority` 在 1-100 范围内 |
| DailyLog | `sprint_id` 和 `member_id` 引用存在的实体；`date` 为有效日期；`hours_spent` 在 0-24 范围内 |
| Retro | `sprint_id` 引用存在的 Sprint；`category` 为有效枚举值；`votes` >= 0 |
| RetroRating | `sprint_id` 引用存在的 Sprint；`dimension` 为有效枚举值；`score` 在 1-5 范围内 |
| AgentMessage | `role` 为 `agent` / `user` / `system` 之一；`content` 非空 |

### 7.3 外键一致性校验

导入时按以下顺序写入，确保外键引用有效：

```
sprints (无依赖)
  -> members (无依赖)
    -> tasks (依赖 sprints, members)
      -> daily_logs (依赖 sprints, members)
        -> retros (依赖 sprints)
          -> retro_ratings (依赖 sprints)
            -> agent_messages (无依赖)
```

若引用的外键不存在，导入将失败并返回详细的错误信息。

---

## 8. 从 v1.0 格式迁移

### 8.1 格式变化概览

| 变更项 | v1.0 | v2.0 |
|--------|------|------|
| 文件结构 | 多个独立文件 | 单个 init.json |
| Sprint ID | 简单字符串 | `spr-xxx` 格式 |
| Member ID | 简单字符串 | `mem-xxx` 格式 |
| Task ID | 简单字符串 | `task-xxx` 格式 |
| 任务状态 | `pending`, `doing`, `completed` | `todo`, `progress`, `done`, `paused` |
| 字段命名 | 驼峰命名 | 下划线命名 |
| 日期格式 | 多种格式 | 严格 ISO `YYYY-MM-DD` |
| 新增实体 | 无 | `agent_messages` |
| 数据导入 | 手动 SQL 插入 | init.json 自动加载 |

### 8.2 状态值映射

```python
TASK_STATUS_MAP = {
    "pending": "todo",
    "doing": "progress",
    "completed": "done"
}

# v1.0 中无 "paused" 状态，迁移时可映射为 "todo"
```

### 8.3 ID 转换规则

```python
# v1.0 ID 通常为数字或短字符串，v2.0 使用带前缀格式
def convert_id(old_id: str, prefix: str) -> str:
    """将 v1.0 ID 转换为 v2.0 格式"""
    if old_id.startswith(prefix + "-"):
        return old_id  # 已经是新格式
    return f"{prefix}-{old_id.zfill(3)}"

# 示例:
# "1"    -> "spr-001"
# "user5" -> "mem-005"
# "task42" -> "task-042"
```

### 8.4 迁移步骤

1. **收集 v1.0 数据文件**：找到所有 v1.0 版本的 JSON 数据文件
2. **运行迁移脚本**：使用 `scripts/migrate_v1_to_v2.py` 自动转换
3. **验证转换结果**：检查生成的 `init.json` 是否符合本规范
4. **测试导入**：通过设置页或 API 测试导入
5. **确认数据完整性**：对比原始数据和导入后的数据

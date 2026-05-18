# Sprint Agent v2.0 API 接口文档

> 文档版本: v2.0
> 基础地址: `http://localhost:8000`
> 所有请求/响应均为 `application/json` 格式

---

## 目录

- [快速参考表](#快速参考表)
- [1. Sprint API](#1-sprint-api)
- [2. Tasks API](#2-tasks-api)
- [3. Members API](#3-members-api)
- [4. Standup API](#4-standup-api)
- [5. Retro API](#5-retro-api)
- [6. Agent API](#6-agent-api)
- [7. Settings API](#7-settingsapi)
- [附录：常用 curl 命令示例](#附录常用-curl-命令示例)

---

## 快速参考表

| 方法 | 路径 | 说明 | 对应路由 |
|------|------|------|---------|
| `GET`    | `/api/sprint` | 获取所有迭代列表 | sprint |
| `POST`   | `/api/sprint` | 创建新迭代 | sprint |
| `GET`    | `/api/sprint/{id}` | 根据 ID 获取迭代详情 | sprint |
| `PUT`    | `/api/sprint/{id}` | 更新迭代信息 | sprint |
| `DELETE` | `/api/sprint/{id}` | 删除迭代 | sprint |
| `GET`    | `/api/sprint/{id}/stats` | 获取迭代统计数据 | sprint |
| `GET`    | `/api/tasks` | 获取任务列表（支持筛选） | tasks |
| `POST`   | `/api/tasks` | 创建新任务 | tasks |
| `GET`    | `/api/tasks/{id}` | 获取任务详情 | tasks |
| `PUT`    | `/api/tasks/{id}` | 更新任务 | tasks |
| `DELETE` | `/api/tasks/{id}` | 删除任务 | tasks |
| `POST`   | `/api/tasks/{id}/move` | 移动任务状态 | tasks |
| `POST`   | `/api/tasks/bulk` | 批量更新任务 | tasks |
| `GET`    | `/api/members` | 获取成员列表 | members |
| `POST`   | `/api/members` | 创建新成员 | members |
| `GET`    | `/api/members/{id}` | 获取成员详情 | members |
| `PUT`    | `/api/members/{id}` | 更新成员信息 | members |
| `DELETE` | `/api/members/{id}` | 删除成员 | members |
| `GET`    | `/api/standup` | 获取每日站会记录 | standup |
| `POST`   | `/api/standup` | 创建/更新站会记录 | standup |
| `POST`   | `/api/standup/batch` | 批量提交站会记录 | standup |
| `GET`    | `/api/standup/yesterday` | 获取昨日站会记录 | standup |
| `GET`    | `/api/retro/{sprint_id}` | 获取回顾项目 | retro |
| `POST`   | `/api/retro` | 添加回顾项目 | retro |
| `POST`   | `/api/retro/vote` | 投票 | retro |
| `POST`   | `/api/retro/rate` | 提交评分 | retro |
| `GET`    | `/api/retro/{sprint_id}/report` | 获取回顾报告 | retro |
| `POST`   | `/api/agent/message` | 发送消息给助手 | agent |
| `GET`    | `/api/agent/history` | 获取对话历史 | agent |
| `POST`   | `/api/agent/action` | 执行 UI 动作 | agent |
| `GET`    | `/api/agent/context` | 获取助手上下文 | agent |
| `GET`    | `/api/settings` | 获取系统配置 | settings |
| `PUT`    | `/api/settings` | 更新系统配置 | settings |
| `POST`   | `/api/import` | 导入 JSON 数据 | settings |
| `GET`    | `/api/export` | 导出所有数据 | settings |
| `POST`   | `/api/reset` | 重置数据库 | settings |
| `GET`    | `/api/health` | 健康检查 | settings |

---

## 1. Sprint API

迭代 (Sprint) 是敏捷开发的核心管理单元，包含名称、目标、起止日期和状态。

### `GET /api/sprint`

获取所有迭代列表。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `status` | string | 否 | 按状态筛选：`planning` / `active` / `completed` / `cancelled` |
| `limit`  | integer | 否 | 返回数量上限，默认 100 |
| `offset` | integer | 否 | 分页偏移量，默认 0 |

**响应示例 (200)：**

```json
{
  "items": [
    {
      "id": 1,
      "name": "Sprint 1",
      "goal": "完成核心功能",
      "start_date": "2024-01-01",
      "end_date": "2024-01-14",
      "status": "active",
      "created_at": "2024-01-01T09:00:00"
    }
  ],
  "total": 1
}
```

---

### `POST /api/sprint`

创建新迭代。

**请求体 (SprintCreate)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 迭代名称，最大 255 字符 |
| `goal` | string | 否 | 迭代目标描述 |
| `start_date` | string | 是 | 开始日期，格式 `YYYY-MM-DD` |
| `end_date` | string | 是 | 结束日期，格式 `YYYY-MM-DD` |
| `status` | string | 否 | 状态，默认 `planning` |

**请求示例：**

```json
{
  "name": "Sprint 2",
  "goal": "优化性能与用户体验",
  "start_date": "2024-01-15",
  "end_date": "2024-01-28",
  "status": "planning"
}
```

**响应示例 (201)：**

```json
{
  "id": 2,
  "name": "Sprint 2",
  "goal": "优化性能与用户体验",
  "start_date": "2024-01-15",
  "end_date": "2024-01-28",
  "status": "planning",
  "created_at": "2024-01-15T08:00:00"
}
```

**错误码：**

| 状态码 | 说明 |
|--------|------|
| `422` | 参数校验失败（如日期格式错误、缺少必填字段） |

---

### `GET /api/sprint/{id}`

根据 ID 获取单个迭代详情。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 迭代唯一标识 |

**响应示例 (200)：**

```json
{
  "id": 1,
  "name": "Sprint 1",
  "goal": "完成核心功能",
  "start_date": "2024-01-01",
  "end_date": "2024-01-14",
  "status": "active",
  "created_at": "2024-01-01T09:00:00"
}
```

**错误码：**

| 状态码 | 说明 |
|--------|------|
| `404` | 指定 ID 的迭代不存在 |

---

### `PUT /api/sprint/{id}`

更新迭代信息。所有字段均可选，仅更新提供的字段。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 迭代唯一标识 |

**请求体 (SprintUpdate)：**

所有字段均为可选：

```json
{
  "name": "Sprint 1 - 已更新",
  "goal": "更新后的目标",
  "status": "completed"
}
```

**响应示例 (200)：**

```json
{
  "id": 1,
  "name": "Sprint 1 - 已更新",
  "goal": "更新后的目标",
  "start_date": "2024-01-01",
  "end_date": "2024-01-14",
  "status": "completed",
  "created_at": "2024-01-01T09:00:00"
}
```

**错误码：**

| 状态码 | 说明 |
|--------|------|
| `404` | 指定 ID 的迭代不存在 |
| `422` | 参数校验失败 |

---

### `DELETE /api/sprint/{id}`

删除迭代及其关联的所有数据（任务、站会记录、回顾项）。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 迭代唯一标识 |

**响应：** 返回 `204 No Content`，无响应体。

**错误码：**

| 状态码 | 说明 |
|--------|------|
| `404` | 指定 ID 的迭代不存在 |

---

### `GET /api/sprint/{id}/stats`

获取迭代的统计数据，包括任务分布和故事点完成情况。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 迭代唯一标识 |

**响应示例 (200)：**

```json
{
  "sprint_id": 1,
  "total_tasks": 12,
  "todo": 3,
  "progress": 5,
  "done": 4,
  "paused": 0,
  "total_story_points": 45,
  "completed_story_points": 20,
  "remaining_story_points": 25,
  "completion_rate": 44.4,
  "members_active": 4
}
```

**错误码：**

| 状态码 | 说明 |
|--------|------|
| `404` | 指定 ID 的迭代不存在 |

---

## 2. Tasks API

任务 (Task) 是迭代中的工作单元，支持状态流转、优先级设置和故事点估算。

### `GET /api/tasks`

获取任务列表，支持多条件筛选。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `sprint_id` | integer | 否 | 按迭代筛选 |
| `status` | string | 否 | 按状态筛选：`todo` / `progress` / `done` / `paused` |
| `assignee_id` | integer | 否 | 按负责人筛选 |
| `priority` | string | 否 | 按优先级筛选：`low` / `medium` / `high` / `urgent` |
| `limit` | integer | 否 | 返回数量上限，默认 100 |
| `offset` | integer | 否 | 分页偏移量，默认 0 |

**响应示例 (200)：**

```json
{
  "items": [
    {
      "id": 1,
      "title": "设计数据库表结构",
      "sprint_id": 1,
      "assignee_id": 1,
      "status": "done",
      "priority": "high",
      "story_points": 5,
      "blocked_by": null,
      "description": "设计用户、订单、商品三张核心表",
      "created_at": "2024-01-02T10:00:00",
      "updated_at": "2024-01-03T16:00:00",
      "assignee": {
        "id": 1,
        "name": "张三",
        "role": "后端开发",
        "capacity": 1.0,
        "avatar": "https://...",
        "created_at": "2024-01-01T09:00:00"
      }
    }
  ],
  "total": 12
}
```

---

### `POST /api/tasks`

创建新任务。

**请求体 (TaskCreate)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 任务标题，最大 500 字符 |
| `sprint_id` | integer | 是 | 所属迭代 ID |
| `assignee_id` | integer | 否 | 负责人 ID |
| `status` | string | 否 | 状态，默认 `todo` |
| `priority` | string | 否 | 优先级，默认 `medium` |
| `story_points` | integer | 否 | 故事点，默认 0 |
| `blocked_by` | string | 否 | 阻塞原因描述 |
| `description` | string | 否 | 任务详细描述 |

**请求示例：**

```json
{
  "title": "实现用户登录接口",
  "sprint_id": 1,
  "assignee_id": 1,
  "status": "todo",
  "priority": "high",
  "story_points": 3,
  "description": "实现 JWT Token 登录认证"
}
```

**响应示例 (201)：**

```json
{
  "id": 2,
  "title": "实现用户登录接口",
  "sprint_id": 1,
  "assignee_id": 1,
  "status": "todo",
  "priority": "high",
  "story_points": 3,
  "blocked_by": null,
  "description": "实现 JWT Token 登录认证",
  "created_at": "2024-01-05T09:00:00",
  "updated_at": "2024-01-05T09:00:00",
  "assignee": null
}
```

**错误码：**

| 状态码 | 说明 |
|--------|------|
| `422` | 参数校验失败 |
| `409` | 所属迭代或负责人不存在（外键约束） |

---

### `GET /api/tasks/{id}`

获取单个任务详情。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 任务唯一标识 |

**响应示例 (200)：** 同 `GET /api/tasks` 中的 item 结构。

**错误码：**

| 状态码 | 说明 |
|--------|------|
| `404` | 指定 ID 的任务不存在 |

---

### `PUT /api/tasks/{id}`

更新任务信息，所有字段可选。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 任务唯一标识 |

**请求体 (TaskUpdate)：**

```json
{
  "status": "progress",
  "assignee_id": 2,
  "story_points": 5
}
```

**响应示例 (200)：** 返回更新后的完整任务对象。

**错误码：**

| 状态码 | 说明 |
|--------|------|
| `404` | 任务不存在 |
| `409` | 更新的迭代或负责人不存在 |

---

### `DELETE /api/tasks/{id}`

删除任务。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 任务唯一标识 |

**响应：** `204 No Content`

---

### `POST /api/tasks/{id}/move`

移动任务到不同状态列（看板拖拽操作）。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 任务唯一标识 |

**请求体 (TaskMove)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `status` | string | 是 | 目标状态：`todo` / `progress` / `done` / `paused` |

**请求示例：**

```json
{
  "status": "done"
}
```

**响应示例 (200)：** 返回更新后的任务对象。

---

### `POST /api/tasks/bulk`

批量更新多个任务的属性。

**请求体 (BulkTaskUpdate)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `ids` | integer[] | 是 | 要更新的任务 ID 列表 |
| `status` | string | 否 | 统一设置的状态 |
| `assignee_id` | integer | 否 | 统一设置的负责人 |
| `sprint_id` | integer | 否 | 统一设置的迭代 |

**请求示例：**

```json
{
  "ids": [1, 2, 3],
  "status": "progress",
  "assignee_id": 2
}
```

**响应示例 (200)：**

```json
{
  "updated": 3,
  "ids": [1, 2, 3]
}
```

---

## 3. Members API

成员 (Member) 代表敏捷团队中的参与人员，包含姓名、角色、容量系数等信息。

### `GET /api/members`

获取所有成员列表。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `role` | string | 否 | 按角色筛选 |
| `limit` | integer | 否 | 返回数量上限，默认 100 |

**响应示例 (200)：**

```json
{
  "items": [
    {
      "id": 1,
      "name": "张三",
      "role": "后端开发",
      "capacity": 1.0,
      "avatar": "https://example.com/avatar1.png",
      "created_at": "2024-01-01T09:00:00"
    },
    {
      "id": 2,
      "name": "李四",
      "role": "前端开发",
      "capacity": 0.8,
      "avatar": "https://example.com/avatar2.png",
      "created_at": "2024-01-01T09:00:00"
    }
  ],
  "total": 4
}
```

---

### `POST /api/members`

创建新成员。

**请求体 (MemberCreate)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 成员姓名 |
| `role` | string | 是 | 角色（如"后端开发"、"产品经理"） |
| `capacity` | float | 否 | 容量系数（0.1 ~ 1.0），默认 1.0 |
| `avatar` | string | 否 | 头像图片 URL |

**请求示例：**

```json
{
  "name": "王五",
  "role": "测试工程师",
  "capacity": 0.9,
  "avatar": "https://example.com/avatar3.png"
}
```

**响应示例 (201)：**

```json
{
  "id": 3,
  "name": "王五",
  "role": "测试工程师",
  "capacity": 0.9,
  "avatar": "https://example.com/avatar3.png",
  "created_at": "2024-01-06T10:00:00"
}
```

---

### `GET /api/members/{id}`

获取单个成员详情。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 成员唯一标识 |

**响应示例 (200)：** 同 `GET /api/members` 中的 item 结构。

**错误码：** `404` — 成员不存在

---

### `PUT /api/members/{id}`

更新成员信息，所有字段可选。

**路径参数：** `id` (integer) — 成员唯一标识

**请求体 (MemberUpdate)：**

```json
{
  "role": "高级后端开发",
  "capacity": 0.7
}
```

**响应示例 (200)：** 返回更新后的成员对象。

**错误码：** `404` — 成员不存在

---

### `DELETE /api/members/{id}`

删除成员。若该成员有关联任务，需先解除关联或一并处理。

**路径参数：** `id` (integer) — 成员唯一标识

**响应：** `204 No Content`

**错误码：** `404` — 成员不存在；`409` — 成员有关联任务

---

## 4. Standup API

每日站会 (Standup/DailyLog) 记录团队成员每天的工作内容、计划和阻塞项。

### `GET /api/standup`

获取每日站会记录列表。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `date` | string | 否 | 按日期筛选，格式 `YYYY-MM-DD` |
| `sprint_id` | integer | 否 | 按迭代筛选 |
| `member_id` | integer | 否 | 按成员筛选 |
| `limit` | integer | 否 | 返回数量上限，默认 100 |

**响应示例 (200)：**

```json
{
  "items": [
    {
      "id": 1,
      "sprint_id": 1,
      "member_id": 1,
      "date": "2024-01-08",
      "completed": "完成了用户登录接口",
      "planned": "今天做权限验证模块",
      "blockers": "等待设计稿确认",
      "hours_spent": 7.5,
      "created_at": "2024-01-08T09:30:00",
      "member": {
        "id": 1,
        "name": "张三",
        "role": "后端开发",
        "capacity": 1.0,
        "avatar": "https://...",
        "created_at": "2024-01-01T09:00:00"
      }
    }
  ],
  "total": 4
}
```

---

### `POST /api/standup`

创建或更新每日站会记录。若该成员当天已有记录则更新，否则创建。

**请求体 (DailyLogCreate)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `sprint_id` | integer | 是 | 所属迭代 ID |
| `member_id` | integer | 是 | 成员 ID |
| `date` | string | 是 | 日期 `YYYY-MM-DD` |
| `completed` | string | 否 | 已完成工作内容 |
| `planned` | string | 否 | 计划工作内容 |
| `blockers` | string | 否 | 阻塞项描述 |
| `hours_spent` | float | 否 | 工时投入，默认 0 |

**请求示例：**

```json
{
  "sprint_id": 1,
  "member_id": 1,
  "date": "2024-01-09",
  "completed": "完成了权限验证模块",
  "planned": " tomorrow 做订单接口",
  "blockers": null,
  "hours_spent": 8.0
}
```

**响应示例 (201/200)：** 返回创建/更新后的记录。

---

### `POST /api/standup/batch`

批量提交多个成员的站会记录。

**请求体 (BatchDailyLog)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `logs` | DailyLogCreate[] | 是 | 日志记录数组 |

**请求示例：**

```json
{
  "logs": [
    {
      "sprint_id": 1,
      "member_id": 1,
      "date": "2024-01-09",
      "completed": "完成 A 功能",
      "planned": "做 B 功能",
      "blockers": null,
      "hours_spent": 8.0
    },
    {
      "sprint_id": 1,
      "member_id": 2,
      "date": "2024-01-09",
      "completed": "完成 UI 设计",
      "planned": "做前端页面",
      "blockers": "需要接口文档",
      "hours_spent": 7.0
    }
  ]
}
```

**响应示例 (201)：**

```json
{
  "created": 2,
  "updated": 0,
  "logs": [...]
}
```

---

### `GET /api/standup/yesterday`

获取昨天的站会记录（快捷接口）。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `sprint_id` | integer | 否 | 按迭代筛选 |

**响应格式：** 同 `GET /api/standup`。

---

## 5. Retro API

回顾会议 (Retro) 用于收集团队成员对迭代的反馈，包含喜欢 (liked)、不喜欢 (disliked) 和行动项 (action) 三类。

### `GET /api/retro/{sprint_id}`

获取指定迭代的回顾项目列表。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `sprint_id` | integer | 迭代唯一标识 |

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `category` | string | 否 | 按类别筛选：`liked` / `disliked` / `action` |

**响应示例 (200)：**

```json
{
  "sprint_id": 1,
  "items": [
    {
      "id": 1,
      "sprint_id": 1,
      "category": "liked",
      "item": "代码评审流程很高效",
      "votes": 5,
      "created_at": "2024-01-14T15:00:00"
    },
    {
      "id": 2,
      "sprint_id": 1,
      "category": "action",
      "item": "增加自动化测试覆盖率",
      "votes": 3,
      "created_at": "2024-01-14T15:30:00"
    }
  ],
  "total": 6
}
```

---

### `POST /api/retro`

添加回顾项目。

**请求体 (RetroCreate)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `sprint_id` | integer | 是 | 所属迭代 ID |
| `category` | string | 是 | 类别：`liked` / `disliked` / `action` |
| `item` | string | 是 | 回顾内容 |
| `votes` | integer | 否 | 初始票数，默认 0 |

**请求示例：**

```json
{
  "sprint_id": 1,
  "category": "liked",
  "item": "每日站会时间控制得很好",
  "votes": 0
}
```

**响应示例 (201)：**

```json
{
  "id": 3,
  "sprint_id": 1,
  "category": "liked",
  "item": "每日站会时间控制得很好",
  "votes": 0,
  "created_at": "2024-01-14T16:00:00"
}
```

---

### `POST /api/retro/vote`

为回顾项目投票（点赞）。

**请求体：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `retro_id` | integer | 是 | 回顾项目 ID |

**请求示例：**

```json
{
  "retro_id": 1
}
```

**响应示例 (200)：**

```json
{
  "id": 1,
  "votes": 6
}
```

---

### `POST /api/retro/rate`

提交回顾评分（多维度打分）。

**请求体 (RetroRatingCreate)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `sprint_id` | integer | 是 | 迭代 ID |
| `dimension` | string | 是 | 评分维度（如"协作"、"交付"、"质量"） |
| `score` | integer | 是 | 分数 1-5 |

**请求示例：**

```json
{
  "sprint_id": 1,
  "dimension": "协作",
  "score": 4
}
```

**响应示例 (201)：**

```json
{
  "id": 1,
  "sprint_id": 1,
  "dimension": "协作",
  "score": 4,
  "created_at": "2024-01-14T17:00:00"
}
```

---

### `GET /api/retro/{sprint_id}/report`

生成完整的回顾报告，包含评分、回顾项和自动摘要。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `sprint_id` | integer | 迭代唯一标识 |

**响应示例 (200) — RetroReport：**

```json
{
  "sprint": {
    "id": 1,
    "name": "Sprint 1",
    "goal": "完成核心功能",
    "start_date": "2024-01-01",
    "end_date": "2024-01-14",
    "status": "completed"
  },
  "ratings": [
    { "dimension": "协作", "score": 4.5 },
    { "dimension": "交付", "score": 4.0 },
    { "dimension": "质量", "score": 3.5 }
  ],
  "items": {
    "liked": [
      { "item": "代码评审流程很高效", "votes": 5 },
      { "item": "每日站会时间控制得很好", "votes": 3 }
    ],
    "disliked": [
      { "item": "需求变更太频繁", "votes": 4 }
    ],
    "action": [
      { "item": "增加自动化测试覆盖率", "votes": 3 },
      { "item": "需求评审前置", "votes": 2 }
    ]
  },
  "summary": "本次迭代整体表现良好，协作顺畅。主要改进方向：需求管理和测试覆盖。"
}
```

---

## 6. Agent API

智能助手 (Agent) 提供自然语言交互能力，支持任务管理、站会记录、状态更新等操作。

### `POST /api/agent/message`

发送消息给智能助手，获取回复。

**请求体 (AgentMessageCreate)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message` | string | 是 | 用户消息内容 |
| `context` | object | 否 | 上下文信息（当前页面、选中任务等） |

**请求示例：**

```json
{
  "message": "把任务 #3 标记为已完成",
  "context": {
    "current_page": "board",
    "sprint_id": 1,
    "selected_task": 3
  }
}
```

**响应示例 (200) — AgentMessageResponse：**

```json
{
  "id": 5,
  "role": "assistant",
  "content": "已将任务「实现用户登录接口」(#3) 标记为 done。",
  "context": {
    "intent": "update_status",
    "action": {
      "action": "update_task_status",
      "parameters": { "task_id": 3, "status": "done" }
    }
  },
  "created_at": "2024-01-09T10:00:00"
}
```

---

### `GET /api/agent/history`

获取对话历史记录。

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `limit` | integer | 否 | 返回数量，默认 50 |
| `offset` | integer | 否 | 偏移量，默认 0 |

**响应示例 (200)：**

```json
{
  "items": [
    {
      "id": 4,
      "role": "user",
      "content": "把任务 #3 标记为已完成",
      "context": null,
      "created_at": "2024-01-09T10:00:00"
    },
    {
      "id": 5,
      "role": "assistant",
      "content": "已将任务标记为 done。",
      "context": { "intent": "update_status" },
      "created_at": "2024-01-09T10:00:01"
    }
  ],
  "total": 6
}
```

---

### `POST /api/agent/action`

执行 UI 动作（由前端调用，助手决定执行）。

**请求体 (AgentAction)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `action` | string | 是 | 动作名称 |
| `parameters` | object | 否 | 动作参数 |

**请求示例：**

```json
{
  "action": "navigate",
  "parameters": {
    "page": "sprint_board",
    "sprint_id": 1
  }
}
```

**响应示例 (200)：**

```json
{
  "success": true,
  "message": "导航已执行"
}
```

---

### `GET /api/agent/context`

获取助手当前上下文，包括当前迭代、任务、成员等信息。

**响应示例 (200) — AgentContext：**

```json
{
  "current_page": "board",
  "sprint_id": 1,
  "selected_task": 3,
  "members": [
    { "id": 1, "name": "张三", "role": "后端开发" },
    { "id": 2, "name": "李四", "role": "前端开发" }
  ],
  "tasks": [
    { "id": 1, "title": "设计数据库", "status": "done" },
    { "id": 2, "title": "实现登录", "status": "progress" },
    { "id": 3, "title": "做权限", "status": "todo" }
  ]
}
```

---

## 7. Settings/Import/Export API

系统设置、数据导入导出和运维管理接口。

### `GET /api/settings`

获取系统配置项。

**响应示例 (200)：**

```json
{
  "team_name": "卓越研发团队",
  "sprint_duration": 14,
  "work_hours_per_day": 8,
  "theme": "light",
  "language": "zh-CN",
  "enable_agent": true,
  "updated_at": "2024-01-01T09:00:00"
}
```

---

### `PUT /api/settings`

更新系统配置项。

**请求体：** 配置键值对对象，所有字段可选。

**请求示例：**

```json
{
  "team_name": "新团队名称",
  "sprint_duration": 10,
  "theme": "dark"
}
```

**响应示例 (200)：** 返回更新后的完整配置。

---

### `POST /api/import`

导入 JSON 数据，支持批量导入所有业务数据。

**请求体：** 符合 `init.json` 格式的完整数据对象。

**请求示例：**

```json
{
  "sprints": [...],
  "members": [...],
  "tasks": [...],
  "daily_logs": [...],
  "retros": [...],
  "retro_ratings": [...]
}
```

**响应示例 (200)：**

```json
{
  "success": true,
  "imported": {
    "sprints": 2,
    "members": 4,
    "tasks": 15,
    "daily_logs": 20,
    "retros": 8,
    "retro_ratings": 6
  }
}
```

**错误码：** `422` — JSON 格式错误；`409` — 数据冲突

---

### `GET /api/export`

导出所有数据为 JSON 格式。

**响应示例 (200)：** 返回与导入格式一致的完整数据 JSON。

```json
{
  "sprints": [...],
  "members": [...],
  "tasks": [...],
  "daily_logs": [...],
  "retros": [...],
  "retro_ratings": [...]
}
```

---

### `POST /api/reset`

重置数据库并重新加载 `init.json`。

> **警告：** 此操作会清空所有现有数据，请谨慎使用。

**请求体：** 可选，可指定自定义数据源路径。

```json
{
  "confirm": true,
  "source": "data/init.json"
}
```

**响应示例 (200)：**

```json
{
  "success": true,
  "message": "数据库已重置并重新加载初始数据",
  "loaded_items": {
    "sprints": 1,
    "members": 3,
    "tasks": 8
  }
}
```

---

### `GET /api/health`

健康检查接口，用于监控服务状态。

**响应示例 (200)：**

```json
{
  "status": "ok",
  "version": "2.0.0",
  "database": "connected",
  "timestamp": "2024-01-09T10:00:00"
}
```

**错误码：** `503` — 数据库连接异常

---

## 附录：常用 curl 命令示例

### Sprint 操作

```bash
# 创建迭代
curl -X POST http://localhost:8000/api/sprint \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sprint 1",
    "goal": "完成 MVP 版本",
    "start_date": "2024-01-01",
    "end_date": "2024-01-14",
    "status": "active"
  }'

# 获取所有迭代
curl http://localhost:8000/api/sprint

# 获取单个迭代
curl http://localhost:8000/api/sprint/1

# 更新迭代状态
curl -X PUT http://localhost:8000/api/sprint/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'

# 删除迭代
curl -X DELETE http://localhost:8000/api/sprint/1

# 获取迭代统计
curl http://localhost:8000/api/sprint/1/stats
```

### Task 操作

```bash
# 创建任务
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "实现用户注册接口",
    "sprint_id": 1,
    "assignee_id": 1,
    "status": "todo",
    "priority": "high",
    "story_points": 5,
    "description": "包含邮箱验证和密码加密"
  }'

# 按迭代筛选任务
curl "http://localhost:8000/api/tasks?sprint_id=1&status=todo"

# 移动任务状态
curl -X POST http://localhost:8000/api/tasks/1/move \
  -H "Content-Type: application/json" \
  -d '{"status": "progress"}'

# 批量更新任务
curl -X POST http://localhost:8000/api/tasks/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "ids": [1, 2, 3],
    "status": "progress",
    "assignee_id": 2
  }'
```

### Member 操作

```bash
# 创建成员
curl -X POST http://localhost:8000/api/members \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张三",
    "role": "后端开发",
    "capacity": 1.0
  }'

# 获取所有成员
curl http://localhost:8000/api/members

# 更新成员
curl -X PUT http://localhost:8000/api/members/1 \
  -H "Content-Type: application/json" \
  -d '{"capacity": 0.8}'
```

### Standup 操作

```bash
# 提交站会记录
curl -X POST http://localhost:8000/api/standup \
  -H "Content-Type: application/json" \
  -d '{
    "sprint_id": 1,
    "member_id": 1,
    "date": "2024-01-09",
    "completed": "完成了登录接口",
    "planned": "做权限模块",
    "blockers": null,
    "hours_spent": 8.0
  }'

# 批量提交站会
curl -X POST http://localhost:8000/api/standup/batch \
  -H "Content-Type: application/json" \
  -d '{
    "logs": [
      {
        "sprint_id": 1,
        "member_id": 1,
        "date": "2024-01-09",
        "completed": "完成 A",
        "planned": "做 B",
        "blockers": null,
        "hours_spent": 8.0
      },
      {
        "sprint_id": 1,
        "member_id": 2,
        "date": "2024-01-09",
        "completed": "完成 UI",
        "planned": "做页面",
        "blockers": "等接口",
        "hours_spent": 7.0
      }
    ]
  }'

# 获取昨日站会
curl "http://localhost:8000/api/standup/yesterday?sprint_id=1"
```

### Retro 操作

```bash
# 添加回顾项
curl -X POST http://localhost:8000/api/retro \
  -H "Content-Type: application/json" \
  -d '{
    "sprint_id": 1,
    "category": "liked",
    "item": "团队协作很顺畅"
  }'

# 投票
curl -X POST http://localhost:8000/api/retro/vote \
  -H "Content-Type: application/json" \
  -d '{"retro_id": 1}'

# 提交评分
curl -X POST http://localhost:8000/api/retro/rate \
  -H "Content-Type: application/json" \
  -d '{
    "sprint_id": 1,
    "dimension": "协作",
    "score": 5
  }'

# 获取回顾报告
curl http://localhost:8000/api/retro/1/report
```

### Agent 操作

```bash
# 发送消息
curl -X POST http://localhost:8000/api/agent/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "把任务 #3 标记为完成",
    "context": {
      "current_page": "board",
      "sprint_id": 1
    }
  }'

# 获取对话历史
curl http://localhost:8000/api/agent/history

# 获取助手上下文
curl http://localhost:8000/api/agent/context
```

### 数据管理

```bash
# 导出数据
curl http://localhost:8000/api/export > backup.json

# 导入数据
curl -X POST http://localhost:8000/api/import \
  -H "Content-Type: application/json" \
  -d @backup.json

# 健康检查
curl http://localhost:8000/api/health

# 重置数据库
curl -X POST http://localhost:8000/api/reset \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```

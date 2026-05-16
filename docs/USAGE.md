# Sprint Agent 使用手册

## 📋 目录

1. [看板操作](#看板操作)
2. [CLI 命令](#cli-命令)
3. [API 接口](#api-接口)
4. [Sprint 生命周期](#sprint-生命周期)
5. [常见问题](#常见问题)

---

## 🖱️ 看板操作

### 访问看板

打开浏览器访问 http://localhost:8080

### 界面说明

```
┌─────────────────────────────────────────────────────┐
│ 📋 Sprint Agent 看板    5.12-5.23 (2026-05-12~23)   │
│ [🔄 刷新] [➕ 新建任务]                              │
├─────────────────────────────────────────────────────┤
│ 成员:7 任务:12 已完成:3 进行中:5 总预估:45 已投入:28 │
├─────────────────────────────────────────────────────┤
│  📋 未开始[4]  │  🏃 进行中[5]  │  ✅ 已完成[3]  │  ⏸️ 挂起[0]  │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐       │
│  │ 任务A     │  │ 任务B     │  │ 任务C     │       │
│  │ 👤 张三   │  │ 👤 李四   │  │ 👤 王五   │       │
│  │ ⏱️ 0/5天  │  │ ⏱️ 3/8天  │  │ ⏱️ 5/5天  │       │
│  │ [████░░░░]│  │ [███████░]│  │ [████████]│       │
│  └───────────┘  └───────────┘  └───────────┘       │
│  ┌───────────┐  ┌───────────┐                        │
│  │ 任务D ⚠️  │  │ 任务E ⏰  │                        │
│  │ ⚠️ 阻塞    │  │ 逾期      │                        │
│  └───────────┘  └───────────┘                        │
└─────────────────────────────────────────────────────┘
```

### 操作指南

| 操作 | 方式 | 说明 |
|------|------|------|
| **移动任务** | 拖拽 | 将卡片拖到别的列，自动更新状态 |
| **查看详情** | 点击卡片 | 弹出详情窗口，显示进度、日报、阻塞 |
| **新建任务** | 点击「➕ 新建任务」 | 填写表单创建新任务 |
| **刷新数据** | 点击「🔄 刷新」 | 重新加载最新数据 |

### 新建任务

点击「➕ 新建任务」按钮，填写：

- **任务名称** — 简短描述
- **负责人** — 下拉选择团队成员
- **预估工作量** — 低头/抬头预估（人天）
- **优先级** — 1-10，越高越紧急
- **截止日期** — 可选
- **公共任务** — 勾选则为团队公共任务（如站会、MR审阅）

### 卡片颜色说明

| 标识 | 含义 |
|------|------|
| 左边红条 | 高优先级 (≥7) |
| 左边黄条 | 中优先级 (4-6) |
| 左边绿条 | 低优先级 (≤3) |
| 🔵 蓝色标签 | 公共任务 |
| ⚠️ 红色标签 | 有阻塞 |
| ⏰ 红色标签 | 已逾期 |

---

## ⌨️ CLI 命令

除了看板，Sprint Agent 也支持命令行交互。

### 启动 CLI

```bash
python main.py
```

### Planning（迭代规划）

```bash
# 创建 Sprint
/planning start 5.12-5.23 2026-05-12 2026-05-23

# 添加成员
/planning add-member 罗三五 0.5
/planning add-member 潘邦力 0.9

# 添加任务（交互式）
/planning add-task
# 然后输入: 统一治理LLD | 罗三五 | 2.0 | 3.4 | 8 | 2026-05-08

# 直接指定任务信息
/planning add-task 统一治理LLD | 罗三五 | 2.0 | 3.4

# 设置预估
/planning estimate 统一治理LLD 2.0 3.4

# 分配任务
/planning assign 统一治理LLD 罗三五

# 设置 Sprint 目标
/planning goal 完成统一治理模块迁移

# 启动 Sprint
/planning finalize
```

### Daily Standup（日报）

```bash
# 查看今日任务列表
/standup

# 提交日报（结构化）
/standup 1 2h 60% 等峰哥确认接口
# 参数: 任务序号 耗时 进度% 阻塞

# 自然语言日报
"今天在做统一治理LLD，花了2小时，进度60%，等峰哥确认接口"
```

日报后 Agent 会自动追问（可 `/skip` 跳过）：
- 任务完成时："有没有用到更高效的方法？"
- 高难度完成时："最有挑战的部分是什么？"
- 顺手修复时："对团队有什么帮助？"

### Admin（管理）

```bash
# 请假登记
/leave 2 2026-05-15

# 挂起任务（只有 SM 可操作）
/pause 统一治理LLD

# 恢复任务
/resume 统一治理LLD

# 重新分配
/reassign 统一治理LLD 潘邦力
```

### Query（查询）

```bash
# 个人状态
/status 罗三五

# 团队看板（晾晒）
/dashboard
```

### Retro（回顾）

```bash
# 本 Sprint retro
/retro

# 跨 Sprint 趋势分析
/retro trend 3
```

### Self-Assessment（自评）

```bash
# 生成自评表
/assessment generate 2026H1

# 确认事迹
/assessment confirm story-id-xxx

# Review checklist
/assessment review
```

---

## 📡 API 接口

### 接口列表

| 方法 | 路径 | 请求体 | 说明 |
|------|------|--------|------|
| GET | `/api/health` | - | 健康检查 |
| GET | `/api/sprint` | - | 获取当前 Sprint |
| GET | `/api/board` | - | 获取看板数据 |
| POST | `/api/sprint` | `SprintCreate` | 创建 Sprint |
| POST | `/api/sprint/finalize` | - | 启动 Sprint |
| POST | `/api/members` | `MemberCreate` | 添加成员 |
| POST | `/api/tasks` | `TaskCreate` | 添加任务 |
| PATCH | `/api/tasks/{id}/status` | `StatusUpdate` | 更新状态 |
| POST | `/api/daily-log` | `DailyLogCreate` | 添加日报 |
| GET | `/api/dashboard` | - | 团队看板文本 |
| GET | `/api/members/{name}/status` | - | 个人状态 |
| POST | `/api/retro` | `RetroRequest` | 生成 Retro |
| POST | `/api/assessment` | `AssessmentRequest` | 生成自评表 |

### 请求示例

#### 创建 Sprint

```bash
curl -X POST http://localhost:8080/api/sprint \
  -H "Content-Type: application/json" \
  -d '{
    "name": "5.12-5.23",
    "start_date": "2026-05-12",
    "end_date": "2026-05-23",
    "workdays": 10
  }'
```

#### 添加成员

```bash
curl -X POST http://localhost:8080/api/members \
  -H "Content-Type: application/json" \
  -d '{
    "name": "罗三五",
    "coefficient": 0.5
  }'
```

#### 添加任务

```bash
curl -X POST http://localhost:8080/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "统一治理LLD",
    "owner_name": "罗三五",
    "estimate_low": 2.0,
    "estimate_high": 3.4,
    "priority": 8,
    "ddl": "2026-05-20"
  }'
```

#### 更新任务状态

```bash
curl -X PATCH http://localhost:8080/api/tasks/t_xxx/status \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

#### 添加日报

```bash
curl -X POST http://localhost:8080/api/daily-log \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "t_xxx",
    "member_id": "m_罗三五",
    "hours": 2.0,
    "progress_percent": 60,
    "blocker": "等峰哥确认接口"
  }'
```

### 响应格式

所有 API 返回统一格式：

```json
{
  "success": true,
  "data": { ... }
}
```

错误时：

```json
{
  "detail": "错误信息"
}
```

---

## 🔄 Sprint 生命周期

### Phase 1: Planning（规划）

1. SM 创建 Sprint：`/planning start`
2. 添加团队成员：`/planning add-member`
3. 录入需求任务：`/planning add-task`
4. 分配负责人：`/planning assign`
5. 工作量预估：`/planning estimate`
6. 启动 Sprint：`/planning finalize`

### Phase 2: Daily Standup（日报）

每天团队成员提交日报：

1. 查看任务：`/standup`
2. 填报进度：`/standup <序号> <耗时> [进度] [阻塞]`
3. 回答追问（如有）
4. SM 查看看板：`/dashboard`

### Phase 3: Retro（回顾）

Sprint 结束时：

1. 生成本 Sprint 回顾：`/retro`
2. 生成跨 Sprint 趋势：`/retro trend 3`
3. 查看报告文件：`data/retro/retro-xxx.md`

### Phase 4: Self-Assessment（自评）

半年度/年度：

1. 生成自评表：`/assessment generate 2026H1`
2. 补充事迹细节
3. Review checklist：`/assessment review`
4. 导出 Markdown 文件

---

## ❓ 常见问题

### Q: 看板显示"无活跃 Sprint"

A: 需要先创建 Sprint。通过 CLI 执行 `/planning start`，或通过 API POST `/api/sprint`。

### Q: 拖拽卡片后状态没保存

A: 检查 API 服务是否正常运行：`curl http://localhost:8080/api/health`

### Q: 如何修改已有任务信息

A: 当前版本需直接编辑 `data/active/active_sprint.json` 文件，或使用 CLI 命令。

### Q: 数据存在哪里

A: 所有数据在 `data/` 目录：
- `data/active/active_sprint.json` — 当前 Sprint
- `data/sprints/*.json` — 历史 Sprint
- `data/story_pool/pool.json` — 事迹池
- `data/retro/*.md` — Retro 报告
- `data/assessments/*.md` — 自评表

### Q: 如何备份数据

A: 直接复制 `data/` 目录即可，所有数据都是 JSON/Markdown 文本文件。

### Q: 支持多人同时编辑吗

A: 看板读取是实时的，但写入没有并发锁。建议团队协商编辑时间，或先通过 CLI/API 录入数据。

---

## 📊 术语表

| 术语 | 说明 |
|------|------|
| **人天** | 工作量单位，1人天 = 1人工作1天 |
| **低头预估** | 乐观估算（最少需要多少时间） |
| **抬头预估** | 悲观估算（最多需要多少时间） |
| **COE 系数** | 成员效率系数，用于计算实际容量 |
| **难易度** | 实际/预估 (<1 偏难，>1 偏易) |
| **可信度** | 预估/实际 (>1 偏乐观，<1 偏悲观) |
| **STAR** | Situation-Task-Action-Result，事迹描述格式 |
| **Interview/Grill** | Standup 中的主动追问机制 |
| **Story Pool** | 事迹候选池，用于自评表生成 |
| **晾晒** | 透明展示团队状态，便于发现问题 |
| **挂起** | 任务暂停，只有 SM 可操作 |
| **公共任务** | 团队共享任务（站会、MR审阅、Oncall等） |

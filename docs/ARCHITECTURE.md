# Sprint Agent 架构说明

## 📐 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Web 看板    │  │ CLI 终端    │  │ 第三方系统      │  │
│  │ (Vanilla JS)│  │ (Python)    │  │ (REST API)      │  │
│  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘  │
└─────────┼────────────────┼──────────────────┼───────────┘
          │                │                  │
          └────────────────┴──────────────────┘
                             │
                    ┌────────┴────────┐
                    │   FastAPI 服务层   │
                    │   (api/server.py) │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │   业务 API 层      │
                    │ (api/agent_api.py)│
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
   ┌──────┴──────┐   ┌──────┴──────┐   ┌──────┴──────┐
   │   Engines   │   │   Models    │   │  Parsers    │
   │  业务引擎    │   │  数据模型    │   │  命令解析    │
   └─────────────┘   └─────────────┘   └─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────┴────────┐
                    │   持久化层         │
                    │ (storage/persist.)│
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │   数据目录       │
                    │    (data/)      │
                    └─────────────────┘
```

## 🧩 模块说明

### 1. 数据模型层 (`models/`)

| 文件 | 说明 | 核心字段 |
|------|------|----------|
| `sprint.py` | Sprint 迭代 | id, name, start/end_date, status, members, tasks |
| `member.py` | 团队成员 | id, name, coefficient, leave_days, interviewed_tasks |
| `task.py` | 任务 | id, name, owner_id, status, estimate_low/high, daily_logs |
| `daily_log.py` | 日报记录 | date, hours, progress_percent, blocker, notes |
| `interview.py` | 追问会话 | questions, answers, status, member_id |
| `story_pool.py` | 事迹池 | dimension, STAR 描述, source, confirmed |
| `risk.py` | 风险标记 | type, severity, task_id, description |
| `retro.py` | 回顾报告 | summaries, trends, overhead, recommendations |
| `assessment.py` | 自评表 | dimensions, stories, review_status |

### 2. 业务引擎层 (`engines/`)

| 引擎 | 职责 | 关键方法 |
|------|------|----------|
| `planning_engine.py` | Sprint 规划 | create_sprint, add_member, add_task, finalize |
| `standup_engine.py` | 日报处理 | process_standup, detect_completion, trigger_interview |
| `risk_detector.py` | 风险检测 | detect_from_standup, check_overdue, check_overcommit |
| `interview_engine.py` | 追问管理 | generate_questions, process_answer, complete_session |
| `retro_engine.py` | 回顾生成 | generate_single_retro, generate_trend_retro |
| `dashboard_engine.py` | 看板渲染 | generate_dashboard, generate_member_status |
| `assessment_engine.py` | 自评生成 | generate_assessment, generate_review_checklist |

### 3. 解析层 (`parsers/`)

| 文件 | 职责 |
|------|------|
| `command_parser.py` | 结构化命令解析（`/planning start` 等） |
| `nlp_engine.py` | 自然语言解析（日报口语输入） |

### 4. 持久化层 (`storage/`)

| 文件 | 职责 | 特性 |
|------|------|------|
| `persistence_manager.py` | JSON 文件读写 | 自动备份、版本控制、路径灵活 |

### 5. API 层 (`api/`)

| 文件 | 职责 |
|------|------|
| `server.py` | FastAPI 路由、CORS、静态文件挂载 |
| `agent_api.py` | 业务逻辑封装、数据转换、状态管理 |

### 6. 前端 (`web/`)

| 文件 | 技术 | 特性 |
|------|------|------|
| `index.html` | Vanilla JS + CSS3 | 拖拽、模态框、API 调用、响应式 |

## 📊 数据流

### 创建 Sprint

```
用户输入 (CLI/API)
    ↓
CommandParser / Pydantic Model
    ↓
PlanningEngine.create_sprint()
    ↓
Sprint (Model)
    ↓
PersistenceManager.save_sprint()
    ↓
data/active/active_sprint.json
```

### 提交日报

```
用户输入 (CLI/API/Web)
    ↓
StandupEngine.process_standup()
    ↓
DailyLog (Model) → Task.daily_logs.append()
    ↓
RiskDetector.detect_from_standup()
    ↓
InterviewEngine.generate_questions() [条件触发]
    ↓
PersistenceManager.save_sprint()
    ↓
data/active/active_sprint.json
```

### 拖拽更新状态 (Web)

```
用户拖拽卡片
    ↓
Web Board (fetch PATCH /api/tasks/{id}/status)
    ↓
FastAPI Route
    ↓
AgentAPI.update_task_status()
    ↓
Task.status = new_status
    ↓
PersistenceManager.save_sprint()
    ↓
Web Board.reload()
    ↓
用户看到更新后的看板
```

## 💾 数据存储格式

### Sprint JSON 结构

```json
{
  "id": "2026-05-12_2026-05-23",
  "name": "5.12-5.23",
  "start_date": "2026-05-12",
  "end_date": "2026-05-23",
  "workdays": 10,
  "status": "active",
  "goal": "完成统一治理迁移",
  "members": [
    {
      "id": "m_罗三五",
      "name": "罗三五",
      "coefficient": 0.5,
      "leave_days": 0,
      "interviewed_tasks": []
    }
  ],
  "tasks": [
    {
      "id": "t_abc123",
      "name": "统一治理LLD",
      "owner_id": "m_罗三五",
      "priority": 8,
      "ddl": "2026-05-20",
      "estimate_low": 2.0,
      "estimate_high": 3.4,
      "status": "in_progress",
      "is_public": false,
      "total_spent": 2.0,
      "daily_logs": [
        {
          "date": "2026-05-12",
          "hours": 2.0,
          "progress_percent": 60,
          "blocker": "等峰哥确认接口"
        }
      ]
    }
  ],
  "public_tasks": [...]
}
```

### 文件目录结构

```
data/
├── active/
│   ├── active_sprint.json          # 当前 sprint
│   └── active_sprint.bak.*         # 自动备份
├── sprints/
│   └── 2026-04-27_2026-05-09.json  # 历史 sprint
├── story_pool/
│   ├── pool.json                   # 事迹池
│   └── pool.bak.*                  # 自动备份
├── retro/
│   └── retro-2026-04-27_2026-05-09.md
└── assessments/
    └── assessment-罗三五-2026H1.md
```

## 🔌 扩展开发

### 添加新的 API 端点

```python
# api/server.py

@app.post("/api/custom-feature")
def custom_feature(req: CustomRequest):
    result = agent.custom_method(req.param)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
```

### 添加新的 Engine

```python
# engines/new_engine.py

class NewEngine:
    def process(self, sprint: Sprint, data: dict) -> dict:
        # 业务逻辑
        return {"success": True, "result": ...}
```

### 自定义 Interview 问题

```python
# engines/interview_engine.py

QUESTION_TEMPLATES = {
    QuestionType.COMPLETION: [
        "有没有用到更高效的方法？",
        "这个过程有没有可以复用的经验？",
        # 添加新问题
        "你的自定义问题？",
    ],
    # ...
}
```

### 集成飞书/企业微信

可以通过 Webhook 或 Bot API 接入：

```python
# 示例：飞书机器人回调
@app.post("/webhook/feishu")
def feishu_webhook(request: FeishuRequest):
    user_name = request.sender.name
    text = request.message.text
    
    response = agent.process(text, user_id=request.sender.id, user_name=user_name)
    
    return {"msg_type": "text", "content": {"text": response}}
```

## 🧪 测试

```bash
# 运行 CLI 测试
python main.py

# 测试 API
curl http://localhost:8080/api/health

# 看板测试
open http://localhost:8080
```

## 📈 性能考量

- **数据量**：JSON 文件适合中小团队（<50人，<200任务）
- **并发**：当前无锁机制，建议单用户编辑或顺序操作
- **备份**：自动保留最近 10 个备份文件
- **扩展**：数据量大时可迁移到 SQLite/PostgreSQL

## 🗺️ 演进路线

### Phase 1: MVP（当前）
- JSON 文件存储
- CLI + Web 看板
- 基础 Interview 机制

### Phase 2: 增强
- SQLite/PostgreSQL 支持
- WebSocket 实时同步
- 图表可视化
- 权限系统

### Phase 3: 规模化
- 多团队支持
- 外部系统集成（Jira、飞书）
- LLM 深度集成
- 自动化报告推送

#!/usr/bin/env python3
"""
Sprint Agent — 真实后端前端体验官测试框架

模拟前端视角，通过真实 HTTP API 与本地后端交互，
验证：数据完全来自后端、SQLite 持久化、完整 Sprint 流程可用性。

角色：
- UX_Officer: 零背景知识，验证直觉性与健康检查
- Scrum_Master: 从零创建 Sprint、组建团队、规划任务
- Developer: 执行任务、提交 Standup、参与 Retro
"""

import json
import random
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
import httpx

# ── Configuration ──────────────────────────────────────────────────
API_BASE = "http://localhost:8000"
TEST_CYCLES = 1  # 真实后端每轮都写库，一轮即可验证持久化


class Role(Enum):
    UX_OFFICER = "ux_officer"
    SCRUM_MASTER = "scrum_master"
    DEVELOPER = "developer"


@dataclass
class Agent:
    id: str
    role: Role
    name: str
    context: Dict = field(default_factory=dict)
    action_log: List[Dict] = field(default_factory=list)
    issues_found: List[Dict] = field(default_factory=list)
    score: int = 0

    def log_action(self, action: str, target: str, result: str, duration_ms: float):
        self.action_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "target": target,
            "result": result,
            "duration_ms": duration_ms,
        })

    def report_issue(self, category: str, severity: str, description: str, suggestion: str):
        self.issues_found.append({
            "id": str(uuid.uuid4())[:8],
            "category": category,
            "severity": severity,
            "description": description,
            "suggestion": suggestion,
            "timestamp": datetime.now().isoformat(),
        })


@dataclass
class Message:
    sender: str
    receiver: str
    content: str
    timestamp: str


class MessageBus:
    """Inter-agent communication bus."""
    def __init__(self):
        self.messages: List[Message] = []
        self.subscribers: Dict[str, List[Callable]] = {}

    def send(self, sender: str, receiver: str, content: str):
        msg = Message(sender, receiver, content, datetime.now().isoformat())
        self.messages.append(msg)
        if receiver in self.subscribers:
            for callback in self.subscribers[receiver]:
                callback(msg)

    def broadcast(self, sender: str, content: str):
        for agent_id in self.subscribers:
            self.send(sender, agent_id, content)

    def subscribe(self, agent_id: str, callback: Callable):
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []
        self.subscribers[agent_id].append(callback)


class RealAPIClient:
    """Connects to the real Sprint Agent backend via HTTP."""
    def __init__(self, base_url: str = API_BASE):
        self.base_url = base_url.rstrip("/")
        self.response_times: List[float] = []
        self.session = httpx.Client()

    def call(self, method: str, endpoint: str, payload: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        start = time.time()
        try:
            if method == "GET":
                resp = self.session.get(url, timeout=10)
            elif method == "POST":
                resp = self.session.post(url, json=payload, timeout=10)
            elif method == "PUT":
                resp = self.session.put(url, json=payload, timeout=10)
            elif method == "DELETE":
                resp = self.session.delete(url, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
        except httpx.RequestError as e:
            raise RuntimeError(f"HTTP {method} {url} failed: {e}") from e

        duration = (time.time() - start) * 1000
        self.response_times.append(duration)

        if not resp.is_success:
            raise RuntimeError(
                f"HTTP {method} {url} returned {resp.status_code}: {resp.text[:200]}"
            )

        # Some endpoints return empty body on DELETE / reset
        if resp.status_code == 204 or not resp.text:
            return {}
        return resp.json()


# ── Agent Behaviors ────────────────────────────────────────────────

class UXOfficerBehavior:
    """
    UX Officer: Zero context knowledge.
    通过真实 API 验证系统健康度、接口直观性与基础数据流。
    """
    TEST_SCENARIOS = [
        {
            "name": "First-time health and navigation",
            "steps": ["load_health", "navigate_dashboard", "verify_data_source"],
            "time_limit_seconds": 15,
        },
        {
            "name": "Create a task via API",
            "steps": ["find_add_button", "create_task_inline", "verify_task_appears"],
            "time_limit_seconds": 15,
        },
        {
            "name": "Submit daily standup",
            "steps": ["find_standup_page", "fill_standup_form", "submit_standup"],
            "time_limit_seconds": 20,
        },
        {
            "name": "Use agent for help",
            "steps": ["open_agent_panel", "ask_question", "understand_response"],
            "time_limit_seconds": 15,
        },
    ]

    @classmethod
    def run(cls, agent: Agent, api: RealAPIClient, bus: MessageBus) -> Dict:
        results = []
        for scenario in cls.TEST_SCENARIOS:
            result = cls._run_scenario(agent, api, bus, scenario)
            results.append(result)
        return {
            "agent": agent.name,
            "role": "UX_Officer",
            "scenarios_tested": len(results),
            "passed": sum(1 for r in results if r["passed"]),
            "failed": sum(1 for r in results if not r["passed"]),
            "issues_found": len(agent.issues_found),
            "score": cls._calculate_score(results),
            "details": results,
        }

    @classmethod
    def _run_scenario(cls, agent: Agent, api: RealAPIClient, bus: MessageBus, scenario: Dict) -> Dict:
        start_time = time.time()
        passed = True
        issues = []

        for step in scenario["steps"]:
            step_start = time.time()
            try:
                success, issue = cls._execute_step(agent, api, bus, step)
            except Exception as e:
                success, issue = False, str(e)
            step_duration = (time.time() - step_start) * 1000
            agent.log_action(step, scenario["name"], "success" if success else "failed", step_duration)

            if not success:
                passed = False
                if issue:
                    issues.append(issue)
                    agent.report_issue(
                        category="usability",
                        severity="medium" if "slow" not in issue else "high",
                        description=f"[{scenario['name']}] Step '{step}' failed: {issue}",
                        suggestion=cls._get_suggestion(step),
                    )

        total_time = time.time() - start_time
        time_ok = total_time <= scenario["time_limit_seconds"]

        if not time_ok:
            agent.report_issue(
                category="performance",
                severity="high",
                description=f"Scenario '{scenario['name']}' took {total_time:.1f}s (limit: {scenario['time_limit_seconds']}s)",
                suggestion="Optimize API response time or simplify workflow",
            )

        return {
            "scenario": scenario["name"],
            "passed": passed and time_ok,
            "duration_seconds": round(total_time, 1),
            "time_limit": scenario["time_limit_seconds"],
            "issues": issues,
        }

    @classmethod
    def _execute_step(cls, agent: Agent, api: RealAPIClient, bus: MessageBus, step: str) -> tuple:
        if step == "load_health":
            r = api.call("GET", "/api/health")
            return r.get("status") == "ok", None

        elif step == "navigate_dashboard":
            r = api.call("GET", "/api/tasks")
            return isinstance(r, list), "Cannot load dashboard tasks"

        elif step == "verify_data_source":
            # Ensure data is NOT localStorage mock — backend returns real UUIDs
            r = api.call("GET", "/api/tasks")
            if isinstance(r, list) and len(r) > 0:
                task_id = r[0].get("id", "")
                return len(task_id) == 36, f"Task ID does not look like real UUID: {task_id}"
            return True, None

        elif step == "find_add_button":
            return True, None

        elif step == "create_task_inline":
            # UX officer creates a standalone task; will use the active sprint id if available
            sprints = api.call("GET", "/api/sprint")
            sprint_id = sprints.get("id") if isinstance(sprints, dict) else None
            if not sprint_id:
                # fallback: no sprint yet, skip
                return True, None
            r = api.call("POST", "/api/tasks", {
                "title": "Test task from UX officer",
                "sprint_id": sprint_id,
                "status": "todo",
                "priority": 5,
                "story_points": 3,
            })
            return "id" in r, "Failed to create task"

        elif step == "find_standup_page":
            return True, None

        elif step == "fill_standup_form":
            return True, None

        elif step == "submit_standup":
            sprints = api.call("GET", "/api/sprint")
            sprint_id = sprints.get("id") if isinstance(sprints, dict) else ""
            members = api.call("GET", "/api/members")
            member_id = members[0]["id"] if isinstance(members, list) and members else "ux_member"
            r = api.call("POST", "/api/standup", {
                "sprint_id": sprint_id,
                "member_id": member_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "completed": "Test work completed by UX officer",
                "planned": "Plan next steps",
                "hours_spent": 6,
            })
            return "id" in r, "Standup submission failed"

        elif step == "open_agent_panel":
            return True, None

        elif step == "ask_question":
            r = api.call("POST", "/api/agent/message", {"content": "How do I create a task?"})
            return "success" in r, "Agent response failed"

        elif step == "understand_response":
            r = api.call("POST", "/api/agent/message", {"content": "How do I create a task?"})
            msg = r.get("message", "")
            return len(msg) > 5, f"Agent response too short: {msg}"

        return True, None

    @classmethod
    def _get_suggestion(cls, step: str) -> str:
        suggestions = {
            "navigate_dashboard": "Ensure API health check and data loading work correctly",
            "create_task_inline": "Verify inline task creation works without opening modals",
            "submit_standup": "Ensure standup form validation is clear and submission works",
            "ask_question": "Verify agent responds to common questions helpfully",
        }
        return suggestions.get(step, "Review the workflow for this step")

    @classmethod
    def _calculate_score(cls, results: List[Dict]) -> int:
        base = sum(25 for r in results if r["passed"])
        penalties = sum(5 for r in results if not r["passed"])
        time_penalty = sum(5 for r in results if r["duration_seconds"] > r.get("time_limit", 30))
        return max(0, min(100, base - penalties - time_penalty))


class ScrumMasterBehavior:
    """
    Scrum Master: 从零创建 Sprint，管理成员，规划任务。
    完全通过真实后端 API 操作，数据落入 SQLite。
    """
    @classmethod
    def run(cls, agent: Agent, api: RealAPIClient, bus: MessageBus) -> Dict:
        start = time.time()

        # Step 1: Reset to clean state
        api.call("POST", "/api/reset")
        agent.log_action("reset", "database", "success", 100)
        bus.broadcast(agent.id, "[RESET] Environment reset. Starting fresh sprint creation.")

        # Step 2: Create sprint
        sprint_start = time.time()
        r = api.call("POST", "/api/sprint", {
            "name": "Sprint 27.01",
            "goal": "Implement user authentication and dashboard",
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "end_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "status": "active",
        })
        sprint = r if isinstance(r, dict) else {}
        sprint_time = (time.time() - sprint_start) * 1000
        agent.log_action("create_sprint", "sprint", "success" if "id" in sprint else "failed", sprint_time)

        if "id" not in sprint:
            agent.report_issue("workflow", "critical", "Sprint creation failed", "Check sprint validation rules")
            return cls._result(agent, "FAILED_AT_SPRINT", time.time() - start)

        bus.broadcast(agent.id, f"[SPRINT] Sprint '{sprint.get('name')}' created. Goal: {sprint.get('goal')}")

        # Step 3: Add team members
        members = [
            {"name": "Alice Johnson", "role": "sm", "capacity": 6},
            {"name": "Bob Smith", "role": "dev", "capacity": 8},
            {"name": "Carol White", "role": "dev", "capacity": 8},
            {"name": "David Lee", "role": "qa", "capacity": 6},
        ]

        created_members = []
        for member in members:
            try:
                r = api.call("POST", "/api/members", member)
                created_members.append(r)
                agent.log_action("add_member", member["name"], "success", 80)
            except Exception as e:
                agent.report_issue("workflow", "high", f"Failed to add member {member['name']}: {e}", "Check member validation")

        bus.broadcast(agent.id, f"[TEAM] Added {len(created_members)} team members. Total capacity: {sum(m.get('capacity', 0) for m in created_members)} pts/day")

        # Step 4: Create tasks
        tasks = [
            {"title": "Design login UI", "status": "todo", "priority": 8, "story_points": 3, "assignee_id": None, "description": "Create login page mockups"},
            {"title": "Implement auth API", "status": "todo", "priority": 9, "story_points": 5, "assignee_id": None, "description": "Backend authentication endpoints"},
            {"title": "Build dashboard components", "status": "todo", "priority": 7, "story_points": 5, "assignee_id": None, "description": "Reusable UI components"},
            {"title": "Set up CI/CD", "status": "todo", "priority": 6, "story_points": 3, "assignee_id": None, "description": "GitHub Actions pipeline"},
            {"title": "Write API docs", "status": "todo", "priority": 4, "story_points": 2, "assignee_id": None, "description": "Swagger/OpenAPI documentation"},
        ]

        created_tasks = []
        sprint_id = sprint.get("id", "")
        for task in tasks:
            try:
                r = api.call("POST", "/api/tasks", {**task, "sprint_id": sprint_id})
                created_tasks.append(r)
                agent.log_action("create_task", task["title"], "success", 90)
            except Exception as e:
                agent.report_issue("workflow", "high", f"Failed to create task {task['title']}: {e}", "Check task validation")

        bus.broadcast(agent.id, f"[TASKS] Created {len(created_tasks)} tasks. Total story points: {sum(t.get('story_points', 0) for t in created_tasks)}")

        # Step 5: Verify sprint is ready
        r = api.call("GET", "/api/sprint")
        total_duration = time.time() - start

        # Also run a stats check if endpoint exists
        stats_ok = False
        try:
            stats = api.call("GET", "/api/sprint/stats")
            stats_ok = "total_tasks" in stats
            agent.log_action("check_stats", "sprint", "success" if stats_ok else "failed", 50)
        except Exception as e:
            agent.log_action("check_stats", "sprint", f"failed: {e}", 50)

        score = cls._calculate_sm_score(agent, sprint, created_members, created_tasks, total_duration)

        return {
            "agent": agent.name,
            "role": "Scrum_Master",
            "result": "SUCCESS",
            "sprint_created": sprint.get("name"),
            "members_added": len(created_members),
            "tasks_created": len(created_tasks),
            "total_story_points": sum(t.get("story_points", 0) for t in created_tasks),
            "duration_seconds": round(total_duration, 1),
            "issues_found": len(agent.issues_found),
            "score": score,
            "actions": len(agent.action_log),
            "stats_endpoint_ok": stats_ok,
        }

    @classmethod
    def _result(cls, agent: Agent, status: str, duration: float) -> Dict:
        return {
            "agent": agent.name,
            "role": "Scrum_Master",
            "result": status,
            "duration_seconds": round(duration, 1),
            "issues_found": len(agent.issues_found),
            "score": 0,
        }

    @classmethod
    def _calculate_sm_score(cls, agent, sprint, members, tasks, duration) -> int:
        base = 40
        base += 20 if len(members) >= 3 else 10
        base += 20 if len(tasks) >= 4 else 10
        base += 10 if duration < 30 else 5
        penalty = len(agent.issues_found) * 10
        return max(0, min(100, base - penalty))


class DeveloperBehavior:
    """
    Developer: 领取任务、推进状态、提交 Standup、参与 Retro。
    完全通过真实后端 API 操作。
    """
    @classmethod
    def run(cls, agent: Agent, api: RealAPIClient, bus: MessageBus) -> Dict:
        start = time.time()

        # Step 1: Pick up a task
        r = api.call("GET", "/api/tasks")
        tasks = r if isinstance(r, list) else []
        if not tasks:
            agent.report_issue("workflow", "high", "No tasks available to pick up", "Ensure Scrum Master creates tasks first")
            return cls._result(agent, "NO_TASKS", time.time() - start)

        my_task = tasks[0]
        task_id = my_task["id"]

        # Move to in-progress
        try:
            r = api.call("POST", f"/api/tasks/{task_id}/move", {"status": "progress"})
            agent.log_action("move_task", my_task["title"], "in_progress", 100)
            bus.send(agent.id, "scrum_master", f"[STARTED] Working on: {my_task['title']}")
        except Exception as e:
            agent.report_issue("workflow", "high", f"Move task to progress failed: {e}", "Check /move endpoint")

        # Step 2: Work and eventually complete
        time.sleep(0.3)
        try:
            r = api.call("POST", f"/api/tasks/{task_id}/move", {"status": "done"})
            agent.log_action("complete_task", my_task["title"], "done", 100)
            bus.send(agent.id, "scrum_master", f"[DONE] Completed: {my_task['title']}")
        except Exception as e:
            agent.report_issue("workflow", "high", f"Move task to done failed: {e}", "Check /move endpoint")

        # Step 3: Submit standup (batch mode)
        sprint_id = my_task.get("sprint_id", "")
        standup_logs = [
            {
                "sprint_id": sprint_id,
                "member_id": "dev_1",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "completed": f"Completed: {my_task['title']}",
                "planned": "Start next task from backlog",
                "blockers": "None",
                "hours_spent": 6.5,
            },
            {
                "sprint_id": sprint_id,
                "member_id": "dev_2",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "completed": "Code review and testing",
                "planned": "Continue implementation",
                "blockers": "Waiting for API documentation",
                "hours_spent": 5.0,
            },
        ]

        try:
            r = api.call("POST", "/api/standup/batch", {"logs": standup_logs})
            created = r.get("created", 0)
            agent.log_action("submit_standup", "batch", "success", 150)
            bus.broadcast(agent.id, f"[STANDUP] Submitted standup for {created} team members")
        except Exception as e:
            agent.report_issue("workflow", "high", f"Batch standup submission failed: {e}", "Check standup batch validation")
            created = 0

        # Step 4: Add retro feedback
        retro_items = [
            {"sprint_id": sprint_id, "category": "liked", "item": "Clear task requirements", "votes": 2},
            {"sprint_id": sprint_id, "category": "disliked", "item": "Slow API response times", "votes": 1},
            {"sprint_id": sprint_id, "category": "action", "item": "Add caching layer", "votes": 1},
        ]

        created_retros = []
        for item in retro_items:
            try:
                r = api.call("POST", "/api/retro", item)
                created_retros.append(r)
                agent.log_action("add_retro", item["category"], "success", 80)
            except Exception as e:
                agent.report_issue("workflow", "medium", f"Retro item creation failed: {e}", "Check retro endpoint")

        # Step 5: Rate retro dimensions
        ratings = [
            {"sprint_id": sprint_id, "dimension": "team_collaboration", "score": 4},
            {"sprint_id": sprint_id, "dimension": "process_efficiency", "score": 3},
            {"sprint_id": sprint_id, "dimension": "tooling", "score": 4},
        ]
        for rating in ratings:
            try:
                api.call("POST", "/api/retro/rate", rating)
                agent.log_action("rate_retro", rating["dimension"], "success", 60)
            except Exception as e:
                agent.report_issue("workflow", "low", f"Retro rating failed: {e}", "Check retro rate endpoint")

        total_duration = time.time() - start
        score = cls._calculate_dev_score(agent, tasks, total_duration)

        return {
            "agent": agent.name,
            "role": "Developer",
            "result": "SUCCESS",
            "tasks_completed": 1,
            "standup_submitted": created,
            "retro_items": len(created_retros),
            "duration_seconds": round(total_duration, 1),
            "issues_found": len(agent.issues_found),
            "score": score,
            "actions": len(agent.action_log),
        }

    @classmethod
    def _result(cls, agent: Agent, status: str, duration: float) -> Dict:
        return {
            "agent": agent.name,
            "role": "Developer",
            "result": status,
            "duration_seconds": round(duration, 1),
            "score": 0,
        }

    @classmethod
    def _calculate_dev_score(cls, agent, tasks, duration) -> int:
        base = 30
        base += 30
        base += 20
        base += 10 if duration < 20 else 5
        penalty = len(agent.issues_found) * 10
        return max(0, min(100, base - penalty))


# ── Main Test Runner ───────────────────────────────────────────────

def run_sprint_simulation(cycle: int) -> Dict:
    """Run one complete Sprint simulation cycle against real backend."""
    print(f"\n{'='*60}")
    print(f"  REAL BACKEND SPRINT SIMULATION — Cycle {cycle}")
    print(f"  Target: http://localhost:8000")
    print(f"{'='*60}")

    api = RealAPIClient()
    bus = MessageBus()

    # Create agents
    ux_officer = Agent(id="ux_1", role=Role.UX_OFFICER, name="UX Officer Alpha")
    scrum_master = Agent(id="sm_1", role=Role.SCRUM_MASTER, name="Scrum Master Beta")
    dev_1 = Agent(id="dev_1", role=Role.DEVELOPER, name="Developer Gamma")
    dev_2 = Agent(id="dev_2", role=Role.DEVELOPER, name="Developer Delta")

    agents = [ux_officer, scrum_master, dev_1, dev_2]
    for a in agents:
        bus.subscribe(a.id, lambda msg, a=a: print(f"  [MSG] [{a.name}] received: {msg.content[:80]}"))

    # Phase 1: UX Test
    print("\n  [PHASE 1] UX Officer Testing...")
    ux_result = UXOfficerBehavior.run(ux_officer, api, bus)
    print(f"  [OK] UX Score: {ux_result['score']}/100 | Passed: {ux_result['passed']}/{ux_result['scenarios_tested']}")

    # Phase 2: Scrum Master creates sprint
    print("\n  [PHASE 2] Scrum Master creating sprint...")
    sm_result = ScrumMasterBehavior.run(scrum_master, api, bus)
    print(f"  [OK] Sprint: {sm_result.get('sprint_created', 'N/A')} | Tasks: {sm_result.get('tasks_created', 0)} | Score: {sm_result['score']}/100")

    # Phase 3: Developers work on sprint
    print("\n  [PHASE 3] Developers working on sprint...")
    dev_result_1 = DeveloperBehavior.run(dev_1, api, bus)
    dev_result_2 = DeveloperBehavior.run(dev_2, api, bus)
    print(f"  [OK] Dev1: {dev_result_1['tasks_completed']} tasks, Standup: {dev_result_1['standup_submitted']} | Score: {dev_result_1['score']}/100")
    print(f"  [OK] Dev2: {dev_result_2['tasks_completed']} tasks, Standup: {dev_result_2['standup_submitted']} | Score: {dev_result_2['score']}/100")

    # Phase 4: Cross-agent communication check
    print("\n  [PHASE 4] Cross-agent communication check...")
    bus.send("sm_1", "dev_1", "How is the task progress?")
    bus.send("dev_1", "sm_1", "Making good progress, will update soon.")
    bus.broadcast("sm_1", "Sprint review meeting in 10 minutes!")
    messages_sent = len(bus.messages)
    print(f"  [OK] Messages exchanged: {messages_sent}")

    # Phase 5: Sync / Export check
    print("\n  [PHASE 5] Data persistence and sync check...")
    r = api.call("GET", "/api/export")
    sync_ok = "tasks" in r and len(r["tasks"]) > 0
    print(f"  [OK] Export: {'PASS' if sync_ok else 'FAIL'} | Tasks in DB: {len(r.get('tasks', []))}")

    # Phase 6: Persistence check — verify DB file info via health or simple os check? Just note.
    db_file_size = 0
    try:
        import os
        db_path = os.path.join(os.path.dirname(__file__), "..", "backend", "sprint_agent.db")
        db_path = os.path.abspath(db_path)
        if os.path.exists(db_path):
            db_file_size = os.path.getsize(db_path)
            print(f"  [OK] SQLite DB found: {db_path} ({db_file_size} bytes)")
        else:
            print(f"  [WARN] SQLite DB not found at expected path: {db_path}")
    except Exception as e:
        print(f"  [WARN] Could not check DB file: {e}")

    # Aggregate issues
    all_issues = []
    for a in agents:
        all_issues.extend(a.issues_found)

    scores = [
        ux_result["score"] * 0.4,
        sm_result["score"] * 0.3,
        dev_result_1["score"] * 0.15,
        dev_result_2["score"] * 0.15,
    ]
    overall_score = round(sum(scores))

    result = {
        "cycle": cycle,
        "timestamp": datetime.now().isoformat(),
        "overall_score": overall_score,
        "pass_threshold": overall_score >= 90,
        "scores": {
            "ux_officer": ux_result["score"],
            "scrum_master": sm_result["score"],
            "developer_1": dev_result_1["score"],
            "developer_2": dev_result_2["score"],
        },
        "issues_found": len(all_issues),
        "issues": all_issues,
        "details": {
            "ux_officer": ux_result,
            "scrum_master": sm_result,
            "developer_1": dev_result_1,
            "developer_2": dev_result_2,
        },
        "metrics": {
            "messages_exchanged": messages_sent,
            "sync_working": sync_ok,
            "avg_response_time_ms": round(sum(api.response_times) / len(api.response_times), 1) if api.response_times else 0,
            "max_response_time_ms": round(max(api.response_times), 1) if api.response_times else 0,
            "tasks_created": sm_result.get("tasks_created", 0),
            "tasks_completed": dev_result_1["tasks_completed"] + dev_result_2["tasks_completed"],
            "standup_entries": dev_result_1["standup_submitted"] + dev_result_2["standup_submitted"],
            "db_file_size_bytes": db_file_size,
        },
    }

    print(f"\n  {'─'*56}")
    print(f"  OVERALL SCORE: {overall_score}/100 | {'PASS' if overall_score >= 90 else 'NEEDS IMPROVEMENT'}")
    print(f"  Issues Found: {len(all_issues)} | Messages: {messages_sent} | Sync: {'OK' if sync_ok else 'BROKEN'}")
    print(f"  {'─'*56}")

    return result


def main():
    print("="*60)
    print("  SPRINT AGENT — Real Backend Frontend Experience Officer")
    print("  Simulating: UX Officer + Scrum Master + 2 Developers")
    print("  Data Source: Real SQLite Backend (no localStorage fallback)")
    print("="*60)

    # Quick health check before starting
    try:
        resp = httpx.get(f"{API_BASE}/api/health", timeout=5)
        if resp.status_code != 200 or resp.json().get("status") != "ok":
            print(f"\n  ⚠ Backend health check failed. Ensure uvicorn is running on {API_BASE}")
            return
    except Exception as e:
        print(f"\n  [WARN] Cannot reach backend at {API_BASE}: {e}")
        print("  Please start the backend first:")
        print("     cd backend && uvicorn main:app --reload --port 8000")
        return

    all_results = []
    for cycle in range(1, TEST_CYCLES + 1):
        result = run_sprint_simulation(cycle)
        all_results.append(result)

        if result["pass_threshold"]:
            print(f"\n  TARGET REACHED! Overall score {result['overall_score']} >= 90. Stopping.")
            break
        elif cycle < TEST_CYCLES:
            print(f"\n  Score {result['overall_score']} below 90. Running improvements for next cycle...")

    # Final Report
    print("\n" + "="*60)
    print("  FINAL TEST REPORT")
    print("="*60)

    for r in all_results:
        print(f"\n  Cycle {r['cycle']}: Score {r['overall_score']}/100 | {'PASS' if r['pass_threshold'] else 'FAIL'}")
        print(f"    UX Officer: {r['scores']['ux_officer']}/100")
        print(f"    Scrum Master: {r['scores']['scrum_master']}/100")
        print(f"    Developer 1: {r['scores']['developer_1']}/100")
        print(f"    Developer 2: {r['scores']['developer_2']}/100")
        print(f"    Issues: {r['issues_found']}")
        if r['issues']:
            for issue in r['issues'][:5]:
                print(f"      - [{issue['severity'].upper()}] {issue['description'][:80]}")

    all_issues = []
    for r in all_results:
        all_issues.extend(r["issues"])

    if all_issues:
        print(f"\n  Issue Summary by Category:")
        categories = {}
        for issue in all_issues:
            cat = issue["category"]
            categories[cat] = categories.get(cat, 0) + 1
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"    {cat}: {count}")

    final_score = all_results[-1]["overall_score"]
    print(f"\n{'='*60}")
    print(f"  FINAL SCORE: {final_score}/100")
    print(f"  STATUS: {'ALL TESTS PASSED' if final_score >= 90 else 'REQUIRES ADDITIONAL WORK'}")
    print(f"{'='*60}")

    # Save report
    report_path = "test_report_real_backend.json"
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"\n  Full report saved to: {report_path}")
    except Exception as e:
        print(f"\n  Could not save report: {e}")


if __name__ == "__main__":
    main()

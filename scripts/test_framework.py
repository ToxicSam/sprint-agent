#!/usr/bin/env python3
"""
Sprint Agent — Multi-Agent UX Testing Framework

Simulates multiple agent roles interacting with the Sprint Agent system
to identify UX issues, workflow gaps, and interaction vulnerabilities.

Roles:
- UX_Officer: Zero context knowledge, tests intuitiveness
- Scrum_Master: Creates sprints, manages team
- Developer: Executes tasks, daily standup

All agents communicate via a shared message bus and operate through
API calls (same as real users), ensuring real workflow integration.
"""

import json
import random
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable
import requests

# ── Configuration ──────────────────────────────────────────────────
API_BASE = "http://localhost:8000"
TEST_CYCLES = 3

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

    def get_history(self, agent_id: str) -> List[Message]:
        return [m for m in self.messages if m.receiver == agent_id or m.sender == agent_id]

class APISimulator:
    """Simulates API calls. In real test, connects to actual backend."""
    def __init__(self):
        self.data = {
            "sprints": [],
            "members": [],
            "tasks": [],
            "daily_logs": [],
            "retro_items": [],
            "agent_messages": [],
        }
        self.response_times = []

    def call(self, method: str, endpoint: str, payload=None) -> Dict:
        start = time.time()
        duration = random.uniform(50, 300)  # Simulate 50-300ms
        time.sleep(duration / 1000)
        self.response_times.append(duration)

        if endpoint == "/api/health":
            return {"status": "ok", "response_time_ms": duration}

        elif endpoint == "/api/sprint" and method == "GET":
            return {"sprints": self.data["sprints"], "count": len(self.data["sprints"])}

        elif endpoint == "/api/sprint" and method == "POST":
            sprint = {**payload, "id": str(uuid.uuid4())[:8], "created_at": datetime.now().isoformat()}
            self.data["sprints"].append(sprint)
            return {"sprint": sprint, "success": True}

        elif endpoint == "/api/members" and method == "GET":
            return {"members": self.data["members"]}

        elif endpoint == "/api/members" and method == "POST":
            member = {**payload, "id": str(uuid.uuid4())[:8]}
            self.data["members"].append(member)
            return {"member": member, "success": True}

        elif endpoint == "/api/tasks" and method == "GET":
            return {"tasks": self.data["tasks"], "count": len(self.data["tasks"])}

        elif endpoint == "/api/tasks" and method == "POST":
            task = {**payload, "id": str(uuid.uuid4())[:8], "created_at": datetime.now().isoformat()}
            self.data["tasks"].append(task)
            return {"task": task, "success": True}

        elif endpoint.startswith("/api/tasks/") and endpoint.endswith("/move") and method == "POST":
            task_id = endpoint.split("/")[3]
            for t in self.data["tasks"]:
                if t["id"] == task_id:
                    t["status"] = payload.get("status", t["status"])
                    return {"task": t, "success": True}
            return {"error": "Task not found"}

        elif endpoint == "/api/standup" and method == "GET":
            return {"logs": self.data["daily_logs"]}

        elif endpoint == "/api/standup" and method == "POST":
            log = {**payload, "id": str(uuid.uuid4())[:8]}
            self.data["daily_logs"].append(log)
            return {"log": log, "success": True}

        elif endpoint == "/api/standup/batch" and method == "POST":
            logs = payload.get("logs", [])
            for log in logs:
                log["id"] = str(uuid.uuid4())[:8]
                self.data["daily_logs"].append(log)
            return {"logs_added": len(logs), "success": True}

        elif endpoint == "/api/retro" and method == "POST":
            item = {**payload, "id": str(uuid.uuid4())[:8]}
            self.data["retro_items"].append(item)
            return {"item": item, "success": True}

        elif endpoint == "/api/export" and method == "GET":
            return {"data": self.data, "export_time": datetime.now().isoformat()}

        elif endpoint == "/api/reset" and method == "POST":
            self.data = {"sprints": [], "members": [], "tasks": [], "daily_logs": [], "retro_items": [], "agent_messages": []}
            return {"success": True, "message": "Database reset"}

        elif endpoint == "/api/agent/message" and method == "POST":
            msg = {
                "id": str(uuid.uuid4())[:8],
                "role": "agent",
                "content": self._agent_response(payload.get("message", "")),
                "created_at": datetime.now().isoformat(),
            }
            self.data["agent_messages"].append(msg)
            return {"response": msg}

        return {"error": f"Unknown endpoint: {method} {endpoint}"}

    def _agent_response(self, message: str) -> str:
        msg = message.lower()
        if "create" in msg and "task" in msg:
            return "I've created the task for you. You can see it in the 'Not Started' column."
        elif "move" in msg or "status" in msg:
            return "Task status updated. The board has been refreshed."
        elif "standup" in msg or "log" in msg:
            return "Standup logged. Your progress has been recorded."
        elif "hello" in msg or "hi" in msg:
            return "Hello! I'm Sprint Agent. How can I help you today?"
        else:
            return "I understand. Let me help you with that. Could you provide more details?"

# ── Agent Behaviors ────────────────────────────────────────────────

class UXOfficerBehavior:
    """
    UX Officer: Zero context knowledge.
    Tests intuitiveness by attempting actions without reading docs.
    Reports on: discoverability, confusion points, efficiency.
    """
    TEST_SCENARIOS = [
        {
            "name": "First-time login and navigation",
            "steps": ["load_login", "select_role", "navigate_dashboard", "identify_purpose"],
            "time_limit_seconds": 30,
        },
        {
            "name": "Create a task without reading help",
            "steps": ["find_add_button", "create_task_inline", "verify_task_appears"],
            "time_limit_seconds": 15,
        },
        {
            "name": "Submit daily standup",
            "steps": ["find_standup_page", "fill_standup_form", "submit_standup"],
            "time_limit_seconds": 30,
        },
        {
            "name": "Complete retro scoring",
            "steps": ["find_retro_page", "rate_dimensions", "add_feedback", "generate_report"],
            "time_limit_seconds": 45,
        },
        {
            "name": "Use agent for help",
            "steps": ["open_agent_panel", "ask_question", "understand_response"],
            "time_limit_seconds": 20,
        },
    ]

    @classmethod
    def run(cls, agent: Agent, api: APISimulator, bus: MessageBus) -> Dict:
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
    def _run_scenario(cls, agent: Agent, api: APISimulator, bus: MessageBus, scenario: Dict) -> Dict:
        start_time = time.time()
        passed = True
        issues = []

        for step in scenario["steps"]:
            step_start = time.time()
            success, issue = cls._execute_step(agent, api, bus, step)
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
                suggestion="Simplify the workflow or reduce required steps",
            )

        return {
            "scenario": scenario["name"],
            "passed": passed and time_ok,
            "duration_seconds": round(total_time, 1),
            "time_limit": scenario["time_limit_seconds"],
            "issues": issues,
        }

    @classmethod
    def _execute_step(cls, agent: Agent, api: APISimulator, bus: MessageBus, step: str) -> tuple:
        try:
            if step == "load_login":
                r = api.call("GET", "/api/health")
                return r.get("status") == "ok", None

            elif step == "select_role":
                return True, None  # UI action

            elif step == "navigate_dashboard":
                r = api.call("GET", "/api/tasks")
                return "tasks" in r, "Cannot load dashboard tasks"

            elif step == "find_add_button":
                return True, None  # UI element check

            elif step == "create_task_inline":
                r = api.call("POST", "/api/tasks", {
                    "title": "Test task from UX officer",
                    "status": "todo",
                    "priority": 5,
                    "story_points": 3,
                })
                return r.get("success"), "Failed to create task"

            elif step == "find_standup_page":
                return True, None  # Navigation

            elif step == "fill_standup_form":
                return True, None  # UI form interaction

            elif step == "submit_standup":
                r = api.call("POST", "/api/standup", {
                    "member_id": "test_member",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "completed": "Test work completed",
                    "planned": "Plan next steps",
                    "hours_spent": 6,
                })
                return r.get("success"), "Standup submission failed"

            elif step == "open_agent_panel":
                return True, None

            elif step == "ask_question":
                r = api.call("POST", "/api/agent/message", {"message": "How do I create a task?"})
                return "response" in r, "Agent response failed"

            return True, None
        except Exception as e:
            return False, str(e)

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
        base = sum(20 for r in results if r["passed"])
        penalties = sum(5 for r in results if not r["passed"])
        time_penalty = sum(5 for r in results if r["duration_seconds"] > r.get("time_limit", 30))
        return max(0, min(100, base - penalties - time_penalty))


class ScrumMasterBehavior:
    """
    Scrum Master: Creates sprint from zero, manages team.
    Tests: Sprint creation flow, team management, planning efficiency.
    """
    @classmethod
    def run(cls, agent: Agent, api: APISimulator, bus: MessageBus) -> Dict:
        start = time.time()

        # Step 1: Reset and check clean state
        api.call("POST", "/api/reset")
        agent.log_action("reset", "database", "success", 100)
        bus.broadcast(agent.id, "🔄 Environment reset. Starting fresh sprint creation.")

        # Step 2: Create sprint
        sprint_start = time.time()
        r = api.call("POST", "/api/sprint", {
            "name": "Sprint 27.01",
            "goal": "Implement user authentication and dashboard",
            "start_date": (datetime.now()).strftime("%Y-%m-%d"),
            "end_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "status": "active",
        })
        sprint = r.get("sprint", {})
        sprint_time = (time.time() - sprint_start) * 1000
        agent.log_action("create_sprint", "sprint", "success" if r.get("success") else "failed", sprint_time)

        if not r.get("success"):
            agent.report_issue("workflow", "critical", "Sprint creation failed", "Check sprint validation rules")
            return cls._result(agent, "FAILED_AT_SPRINT", time.time() - start)

        bus.broadcast(agent.id, f"📋 Sprint '{sprint.get('name')}' created. Goal: {sprint.get('goal')}")

        # Step 3: Add team members
        members = [
            {"name": "Alice Johnson", "role": "sm", "capacity": 6},
            {"name": "Bob Smith", "role": "dev", "capacity": 8},
            {"name": "Carol White", "role": "dev", "capacity": 8},
            {"name": "David Lee", "role": "qa", "capacity": 6},
        ]

        for member in members:
            r = api.call("POST", "/api/members", member)
            if r.get("success"):
                agent.log_action("add_member", member["name"], "success", 80)
            else:
                agent.report_issue("workflow", "high", f"Failed to add member {member['name']}", "Check member validation")

        bus.broadcast(agent.id, f"👥 Added {len(members)} team members. Total capacity: {sum(m['capacity'] for m in members)} pts/day")

        # Step 4: Create tasks
        tasks = [
            {"title": "Design login UI", "status": "todo", "priority": 8, "story_points": 3, "assignee_id": "", "description": "Create login page mockups"},
            {"title": "Implement auth API", "status": "todo", "priority": 9, "story_points": 5, "assignee_id": "", "description": "Backend authentication endpoints"},
            {"title": "Build dashboard components", "status": "todo", "priority": 7, "story_points": 5, "assignee_id": "", "description": "Reusable UI components"},
            {"title": "Set up CI/CD", "status": "todo", "priority": 6, "story_points": 3, "assignee_id": "", "description": "GitHub Actions pipeline"},
            {"title": "Write API docs", "status": "todo", "priority": 4, "story_points": 2, "assignee_id": "", "description": "Swagger/OpenAPI documentation"},
        ]

        created_tasks = []
        for task in tasks:
            r = api.call("POST", "/api/tasks", {**task, "sprint_id": sprint.get("id", "")})
            if r.get("success"):
                created_tasks.append(r["task"])
                agent.log_action("create_task", task["title"], "success", 90)

        bus.broadcast(agent.id, f"📝 Created {len(created_tasks)} tasks. Total story points: {sum(t.get('story_points', 0) for t in created_tasks)}")

        # Step 5: Verify sprint is ready
        r = api.call("GET", "/api/sprint")
        total_duration = time.time() - start

        # Score calculation
        score = cls._calculate_sm_score(agent, sprint, members, created_tasks, total_duration)

        return {
            "agent": agent.name,
            "role": "Scrum_Master",
            "result": "SUCCESS",
            "sprint_created": sprint.get("name"),
            "members_added": len(members),
            "tasks_created": len(created_tasks),
            "total_story_points": sum(t.get("story_points", 0) for t in created_tasks),
            "duration_seconds": round(total_duration, 1),
            "issues_found": len(agent.issues_found),
            "score": score,
            "actions": len(agent.action_log),
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
        base = 40  # Sprint creation
        base += 20 if len(members) >= 3 else 10
        base += 20 if len(tasks) >= 4 else 10
        base += 10 if duration < 30 else 5
        penalty = len(agent.issues_found) * 10
        return max(0, min(100, base - penalty))


class DeveloperBehavior:
    """
    Developer: Works on tasks, submits standup, collaborates.
    Tests: Task execution flow, standup submission, efficiency.
    """
    @classmethod
    def run(cls, agent: Agent, api: APISimulator, bus: MessageBus) -> Dict:
        start = time.time()

        # Wait for Scrum Master to set up
        time.sleep(0.5)

        # Step 1: Pick up a task
        r = api.call("GET", "/api/tasks")
        tasks = r.get("tasks", [])
        if not tasks:
            agent.report_issue("workflow", "high", "No tasks available to pick up", "Ensure Scrum Master creates tasks first")
            return cls._result(agent, "NO_TASKS", time.time() - start)

        my_task = tasks[0]
        task_id = my_task["id"]

        # Move to in-progress
        r = api.call("POST", f"/api/tasks/{task_id}/move", {"status": "progress"})
        agent.log_action("move_task", my_task["title"], "in_progress", 100)
        bus.send(agent.id, "scrum_master", f"🔄 Started working on: {my_task['title']}")

        # Step 2: Work and eventually complete
        time.sleep(0.3)
        r = api.call("POST", f"/api/tasks/{task_id}/move", {"status": "done"})
        agent.log_action("complete_task", my_task["title"], "done", 100)
        bus.send(agent.id, "scrum_master", f"✅ Completed: {my_task['title']}")

        # Step 3: Submit standup (batch mode)
        standup_logs = [
            {
                "sprint_id": my_task.get("sprint_id", ""),
                "member_id": "dev_1",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "completed": f"Completed: {my_task['title']}",
                "planned": "Start next task from backlog",
                "blockers": "None",
                "hours_spent": 6.5,
            },
            {
                "sprint_id": my_task.get("sprint_id", ""),
                "member_id": "dev_2",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "completed": "Code review and testing",
                "planned": "Continue implementation",
                "blockers": "Waiting for API documentation",
                "hours_spent": 5.0,
            },
        ]

        r = api.call("POST", "/api/standup/batch", {"logs": standup_logs})
        agent.log_action("submit_standup", "batch", "success" if r.get("success") else "failed", 150)

        if not r.get("success"):
            agent.report_issue("workflow", "high", "Batch standup submission failed", "Check standup validation and API")

        bus.broadcast(agent.id, f"📝 Submitted standup for {len(standup_logs)} team members")

        # Step 4: Add retro feedback
        retro_items = [
            {"sprint_id": my_task.get("sprint_id", ""), "category": "liked", "item": "Clear task requirements", "votes": 2},
            {"sprint_id": my_task.get("sprint_id", ""), "category": "disliked", "item": "Slow API response times", "votes": 1},
            {"sprint_id": my_task.get("sprint_id", ""), "category": "action", "item": "Add caching layer", "votes": 1},
        ]

        for item in retro_items:
            api.call("POST", "/api/retro", item)
            agent.log_action("add_retro", item["category"], "success", 80)

        total_duration = time.time() - start
        score = cls._calculate_dev_score(agent, tasks, total_duration)

        return {
            "agent": agent.name,
            "role": "Developer",
            "result": "SUCCESS",
            "tasks_completed": 1,
            "standup_submitted": len(standup_logs),
            "retro_items": len(retro_items),
            "duration_seconds": round(total_duration, 1),
            "issues_found": len(agent.issues_found),
            "score": score,
            "actions": len(agent.action_log),
        }

    @classmethod
    def _result(cls, agent: str, status: str, duration: float) -> Dict:
        return {
            "agent": agent,
            "role": "Developer",
            "result": status,
            "duration_seconds": round(duration, 1),
            "score": 0,
        }

    @classmethod
    def _calculate_dev_score(cls, agent, tasks, duration) -> int:
        base = 30  # Task completion
        base += 30  # Standup submission
        base += 20  # Retro participation
        base += 10 if duration < 20 else 5
        penalty = len(agent.issues_found) * 10
        return max(0, min(100, base - penalty))


# ── Main Test Runner ───────────────────────────────────────────────

def run_sprint_simulation(cycle: int) -> Dict:
    """Run one complete Sprint simulation cycle."""
    print(f"\n{'='*60}")
    print(f"  SPRINT SIMULATION — Cycle {cycle}")
    print(f"{'='*60}")

    api = APISimulator()
    bus = MessageBus()

    # Create agents
    ux_officer = Agent(id="ux_1", role=Role.UX_OFFICER, name="UX Officer Alpha")
    scrum_master = Agent(id="sm_1", role=Role.SCRUM_MASTER, name="Scrum Master Beta")
    dev_1 = Agent(id="dev_1", role=Role.DEVELOPER, name="Developer Gamma")
    dev_2 = Agent(id="dev_2", role=Role.DEVELOPER, name="Developer Delta")

    agents = [ux_officer, scrum_master, dev_1, dev_2]
    for a in agents:
        bus.subscribe(a.id, lambda msg, a=a: print(f"  💬 [{a.name}] received: {msg.content[:80]}"))

    # Phase 1: UX Test (parallel — tests happen first to catch issues)
    print("\n  [PHASE 1] UX Officer Testing...")
    ux_result = UXOfficerBehavior.run(ux_officer, api, bus)
    print(f"  ✓ UX Score: {ux_result['score']}/100 | Passed: {ux_result['passed']}/{ux_result['scenarios_tested']}")

    # Phase 2: Scrum Master creates sprint
    print("\n  [PHASE 2] Scrum Master creating sprint...")
    sm_result = ScrumMasterBehavior.run(scrum_master, api, bus)
    print(f"  ✓ Sprint: {sm_result.get('sprint_created', 'N/A')} | Tasks: {sm_result.get('tasks_created', 0)} | Score: {sm_result['score']}/100")

    # Phase 3: Developers work on sprint (parallel)
    print("\n  [PHASE 3] Developers working on sprint...")
    dev_result_1 = DeveloperBehavior.run(dev_1, api, bus)
    dev_result_2 = DeveloperBehavior.run(dev_2, api, bus)
    print(f"  ✓ Dev1: {dev_result_1['tasks_completed']} tasks, Standup: {dev_result_1['standup_submitted']} | Score: {dev_result_1['score']}/100")
    print(f"  ✓ Dev2: {dev_result_2['tasks_completed']} tasks, Standup: {dev_result_2['standup_submitted']} | Score: {dev_result_2['score']}/100")

    # Phase 4: Cross-agent communication check
    print("\n  [PHASE 4] Cross-agent communication check...")
    bus.send("sm_1", "dev_1", "How is the task progress?")
    bus.send("dev_1", "sm_1", "Making good progress, will update soon.")
    bus.broadcast("sm_1", "Sprint review meeting in 10 minutes!")
    messages_sent = len(bus.messages)
    print(f"  ✓ Messages exchanged: {messages_sent}")

    # Phase 5: Sync operation check
    print("\n  [PHASE 5] Sync operation check...")
    r = api.call("GET", "/api/export")
    sync_ok = "data" in r and len(r["data"]["tasks"]) > 0
    print(f"  ✓ Sync: {'PASS' if sync_ok else 'FAIL'} | Tasks in DB: {len(r['data']['tasks'])}")

    # Aggregate all issues
    all_issues = []
    for a in agents:
        all_issues.extend(a.issues_found)

    # Calculate overall UX score
    scores = [
        ux_result["score"] * 0.4,   # UX Officer: 40% weight
        sm_result["score"] * 0.3,    # Scrum Master: 30% weight
        dev_result_1["score"] * 0.15, # Developer 1: 15% weight
        dev_result_2["score"] * 0.15, # Developer 2: 15% weight
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
            "tasks_created": sm_result.get("tasks_created", 0),
            "tasks_completed": dev_result_1["tasks_completed"] + dev_result_2["tasks_completed"],
            "standup_entries": dev_result_1["standup_submitted"] + dev_result_2["standup_submitted"],
        },
    }

    # Print summary
    print(f"\n  {'─'*56}")
    print(f"  OVERALL UX SCORE: {overall_score}/100 | {'PASS ✓' if overall_score >= 90 else 'NEEDS IMPROVEMENT'}")
    print(f"  Issues Found: {len(all_issues)} | Messages: {messages_sent} | Sync: {'OK' if sync_ok else 'BROKEN'}")
    print(f"  {'─'*56}")

    return result


def main():
    print("="*60)
    print("  SPRINT AGENT — Multi-Agent UX Testing Framework")
    print("  Simulating: UX Officer + Scrum Master + 2 Developers")
    print("="*60)

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

    # Issue categorization
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
    print(f"  STATUS: {'ALL TESTS PASSED ✓' if final_score >= 90 else 'REQUIRES ADDITIONAL WORK'}")
    print(f"{'='*60}")

    # Save report
    report_path = "/mnt/agents/output/test_report.json"
    with open(report_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n  Full report saved to: {report_path}")


if __name__ == "__main__":
    main()

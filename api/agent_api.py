from pathlib import Path
from typing import Optional, List

from storage.persistence_manager import PersistenceManager
from models import (
    Sprint, SprintStatus, Member, Task, TaskStatus,
    DailyLog, InterviewSession, InterviewStatus,
    StoryPoolEntry, STAR, RiskFlag,
    RetroReport, SelfAssessment, Dimension, ReviewStatus,
)
from engines import (
    PlanningEngine, StandupEngine, RiskDetector,
    InterviewEngine, RetroEngine, DashboardEngine, SelfAssessmentEngine,
)


class SprintAgentAPI:
    """Sprint Agent API 服务层"""

    def __init__(self, data_dir: Optional[Path] = None):
        self.persistence = PersistenceManager(data_dir)
        self.planning = PlanningEngine()
        self.standup = StandupEngine()
        self.risk_detector = RiskDetector()
        self.interview = InterviewEngine()
        self.retro = RetroEngine()
        self.dashboard = DashboardEngine()
        self.assessment = SelfAssessmentEngine()

        # 运行时状态
        self.active_sprint: Optional[Sprint] = None
        self.story_pool: List[StoryPoolEntry] = []
        self.active_risks: List[RiskFlag] = []
        self.pending_interviews: dict = {}
        self.config: dict = {}

        self._load_state()

    def _load_state(self):
        self.active_sprint = self.persistence.load_active_sprint()
        self.story_pool = self.persistence.load_story_pool()
        self.config = self.persistence.load_config()

    def _save_state(self):
        if self.active_sprint:
            self.persistence.save_sprint(self.active_sprint)
        self.persistence.save_story_pool(self.story_pool)
        self.persistence.save_config(self.config)

    def get_sprint(self) -> Optional[dict]:
        """获取当前 sprint 数据"""
        if not self.active_sprint:
            return None
        return self.active_sprint.to_dict()

    def get_board_data(self) -> dict:
        """获取看板数据"""
        if not self.active_sprint:
            return {"sprint": None, "stats": self._empty_stats()}

        all_tasks = self.active_sprint.tasks + self.active_sprint.public_tasks
        stats = self._calculate_stats(all_tasks)

        return {
            "sprint": self.active_sprint.to_dict(),
            "stats": stats,
        }

    def update_task_status(self, task_id: str, new_status: str) -> dict:
        """更新任务状态"""
        if not self.active_sprint:
            return {"success": False, "error": "没有活跃的 Sprint"}

        status_map = {
            "not_started": TaskStatus.NOT_STARTED,
            "in_progress": TaskStatus.IN_PROGRESS,
            "completed": TaskStatus.COMPLETED,
            "paused": TaskStatus.PAUSED,
        }

        if new_status not in status_map:
            return {"success": False, "error": f"无效状态: {new_status}"}

        all_tasks = self.active_sprint.tasks + self.active_sprint.public_tasks
        task = None
        for t in all_tasks:
            if t.id == task_id:
                task = t
                break

        if not task:
            return {"success": False, "error": "找不到任务"}

        task.status = status_map[new_status]
        if new_status == "completed":
            from datetime import datetime
            task.completed_at = datetime.now()
        else:
            task.completed_at = None

        self._save_state()
        return {"success": True, "task": task.to_dict()}

    def add_daily_log(self, task_id: str, member_id: str, hours: float,
                      progress_percent: Optional[int] = None,
                      blocker: Optional[str] = None,
                      notes: Optional[str] = None) -> dict:
        """添加日报记录"""
        if not self.active_sprint:
            return {"success": False, "error": "没有活跃的 Sprint"}

        member = None
        for m in self.active_sprint.members:
            if m.id == member_id:
                member = m
                break

        if not member:
            return {"success": False, "error": "找不到成员"}

        all_tasks = self.active_sprint.tasks + self.active_sprint.public_tasks
        task = None
        for t in all_tasks:
            if t.id == task_id:
                task = t
                break

        if not task:
            return {"success": False, "error": "找不到任务"}

        log = DailyLog(
            task_id=task_id,
            member_id=member_id,
            hours=hours,
            progress_percent=progress_percent or 0,
            blocker=blocker,
            notes=notes or "",
        )

        task.daily_logs.append(log)
        task.total_spent = sum(l.hours for l in task.daily_logs)

        # 自动检测风险
        result = self.risk_detector.detect_from_standup(task, log, member)
        self.active_risks.extend(result.get("risks", []))

        # 自动更新状态
        if progress_percent and progress_percent >= 100:
            task.status = TaskStatus.COMPLETED

        self._save_state()
        return {
            "success": True,
            "log": log.to_dict(),
            "risks": [r.to_dict() for r in result.get("risks", [])],
        }

    def get_dashboard(self) -> str:
        """获取团队看板文本"""
        if not self.active_sprint:
            return "❌ 没有活跃的 Sprint。"
        return self.dashboard.generate_dashboard(
            self.active_sprint, self.story_pool, self.active_risks
        )

    def get_member_status(self, member_name: str) -> str:
        """获取个人状态"""
        if not self.active_sprint:
            return "❌ 没有活跃的 Sprint。"
        member = self.active_sprint.get_member_by_name(member_name)
        if not member:
            return f"❌ 找不到成员: {member_name}"
        return self.dashboard.generate_member_status(
            member, self.active_sprint, self.active_risks
        )

    def create_sprint(self, name: str, start_date: str, end_date: str,
                      workdays: int = 10) -> dict:
        """创建 Sprint"""
        from datetime import date
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        self.active_sprint = self.planning.create_sprint(name, start, end, workdays)
        self._save_state()
        return {"success": True, "sprint": self.active_sprint.to_dict()}

    def add_member(self, name: str, coefficient: float = 1.0) -> dict:
        """添加成员"""
        if not self.active_sprint:
            return {"success": False, "error": "没有活跃的 Sprint"}
        member = self.planning.add_member(self.active_sprint, name, coefficient)
        self._save_state()
        return {"success": True, "member": member.to_dict()}

    def add_task(self, name: str, owner_name: str,
                 estimate_low: float, estimate_high: float,
                 priority: int = 5, ddl: Optional[str] = None,
                 is_public: bool = False) -> dict:
        """添加任务"""
        if not self.active_sprint:
            return {"success": False, "error": "没有活跃的 Sprint"}

        member = self.active_sprint.get_member_by_name(owner_name)
        if not member:
            return {"success": False, "error": f"找不到成员: {owner_name}"}

        from datetime import date
        ddl_date = date.fromisoformat(ddl) if ddl else None

        task = self.planning.add_task(
            self.active_sprint, name, member.id,
            estimate_low, estimate_high, priority, ddl_date, is_public
        )
        self._save_state()
        return {"success": True, "task": task.to_dict()}

    def finalize_sprint(self) -> dict:
        """启动 Sprint"""
        if not self.active_sprint:
            return {"success": False, "error": "没有活跃的 Sprint"}
        self.planning.finalize_sprint(self.active_sprint)
        self._save_state()
        return {"success": True, "sprint": self.active_sprint.to_dict()}

    def generate_retro(self, trend_count: int = 0) -> dict:
        """生成 Retro 报告"""
        if not self.active_sprint:
            return {"success": False, "error": "没有活跃的 Sprint"}

        if trend_count > 0:
            historical = self.persistence.load_historical_sprints(trend_count)
            report = self.retro.generate_trend_retro(
                historical, self.active_sprint, self.story_pool, self.active_risks, trend_count
            )
        else:
            report = self.retro.generate_single_retro(
                self.active_sprint, self.story_pool, self.active_risks
            )

        content = self.retro.render_markdown(report, self.active_sprint)
        file_path = self.persistence.export_retro_markdown(content, self.active_sprint.id)
        return {
            "success": True,
            "report": content,
            "file_path": str(file_path),
        }

    def generate_assessment(self, member_name: str, period: str) -> dict:
        """生成自评表"""
        if not self.active_sprint:
            return {"success": False, "error": "没有活跃的 Sprint"}

        member = self.active_sprint.get_member_by_name(member_name)
        if not member:
            return {"success": False, "error": f"找不到成员: {member_name}"}

        historical = self.persistence.load_historical_sprints(12)
        historical.insert(0, self.active_sprint)

        assessment = self.assessment.generate_assessment(
            member, period, historical, self.story_pool
        )
        file_path = self.persistence.export_assessment_markdown(
            assessment.markdown_content, member.name, period
        )

        total_stories = sum(len(d.stories) for d in assessment.dimensions)
        return {
            "success": True,
            "total_stories": total_stories,
            "sprint_count": len(historical),
            "file_path": str(file_path),
            "content": assessment.markdown_content,
        }

    def _calculate_stats(self, tasks: list) -> dict:
        """计算统计数据"""
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        in_progress = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)
        not_started = sum(1 for t in tasks if t.status == TaskStatus.NOT_STARTED)
        paused = sum(1 for t in tasks if t.status == TaskStatus.PAUSED)

        total_estimate = sum(t.estimate_high or 0 for t in tasks)
        total_spent = sum(t.total_spent or 0 for t in tasks)

        blocked = sum(1 for t in tasks
                      if t.blocker or (t.daily_logs and any(l.blocker for l in t.daily_logs)))

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "paused": paused,
            "total_estimate": round(total_estimate, 1),
            "total_spent": round(total_spent, 1),
            "blocked": blocked,
            "completion_rate": round(completed / total * 100, 1) if total > 0 else 0,
        }

    def _empty_stats(self) -> dict:
        return {
            "total": 0, "completed": 0, "in_progress": 0,
            "not_started": 0, "paused": 0,
            "total_estimate": 0, "total_spent": 0,
            "blocked": 0, "completion_rate": 0,
        }

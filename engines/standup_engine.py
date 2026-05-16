import uuid
from datetime import date, datetime
from typing import List, Optional, Tuple

from models.sprint import Sprint
from models.member import Member
from models.task import Task, TaskStatus
from models.daily_log import DailyLog
from models.risk import RiskFlag
from models.interview import InterviewSession
from .risk_detector import RiskDetector
from .interview_engine import InterviewEngine


class StandupEngine:
    """日报引擎"""
    
    def __init__(self):
        self.risk_detector = RiskDetector()
        self.interview_engine = InterviewEngine()
    
    def process_standup_structured(
        self,
        member: Member,
        sprint: Sprint,
        task_index: int,
        hours: float,
        progress: Optional[int] = None,
        blocker: Optional[str] = None,
        notes: str = ""
    ) -> dict:
        """处理结构化日报"""
        # 获取任务
        all_tasks = member.tasks
        if task_index < 1 or task_index > len(all_tasks):
            return {
                "success": False,
                "error": f"无效任务序号 {task_index}，当前有 {len(all_tasks)} 个任务"
            }
        
        task = all_tasks[task_index - 1]
        
        # 创建日志
        log = DailyLog(
            id=f"log_{uuid.uuid4().hex[:8]}",
            date=date.today(),
            member_id=member.id,
            task_id=task.id,
            hours=hours,
            progress_percent=progress,
            blocker=blocker,
            notes=notes,
        )
        
        # 更新任务
        task.daily_logs.append(log)
        task.total_spent += hours
        
        # 更新状态
        if task.status == TaskStatus.NOT_STARTED and hours > 0:
            task.status = TaskStatus.IN_PROGRESS
        
        if progress == 100:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
        
        task.blocker = blocker
        
        # 风险检测
        risks = self.risk_detector.detect_all(task, member, sprint)
        
        # Interview 触发判断
        interview = self.interview_engine.should_trigger(task, member, log, sprint)
        
        return {
            "success": True,
            "log": log,
            "risks": risks,
            "interview": interview,
            "task": task,
        }
    
    def process_standup_natural(
        self,
        member: Member,
        sprint: Sprint,
        text: str
    ) -> dict:
        """处理自然语言日报"""
        from parsers.nlp_engine import NLPEngine
        
        nlp = NLPEngine()
        
        # 获取可用任务名列表
        available_tasks = [t.name for t in member.tasks]
        
        # 提取任务名
        task_name = nlp.extract_task_name(text, available_tasks)
        
        # 解析日志
        log = nlp.parse_standup(text, member.id, task_name)
        
        if not log:
            confidence = nlp.calculate_confidence(text)
            return {
                "success": False,
                "error": f"无法解析日报（置信度 {confidence:.0%}），请使用结构化指令：/standup <序号> <耗时> [进度] [阻塞]",
                "available_tasks": [(i+1, t.name) for i, t in enumerate(member.tasks)],
            }
        
        # 找到对应任务
        task = None
        for t in member.tasks:
            if t.name == task_name or t.id == task_name:
                task = t
                break
        
        if not task:
            return {
                "success": False,
                "error": f"未找到任务 '{task_name}'",
                "available_tasks": [(i+1, t.name) for i, t in enumerate(member.tasks)],
            }
        
        log.date = date.today()
        log.task_id = task.id
        log.id = f"log_{uuid.uuid4().hex[:8]}"
        
        # 更新任务
        task.daily_logs.append(log)
        task.total_spent += log.hours
        
        if task.status == TaskStatus.NOT_STARTED and log.hours > 0:
            task.status = TaskStatus.IN_PROGRESS
        
        if log.progress_percent == 100:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
        
        task.blocker = log.blocker
        
        # 风险检测
        risks = self.risk_detector.detect_all(task, member, sprint)
        
        # Interview
        interview = self.interview_engine.should_trigger(task, member, log, sprint)
        
        return {
            "success": True,
            "log": log,
            "risks": risks,
            "interview": interview,
            "task": task,
        }
    
    def get_standup_prompt(self, member: Member, sprint: Sprint) -> str:
        """生成日报引导"""
        lines = ["📋 今日任务列表："]
        
        for i, task in enumerate(member.tasks, 1):
            status_emoji = {
                TaskStatus.NOT_STARTED: "⚪",
                TaskStatus.IN_PROGRESS: "🔵",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.PAUSED: "⏸️",
            }.get(task.status, "⚪")
            
            progress_str = f" {task.total_spent:.1f}/{task.estimate_high:.1f}天" if task.estimate_high > 0 else ""
            lines.append(f"{i}. {status_emoji} {task.name}{progress_str}")
        
        lines.append("")
        lines.append("请回复: `<序号> <耗时h> [进度%] [阻塞]`")
        lines.append("例: `1 2h 60% 等峰哥确认接口`")
        
        return "\n".join(lines)
    
    def add_missing_data_placeholder(self, member: Member, task: Task, log_date: date) -> DailyLog:
        """添加数据缺失标记"""
        log = DailyLog(
            id=f"log_missing_{uuid.uuid4().hex[:8]}",
            date=log_date,
            member_id=member.id,
            task_id=task.id,
            hours=0,
            notes="数据缺失",
        )
        task.daily_logs.append(log)
        return log

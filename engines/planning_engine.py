import uuid
from datetime import date, datetime, timedelta
from typing import List, Optional

from models.sprint import Sprint, SprintStatus
from models.member import Member
from models.task import Task, TaskStatus


class PlanningEngine:
    """Sprint 规划引擎"""
    
    PUBLIC_TASK_TEMPLATES = [
        "MR审阅",
        "Sprint Review",
        "Oncall",
        "站会",
        "技术分享",
    ]
    
    def create_sprint(
        self,
        name: str,
        start_date: date,
        end_date: date,
        goal: str = ""
    ) -> Sprint:
        """创建新 sprint"""
        sprint_id = f"{start_date.isoformat()}_{end_date.isoformat()}"
        workdays = self._calculate_workdays(start_date, end_date)
        
        sprint = Sprint(
            id=sprint_id,
            name=name,
            start_date=start_date,
            end_date=end_date,
            workdays=workdays,
            status=SprintStatus.PLANNING,
            goal=goal,
        )
        return sprint
    
    def add_member(
        self,
        sprint: Sprint,
        name: str,
        coefficient: float = 1.0
    ) -> Member:
        """添加成员"""
        member = Member(
            id=f"m_{name}",
            name=name,
            coefficient=coefficient,
        )
        sprint.members.append(member)
        return member
    
    def add_task(
        self,
        sprint: Sprint,
        name: str,
        owner_id: str,
        estimate_low: float,
        estimate_high: float,
        priority: int = 5,
        ddl: Optional[date] = None,
        is_public: bool = False,
        us: str = ""
    ) -> Task:
        """添加任务"""
        task = Task(
            id=f"t_{uuid.uuid4().hex[:8]}",
            name=name,
            us=us,
            owner_id=owner_id,
            priority=priority,
            ddl=ddl,
            estimate_low=estimate_low,
            estimate_high=estimate_high,
            is_public=is_public,
        )
        
        if is_public:
            sprint.public_tasks.append(task)
        else:
            sprint.tasks.append(task)
            # 绑定到成员
            member = sprint.get_member_by_name(owner_id)
            if member:
                member.tasks.append(task)
        
        return task
    
    def assign_task(self, task: Task, member: Member) -> None:
        """分配任务"""
        task.owner_id = member.id
        member.tasks.append(task)
    
    def set_member_leave(
        self,
        member: Member,
        days: float,
        from_date: Optional[date] = None
    ) -> None:
        """记录请假"""
        member.leave_days += days
    
    def finalize_sprint(self, sprint: Sprint) -> None:
        """启动 sprint"""
        sprint.status = SprintStatus.ACTIVE
        
        # 为每个成员生成公共任务
        for template_name in self.PUBLIC_TASK_TEMPLATES:
            for member in sprint.members:
                task = Task(
                    id=f"pt_{template_name}_{member.id}",
                    name=template_name,
                    owner_id=member.id,
                    is_public=True,
                    estimate_low=0,
                    estimate_high=0,
                )
                sprint.public_tasks.append(task)
                member.tasks.append(task)
    
    def generate_carry_over(self, sprint: Sprint) -> dict:
        """生成 carry-over 清单"""
        result = {
            "completed": [],
            "in_progress": [],
            "not_started": [],
            "paused": [],
        }
        
        for task in sprint.tasks:
            if task.status == TaskStatus.COMPLETED:
                result["completed"].append(task)
            elif task.status == TaskStatus.IN_PROGRESS:
                result["in_progress"].append(task)
            elif task.status == TaskStatus.NOT_STARTED:
                result["not_started"].append(task)
            elif task.status == TaskStatus.PAUSED:
                result["paused"].append(task)
        
        return result
    
    def _calculate_workdays(self, start: date, end: date) -> int:
        """计算工作日（排除周末）"""
        days = 0
        current = start
        while current <= end:
            if current.weekday() < 5:  # 周一到周五
                days += 1
            current += timedelta(days=1)
        return days
    
    def set_task_estimate(
        self,
        task: Task,
        estimate_low: float,
        estimate_high: float
    ) -> None:
        """设置工作量预估"""
        task.estimate_low = estimate_low
        task.estimate_high = estimate_high
    
    def pause_task(self, task: Task, reason: str) -> None:
        """挂起任务"""
        task.status = TaskStatus.PAUSED
        task.paused_at = datetime.now()
        task.paused_reason = reason
    
    def resume_task(self, task: Task) -> None:
        """恢复任务"""
        task.status = TaskStatus.IN_PROGRESS
        task.paused_at = None
        task.paused_reason = ""
    
    def reassign_task(self, task: Task, new_member: Member, old_member: Member) -> None:
        """重新分配任务"""
        if task in old_member.tasks:
            old_member.tasks.remove(task)
        task.owner_id = new_member.id
        new_member.tasks.append(task)

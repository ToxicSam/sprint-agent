import uuid
from datetime import date, datetime, timedelta
from typing import List, Optional

from models.sprint import Sprint
from models.member import Member
from models.task import Task, TaskStatus
from models.daily_log import DailyLog
from models.risk import RiskFlag, RiskType, RiskSeverity
from models.interview import InterviewSession, InterviewStatus, Question, QuestionType, Answer


class RiskDetector:
    """风险检测器"""
    
    ESTIMATE_EXCEED_THRESHOLD = 0.20
    ESTIMATE_CRITICAL_THRESHOLD = 0.50
    NO_PROGRESS_DAYS = 3
    CAPACITY_WARNING_THRESHOLD = 0.90
    CAPACITY_CRITICAL_THRESHOLD = 1.00
    DEADLINE_DAYS_WARNING = 2
    BLOCKER_STUCK_DAYS = 2
    
    def detect_all(self, task: Task, member: Member, sprint: Sprint) -> List[RiskFlag]:
        """检测所有风险"""
        risks = []
        
        # 1. 预估超支
        if task.estimate_high > 0 and task.total_spent > task.estimate_high * (1 + self.ESTIMATE_EXCEED_THRESHOLD):
            severity = RiskSeverity.HIGH if task.total_spent > task.estimate_high * (1 + self.ESTIMATE_CRITICAL_THRESHOLD) else RiskSeverity.MEDIUM
            deviation = ((task.total_spent - task.estimate_high) / task.estimate_high) * 100
            risks.append(RiskFlag(
                id=f"risk_{uuid.uuid4().hex[:8]}",
                type=RiskType.ESTIMATE_EXCEEDED,
                severity=severity,
                member_id=member.id,
                task_id=task.id,
                message=f"预估 {task.estimate_high}天，已花 {task.total_spent}天，超支 {deviation:.0f}%"
            ))
        
        # 2. 连续无进展
        recent_logs = self._get_recent_logs(task, days=self.NO_PROGRESS_DAYS)
        if len(recent_logs) >= self.NO_PROGRESS_DAYS and all(l.hours == 0 for l in recent_logs):
            risks.append(RiskFlag(
                id=f"risk_{uuid.uuid4().hex[:8]}",
                type=RiskType.NO_PROGRESS,
                severity=RiskSeverity.MEDIUM,
                member_id=member.id,
                task_id=task.id,
                message=f"连续 {self.NO_PROGRESS_DAYS} 天无进展"
            ))
        
        # 3. 容量告警
        member_total = sum(t.total_spent for t in member.tasks)
        capacity = member.capacity(sprint)
        if member_total > capacity * self.CAPACITY_WARNING_THRESHOLD:
            severity = RiskSeverity.HIGH if member_total > capacity else RiskSeverity.MEDIUM
            risks.append(RiskFlag(
                id=f"risk_{uuid.uuid4().hex[:8]}",
                type=RiskType.CAPACITY_WARNING,
                severity=severity,
                member_id=member.id,
                message=f"已用 {member_total:.1f}/{capacity:.1f} 天容量"
            ))
        
        # 4. 分配超容量
        member_estimate_total = sum(t.estimate_high for t in member.tasks)
        if member_estimate_total > capacity:
            risks.append(RiskFlag(
                id=f"risk_{uuid.uuid4().hex[:8]}",
                type=RiskType.OVER_CAPACITY,
                severity=RiskSeverity.HIGH,
                member_id=member.id,
                message=f"任务预估总量 {member_estimate_total:.1f} 超过容量 {capacity:.1f}"
            ))
        
        # 5. DDL 临近
        if task.ddl and task.status != TaskStatus.COMPLETED:
            days_to_ddl = (task.ddl - date.today()).days
            if days_to_ddl <= self.DEADLINE_DAYS_WARNING and task.status == TaskStatus.NOT_STARTED:
                risks.append(RiskFlag(
                    id=f"risk_{uuid.uuid4().hex[:8]}",
                    type=RiskType.DEADLINE_APPROACHING,
                    severity=RiskSeverity.HIGH,
                    member_id=member.id,
                    task_id=task.id,
                    message=f"DDL {task.ddl} 距今 {days_to_ddl} 天，任务未开始"
                ))
        
        # 6. 阻塞长期未解决
        if task.blocker:
            blocker_logs = self._get_logs_with_blocker(task, days=self.BLOCKER_STUCK_DAYS)
            if len(blocker_logs) >= self.BLOCKER_STUCK_DAYS:
                risks.append(RiskFlag(
                    id=f"risk_{uuid.uuid4().hex[:8]}",
                    type=RiskType.BLOCKER_STUCK,
                    severity=RiskSeverity.MEDIUM,
                    member_id=member.id,
                    task_id=task.id,
                    message=f"阻塞 '{task.blocker}' 已 {len(blocker_logs)} 天未解决"
                ))
        
        return risks
    
    def auto_resolve_risks(self, task: Task, member: Member, existing_risks: List[RiskFlag]) -> List[RiskFlag]:
        """自动解除已解决的风险"""
        resolved = []
        for risk in existing_risks:
            if risk.resolved_at:
                continue
            
            should_resolve = False
            
            if risk.type == RiskType.ESTIMATE_EXCEEDED:
                if task.status == TaskStatus.COMPLETED:
                    should_resolve = True
            
            elif risk.type == RiskType.NO_PROGRESS:
                recent_logs = self._get_recent_logs(task, days=1)
                if recent_logs and recent_logs[0].hours > 0:
                    should_resolve = True
            
            elif risk.type == RiskType.CAPACITY_WARNING:
                member_total = sum(t.total_spent for t in member.tasks)
                # 这里需要 sprint 参数，简化处理
                should_resolve = False
            
            elif risk.type == RiskType.DEADLINE_APPROACHING:
                if task.status == TaskStatus.COMPLETED or (task.ddl and task.ddl > date.today() + timedelta(days=self.DEADLINE_DAYS_WARNING)):
                    should_resolve = True
            
            elif risk.type == RiskType.BLOCKER_STUCK:
                if not task.blocker:
                    should_resolve = True
            
            if should_resolve:
                risk.resolved_at = datetime.now()
                risk.auto_resolved = True
                resolved.append(risk)
        
        return resolved
    
    def _get_recent_logs(self, task: Task, days: int) -> List[DailyLog]:
        """获取最近 N 天的日志"""
        cutoff = date.today() - timedelta(days=days)
        return [log for log in task.daily_logs if log.date and log.date >= cutoff]
    
    def _get_logs_with_blocker(self, task: Task, days: int) -> List[DailyLog]:
        """获取带阻塞的最近日志"""
        cutoff = date.today() - timedelta(days=days)
        return [log for log in task.daily_logs if log.date and log.date >= cutoff and log.blocker]

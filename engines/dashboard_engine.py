from datetime import date, datetime, timedelta
from typing import List, Dict

from models.sprint import Sprint
from models.member import Member
from models.task import Task, TaskStatus
from models.risk import RiskFlag, RiskSeverity
from models.story_pool import StoryPoolEntry


class DashboardEngine:
    """晾晒看板引擎"""
    
    def generate_dashboard(
        self,
        sprint: Sprint,
        story_pool: List[StoryPoolEntry],
        active_risks: List[RiskFlag],
    ) -> str:
        """生成文本看板"""
        lines = []
        
        # 标题
        lines.append("═══════════════════════════════════════")
        lines.append(f"  Sprint {sprint.name} Dashboard (晾晒)")
        lines.append("═══════════════════════════════════════")
        lines.append("")
        
        # 整体状态
        overall_progress = self._calculate_overall_progress(sprint)
        health = self._get_sprint_health(sprint, active_risks)
        missing_data = self._calculate_missing_data(sprint)
        
        lines.append(f"整体进度: {overall_progress:.0f}% | "
                    f"状态: {health} | "
                    f"风险: {len([r for r in active_risks if not r.resolved_at])} | "
                    f"数据缺失: {missing_data['total']}天")
        lines.append("")
        
        # 成员状态
        lines.append("── 成员状态 ──")
        for member in sprint.members:
            member_status = self._render_member_status(member, sprint, active_risks)
            lines.append(member_status)
        lines.append("")
        
        # 公共开销
        public_overhead = self._calculate_public_overhead(sprint)
        if public_overhead:
            lines.append("── 公共开销 ──")
            for name, hours in public_overhead.items():
                lines.append(f"  {name}: {hours:.1f}h")
            lines.append("")
        
        # 风险详情
        unresolved_risks = [r for r in active_risks if not r.resolved_at]
        if unresolved_risks:
            lines.append("── 风险详情 ──")
            for risk in unresolved_risks[:5]:  # 最多显示5个
                member = sprint.get_member_by_name(risk.member_id)
                member_name = member.name if member else risk.member_id
                lines.append(f"{risk.severity.value} {member_name}: {risk.message}")
            if len(unresolved_risks) > 5:
                lines.append(f"  ... 还有 {len(unresolved_risks) - 5} 个风险")
            lines.append("")
        
        # Interview 统计
        sprint_stories = [s for s in story_pool if s.sprint_id == sprint.id]
        if sprint_stories:
            lines.append("── 事迹统计 ──")
            for member in sprint.members:
                member_stories = [s for s in sprint_stories if s.member_id == member.id]
                if member_stories:
                    lines.append(f"  {member.name}: {len(member_stories)} 个事迹候选")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_member_status(
        self,
        member: Member,
        sprint: Sprint,
        active_risks: List[RiskFlag],
    ) -> str:
        """生成个人状态卡片"""
        lines = []
        
        capacity = member.capacity(sprint)
        total_spent = sum(t.total_spent for t in member.tasks)
        utilization = (total_spent / capacity * 100) if capacity > 0 else 0
        
        # 进度条
        bar = self._render_progress_bar(total_spent, capacity)
        
        # 风险计数
        member_risks = [r for r in active_risks 
                        if r.member_id == member.id and not r.resolved_at]
        risk_emoji = "🔴" if any(r.severity.value == "🔴" for r in member_risks) else \
                     "🟡" if member_risks else "✅"
        
        lines.append(f"{member.name:8s} {bar} {total_spent:.1f}/{capacity:.1f}天 "
                    f"| {risk_emoji} {len(member_risks)}个风险")
        
        # 当前阻塞
        current_blockers = []
        for task in member.tasks:
            if task.blocker and task.status != TaskStatus.COMPLETED:
                current_blockers.append(f"{task.name}: {task.blocker}")
        
        if current_blockers:
            lines.append(f"         阻塞: {'; '.join(current_blockers[:2])}")
        
        return "\n".join(lines)
    
    def _render_progress_bar(self, used: float, total: float, width: int = 10) -> str:
        """渲染 Unicode 进度条"""
        if total <= 0:
            return "░" * width
        filled = int((used / total) * width)
        filled = min(filled, width)
        return "█" * filled + "░" * (width - filled)
    
    def _calculate_overall_progress(self, sprint: Sprint) -> float:
        """计算整体进度"""
        if not sprint.tasks:
            return 0.0
        
        total_weight = 0.0
        completed_weight = 0.0
        
        for task in sprint.tasks:
            weight = task.estimate_high if task.estimate_high > 0 else 1.0
            total_weight += weight
            
            if task.status == TaskStatus.COMPLETED:
                completed_weight += weight
            elif task.status == TaskStatus.IN_PROGRESS:
                # 按进度百分比计算
                progress = 0.0
                if task.daily_logs:
                    latest_log = max(task.daily_logs, key=lambda l: l.date or date.min)
                    if latest_log.progress_percent:
                        progress = latest_log.progress_percent / 100.0
                completed_weight += weight * progress
        
        return (completed_weight / total_weight * 100) if total_weight > 0 else 0.0
    
    def _get_sprint_health(self, sprint: Sprint, risks: List[RiskFlag]) -> str:
        """判断 sprint 健康度"""
        unresolved = [r for r in risks if not r.resolved_at]
        has_high = any(r.severity.value == "🔴" for r in unresolved)
        
        if has_high:
            return "🔴 紧急"
        
        overall_progress = self._calculate_overall_progress(sprint)
        mid_point = sprint.workdays / 2
        days_passed = (date.today() - sprint.start_date).days
        
        if days_passed > mid_point and overall_progress < 50:
            return "🟡 警告"
        
        if unresolved:
            return "🟡 警告"
        
        return "🟢 健康"
    
    def _calculate_missing_data(self, sprint: Sprint) -> dict:
        """计算数据缺失"""
        total_missing = 0
        per_member = {}
        
        days_passed = (date.today() - sprint.start_date).days + 1
        
        for member in sprint.members:
            member_missing = 0
            # 检查每个工作日是否有日志
            for day_offset in range(min(days_passed, sprint.workdays)):
                check_date = sprint.start_date + timedelta(days=day_offset)
                if check_date.weekday() >= 5:  # 跳过周末
                    continue
                
                has_log = False
                for task in member.tasks:
                    for log in task.daily_logs:
                        if log.date == check_date and log.hours > 0:
                            has_log = True
                            break
                    if has_log:
                        break
                
                if not has_log:
                    member_missing += 1
                    total_missing += 1
            
            if member_missing > 0:
                per_member[member.name] = member_missing
        
        return {"total": total_missing, "per_member": per_member}
    
    def _calculate_public_overhead(self, sprint: Sprint) -> Dict[str, float]:
        """计算公共开销"""
        overhead = {}
        
        for task in sprint.public_tasks:
            if task.name not in overhead:
                overhead[task.name] = 0.0
            overhead[task.name] += task.total_spent
        
        return overhead
    
    def _render_member_status(
        self,
        member: Member,
        sprint: Sprint,
        active_risks: List[RiskFlag],
    ) -> str:
        """渲染成员状态行"""
        capacity = member.capacity(sprint)
        total_spent = sum(t.total_spent for t in member.tasks)
        bar = self._render_progress_bar(total_spent, capacity)
        
        member_risks = [r for r in active_risks 
                        if r.member_id == member.id and not r.resolved_at]
        risk_emoji = "🔴" if any(r.severity.value == "🔴" for r in member_risks) else \
                     "🟡" if member_risks else "✅"
        
        line = f"{member.name:8s} {bar} {total_spent:.1f}/{capacity:.1f}天 | {risk_emoji} {len(member_risks)}个风险"
        
        # 阻塞
        blockers = []
        for task in member.tasks:
            if task.blocker and task.status != TaskStatus.COMPLETED:
                blockers.append(f"{task.name}: {task.blocker}")
        
        if blockers:
            line += f"\n         阻塞: {'; '.join(blockers[:2])}"
        
        return line

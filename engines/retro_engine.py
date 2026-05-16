import uuid
from datetime import date, datetime, timedelta
from typing import List, Optional

from models.sprint import Sprint, SprintStatus
from models.member import Member
from models.task import Task, TaskStatus
from models.risk import RiskFlag
from models.retro import (
    RetroReport, MemberSummary, PublicOverhead,
    InterviewSummary, TrendAnalysis
)
from models.story_pool import StoryPoolEntry


class RetroEngine:
    """回顾引擎"""

    def generate_single_retro(
        self,
        sprint: Sprint,
        story_pool: List[StoryPoolEntry],
        all_risks: List[RiskFlag],
    ) -> RetroReport:
        """生成本 sprint retro 报告"""
        report = RetroReport(
            id=f"retro_{uuid.uuid4().hex[:8]}",
            sprint_id=sprint.id,
        )

        # 1. 成员摘要
        for member in sprint.members:
            summary = self._calculate_member_summary(member, sprint, story_pool)
            report.member_summaries.append(summary)

        # 2. 风险标记（未解决的）
        report.risk_flags = [r for r in all_risks if r.sprint_id == sprint.id and not r.resolved_at]

        # 3. 公共开销
        report.public_overhead = self._calculate_public_overhead(sprint)

        # 4. Interview 摘要
        report.interview_summary = self._summarize_interviews(sprint, story_pool)

        # 5. 数据缺失
        missing_data = self._calculate_missing_data(sprint)
        report.missing_data_days = missing_data["total"]
        report.missing_data_members = list(missing_data["per_member"].keys())

        return report

    def generate_trend_retro(
        self,
        sprints: List[Sprint],
        focus_sprint: Sprint,
        story_pool: List[StoryPoolEntry],
        all_risks: List[RiskFlag],
        n: int = 3,
    ) -> RetroReport:
        """生成跨 sprint 趋势报告"""
        report = self.generate_single_retro(focus_sprint, story_pool, all_risks)

        # 加载最近 N 个 sprint
        recent_sprints = [s for s in sprints if s.id != focus_sprint.id][:n]
        all_sprints = [focus_sprint] + recent_sprints

        # 趋势分析
        report.trend_analysis = self._generate_trend_analysis(all_sprints, story_pool)

        return report

    def _calculate_member_summary(
        self,
        member: Member,
        sprint: Sprint,
        story_pool: List[StoryPoolEntry],
    ) -> MemberSummary:
        """计算个人摘要"""
        tasks = member.tasks
        total_spent = sum(t.total_spent for t in tasks)
        total_estimate_low = sum(t.estimate_low for t in tasks)
        total_estimate_high = sum(t.estimate_high for t in tasks)

        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        in_progress = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)
        paused = sum(1 for t in tasks if t.status == TaskStatus.PAUSED)

        difficulty = self.calculate_difficulty(total_spent, total_estimate_high)
        credibility = self.calculate_credibility(total_estimate_high, total_spent)
        deviation = self.calculate_estimate_deviation(total_estimate_high, total_spent)

        capacity = member.capacity(sprint)
        utilization = (total_spent / capacity * 100) if capacity > 0 else 0

        # 数据缺失
        missing_days = self._count_missing_days(member, sprint)

        # 事迹数
        stories = [s for s in story_pool if s.member_id == member.id and s.sprint_id == sprint.id]

        return MemberSummary(
            member_id=member.id,
            total_spent=total_spent,
            total_estimate_low=total_estimate_low,
            total_estimate_high=total_estimate_high,
            tasks_completed=completed,
            tasks_in_progress=in_progress,
            tasks_paused=paused,
            difficulty=difficulty,
            credibility=credibility,
            estimate_deviation=deviation,
            capacity_utilization=utilization,
            missing_data_days=missing_days,
            story_count=len(stories),
        )

    def _calculate_public_overhead(self, sprint: Sprint) -> PublicOverhead:
        """计算公共开销"""
        total = 0.0
        breakdown = {}
        member_count = len(sprint.members)

        for task in sprint.public_tasks:
            total += task.total_spent
            if task.name not in breakdown:
                breakdown[task.name] = 0.0
            breakdown[task.name] += task.total_spent

        per_member_avg = total / member_count if member_count > 0 else 0.0

        # 容量占比
        total_capacity = sum(m.capacity(sprint) for m in sprint.members)
        percentage = (total / total_capacity * 100) if total_capacity > 0 else 0.0

        # 简化 breakdown：按人均
        avg_breakdown = {k: v / member_count for k, v in breakdown.items()} if member_count > 0 else breakdown

        return PublicOverhead(
            total_hours=total,
            per_member_avg=per_member_avg,
            breakdown=avg_breakdown,
            percentage_of_capacity=percentage,
        )

    def _summarize_interviews(
        self,
        sprint: Sprint,
        story_pool: List[StoryPoolEntry],
    ) -> InterviewSummary:
        """汇总 interview 数据"""
        sprint_stories = [s for s in story_pool if s.sprint_id == sprint.id and s.source == "interview"]

        return InterviewSummary(
            total_sessions=len(sprint_stories),  # 简化：每个 story 对应一个 session
            completed_sessions=len([s for s in sprint_stories if s.confirmed]),
            skipped_sessions=0,  # 暂不追踪 skip
            stories_generated=len(sprint_stories),
        )

    def _calculate_missing_data(self, sprint: Sprint) -> dict:
        """计算数据缺失"""
        total_missing = 0
        per_member = {}

        days_passed = (date.today() - sprint.start_date).days + 1

        for member in sprint.members:
            member_missing = 0
            for day_offset in range(min(days_passed, sprint.workdays)):
                check_date = sprint.start_date + timedelta(days=day_offset)
                if check_date.weekday() >= 5:
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

    def _count_missing_days(self, member: Member, sprint: Sprint) -> int:
        """计算成员数据缺失天数"""
        days_passed = (date.today() - sprint.start_date).days + 1
        missing = 0

        for day_offset in range(min(days_passed, sprint.workdays)):
            check_date = sprint.start_date + timedelta(days=day_offset)
            if check_date.weekday() >= 5:
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
                missing += 1

        return missing

    def _generate_trend_analysis(
        self,
        sprints: List[Sprint],
        story_pool: List[StoryPoolEntry],
    ) -> TrendAnalysis:
        """生成跨 sprint 趋势分析"""
        sprint_ids = [s.id for s in sprints]

        # 可信度趋势
        accuracy_trend = []
        for sprint in sprints:
            total_estimate = sum(t.estimate_high for m in sprint.members for t in m.tasks)
            total_actual = sum(t.total_spent for m in sprint.members for t in m.tasks)
            credibility = self.calculate_credibility(total_estimate, total_actual)
            accuracy_trend.append(credibility)

        # 容量利用率趋势
        utilization_trend = []
        for sprint in sprints:
            total_capacity = sum(m.capacity(sprint) for m in sprint.members)
            total_spent = sum(t.total_spent for m in sprint.members for t in m.tasks)
            utilization = (total_spent / total_capacity * 100) if total_capacity > 0 else 0
            utilization_trend.append(utilization)

        # 事迹密度趋势
        story_trend = []
        for sprint in sprints:
            stories = [s for s in story_pool if s.sprint_id == sprint.id]
            story_trend.append(len(stories))

        # 公共开销趋势
        overhead_trend = []
        for sprint in sprints:
            total_public = sum(t.total_spent for t in sprint.public_tasks)
            total_capacity = sum(m.capacity(sprint) for m in sprint.members)
            percentage = (total_public / total_capacity * 100) if total_capacity > 0 else 0
            overhead_trend.append(percentage)

        return TrendAnalysis(
            sprint_ids=sprint_ids,
            estimate_accuracy_trend=accuracy_trend,
            capacity_utilization_trend=utilization_trend,
            story_density_trend=story_trend,
            public_overhead_trend=overhead_trend,
        )

    def render_markdown(self, report: RetroReport, sprint: Sprint) -> str:
        """渲染 retro Markdown 报告"""
        lines = []
        lines.append(f"# Sprint {sprint.name} Retro 报告")
        lines.append("")
        lines.append(f"生成时间: {report.generated_at.strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # 整体指标
        lines.append("## 整体指标")
        lines.append("")
        total_estimate = sum(ms.total_estimate_high for ms in report.member_summaries)
        total_actual = sum(ms.total_spent for ms in report.member_summaries)
        avg_difficulty = sum(ms.difficulty for ms in report.member_summaries) / len(report.member_summaries) if report.member_summaries else 0
        avg_credibility = sum(ms.credibility for ms in report.member_summaries) / len(report.member_summaries) if report.member_summaries else 0

        lines.append(f"- 预估总量: {total_estimate:.1f} 人天")
        lines.append(f"- 实际总量: {total_actual:.1f} 人天")
        lines.append(f"- 平均难易度: {avg_difficulty:.2f} (<1 偏难, >1 偏易)")
        lines.append(f"- 平均可信度: {avg_credibility:.2f} (>1 预估偏乐观)")
        lines.append("")

        # 个人表现
        lines.append("## 个人表现")
        lines.append("")
        for ms in report.member_summaries:
            member = sprint.get_member_by_name(ms.member_id)
            name = member.name if member else ms.member_id
            lines.append(f"### {name}")
            lines.append(f"- 完成: {ms.tasks_completed} | 进行中: {ms.tasks_in_progress} | 挂起: {ms.tasks_paused}")
            lines.append(f"- 预估: {ms.total_estimate_high:.1f} | 实际: {ms.total_spent:.1f} | 偏差: {ms.estimate_deviation:+.0f}%")
            lines.append(f"- 难易度: {ms.difficulty:.2f} | 可信度: {ms.credibility:.2f}")
            lines.append(f"- 容量利用率: {ms.capacity_utilization:.0f}%")
            lines.append(f"- 事迹候选: {ms.story_count} 个")
            lines.append(f"- 数据缺失: {ms.missing_data_days} 天")
            lines.append("")

        # 风险
        if report.risk_flags:
            lines.append("## 风险")
            lines.append("")
            for risk in report.risk_flags:
                member = sprint.get_member_by_name(risk.member_id)
                name = member.name if member else risk.member_id
                lines.append(f"{risk.severity.value} **{name}**: {risk.message}")
            lines.append("")

        # 公共开销
        if report.public_overhead:
            lines.append("## 公共开销")
            lines.append("")
            lines.append(f"团队总公共耗时: {report.public_overhead.total_hours:.1f}h")
            lines.append(f"人均: {report.public_overhead.per_member_avg:.1f}h")
            lines.append(f"占容量: {report.public_overhead.percentage_of_capacity:.1f}%")
            lines.append("")
            for name, hours in report.public_overhead.breakdown.items():
                lines.append(f"- {name}: {hours:.1f}h")
            lines.append("")

        # Interview 统计
        if report.interview_summary:
            lines.append("## Interview/Grill 统计")
            lines.append("")
            lines.append(f"- 总 session: {report.interview_summary.total_sessions}")
            lines.append(f"- 完成: {report.interview_summary.completed_sessions}")
            lines.append(f"- 产出事迹: {report.interview_summary.stories_generated}")
            lines.append("")

        # 趋势分析
        if report.trend_analysis:
            lines.append("## 跨 Sprint 趋势")
            lines.append("")
            lines.append("| Sprint | 可信度 | 容量利用率 | 事迹数 | 公共开销% |")
            lines.append("|--------|--------|------------|--------|-----------|")
            for i, sid in enumerate(report.trend_analysis.sprint_ids):
                cred = report.trend_analysis.estimate_accuracy_trend[i] if i < len(report.trend_analysis.estimate_accuracy_trend) else 0
                util = report.trend_analysis.capacity_utilization_trend[i] if i < len(report.trend_analysis.capacity_utilization_trend) else 0
                story = report.trend_analysis.story_density_trend[i] if i < len(report.trend_analysis.story_density_trend) else 0
                overhead = report.trend_analysis.public_overhead_trend[i] if i < len(report.trend_analysis.public_overhead_trend) else 0
                lines.append(f"| {sid} | {cred:.2f} | {util:.0f}% | {story} | {overhead:.1f}% |")
            lines.append("")

        # 数据缺失
        lines.append("## 数据质量")
        lines.append("")
        lines.append(f"数据缺失天数: {report.missing_data_days}")
        if report.missing_data_members:
            lines.append(f"缺失成员: {', '.join(report.missing_data_members)}")
        lines.append("")

        return "\n".join(lines)

    # ========== 核心计算公式 ==========
    @staticmethod
    def calculate_difficulty(actual: float, estimate_high: float) -> float:
        """难易度 = 实际 / 抬头预估"""
        return actual / estimate_high if estimate_high > 0 else 0.0

    @staticmethod
    def calculate_credibility(estimate_high: float, actual: float) -> float:
        """可信度 = 抬头预估 / 实际"""
        return estimate_high / actual if actual > 0 else 0.0

    @staticmethod
    def calculate_estimate_deviation(estimate_high: float, actual: float) -> float:
        """预估偏差百分比"""
        if estimate_high == 0:
            return 0.0
        return ((actual - estimate_high) / estimate_high) * 100

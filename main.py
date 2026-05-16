import sys
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict

from models import (
    Sprint, SprintStatus, Member, Task, TaskStatus,
    DailyLog, InterviewSession, InterviewStatus,
    StoryPoolEntry, STAR, RiskFlag,
    RetroReport, SelfAssessment, Dimension, ReviewStatus,
)
from parsers import CommandParser, ParsedCommand, NLPEngine
from storage import PersistenceManager
from engines import (
    PlanningEngine, StandupEngine, RiskDetector,
    InterviewEngine, RetroEngine, DashboardEngine, SelfAssessmentEngine,
)


class SprintAgent:
    """Sprint Agent 主入口"""

    def __init__(self):
        self.parser = CommandParser()
        self.planning = PlanningEngine()
        self.standup = StandupEngine()
        self.risk_detector = RiskDetector()
        self.interview = InterviewEngine()
        self.retro = RetroEngine()
        self.dashboard = DashboardEngine()
        self.assessment = SelfAssessmentEngine()
        self.persistence = PersistenceManager()
        self.nlp = NLPEngine()

        # 运行时状态
        self.active_sprint: Optional[Sprint] = None
        self.story_pool: List[StoryPoolEntry] = []
        self.active_risks: List[RiskFlag] = []
        self.pending_interviews: Dict[str, InterviewSession] = {}  # session_id -> session
        self.config: Dict = {}

        # 加载持久化数据
        self._load_state()

    def _load_state(self):
        """加载持久化状态"""
        self.active_sprint = self.persistence.load_active_sprint()
        self.story_pool = self.persistence.load_story_pool()
        self.config = self.persistence.load_config()

    def _save_state(self):
        """保存当前状态"""
        if self.active_sprint:
            self.persistence.save_sprint(self.active_sprint)
        self.persistence.save_story_pool(self.story_pool)
        self.persistence.save_config(self.config)

    def process(self, user_input: str, user_id: str = "", user_name: str = "") -> str:
        """处理用户输入，返回响应文本"""
        user_input = user_input.strip()

        # 1. 尝试结构化解析
        cmd = self.parser.parse(user_input)

        # 2. 如果没有结构化命令，尝试自然语言
        if not cmd:
            # 检查是否是 interview 回答
            if self._is_interview_answer(user_id):
                return self._handle_interview_answer(user_id, user_input)

            # 尝试自然语言 standup
            if self.active_sprint and self.active_sprint.status == SprintStatus.ACTIVE:
                member = self.active_sprint.get_member_by_name(user_name or user_id)
                if member:
                    return self._handle_natural_standup(member, user_input)

            return "❓ 无法识别指令。使用 `/help` 查看可用命令。"

        # 3. 路由到对应处理器
        return self._route_command(cmd, user_id, user_name)

    def _route_command(self, cmd: ParsedCommand, user_id: str, user_name: str) -> str:
        """路由命令到对应处理器"""
        action = cmd.action
        sub = cmd.sub_action

        # Planning
        if action == "planning":
            return self._handle_planning(cmd, user_id, user_name)

        # Standup
        if action == "standup":
            return self._handle_standup(cmd, user_id, user_name)

        # Admin
        if action == "admin":
            return self._handle_admin(cmd, user_id, user_name)

        # Query
        if action == "query":
            return self._handle_query(cmd, user_id, user_name)

        # Retro
        if action == "retro":
            return self._handle_retro(cmd, user_id, user_name)

        # Assessment
        if action == "assessment":
            return self._handle_assessment(cmd, user_id, user_name)

        # Config
        if action == "config":
            return self._handle_config(cmd, user_id, user_name)

        # Interview
        if action == "interview":
            return self._handle_interview_command(cmd, user_id, user_name)

        # Import
        if action == "import":
            return self._handle_import(cmd, user_id, user_name)

        return f"❓ 未知命令: {cmd.raw}"

    # ========== Planning Handlers ==========

    def _handle_planning(self, cmd: ParsedCommand, user_id: str, user_name: str) -> str:
        if not self._is_sm(user_id):
            return "❌ 只有 Scrum Master 可以执行规划命令。"

        sub = cmd.sub_action

        if sub == "start":
            name, start_str, end_str = cmd.args[0], cmd.args[1], cmd.args[2]
            start_date = date.fromisoformat(start_str)
            end_date = date.fromisoformat(end_str)
            self.active_sprint = self.planning.create_sprint(name, start_date, end_date)
            self._save_state()
            return f"✅ Sprint '{name}' 已创建 ({start_str} ~ {end_str})，请添加成员和任务。"

        if sub == "add-member":
            if not self.active_sprint:
                return "❌ 没有活跃的 Sprint，先执行 /planning start"
            name, coeff = cmd.args[0], float(cmd.args[1])
            member = self.planning.add_member(self.active_sprint, name, coeff)
            self._save_state()
            return f"✅ 成员 '{name}' 已添加，COE系数 {coeff}。"

        if sub == "add-task":
            if not self.active_sprint:
                return "❌ 没有活跃的 Sprint"
            # 尝试解析
            task_info = cmd.args[0] if cmd.args else ""
            return self._interactive_add_task(task_info)

        if sub == "assign":
            if not self.active_sprint:
                return "❌ 没有活跃的 Sprint"
            task_name, member_name = cmd.args[0], cmd.args[1]
            task = self.active_sprint.get_task_by_name(task_name)
            member = self.active_sprint.get_member_by_name(member_name)
            if not task:
                return f"❌ 找不到任务: {task_name}"
            if not member:
                return f"❌ 找不到成员: {member_name}"
            self.planning.assign_task(task, member)
            self._save_state()
            return f"✅ 任务 '{task_name}' 已分配给 '{member_name}'。"

        if sub == "estimate":
            if not self.active_sprint:
                return "❌ 没有活跃的 Sprint"
            task_name, low, high = cmd.args[0], float(cmd.args[1]), float(cmd.args[2])
            task = self.active_sprint.get_task_by_name(task_name)
            if not task:
                return f"❌ 找不到任务: {task_name}"
            self.planning.set_task_estimate(task, low, high)
            self._save_state()
            return f"✅ 任务 '{task_name}' 预估: 低头 {low}天，抬头 {high}天。"

        if sub == "goal":
            if not self.active_sprint:
                return "❌ 没有活跃的 Sprint"
            self.active_sprint.goal = cmd.args[0]
            self._save_state()
            return f"✅ Sprint 目标已设置: {cmd.args[0]}"

        if sub == "finalize":
            if not self.active_sprint:
                return "❌ 没有活跃的 Sprint"
            self.planning.finalize_sprint(self.active_sprint)
            self._save_state()
            return f"🚀 Sprint '{self.active_sprint.name}' 已启动！\n\n使用 `/standup` 开始日报。"

        return f"❓ 未知 planning 命令: {sub}"

    def _interactive_add_task(self, text: str) -> str:
        """交互式或命令行添加任务"""
        # 尝试解析完整格式: 任务名 | 负责人 | 低头预估 | 抬头预估 | [优先级] | [DDL]
        parts = [p.strip() for p in text.split("|")]
        if len(parts) >= 4:
            name = parts[0]
            owner_name = parts[1]
            low = float(parts[2])
            high = float(parts[3])
            priority = int(parts[4]) if len(parts) > 4 else 5
            ddl_str = parts[5] if len(parts) > 5 else None
            ddl = date.fromisoformat(ddl_str) if ddl_str else None

            member = self.active_sprint.get_member_by_name(owner_name)
            if not member:
                return f"❌ 找不到成员: {owner_name}"

            task = self.planning.add_task(
                self.active_sprint, name, member.id, low, high, priority, ddl
            )
            self._save_state()
            return f"✅ 任务 '{name}' 已添加，负责人: {owner_name}，预估: {low}-{high}天。"

        return """📋 添加任务格式:
任务名 | 负责人 | 低头预估 | 抬头预估 | [优先级] | [DDL]

例:
统一治理LLD | 罗三五 | 2.0 | 3.4 | 8 | 2026-05-08

请回复任务信息:"""

    # ========== Standup Handlers ==========

    def _handle_standup(self, cmd: ParsedCommand, user_id: str, user_name: str) -> str:
        if not self.active_sprint or self.active_sprint.status != SprintStatus.ACTIVE:
            return "❌ 没有进行中的 Sprint。"

        member = self.active_sprint.get_member_by_name(user_name or user_id)
        if not member:
            return f"❌ 你不是当前 Sprint 的成员。"

        sub = cmd.sub_action

        if sub == "prompt":
            return self.standup.get_standup_prompt(member, self.active_sprint)

        if sub == "report":
            task_idx = int(cmd.args[0])
            hours = float(cmd.args[1])
            progress = int(cmd.args[2]) if len(cmd.args) > 2 and cmd.args[2] else None
            blocker = cmd.args[3] if len(cmd.args) > 3 else None

            result = self.standup.process_standup_structured(
                member, self.active_sprint, task_idx, hours, progress, blocker
            )

            if not result["success"]:
                return f"❌ {result['error']}"

            # 保存风险
            self.active_risks.extend(result["risks"])

            # 处理 interview
            interview_msg = ""
            if result.get("interview"):
                session = result["interview"]
                self.pending_interviews[session.id] = session
                interview_msg = self._format_interview_prompt(session)

            self._save_state()

            msg = f"✅ 已记录: {result['task'].name} +{hours}h"
            if progress:
                msg += f" ({progress}%)"
            if blocker:
                msg += f"\n   阻塞: {blocker}"

            if interview_msg:
                msg += f"\n\n{interview_msg}"

            return msg

        return f"❓ 未知 standup 命令: {sub}"

    def _handle_natural_standup(self, member: Member, text: str) -> str:
        """处理自然语言日报"""
        result = self.standup.process_standup_natural(member, self.active_sprint, text)

        if not result["success"]:
            # 返回结构化指引
            msg = f"❌ {result['error']}\n\n"
            msg += "可用任务:\n"
            for idx, (i, t) in enumerate(result.get("available_tasks", []), 1):
                msg += f"{idx}. {t}\n"
            msg += "\n请使用: `/standup <序号> <耗时> [进度] [阻塞]`"
            return msg

        # 保存风险
        self.active_risks.extend(result["risks"])

        # 处理 interview
        interview_msg = ""
        if result.get("interview"):
            session = result["interview"]
            self.pending_interviews[session.id] = session
            interview_msg = self._format_interview_prompt(session)

        self._save_state()

        msg = f"✅ 已记录: {result['task'].name} +{result['log'].hours}h"
        if result['log'].progress_percent:
            msg += f" ({result['log'].progress_percent}%)"

        if interview_msg:
            msg += f"\n\n{interview_msg}"

        return msg

    def _format_interview_prompt(self, session: InterviewSession) -> str:
        """格式化 interview 追问"""
        lines = ["🤔 追问 (可直接回复，或 `/skip` 跳过):"]
        for i, q in enumerate(session.questions, 1):
            lines.append(f"  {i}. {q.text}")
        lines.append(f"\n(回复 `/skip` 跳过追问)")
        return "\n".join(lines)

    def _is_interview_answer(self, user_id: str) -> bool:
        """检查用户是否有待回答的 interview"""
        for session in self.pending_interviews.values():
            if session.status == InterviewStatus.PENDING:
                member = None
                if self.active_sprint:
                    member = self.active_sprint.get_member_by_name(user_id)
                if member and session.member_id == member.id:
                    return True
        return False

    def _handle_interview_answer(self, user_id: str, text: str) -> str:
        """处理 interview 回答"""
        # 找到对应的 session
        session = None
        for s in self.pending_interviews.values():
            if s.status == InterviewStatus.PENDING:
                member = self.active_sprint.get_member_by_name(user_id)
                if member and s.member_id == member.id:
                    session = s
                    break

        if not session:
            return "❓ 没有待回答的追问。"

        # 处理回答
        answer_idx = len(session.answers)
        if answer_idx >= len(session.questions):
            # 所有问题已回答，完成 session
            story = self.interview.complete_session(session)
            if story:
                self.story_pool.append(story)
                del self.pending_interviews[session.id]
                self._save_state()
                return f"💡 事迹已归档到「{story.dimension_name}」维度。"
            return "✅ 追问已记录。"

        self.interview.process_answer(session, text, answer_idx)

        # 检查是否还有下一个问题
        if len(session.answers) >= len(session.questions):
            # 完成
            story = self.interview.complete_session(session)
            if story:
                self.story_pool.append(story)
                del self.pending_interviews[session.id]
                self._save_state()
                return f"💡 事迹已归档到「{story.dimension_name}」维度。"
            return "✅ 追问已记录。"

        # 还有下一个问题
        next_q = session.questions[len(session.answers)]
        return f"🤔 追问 {len(session.answers) + 1}: {next_q.text}\n(回复 `/skip` 跳过)"

    def _handle_interview_command(self, cmd: ParsedCommand, user_id: str, user_name: str) -> str:
        """处理 interview 相关命令"""
        sub = cmd.sub_action

        if sub == "skip":
            # 找到用户当前的 interview
            for sid, session in list(self.pending_interviews.items()):
                member = self.active_sprint.get_member_by_name(user_id) if self.active_sprint else None
                if member and session.member_id == member.id and session.status == InterviewStatus.PENDING:
                    self.interview.skip_session(session)
                    del self.pending_interviews[sid]
                    self._save_state()
                    return "⏭️ 已跳过追问。"
            return "❓ 没有待回答的追问。"

        if sub == "answer":
            # 已在前面的逻辑中处理
            return "请直接回复追问内容。"

        return f"❓ 未知 interview 命令: {sub}"

    # ========== Admin Handlers ==========

    def _handle_admin(self, cmd: ParsedCommand, user_id: str, user_name: str) -> str:
        if not self._is_sm(user_id):
            return "❌ 只有 Scrum Master 可以执行管理命令。"

        sub = cmd.sub_action

        if sub == "leave":
            member_name = user_name or cmd.args[0] if cmd.args else None
            days = float(cmd.args[0]) if cmd.args else 0
            from_date = date.fromisoformat(cmd.args[1]) if len(cmd.args) > 1 else date.today()

            if not self.active_sprint:
                return "❌ 没有活跃的 Sprint"

            member = self.active_sprint.get_member_by_name(member_name or user_name)
            if not member:
                return f"❌ 找不到成员"

            self.planning.set_member_leave(member, days, from_date)
            self._save_state()
            return f"✅ {member.name} 请假 {days} 天，已扣减容量。"

        if sub == "pause":
            if not self.active_sprint:
                return "❌ 没有活跃的 Sprint"
            task_name = cmd.args[0]
            task = self.active_sprint.get_task_by_name(task_name)
            if not task:
                return f"❌ 找不到任务: {task_name}"
            self.planning.pause_task(task, "SM 手动挂起")
            self._save_state()
            return f"⏸️ 任务 '{task_name}' 已挂起。"

        if sub == "resume":
            if not self.active_sprint:
                return "❌ 没有活跃的 Sprint"
            task_name = cmd.args[0]
            task = self.active_sprint.get_task_by_name(task_name)
            if not task:
                return f"❌ 找不到任务: {task_name}"
            self.planning.resume_task(task)
            self._save_state()
            return f"▶️ 任务 '{task_name}' 已恢复。"

        if sub == "reassign":
            if not self.active_sprint:
                return "❌ 没有活跃的 Sprint"
            task_name, new_member_name = cmd.args[0], cmd.args[1]
            task = self.active_sprint.get_task_by_name(task_name)
            new_member = self.active_sprint.get_member_by_name(new_member_name)
            old_member = self.active_sprint.get_member_by_name(task.owner_id) if task else None

            if not task:
                return f"❌ 找不到任务: {task_name}"
            if not new_member:
                return f"❌ 找不到成员: {new_member_name}"

            self.planning.reassign_task(task, new_member, old_member)
            self._save_state()
            return f"✅ 任务 '{task_name}' 已重新分配给 '{new_member_name}'。"

        return f"❓ 未知 admin 命令: {sub}"

    # ========== Query Handlers ==========

    def _handle_query(self, cmd: ParsedCommand, user_id: str, user_name: str) -> str:
        sub = cmd.sub_action

        if sub == "status":
            if not self.active_sprint:
                return "❌ 没有活跃的 Sprint。"

            member_name = cmd.args[0] if cmd.args else user_name
            member = self.active_sprint.get_member_by_name(member_name)
            if not member:
                return f"❌ 找不到成员: {member_name}"

            return self.dashboard.generate_member_status(
                member, self.active_sprint, self.active_risks
            )

        if sub == "dashboard":
            if not self.active_sprint:
                return "❌ 没有活跃的 Sprint。"
            return self.dashboard.generate_dashboard(
                self.active_sprint, self.story_pool, self.active_risks
            )

        return f"❓ 未知 query 命令: {sub}"

    # ========== Retro Handlers ==========

    def _handle_retro(self, cmd: ParsedCommand, user_id: str, user_name: str) -> str:
        if not self.active_sprint:
            return "❌ 没有活跃的 Sprint。"

        sub = cmd.sub_action

        if sub == "single":
            report = self.retro.generate_single_retro(
                self.active_sprint, self.story_pool, self.active_risks
            )
            content = self.retro.render_markdown(report, self.active_sprint)
            file_path = self.persistence.export_retro_markdown(content, self.active_sprint.id)
            return f"📊 Retro 报告已生成！\n\n{content[:500]}...\n\n📄 完整报告: {file_path}"

        if sub == "trend":
            n = int(cmd.args[0]) if cmd.args else 3
            historical = self.persistence.load_historical_sprints(n)
            report = self.retro.generate_trend_retro(
                historical, self.active_sprint, self.story_pool, self.active_risks, n
            )
            content = self.retro.render_markdown(report, self.active_sprint)
            file_path = self.persistence.export_retro_markdown(content, self.active_sprint.id)
            return f"📈 跨 Sprint 趋势报告已生成！\n\n{content[:500]}...\n\n📄 完整报告: {file_path}"

        return f"❓ 未知 retro 命令: {sub}"

    # ========== Assessment Handlers ==========

    def _handle_assessment(self, cmd: ParsedCommand, user_id: str, user_name: str) -> str:
        sub = cmd.sub_action

        if sub == "generate":
            member = self.active_sprint.get_member_by_name(user_name or user_id) if self.active_sprint else None
            if not member:
                return f"❌ 找不到成员信息。"

            period = cmd.args[0] if cmd.args else self._get_current_period()
            # 加载最近半年的 sprint
            historical = self.persistence.load_historical_sprints(12)  # 约半年
            if self.active_sprint:
                historical.insert(0, self.active_sprint)

            assessment = self.assessment.generate_assessment(
                member, period, historical, self.story_pool
            )
            file_path = self.persistence.export_assessment_markdown(
                assessment.markdown_content, member.name, period
            )

            # 统计
            total_stories = sum(len(d.stories) for d in assessment.dimensions)
            return f"📝 自评表已生成！\n\n" \
                   f"基于 {len(historical)} 个 Sprint\n" \
                   f"自动提取 {total_stories} 个事迹\n" \
                   f"📄 文件: {file_path}\n\n" \
                   f"请补充细节后执行 `/assessment review` 生成 checklist。"

        if sub == "confirm":
            story_id = cmd.args[0] if cmd.args else ""
            for story in self.story_pool:
                if story.id == story_id:
                    self.assessment.confirm_story(story)
                    self._save_state()
                    return f"✅ 事迹已确认: {story_id}"
            return f"❌ 找不到事迹: {story_id}"

        if sub == "review":
            # 生成 review checklist
            period = self._get_current_period()
            member = self.active_sprint.get_member_by_name(user_name) if self.active_sprint else None
            if not member:
                return "❌ 找不到成员信息。"

            historical = self.persistence.load_historical_sprints(12)
            if self.active_sprint:
                historical.insert(0, self.active_sprint)
            assessment = self.assessment.generate_assessment(
                member, period, historical, self.story_pool
            )
            checklist = self.assessment.generate_review_checklist(assessment)
            return f"📋 Review Checklist:\n\n{checklist}"

        return f"❓ 未知 assessment 命令: {sub}"

    # ========== Config Handlers ==========

    def _handle_config(self, cmd: ParsedCommand, user_id: str, user_name: str) -> str:
        if not self._is_sm(user_id):
            return "❌ 只有 Scrum Master 可以修改配置。"

        key, value = cmd.args[0], cmd.args[1]
        self.config[key] = value
        self.persistence.save_config(self.config)
        return f"✅ 配置已更新: {key} = {value}"

    # ========== Import Handlers ==========

    def _handle_import(self, cmd: ParsedCommand, user_id: str, user_name: str) -> str:
        if not self._is_sm(user_id):
            return "❌ 只有 Scrum Master 可以导入数据。"

        sub = cmd.sub_action
        if sub == "excel":
            file_path = cmd.args[0]
            # TODO: 实现 Excel 导入
            return f"📥 Excel 导入功能开发中，文件路径: {file_path}"

        return f"❓ 未知 import 命令: {sub}"

    # ========== Helpers ==========

    def _is_sm(self, user_id: str) -> bool:
        """检查用户是否是 Scrum Master"""
        # MVP 简化：配置中的 sm_id，或第一个成员
        sm_id = self.config.get("sm_id")
        if sm_id:
            return user_id == sm_id
        # 默认允许所有人（MVP 阶段简化权限）
        return True

    def _get_current_period(self) -> str:
        """获取当前半年度周期"""
        now = datetime.now()
        half = "H1" if now.month <= 6 else "H2"
        return f"{now.year}{half}"


def main():
    """CLI 入口"""
    agent = SprintAgent()
    print("🚀 Sprint Agent 已启动")
    print("输入 /help 查看可用命令，或输入指令开始。\n")

    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "/exit"]:
                print("👋 再见")
                break
            if user_input == "/help":
                print(_get_help_text())
                continue

            response = agent.process(user_input)
            print(response)
            print()
        except KeyboardInterrupt:
            print("\n👋 再见")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")


def _get_help_text() -> str:
    return """
📖 Sprint Agent 命令帮助

【Planning】
/planning start <名称> <开始日期> <结束日期>
/planning add-member <姓名> <COE系数>
/planning add-task <任务名> | <负责人> | <低头预估> | <抬头预估>
/planning assign <任务名> <成员名>
/planning estimate <任务名> <低头> <抬头>
/planning goal <Sprint目标>
/planning finalize

【Daily Standup】
/standup              # 查看今日任务列表
/standup <序号> <耗时> [进度%] [阻塞]

【Admin】
/leave <天数> [日期]
/pause <任务名>
/resume <任务名>
/reassign <任务名> <新成员>

【Query】
/status [成员名]      # 查看个人状态
/dashboard            # 团队看板（晾晒）

【Retro】
/retro                # 本 Sprint retro
/retro trend [N]      # 跨 Sprint 趋势

【Self-Assessment】
/assessment generate [周期]
/assessment confirm <事迹ID>
/assessment review    # Review checklist

【Interview】
/skip                 # 跳过追问

【Config】
/config <key> <value>
"""


if __name__ == "__main__":
    main()

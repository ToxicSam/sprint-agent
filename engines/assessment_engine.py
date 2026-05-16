import uuid
import re
from datetime import datetime, timedelta
from typing import List, Dict

from models.sprint import Sprint
from models.member import Member
from models.story_pool import StoryPoolEntry, STAR
from models.assessment import SelfAssessment, Dimension, ReviewStatus


class SelfAssessmentEngine:
    """自评表引擎"""

    # 华为模板 9 大维度配置
    DIMENSION_CONFIG = {
        "core_execution": {
            "name": "核心产出 — 攻坚克难、使命必达",
            "weight": 0.13,
            "keywords": ["攻关", "攻坚", "难题", "复杂", "从零", "突破", "挑战", "困难"],
        },
        "core_technical": {
            "name": "核心产出 — 技术知识",
            "weight": 0.09,
            "keywords": ["技术", "架构", "设计", "原理", "性能", "优化", "深度", "调研"],
        },
        "core_quality": {
            "name": "核心产出 — 质量优先",
            "weight": 0.13,
            "keywords": ["质量", "测试", "bug", "稳定", "可靠", "安全", "覆盖", "回归"],
        },
        "collab_review": {
            "name": "周边协同 — 质量优先/Review",
            "weight": 0.09,
            "keywords": ["review", "评审", "把关", "代码审查", "检视", "审核"],
        },
        "collab_ownership": {
            "name": "周边协同 — 团队主人翁意识",
            "weight": 0.13,
            "keywords": ["顺手", "主动", "额外", "团队", "公共", "维护", "清理", "整理"],
        },
        "collab_innovation": {
            "name": "周边协同 — 发明创造与效率提升",
            "weight": 0.13,
            "keywords": ["工具", "自动化", "效率", "改进", "创新", "脚本", "提速", "简化"],
        },
        "collab_empowerment": {
            "name": "周边协同 — 为他人赋能",
            "weight": 0.09,
            "keywords": ["分享", "培训", "指导", "mentor", "文档", "赋能", "传帮带"],
        },
        "core_customer": {
            "name": "核心产出 — 成就客户/勇耕盐碱地",
            "weight": 0.12,
            "keywords": ["客户", "业务", "需求", "交付", "上线", "价值", "盐碱地", "新领域"],
        },
        "collab_customer": {
            "name": "周边协同 — 成就客户/用户优先",
            "weight": 0.09,
            "keywords": ["用户体验", "易用", "友好", "响应", "支持", "及时", "态度"],
        },
    }

    def generate_assessment(
        self,
        member: Member,
        period: str,
        sprints: List[Sprint],
        story_pool: List[StoryPoolEntry],
    ) -> SelfAssessment:
        """生成自评表"""
        assessment = SelfAssessment(
            id=f"sa_{uuid.uuid4().hex[:8]}",
            period=period,
            member_id=member.id,
        )

        # 收集周期内的 sprint IDs
        assessment.raw_sprint_ids = [s.id for s in sprints]

        # 获取周期内的事迹
        period_stories = [
            s for s in story_pool
            if s.member_id == member.id and s.sprint_id in assessment.raw_sprint_ids
        ]

        assessment.auto_stories = period_stories

        # 按维度分类
        dimensions = self._create_dimensions()
        classified = self._classify_stories(period_stories)

        for key, dim in dimensions.items():
            if key in classified:
                dim.stories = classified[key]
            assessment.dimensions.append(dim)

        # 渲染 Markdown
        assessment.markdown_content = self._render_markdown(assessment, member, sprints)

        return assessment

    def _create_dimensions(self) -> Dict[str, Dimension]:
        """创建维度结构"""
        dimensions = {}
        for key, config in self.DIMENSION_CONFIG.items():
            dimensions[key] = Dimension(
                key=key,
                name=config["name"],
                weight=config["weight"],
            )
        return dimensions

    def _classify_stories(
        self,
        stories: List[StoryPoolEntry],
    ) -> Dict[str, List[StoryPoolEntry]]:
        """按维度分类事迹"""
        classified: Dict[str, List[StoryPoolEntry]] = {key: [] for key in self.DIMENSION_CONFIG}

        for story in stories:
            # 1. 如果已有明确维度，直接使用
            if story.dimension and story.dimension in classified:
                classified[story.dimension].append(story)
                continue

            # 2. 通过 keywords 匹配
            matched = False
            text = f"{story.star.situation} {story.star.task} {story.star.action} {story.star.result}"
            text = text.lower()

            for key, config in self.DIMENSION_CONFIG.items():
                for keyword in config["keywords"]:
                    if keyword.lower() in text:
                        classified[key].append(story)
                        matched = True
                        break
                if matched:
                    break

            # 3. 未匹配放入第一个维度（默认）
            if not matched:
                classified["core_execution"].append(story)

        return classified

    def _render_markdown(
        self,
        assessment: SelfAssessment,
        member: Member,
        sprints: List[Sprint],
    ) -> str:
        """渲染自评表 Markdown"""
        lines = []
        lines.append(f"# {member.name} — 半年度自评表 ({assessment.period})")
        lines.append("")
        lines.append(f"> 生成时间: {assessment.generated_at.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"> 基于 Sprint: {', '.join([s.name for s in sprints])}")
        lines.append("")

        # 各维度
        for dim in assessment.dimensions:
            lines.append(f"## {dim.name}（权重 {dim.weight * 100:.0f}%）")
            lines.append("")

            if dim.stories:
                for story in dim.stories:
                    lines.append(self._render_star_story(story))
            else:
                lines.append("_（本周期暂无匹配事迹，可手动补充）_")
                lines.append("")

            lines.append("")

        # 其他部分
        lines.append("## 其他想提及的事情")
        lines.append("")
        lines.append("_（请补充）_")
        lines.append("")

        lines.append("## 继续进步的方向")
        lines.append("")
        lines.append("_（请补充）_")
        lines.append("")

        return "\n".join(lines)

    def _render_star_story(self, story: StoryPoolEntry) -> str:
        """渲染单个 STAR 事迹"""
        lines = []

        task_name = story.task_id or "通用事迹"
        lines.append(f"### {task_name}")
        lines.append("")

        if story.star.situation:
            lines.append(f"**S-背景**: {story.star.situation}")
            lines.append("")
        if story.star.task:
            lines.append(f"**T-问题/任务**: {story.star.task}")
            lines.append("")
        if story.star.action:
            lines.append(f"**A-分析与对策**: {story.star.action}")
            lines.append("")
        if story.star.result:
            lines.append(f"**R-处理结果**: {story.star.result}")
            lines.append("")
        if story.star.review:
            lines.append(f"**Review-经验教训**: {story.star.review}")
            lines.append("")

        lines.append(f"*来源: {'Interview' if story.source == 'interview' else story.source} | "
                    f"质量评分: {story.quality_score:.0%} | "
                    f"{'已确认' if story.confirmed else '待确认'}*")
        lines.append("")
        lines.append("---")
        lines.append("")

        return "\n".join(lines)

    def generate_review_checklist(self, assessment: SelfAssessment) -> str:
        """生成 review checklist"""
        lines = []
        lines.append(f"# Review Checklist — {assessment.period}")
        lines.append("")
        lines.append(f"当前轮次: {assessment.review_round} / 建议 ≤3 轮")
        lines.append("")

        lines.append("## 检查项")
        lines.append("")
        lines.append("- [ ] STAR 描述是否完整（S/T/A/R 四要素齐全）")
        lines.append("- [ ] 每个事迹是否有具体数据/结果支撑")
        lines.append("- [ ] 维度分类是否合理（有无错放）")
        lines.append("- [ ] 有无遗漏的重要事迹")
        lines.append("- [ ] 语言是否精炼、专业")
        lines.append("- [ ] 是否体现个人独特贡献（非团队共性）")
        lines.append("")

        # 维度覆盖度
        lines.append("## 维度覆盖度")
        lines.append("")
        for dim in assessment.dimensions:
            status = "✅" if dim.stories else "⚠️"
            lines.append(f"{status} {dim.name}: {len(dim.stories)} 个事迹")
        lines.append("")

        # 改进建议
        lines.append("## 改进建议")
        lines.append("")
        lines.append("_（Committer 填写）_")
        lines.append("")

        return "\n".join(lines)

    def confirm_story(self, story: StoryPoolEntry) -> None:
        """工程师确认事迹"""
        story.confirmed = True

    def add_manual_story(
        self,
        assessment: SelfAssessment,
        star: STAR,
        dimension_key: str,
        task_name: str = "",
    ) -> StoryPoolEntry:
        """工程师手动添加事迹"""
        story = StoryPoolEntry(
            id=f"story_manual_{uuid.uuid4().hex[:8]}",
            member_id=assessment.member_id,
            sprint_id="",
            task_id=task_name,
            dimension=dimension_key,
            dimension_name=self.DIMENSION_CONFIG.get(dimension_key, {}).get("name", "未分类"),
            star=star,
            source="manual",
            confirmed=True,
            quality_score=1.0,  # 人工输入默认满分
        )
        assessment.manual_stories.append(story)

        # 添加到对应维度
        for dim in assessment.dimensions:
            if dim.key == dimension_key:
                dim.stories.append(story)
                break

        return story

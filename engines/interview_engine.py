import uuid
import re
from datetime import datetime, timedelta
from typing import List, Optional

from models.sprint import Sprint
from models.member import Member
from models.task import Task, TaskStatus
from models.daily_log import DailyLog
from models.interview import InterviewSession, InterviewStatus, Question, QuestionType, Answer
from models.story_pool import StoryPoolEntry, STAR


class InterviewEngine:
    """Interview/Grill 引擎"""
    
    # 触发关键词
    EXTRA_CONTRIBUTION_KEYWORDS = ["顺手", "额外", "顺便", "也修了", "发现", "顺手修", "顺手改"]
    BLOCKER_RESOLVED_KEYWORDS = ["解决", "搞定", "修复", "通过了", "对齐了", "ok了", "完成了"]
    
    # 追问模板
    QUESTION_TEMPLATES = {
        "methodology": [
            "这个任务你有没有用到比之前更高效的方法？如果有，是什么？",
            "如果重来一次，哪个环节可以省时间？",
            "你解决的这个难点，能不能抽象成一个团队可复用的经验？",
        ],
        "star_extraction": [
            "这个任务最有挑战的部分是什么？你是怎么解决的？",
            "这个任务的背景是什么？你面临的核心挑战是什么？",
            "你采取了什么具体措施？最终效果如何？",
        ],
        "dimension_alignment": [
            "你顺手做的这件事对团队有帮助吗？属于哪类贡献？",
            "这件事除了完成任务本身，还有什么额外价值？",
        ],
    }
    
    def should_trigger(
        self,
        task: Task,
        member: Member,
        log: DailyLog,
        sprint: Sprint
    ) -> Optional[InterviewSession]:
        """判断是否需要触发 interview"""
        
        # 排除条件
        if task.is_public:
            return None
        if task.id in member.interviewed_tasks:
            return None
        if task.status == TaskStatus.PAUSED:
            return None
        
        # 触发规则
        triggers = []
        
        # 规则1: 任务完成
        if task.status == TaskStatus.COMPLETED:
            triggers.append("completed")
        
        # 规则2: 超预期（实际 < 低头预估 * 0.8）
        if task.total_spent < task.estimate_low * 0.8:
            triggers.append("under_estimate")
        
        # 规则3: 高难度完成（实际 > 抬头预估，但完成了）
        if task.total_spent > task.estimate_high * 1.2 and task.status == TaskStatus.COMPLETED:
            triggers.append("hard_completed")
        
        # 规则4: 阻塞解决
        if log.notes and any(kw in log.notes for kw in self.BLOCKER_RESOLVED_KEYWORDS):
            triggers.append("blocker_resolved")
        
        # 规则5: 额外贡献
        if log.notes and any(kw in log.notes for kw in self.EXTRA_CONTRIBUTION_KEYWORDS):
            triggers.append("extra_contribution")
        
        if not triggers:
            return None
        
        # 标记已 interview
        member.interviewed_tasks.add(task.id)
        
        # 生成追问
        questions = self._generate_questions(triggers, task, member)
        
        session = InterviewSession(
            id=f"iv_{uuid.uuid4().hex[:8]}",
            date=datetime.now(),
            member_id=member.id,
            task_id=task.id,
            standup_log_id=log.id,
            questions=questions,
            status=InterviewStatus.PENDING,
        )
        
        return session
    
    def _generate_questions(
        self,
        triggers: List[str],
        task: Task,
        member: Member
    ) -> List[Question]:
        """根据触发条件生成追问（最多 2 个）"""
        questions = []
        
        if "completed" in triggers or "under_estimate" in triggers:
            questions.append(Question(
                id=f"q_{uuid.uuid4().hex[:8]}",
                type=QuestionType.METHODOLOGY,
                text="这个任务你有没有用到比之前更高效的方法？",
                target_dimension="efficiency_improvement",
                order=1,
            ))
        
        if "hard_completed" in triggers or "blocker_resolved" in triggers:
            questions.append(Question(
                id=f"q_{uuid.uuid4().hex[:8]}",
                type=QuestionType.STAR_EXTRACTION,
                text="这个任务最有挑战的部分是什么？你是怎么解决的？",
                target_dimension="technical_excellence",
                order=1,
            ))
        
        if "extra_contribution" in triggers:
            questions.append(Question(
                id=f"q_{uuid.uuid4().hex[:8]}",
                type=QuestionType.DIMENSION_ALIGNMENT,
                text="你顺手做的这件事对团队有帮助吗？",
                target_dimension="team_ownership",
                order=1,
            ))
        
        # 补充第二个问题（如果有）
        if len(questions) == 1 and "completed" in triggers:
            questions.append(Question(
                id=f"q_{uuid.uuid4().hex[:8]}",
                type=QuestionType.STAR_EXTRACTION,
                text="这个任务的经验能不能抽象成团队可复用的？",
                target_dimension="knowledge_sharing",
                order=2,
            ))
        
        return questions[:2]
    
    def process_answer(
        self,
        session: InterviewSession,
        answer_text: str,
        question_index: int = 0
    ) -> Answer:
        """处理用户回答"""
        if question_index >= len(session.questions):
            raise ValueError(f"问题索引越界: {question_index}")
        
        question = session.questions[question_index]
        answer = Answer(
            question_id=question.id,
            text=answer_text,
        )
        session.answers.append(answer)
        
        # 如果所有问题都回答完了，完成 session
        if len(session.answers) >= len(session.questions):
            session.status = InterviewStatus.ANSWERED
        
        return answer
    
    def complete_session(self, session: InterviewSession) -> Optional[StoryPoolEntry]:
        """完成 interview session，提取 STAR"""
        if len(session.answers) == 0:
            return None
        
        # 合并所有回答
        full_text = " ".join([a.text for a in session.answers])
        
        # 提取 STAR
        star = self._extract_star(full_text)
        
        # 对齐维度
        dimension_key, dimension_name = self._align_dimension(
            session.questions[0].target_dimension,
            full_text
        )
        
        # 质量评分
        quality = self._score_star_quality(star)
        
        # 创建 StoryPoolEntry
        story = StoryPoolEntry(
            id=f"story_{uuid.uuid4().hex[:8]}",
            member_id=session.member_id,
            sprint_id=session.id.split("_")[0] if "_" in session.id else "",
            task_id=session.task_id,
            dimension=dimension_key,
            dimension_name=dimension_name,
            star=star,
            source="interview",
            quality_score=quality,
            interview_session_id=session.id,
        )
        
        session.stories_extracted.append(story.id)
        session.status = InterviewStatus.CONFIRMED
        session.completed_at = datetime.now()
        
        return story
    
    def skip_session(self, session: InterviewSession) -> None:
        """用户跳过"""
        session.skipped = True
        session.status = InterviewStatus.SKIPPED
        session.completed_at = datetime.now()
    
    def _extract_star(self, text: str) -> STAR:
        """从回答中提取 STAR（规则引擎版）"""
        star = STAR()
        
        # 分段
        sentences = re.split(r'[。\n]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # S-背景
        for s in sentences:
            if any(kw in s for kw in ["当时", "背景", "发现", "遇到", "问题", "由于"]):
                star.situation = s
                break
        
        # T-任务
        for s in sentences:
            if any(kw in s for kw in ["需要", "任务", "负责", "目标", "挑战", "要搞定"]):
                star.task = s
                break
        
        # A-行动
        for s in sentences:
            if any(kw in s for kw in ["做了", "采取", "通过", "使用", "协调", "推动", "设计", "实现"]):
                star.action = s
                break
        
        # R-结果
        for s in sentences:
            if any(kw in s for kw in ["结果", "完成", "实现", "提升", "解决", "达到", "成功"]):
                star.result = s
                break
        
        # Review-经验教训
        for s in sentences:
            if any(kw in s for kw in ["如果", "下次", "应该", "教训", "经验", "可以", "建议"]):
                star.review = s
                break
        
        return star
    
    def _align_dimension(self, target_dimension: str, text: str) -> tuple:
        """对齐自评表维度"""
        DIMENSION_MAP = {
            "efficiency_improvement": ("collab_innovation", "周边协同 — 发明创造与效率提升"),
            "technical_excellence": ("core_technical", "核心产出 — 技术知识"),
            "team_ownership": ("collab_ownership", "周边协同 — 团队主人翁意识"),
            "knowledge_sharing": ("collab_empowerment", "周边协同 — 为他人赋能"),
            "perseverance": ("core_execution", "核心产出 — 攻坚克难、使命必达"),
            "problem_solving": ("core_execution", "核心产出 — 攻坚克难、使命必达"),
            "customer_focus": ("collab_customer", "周边协同 — 成就客户/用户优先"),
        }
        
        return DIMENSION_MAP.get(target_dimension, ("uncategorized", "未分类"))
    
    def _score_star_quality(self, star: STAR) -> float:
        """评估 STAR 完整度，0-1"""
        score = 0.0
        if star.situation:
            score += 0.25
        if star.task:
            score += 0.25
        if star.action:
            score += 0.25
        if star.result:
            score += 0.25
        return score
    
    def check_expired_sessions(self, sessions: List[InterviewSession]) -> List[InterviewSession]:
        """检查过期的 interview session（>24h）"""
        expired = []
        cutoff = datetime.now() - timedelta(hours=24)
        for session in sessions:
            if session.status == InterviewStatus.PENDING and session.created_at < cutoff:
                session.status = InterviewStatus.EXPIRED
                expired.append(session)
        return expired

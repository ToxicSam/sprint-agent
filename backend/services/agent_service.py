"""Agent intent classification with LLM support and regex fallback."""

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from models import Sprint, Task, Member


# ---------------------------------------------------------------------------
# Regex-based patterns (fallback)
# ---------------------------------------------------------------------------
INTENT_PATTERNS: List[Tuple[str, List[str]]] = [
    ("create_task", [
        # English patterns
        r"create\s+(?:a\s+)?(?:new\s+)?task",
        r"add\s+(?:a\s+)?(?:new\s+)?task",
        r"make\s+(?:a\s+)?(?:new\s+)?task",
        r"new\s+task",
        # Chinese patterns
        r"创建\s*(?:一个\s*)?(?:新\s*)?任务",
        r"新建\s*(?:一个\s*)?任务",
        r"添加\s*(?:一个\s*)?任务",
        r"增加\s*(?:一个\s*)?任务",
    ]),
    ("move_task", [
        # Quoted task title patterns (PRIORITY - handles multi-word titles)
        r"move\s+(?:task\s+)?['\"\u201c\u2018](.+?)['\"\u201d\u2019]\s+(?:to|into|in)\s+(.+)",
        r"set\s+(?:task\s+)?['\"\u201c\u2018](.+?)['\"\u201d\u2019]\s+(?:status\s+)?to\s+(.+)",
        r"change\s+(?:task\s+)?['\"\u201c\u2018](.+?)['\"\u201d\u2019]\s+(?:status\s+)?to\s+(.+)",
        # English patterns
        r"move\s+(?:task\s+)?(\S+)\s+to\s+(\S+)",
        r"move\s+(?:task\s+)?(\S+)\s+(?:into|in)\s+(\S+)",
        r"set\s+(?:task\s+)?(\S+)\s+(?:status\s+)?to\s+(\S+)",
        r"change\s+(?:task\s+)?(\S+)\s+(?:status\s+)?to\s+(\S+)",
        # Chinese patterns
        r"将\s*(?:任务\s*)?(\S+)\s*(?:移|移动|挪|放到|移至)\s*(\S+)",
        r"(?:把|将)\s*(?:任务\s*)?(\S+)\s*(?:状态\s*)?(?:改|设置|设为)\s*(\S+)",
    ]),
    ("update_task", [
        # English patterns
        r"update\s+(?:task\s+)?(\S+)",
        r"change\s+(?:task\s+)?(\S+)",
        r"edit\s+(?:task\s+)?(\S+)",
        # Chinese patterns
        r"更新\s*(?:任务\s*)?(\S+)",
        r"修改\s*(?:任务\s*)?(\S+)",
        r"编辑\s*(?:任务\s*)?(\S+)",
    ]),
    ("standup_log", [
        # English patterns
        r"log\s+(?:standup|daily)\s+(?:for\s+)?(\S+)",
        r"submit\s+(?:standup|daily)\s+(?:for\s+)?(\S+)",
        r"add\s+(?:a\s+)?(?:daily\s+)?log",
        r"standup\s+(?:for\s+)?(\S+)",
        # Chinese patterns
        r"记录\s*(?:每日\s*)?(?:站会|例会|日报|日志)",
        r"提交\s*(?:每日\s*)?(?:站会|例会|日报|日志)",
        r"写\s*(?:每日\s*)?(?:站会|例会|日报|日志)",
    ]),
    ("retro_score", [
        # English patterns
        r"rate\s+(?:the\s+)?(?:retro|sprint)",
        r"score\s+(?:the\s+)?(?:retro|sprint)",
        r"retro\s+rating",
        r"sprint\s+score",
        # Chinese patterns
        r"(?:给\s*)?(?: retro|回顾|迭代|sprint)\s*(?:评分|打分|评价)",
        r"评分\s*(?:retro|回顾|迭代|sprint)",
    ]),
    ("delete_task", [
        # Quoted task title patterns (PRIORITY - handles multi-word titles)
        r"delete\s+(?:task\s+)?['\"\u201c\u2018](.+?)['\"\u201d\u2019]",
        r"remove\s+(?:task\s+)?['\"\u201c\u2018](.+?)['\"\u201d\u2019]",
        # English patterns
        r"delete\s+(?:task\s+)?(\S+)",
        r"remove\s+(?:task\s+)?(\S+)",
        # Chinese patterns
        r"删除\s*(?:任务\s*)?(\S+)",
        r"移除\s*(?:任务\s*)?(\S+)",
    ]),
    ("sprint_stats", [
        # English patterns
        r"sprint\s+stats",
        r"show\s+(?:me\s+)?(?:the\s+)?stats",
        r"how\s+is\s+the\s+sprint\s+going",
        r"sprint\s+progress",
        # Chinese patterns
        r"(?:sprint|迭代|冲刺)\s*(?:进展|进度|状态|统计|如何|怎么样)",
        r"(?:查看|显示|看看)\s*(?:sprint|迭代|冲刺)\s*(?:进展|进度|状态|统计)",
    ]),
]

STATUS_ALIASES: Dict[str, List[str]] = {
    "todo": ["todo", "backlog", "to do", "to-do", "open", "not started",
             "待办", "未开始", "待处理", "新建"],
    "progress": ["progress", "in progress", "in-progress", "doing", "wip", "working", "started",
                 "进行中", "在处理", "开发中"],
    "done": ["done", "completed", "complete", "finished", "closed", "resolved",
             "完成", "已完成", "结束", "关闭"],
    "paused": ["paused", "blocked", "on hold", "hold", "waiting",
               "暂停", "阻塞", "等待", "搁置"],
}

ALLOWED_INTENTS = [
    "create_task", "move_task", "update_task", "delete_task",
    "standup_log", "retro_score", "sprint_stats", "general_chat",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def normalize_status(raw: str) -> str:
    raw_lower = raw.lower().strip()
    for canonical, aliases in STATUS_ALIASES.items():
        if raw_lower in aliases:
            return canonical
    return raw_lower


def classify_intent_regex(message: str) -> Tuple[str, Dict[str, Any]]:
    """Classify intent using regex patterns (fallback)."""
    text = message.lower().strip()
    for intent, patterns in INTENT_PATTERNS:
        for pat in patterns:
            match = re.search(pat, text)
            if match:
                entities: Dict[str, Any] = {}
                groups = match.groups()
                if intent == "move_task" and len(groups) >= 2:
                    raw_ref = groups[0]
                    # Try to extract quoted title for multi-word task names
                    quoted = re.search(r'["\'\u201c\u2018](.+?)["\'\u201d\u2019]', message)
                    if quoted:
                        entities["task_ref"] = quoted.group(1)
                    else:
                        entities["task_ref"] = raw_ref
                    # Join remaining groups for multi-word status like "in progress"
                    # CRITICAL FIX: Also include text after the regex match
                    # because \S+ only captures one word (e.g., "in" not "in progress")
                    status_text = " ".join(groups[1:])
                    remaining = text[match.end():].strip()
                    if remaining:
                        # Append first word from remaining (e.g., "progress" after "in")
                        first_word = remaining.split()[0] if remaining.split() else ""
                        # Check if combined forms a known status alias
                        combined = f"{status_text} {first_word}".strip()
                        if combined in STATUS_ALIASES.get("progress", []) or \
                           combined in STATUS_ALIASES.get("todo", []) or \
                           combined in STATUS_ALIASES.get("done", []) or \
                           combined in STATUS_ALIASES.get("paused", []):
                            status_text = combined
                        elif f"{status_text} {first_word}".strip() in ["in progress", "on hold"]:
                            status_text = combined
                    # Only take the first 2 words max
                    status_words = status_text.split()
                    if len(status_words) > 2:
                        status_text = " ".join(status_words[:2])
                    entities["target_status"] = normalize_status(status_text)
                elif intent in ("update_task", "delete_task", "standup_log") and groups:
                    raw_ref = groups[0]
                    # Try to extract quoted title for multi-word task names
                    quoted = re.search(r'["\'\u201c\u2018](.+?)["\'\u201d\u2019]', message)
                    if quoted:
                        entities["task_ref"] = quoted.group(1)
                    else:
                        entities["task_ref"] = raw_ref
                return intent, entities
    return "general_chat", {}


# ---------------------------------------------------------------------------
# LLM Intent Classifier
# ---------------------------------------------------------------------------
class LLMIntentClassifier:
    """OpenAI-compatible LLM-based intent classifier with regex fallback."""

    def __init__(self) -> None:
        self.api_key: Optional[str] = os.environ.get("LLM_API_KEY")
        self.api_base: str = os.environ.get("LLM_API_BASE", "https://api.openai.com/v1")
        self.model: str = os.environ.get("LLM_MODEL", "gpt-4o-mini")
        self.enabled: bool = bool(self.api_key and self.api_base)
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            headers: Dict[str, str] = {
                "Content-Type": "application/json",
            }
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.AsyncClient(
                base_url=self.api_base,
                headers=headers,
                timeout=httpx.Timeout(30.0, connect=10.0),
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _build_intent_tool(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "classify_intent",
                "description": "Classify the user's intent from their message to the Sprint Agent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "intent": {
                            "type": "string",
                            "description": (
                                "The classified intent. Must be one of: "
                                "create_task, move_task, update_task, delete_task, "
                                "standup_log, retro_score, sprint_stats, general_chat"
                            ),
                            "enum": ALLOWED_INTENTS,
                        },
                        "entities": {
                            "type": "object",
                            "description": "Extracted entities relevant to the intent",
                            "properties": {
                                "task_ref": {
                                    "type": "string",
                                    "description": "Task ID or title reference",
                                },
                                "target_status": {
                                    "type": "string",
                                    "description": "Target status for move_task intent (todo, progress, done, paused)",
                                },
                                "title": {
                                    "type": "string",
                                    "description": "Task title for create_task intent",
                                },
                                "member_ref": {
                                    "type": "string",
                                    "description": "Member name or ID reference",
                                },
                            },
                        },
                        "response": {
                            "type": "string",
                            "description": "A friendly response message to the user",
                        },
                    },
                    "required": ["intent", "entities", "response"],
                },
            },
        }

    def _build_prompt(self, message: str, context: Dict[str, Any]) -> str:
        sprint_name = context.get("current_sprint", {}).get("name", "No active sprint")
        sprint_status = context.get("current_sprint", {}).get("status", "unknown")

        tasks_summary = ""
        for task in context.get("recent_tasks", []):
            assignee = task.get("assignee", {})
            assignee_name = assignee.get("name", "Unassigned") if assignee else "Unassigned"
            tasks_summary += f"\n  - [{task.get('status', '?')}] {task.get('title', '?')} ({assignee_name})"
        if not tasks_summary:
            tasks_summary = "\n  (no tasks)"

        members_list = ", ".join(
            f"{m.get('name', '?')} ({m.get('role', '?')})"
            for m in context.get("members", [])
        ) or "(no members)"

        return (
            "You are Sprint Agent, an AI assistant for a Scrum team. "
            "Analyze the user's message and classify their intent.\n\n"
            f"Current Sprint: {sprint_name} ({sprint_status})\n"
            f"Tasks:{tasks_summary}\n"
            f"Members: {members_list}\n\n"
            f'User message: "{message}"\n\n'
            "Use the classify_intent function to return the intent classification."
        )

    async def classify(
        self, message: str, context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any], str]:
        """Classify intent using LLM. Returns (intent, entities, response_text)."""
        if not self.enabled:
            raise RuntimeError("LLM not configured")

        tool = self._build_intent_tool()
        prompt = self._build_prompt(message, context)

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful Scrum assistant. Classify user intents accurately. "
                        "When uncertain, use general_chat intent. Always respond in the same "
                        "language as the user's message."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "tools": [tool],
            "tool_choice": {"type": "function", "function": {"name": "classify_intent"}},
        }

        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()

            tool_call = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("tool_calls", [{}])[0]
            )
            arguments = json.loads(tool_call.get("function", {}).get("arguments", "{}"))

            intent = arguments.get("intent", "general_chat")
            entities = arguments.get("entities", {})
            response_text = arguments.get("response", "")

            # Validate intent
            if intent not in ALLOWED_INTENTS:
                intent = "general_chat"

            # Normalize target_status
            if "target_status" in entities:
                entities["target_status"] = normalize_status(entities["target_status"])

            return intent, entities, response_text

        except (httpx.HTTPError, json.JSONDecodeError, KeyError, IndexError) as e:
            raise RuntimeError(f"LLM classification failed: {e}")


# Singleton instance
_llm_classifier: Optional[LLMIntentClassifier] = None


def get_llm_classifier() -> LLMIntentClassifier:
    global _llm_classifier
    if _llm_classifier is None:
        _llm_classifier = LLMIntentClassifier()
    return _llm_classifier


async def classify_intent(
    message: str, context: Dict[str, Any] | None = None
) -> Tuple[str, Dict[str, Any], str]:
    """Classify user intent. Tries LLM first, falls back to regex.

    Returns:
        (intent, entities, response_text)
    """
    llm = get_llm_classifier()

    # Try LLM first if configured
    if llm.enabled:
        try:
            intent, entities, response_text = await llm.classify(
                message, context or {}
            )
            return intent, entities, response_text
        except RuntimeError:
            pass  # Fall back to regex

    # Regex fallback
    intent, entities = classify_intent_regex(message)
    return intent, entities, ""


# ---------------------------------------------------------------------------
# Task / Member resolution
# ---------------------------------------------------------------------------
async def resolve_task_ref(db: AsyncSession, ref: str, for_delete: bool = False) -> Optional[Task]:
    # 1. Exact ID match
    task = await crud.get_task(db, ref)
    if task:
        return task

    # 2. Exact title match (case-insensitive)
    result = await db.execute(
        select(Task).filter(func.lower(Task.title) == ref.lower())
    )
    task = result.scalars().first()
    if task:
        return task

    # 3. For non-delete: safe substring match (anchored at word boundaries)
    if not for_delete:
        result = await db.execute(
            select(Task).filter(func.lower(Task.title).like(f"%{ref.lower()}%"))
        )
        return result.scalars().first()

    return None


def extract_task_title(message: str) -> str:
    """Extract task title from user message using various patterns."""
    # Try quoted title
    title_match = re.search(r'["\'\u201c\u2018](.+?)["\'\u201d\u2019]', message)
    if title_match:
        return title_match.group(1)

    # Try English patterns like "create task X", "add task X to ..."
    en_patterns = [
        r'(?:create|add|new)\s+(?:a\s+)?(?:new\s+)?task\s+(?:called\s+)?["\']?(.+?)["\']?(?:\s+(?:in|to|for)\s|$)',
        r'(?:create|add|new)\s+(?:a\s+)?(?:new\s+)?task\s+(?:called\s+)?["\']?(.+?)["\']?(?:\s+(?:with|having|and)\s|$)',
    ]
    for pat in en_patterns:
        match = re.search(pat, message, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # Try Chinese patterns (use \s* not \s+ since Chinese has no spaces between words)
    cn_patterns = [
        r'(?:创建|新建|添加|增加)\s*(?:一个\s*)?(?:新\s*)?任务\s*(?:叫|名为)?\s*["\'\u201c\u2018]?(.+?)["\'\u201d\u2019]?(?:\s*(?:在|到|用于|的|，|,|。|\.|！|!|$))',
        r'(?:创建|新建|添加|增加)\s*(?:一个\s*)?(?:新\s*)?任务\s*(?:叫|名为)?\s*["\'\u201c\u2018]?(.+?)["\'\u201d\u2019]?(?:\s*(?:优先级|状态|指派给|分配给)\s|$)',
    ]
    for pat in cn_patterns:
        match = re.search(pat, message)
        if match:
            return match.group(1).strip()

    return "New Task"


async def resolve_member_ref(db: AsyncSession, ref: str) -> Optional[Member]:
    member = await crud.get_member(db, ref)
    if member:
        return member
    result = await db.execute(
        select(Member).filter(func.lower(Member.name).like(f"%{ref.lower()}%"))
    )
    return result.scalars().first()


# ---------------------------------------------------------------------------
# Intent handlers
# ---------------------------------------------------------------------------
async def handle_intent(
    db: AsyncSession,
    intent: str,
    entities: Dict[str, Any],
    message: str,
    llm_response: str = "",
) -> Dict[str, Any]:
    """Handle a classified intent and return a result dict."""

    if intent == "create_task":
        title = extract_task_title(message) if not entities.get("title") else entities.get("title")
        active = await crud.get_active_sprint(db)
        sprint_id = active.id if active else ""
        task = await crud.create_task(
            db, schemas.TaskCreate(title=title, sprint_id=sprint_id)
        )
        msg = llm_response or f"Created task '{task.title}' ({task.id})."
        return {"success": True, "message": msg, "task_id": task.id}

    if intent == "move_task":
        ref = entities.get("task_ref", "")
        status = entities.get("target_status", "progress")
        task = await resolve_task_ref(db, ref)
        if not task:
            return {"success": False, "message": f"Task '{ref}' not found."}
        moved = await crud.move_task(db, task.id, status)
        msg = llm_response or f"Moved task '{moved.title}' to {moved.status}."
        return {"success": True, "message": msg, "task_id": moved.id}

    if intent == "update_task":
        ref = entities.get("task_ref", "")
        task = await resolve_task_ref(db, ref)
        if not task:
            return {"success": False, "message": f"Task '{ref}' not found."}
        msg = llm_response or f"Task '{task.title}' found. Use the UI to edit details."
        return {"success": True, "message": msg, "task_id": task.id}

    if intent == "delete_task":
        ref = entities.get("task_ref", "")
        task = await resolve_task_ref(db, ref, for_delete=True)
        if not task:
            return {"success": False, "message": f"Task '{ref}' not found. Please specify the exact task ID or full title."}
        await crud.delete_task(db, task.id)
        msg = llm_response or f"Deleted task '{task.title}'."
        return {"success": True, "message": msg, "task_id": task.id}

    if intent == "sprint_stats":
        active = await crud.get_active_sprint(db)
        if not active:
            return {"success": True, "message": llm_response or "No active sprint."}
        stats = await crud.get_sprint_stats(db, active.id)
        msg = llm_response or (
            f"Sprint '{active.name}': {stats['done']}/{stats['total_tasks']} tasks done, "
            f"{stats['completed_story_points']}/{stats['total_story_points']} SP."
        )
        return {"success": True, "message": msg, "stats": stats}

    if intent == "standup_log":
        return {
            "success": True,
            "message": llm_response or "Open the standup page to log your daily update.",
        }

    if intent == "retro_score":
        return {
            "success": True,
            "message": llm_response or "Open the retro page to submit sprint ratings.",
        }

    # general_chat
    return {
        "success": True,
        "message": llm_response or (
            "I'm here to help. You can ask me to create or move tasks, "
            "show sprint stats, or help with standups and retros."
        ),
    }


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------
async def build_context(db: AsyncSession) -> Dict[str, Any]:
    active = await crud.get_active_sprint(db)
    recent_tasks = await crud.get_tasks(
        db, sprint_id=active.id if active else None, limit=10
    )
    members = await crud.get_members(db)
    messages = await crud.get_agent_messages(db, limit=10)

    return {
        "current_sprint": {
            "id": active.id,
            "name": active.name,
            "status": active.status,
        } if active else None,
        "recent_tasks": [
            {"id": t.id, "title": t.title, "status": t.status} for t in recent_tasks
        ],
        "members": [
            {"id": m.id, "name": m.name, "role": m.role} for m in members
        ],
        "messages": [
            {"role": m.role, "content": m.content} for m in messages
        ],
    }


async def is_llm_configured() -> bool:
    """Check if LLM integration is available."""
    return get_llm_classifier().enabled
import re
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ParsedCommand:
    action: str           # 主命令
    sub_action: str = ""  # 子命令
    args: List[str] = None
    raw: str = ""
    confidence: float = 1.0  # 解析置信度

    def __post_init__(self):
        if self.args is None:
            self.args = []


class CommandParser:
    """命令解析器 - 结构化指令"""
    
    # ========== Planning ==========
    PLANNING_START = r"^/planning\s+start\s+(\S+)\s+(\d{4}-\d{2}-\d{2})\s+(\d{4}-\d{2}-\d{2})$"
    PLANNING_ADD_MEMBER = r"^/planning\s+add-member\s+(\S+)\s+(\d+\.?\d*)$"
    PLANNING_ADD_TASK = r"^/planning\s+add-task\s+(.+)$"
    PLANNING_ASSIGN = r"^/planning\s+assign\s+(\S+)\s+(\S+)$"
    PLANNING_ESTIMATE = r"^/planning\s+estimate\s+(\S+)\s+(\d+\.?\d*)\s+(\d+\.?\d*)$"
    PLANNING_SET_GOAL = r"^/planning\s+goal\s+(.+)$"
    PLANNING_FINALIZE = r"^/planning\s+finalize$"
    
    # ========== Standup ==========
    STANDUP = r"^/standup(?:\s+(\d+)\s+(\d+\.?\d*)\s*(\d+)?\s*(.*))?$"
    STANDUP_BATCH = r"^/standup\s+batch$"
    
    # ========== Admin ==========
    LEAVE = r"^/leave\s+(\d+\.?\d*)\s*(\d{4}-\d{2}-\d{2})?$"
    PAUSE = r"^/pause\s+(\S+)$"
    RESUME = r"^/resume\s+(\S+)$"
    REASSIGN = r"^/reassign\s+(\S+)\s+(\S+)$"
    
    # ========== Query ==========
    STATUS = r"^/status\s*(\S+)?$"
    DASHBOARD = r"^/dashboard$"
    RETRO = r"^/retro$"
    RETRO_TREND = r"^/retro\s+trend\s*(\d+)?$"
    ASSESSMENT_GENERATE = r"^/assessment\s+generate\s*(\S+)?$"
    ASSESSMENT_CONFIRM = r"^/assessment\s+confirm\s+(\S+)$"
    ASSESSMENT_REVIEW = r"^/assessment\s+review$"
    
    # ========== Config ==========
    CONFIG = r"^/config\s+(\S+)\s+(\S+)$"
    
    # ========== Interview ==========
    SKIP = r"^/skip$"
    INTERVIEW_ANSWER = r"^/interview\s+answer\s+(\d+)\s+(.+)$"
    
    # ========== Import ==========
    IMPORT_EXCEL = r"^/import\s+excel\s+(.+)$"
    
    def parse(self, text: str) -> Optional[ParsedCommand]:
        """解析命令"""
        text = text.strip()
        
        # Planning
        if text.startswith("/planning"):
            return self._parse_planning(text)
        
        # Standup
        if text.startswith("/standup"):
            return self._parse_standup(text)
        
        # Admin
        if text.startswith("/leave"):
            return self._parse_leave(text)
        if text.startswith("/pause"):
            return self._parse_pause(text)
        if text.startswith("/resume"):
            return self._parse_resume(text)
        if text.startswith("/reassign"):
            return self._parse_reassign(text)
        
        # Query
        if text.startswith("/status"):
            return self._parse_status(text)
        if text.startswith("/dashboard"):
            return self._parse_dashboard(text)
        if text.startswith("/retro"):
            return self._parse_retro(text)
        if text.startswith("/assessment"):
            return self._parse_assessment(text)
        
        # Config
        if text.startswith("/config"):
            return self._parse_config(text)
        
        # Interview
        if text == "/skip":
            return ParsedCommand(action="interview", sub_action="skip", raw=text)
        if text.startswith("/interview"):
            return self._parse_interview_answer(text)
        
        # Import
        if text.startswith("/import"):
            return self._parse_import(text)
        
        return None
    
    def _parse_planning(self, text: str) -> Optional[ParsedCommand]:
        # start
        m = re.match(self.PLANNING_START, text)
        if m:
            return ParsedCommand(
                action="planning", sub_action="start",
                args=[m.group(1), m.group(2), m.group(3)], raw=text
            )
        
        # add-member
        m = re.match(self.PLANNING_ADD_MEMBER, text)
        if m:
            return ParsedCommand(
                action="planning", sub_action="add-member",
                args=[m.group(1), m.group(2)], raw=text
            )
        
        # add-task
        m = re.match(self.PLANNING_ADD_TASK, text)
        if m:
            return ParsedCommand(
                action="planning", sub_action="add-task",
                args=[m.group(1)], raw=text
            )
        
        # assign
        m = re.match(self.PLANNING_ASSIGN, text)
        if m:
            return ParsedCommand(
                action="planning", sub_action="assign",
                args=[m.group(1), m.group(2)], raw=text
            )
        
        # estimate
        m = re.match(self.PLANNING_ESTIMATE, text)
        if m:
            return ParsedCommand(
                action="planning", sub_action="estimate",
                args=[m.group(1), m.group(2), m.group(3)], raw=text
            )
        
        # goal
        m = re.match(self.PLANNING_SET_GOAL, text)
        if m:
            return ParsedCommand(
                action="planning", sub_action="goal",
                args=[m.group(1)], raw=text
            )
        
        # finalize
        m = re.match(self.PLANNING_FINALIZE, text)
        if m:
            return ParsedCommand(
                action="planning", sub_action="finalize",
                raw=text
            )
        
        return ParsedCommand(action="planning", sub_action="unknown", raw=text)
    
    def _parse_standup(self, text: str) -> Optional[ParsedCommand]:
        m = re.match(self.STANDUP, text)
        if m:
            if m.group(1) is None:
                # /standup 无参数 -> 获取任务列表
                return ParsedCommand(action="standup", sub_action="prompt", raw=text)
            args = [m.group(1), m.group(2)]
            if m.group(3):
                args.append(m.group(3))
            if m.group(4):
                args.append(m.group(4).strip())
            return ParsedCommand(
                action="standup", sub_action="report",
                args=args, raw=text
            )
        return ParsedCommand(action="standup", sub_action="unknown", raw=text)
    
    def _parse_leave(self, text: str) -> ParsedCommand:
        m = re.match(self.LEAVE, text)
        if m:
            args = [m.group(1)]
            if m.group(2):
                args.append(m.group(2))
            return ParsedCommand(action="admin", sub_action="leave", args=args, raw=text)
        return ParsedCommand(action="admin", sub_action="unknown", raw=text)
    
    def _parse_pause(self, text: str) -> ParsedCommand:
        m = re.match(self.PAUSE, text)
        if m:
            return ParsedCommand(action="admin", sub_action="pause", args=[m.group(1)], raw=text)
        return ParsedCommand(action="admin", sub_action="unknown", raw=text)
    
    def _parse_resume(self, text: str) -> ParsedCommand:
        m = re.match(self.RESUME, text)
        if m:
            return ParsedCommand(action="admin", sub_action="resume", args=[m.group(1)], raw=text)
        return ParsedCommand(action="admin", sub_action="unknown", raw=text)
    
    def _parse_reassign(self, text: str) -> ParsedCommand:
        m = re.match(self.REASSIGN, text)
        if m:
            return ParsedCommand(action="admin", sub_action="reassign", args=[m.group(1), m.group(2)], raw=text)
        return ParsedCommand(action="admin", sub_action="unknown", raw=text)
    
    def _parse_status(self, text: str) -> ParsedCommand:
        m = re.match(self.STATUS, text)
        if m:
            args = []
            if m.group(1):
                args.append(m.group(1))
            return ParsedCommand(action="query", sub_action="status", args=args, raw=text)
        return ParsedCommand(action="query", sub_action="unknown", raw=text)
    
    def _parse_dashboard(self, text: str) -> ParsedCommand:
        return ParsedCommand(action="query", sub_action="dashboard", raw=text)
    
    def _parse_retro(self, text: str) -> ParsedCommand:
        m = re.match(self.RETRO_TREND, text)
        if m:
            args = []
            if m.group(1):
                args.append(m.group(1))
            return ParsedCommand(action="retro", sub_action="trend", args=args, raw=text)
        
        m = re.match(self.RETRO, text)
        if m:
            return ParsedCommand(action="retro", sub_action="single", raw=text)
        
        return ParsedCommand(action="retro", sub_action="unknown", raw=text)
    
    def _parse_assessment(self, text: str) -> ParsedCommand:
        m = re.match(self.ASSESSMENT_GENERATE, text)
        if m:
            args = []
            if m.group(1):
                args.append(m.group(1))
            return ParsedCommand(action="assessment", sub_action="generate", args=args, raw=text)
        
        m = re.match(self.ASSESSMENT_CONFIRM, text)
        if m:
            return ParsedCommand(action="assessment", sub_action="confirm", args=[m.group(1)], raw=text)
        
        m = re.match(self.ASSESSMENT_REVIEW, text)
        if m:
            return ParsedCommand(action="assessment", sub_action="review", raw=text)
        
        return ParsedCommand(action="assessment", sub_action="unknown", raw=text)
    
    def _parse_config(self, text: str) -> ParsedCommand:
        m = re.match(self.CONFIG, text)
        if m:
            return ParsedCommand(action="config", sub_action="set", args=[m.group(1), m.group(2)], raw=text)
        return ParsedCommand(action="config", sub_action="unknown", raw=text)
    
    def _parse_interview_answer(self, text: str) -> ParsedCommand:
        m = re.match(self.INTERVIEW_ANSWER, text)
        if m:
            return ParsedCommand(action="interview", sub_action="answer", args=[m.group(1), m.group(2)], raw=text)
        return ParsedCommand(action="interview", sub_action="unknown", raw=text)
    
    def _parse_import(self, text: str) -> ParsedCommand:
        m = re.match(self.IMPORT_EXCEL, text)
        if m:
            return ParsedCommand(action="import", sub_action="excel", args=[m.group(1)], raw=text)
        return ParsedCommand(action="import", sub_action="unknown", raw=text)

import re
from typing import Optional

from models.daily_log import DailyLog


class NLPEngine:
    """自然语言解析引擎 - MVP 简化版"""
    
    # 常见模式
    HOURS_PATTERNS = [
        r"花了?\s*(\d+\.?\d*)\s*个?[小时h]",
        r"(\d+\.?\d*)\s*个?[小时h]",
        r"(\d+\.?\d*)h",
    ]
    
    PROGRESS_PATTERNS = [
        r"进度\s*(\d+)%",
        r"完成\s*(\d+)%",
        r"(\d+)%\s*进度",
    ]
    
    BLOCKER_PATTERNS = [
        r"等([^，。]+)",
        r"阻塞[在是]?([^，。]+)",
        r"卡[住在]?([^，。]+)",
        r"blocked by ([^，。]+)",
    ]
    
    EXTRA_CONTRIBUTION_KEYWORDS = ["顺手", "额外", "顺便", "也修了", "发现", "顺手修", "顺手改"]
    BLOCKER_RESOLVED_KEYWORDS = ["解决", "搞定", "修复", "通过了", "对齐了", "ok了", "完成了"]
    
    def parse_standup(self, text: str, member_id: str, task_name: str = None) -> Optional[DailyLog]:
        """
        解析自然语言日报
        返回 DailyLog 或 None（置信度不足）
        """
        text = text.strip()
        
        # 提取耗时
        hours = None
        for pattern in self.HOURS_PATTERNS:
            m = re.search(pattern, text)
            if m:
                hours = float(m.group(1))
                break
        
        if hours is None:
            return None
        
        # 提取进度
        progress = None
        for pattern in self.PROGRESS_PATTERNS:
            m = re.search(pattern, text)
            if m:
                progress = int(m.group(1))
                break
        
        # 提取阻塞
        blocker = None
        for pattern in self.BLOCKER_PATTERNS:
            m = re.search(pattern, text)
            if m:
                blocker = m.group(1).strip()
                break
        
        # 额外贡献检测
        notes = ""
        if any(kw in text for kw in self.EXTRA_CONTRIBUTION_KEYWORDS):
            notes = "[额外贡献] " + text
        
        return DailyLog(
            id=f"log_{member_id}_{task_name or 'unknown'}",
            date=None,  # 由引擎设置
            member_id=member_id,
            task_id=task_name or "",
            hours=hours,
            progress_percent=progress,
            blocker=blocker,
            notes=notes,
        )
    
    def detect_extra_contribution(self, text: str) -> bool:
        """检测顺手修复/额外贡献"""
        return any(kw in text for kw in self.EXTRA_CONTRIBUTION_KEYWORDS)
    
    def detect_blocker_resolved(self, text: str) -> bool:
        """检测阻塞解决"""
        return any(kw in text for kw in self.BLOCKER_RESOLVED_KEYWORDS)
    
    def extract_task_name(self, text: str, available_tasks: list) -> Optional[str]:
        """
        从文本中提取任务名
        策略：匹配可用任务列表中的任务名
        """
        for task_name in available_tasks:
            if task_name in text:
                return task_name
        return None
    
    def calculate_confidence(self, text: str) -> float:
        """
        计算解析置信度
        有耗时 + 有任务名 = 高置信度
        只有耗时 = 中置信度
        无耗时 = 低置信度
        """
        has_hours = any(re.search(p, text) for p in self.HOURS_PATTERNS)
        has_progress = any(re.search(p, text) for p in self.PROGRESS_PATTERNS)
        
        if has_hours and has_progress:
            return 0.9
        elif has_hours:
            return 0.7
        else:
            return 0.3

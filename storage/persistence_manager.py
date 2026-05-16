import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from models.sprint import Sprint
from models.story_pool import StoryPoolEntry


class PersistenceManager:
    """持久化管理器 - JSON 文件存储"""
    
    AUTO_SAVE_INTERVAL = 300  # 5 分钟
    BACKUP_COUNT = 10
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir:
            self.BASE_PATH = Path(data_dir)
        else:
            # 默认使用当前工作目录下的 data 目录
            self.BASE_PATH = Path.cwd() / "data"
        
        self._ensure_directories()
        self._last_save = datetime.now()
    
    def _ensure_directories(self):
        """确保目录结构存在"""
        dirs = [
            self.BASE_PATH,
            self.BASE_PATH / "active",
            self.BASE_PATH / "sprints",
            self.BASE_PATH / "story_pool",
            self.BASE_PATH / "retro",
            self.BASE_PATH / "assessments",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def _backup_file(self, file_path: Path):
        """备份文件"""
        if not file_path.exists():
            return
        bak_path = file_path.with_suffix(f".bak.{datetime.now().strftime('%Y%m%d%H%M%S')}")
        shutil.copy2(file_path, bak_path)
        
        # 清理旧备份
        bak_files = sorted(file_path.parent.glob(f"{file_path.name}.bak.*"))
        if len(bak_files) > self.BACKUP_COUNT:
            for f in bak_files[:-self.BACKUP_COUNT]:
                f.unlink()
    
    def save_sprint(self, sprint: Sprint):
        """保存当前 sprint"""
        file_path = self.BASE_PATH / "active" / "active_sprint.json"
        self._backup_file(file_path)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(sprint.to_dict(), f, ensure_ascii=False, indent=2)
        self._last_save = datetime.now()
    
    def load_active_sprint(self) -> Optional[Sprint]:
        """加载当前活跃 sprint"""
        file_path = self.BASE_PATH / "active" / "active_sprint.json"
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Sprint.from_dict(data)
        except Exception:
            return None
    
    def archive_sprint(self, sprint: Sprint):
        """归档 sprint"""
        # 保存到历史目录
        file_path = self.BASE_PATH / "sprints" / f"{sprint.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(sprint.to_dict(), f, ensure_ascii=False, indent=2)
        
        # 清空 active
        active_path = self.BASE_PATH / "active" / "active_sprint.json"
        if active_path.exists():
            active_path.unlink()
    
    def save_story_pool(self, entries: List[StoryPoolEntry]):
        """保存事迹候选池"""
        file_path = self.BASE_PATH / "story_pool" / "pool.json"
        self._backup_file(file_path)
        data = {
            "version": 1,
            "updated_at": datetime.now().isoformat(),
            "entries": [e.to_dict() for e in entries],
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_story_pool(self) -> List[StoryPoolEntry]:
        """加载事迹候选池"""
        file_path = self.BASE_PATH / "story_pool" / "pool.json"
        if not file_path.exists():
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [StoryPoolEntry.from_dict(e) for e in data.get("entries", [])]
        except Exception:
            return []
    
    def load_historical_sprints(self, limit: int = 10) -> List[Sprint]:
        """加载历史 sprint 列表"""
        sprints_dir = self.BASE_PATH / "sprints"
        if not sprints_dir.exists():
            return []
        
        sprint_files = sorted(sprints_dir.glob("*.json"), reverse=True)
        sprints = []
        for file_path in sprint_files[:limit]:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                sprints.append(Sprint.from_dict(data))
            except Exception:
                continue
        return sprints
    
    def export_retro_markdown(self, content: str, sprint_id: str):
        """导出 retro 报告"""
        file_path = self.BASE_PATH / "retro" / f"retro-{sprint_id}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return str(file_path)
    
    def export_assessment_markdown(self, content: str, member_name: str, period: str):
        """导出自评表"""
        file_path = self.BASE_PATH / "assessments" / f"assessment-{member_name}-{period}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return str(file_path)
    
    def auto_save(self, sprint: Sprint, story_pool: List[StoryPoolEntry]):
        """自动保存"""
        now = datetime.now()
        if (now - self._last_save).seconds >= self.AUTO_SAVE_INTERVAL:
            self.save_sprint(sprint)
            self.save_story_pool(story_pool)
    
    def save_config(self, config: dict):
        """保存全局配置"""
        file_path = self.BASE_PATH / "config.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def load_config(self) -> dict:
        """加载全局配置"""
        file_path = self.BASE_PATH / "config.json"
        if not file_path.exists():
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

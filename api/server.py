from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, List

from api.agent_api import SprintAgentAPI

app = FastAPI(
    title="Sprint Agent API",
    description="团队敏捷迭代自动化 Agent API",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 Agent
data_dir = Path(__file__).parent.parent / "data"
agent = SprintAgentAPI(data_dir)

# 挂载静态文件（前端看板）
web_dir = Path(__file__).parent.parent / "web"
app.mount("/", StaticFiles(directory=str(web_dir), html=True), name="web")


# ========== Pydantic Models ==========

class SprintCreate(BaseModel):
    name: str
    start_date: str
    end_date: str
    workdays: int = 10


class MemberCreate(BaseModel):
    name: str
    coefficient: float = 1.0


class TaskCreate(BaseModel):
    name: str
    owner_name: str
    estimate_low: float
    estimate_high: float
    priority: int = 5
    ddl: Optional[str] = None
    is_public: bool = False


class StatusUpdate(BaseModel):
    status: str


class DailyLogCreate(BaseModel):
    task_id: str
    member_id: str
    hours: float
    progress_percent: Optional[int] = None
    blocker: Optional[str] = None
    notes: Optional[str] = None


class RetroRequest(BaseModel):
    trend_count: int = 0


class AssessmentRequest(BaseModel):
    member_name: str
    period: str


# ========== API Endpoints ==========

@app.get("/api/sprint")
def get_sprint():
    """获取当前 Sprint"""
    sprint = agent.get_sprint()
    if not sprint:
        raise HTTPException(status_code=404, detail="没有活跃的 Sprint")
    return sprint


@app.get("/api/board")
def get_board():
    """获取看板数据"""
    return agent.get_board_data()


@app.post("/api/sprint")
def create_sprint(req: SprintCreate):
    """创建 Sprint"""
    result = agent.create_sprint(req.name, req.start_date, req.end_date, req.workdays)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/api/sprint/finalize")
def finalize_sprint():
    """启动 Sprint"""
    result = agent.finalize_sprint()
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/api/members")
def add_member(req: MemberCreate):
    """添加成员"""
    result = agent.add_member(req.name, req.coefficient)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/api/tasks")
def add_task(req: TaskCreate):
    """添加任务"""
    result = agent.add_task(
        req.name, req.owner_name, req.estimate_low, req.estimate_high,
        req.priority, req.ddl, req.is_public
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.patch("/api/tasks/{task_id}/status")
def update_task_status(task_id: str, req: StatusUpdate):
    """更新任务状态"""
    result = agent.update_task_status(task_id, req.status)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/api/daily-log")
def add_daily_log(req: DailyLogCreate):
    """添加日报记录"""
    result = agent.add_daily_log(
        req.task_id, req.member_id, req.hours,
        req.progress_percent, req.blocker, req.notes
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/api/dashboard")
def get_dashboard():
    """获取团队看板文本"""
    return {"content": agent.get_dashboard()}


@app.get("/api/members/{member_name}/status")
def get_member_status(member_name: str):
    """获取个人状态"""
    return {"content": agent.get_member_status(member_name)}


@app.post("/api/retro")
def generate_retro(req: RetroRequest):
    """生成 Retro 报告"""
    result = agent.generate_retro(req.trend_count)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/api/assessment")
def generate_assessment(req: AssessmentRequest):
    """生成自评表"""
    result = agent.generate_assessment(req.member_name, req.period)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/api/health")
def health_check():
    """健康检查"""
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

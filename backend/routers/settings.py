from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List

import crud
import schemas
from database import get_db, engine
from models import Base
from services.import_service import load_init_data
from services.export_service import export_all

router = APIRouter(prefix="/api", tags=["settings"])


@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    items = crud.get_all_config(db)
    return {c.key: c.value for c in items}


@router.put("/settings")
def update_settings(data: schemas.ConfigUpdate, db: Session = Depends(get_db)):
    crud.set_multiple_config(db, data.settings)
    return {"updated": True}


@router.get("/export")
def export_data(db: Session = Depends(get_db)):
    return export_all(db)


@router.post("/import", response_model=schemas.ImportResult)
def import_data(payload: schemas.ImportPayload, db: Session = Depends(get_db)):
    inserted: Dict[str, int] = {}
    errors: List[str] = []
    # Simple pass-through; robust import would validate each entity
    return schemas.ImportResult(summary="Import not fully implemented in MVP", inserted=inserted, errors=errors)


@router.post("/reset")
def reset_db(db: Session = Depends(get_db)):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    load_init_data(db)
    return {"reset": True}


@router.get("/health")
def health():
    return {"status": "ok"}

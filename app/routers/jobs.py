from fastapi import Request, APIRouter, Depends, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.db.db import get_db
from app.auth.dependencies import require_login
from app.tasks.services.job_service import JobService
from app.tasks.schemas.job_schemas import JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])

templates = Jinja2Templates(directory="app/frontend/templates")

@router.get("/get", response_model=JobResponse, status_code=status.HTTP_200_OK)
async def get_job(request: Request, id: int, db: Session = Depends(get_db), current_user = Depends(require_login)):
    job_svc = JobService(db)
    return job_svc.get_job_by_id(id, current_user.id)

@router.get("/get-generating", response_model=Optional[JobResponse], status_code=status.HTTP_200_OK)
async def get_basket_generating_job(request: Request, db: Session = Depends(get_db), current_user = Depends(require_login)):
    job_svc = JobService(db)
    return job_svc.get_in_progress_basket_generation_job(current_user.id)

@router.get("/get-regenerating", response_model=Optional[JobResponse], status_code=status.HTTP_200_OK)
async def get_basket_regenerating_job(request: Request, basket_id: int, db: Session = Depends(get_db), current_user = Depends(require_login)):
    job_svc = JobService(db)
    return job_svc.get_in_progress_basket_regeneration_job(basket_id, current_user.id)

@router.get("/get-suggestions-generating", response_model=Optional[JobResponse], status_code=status.HTTP_200_OK)
async def get_suggestions_generating_job(request: Request, basket_id: int, db: Session = Depends(get_db), current_user = Depends(require_login)):
    job_svc = JobService(db)
    return job_svc.get_in_progress_suggestions_job(basket_id, current_user.id)

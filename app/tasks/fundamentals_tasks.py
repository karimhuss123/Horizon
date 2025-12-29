import json
from fastapi import HTTPException
from app.core.celery_app import celery_app
from app.market_data.services.fundamentals_service import FundamentalsService
from app.tasks.repositories.job_repo import JobRepo
from app.core.errors.messages import messages
from app.db.db import SessionLocal

@celery_app.task(name="fundamentals_processing_task")
def run_fundamentals_processing(job_id, user_id, outdated_securities):
    try:
        db = SessionLocal()
        jobs = JobRepo(db)
        job = jobs.get_job_by_id(job_id, user_id)
        jobs.update_running_job(job.id, user_id)
        user_id = job.user_id
        
        fund_svc = FundamentalsService(db)
        try:
            fundamentals = fund_svc.process_fundamentals(outdated_securities)
        except HTTPException as e:
            detail = e.detail.get("message") if isinstance(e.detail, dict) else str(e.detail)
            jobs.update_failed_job(job_id, user_id, detail)
            return
        jobs.update_succeeded_job(job_id, user_id)
    except:
        jobs.update_failed_job(job_id, user_id, messages.jobs_basket_suggestions_unexpected_error)
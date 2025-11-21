import json
from fastapi import HTTPException
from app.core.celery_app import celery_app
from app.investment_engine.services.basket_service import BasketService
from app.investment_engine.services.ai_service import AIService
from app.tasks.repositories.job_repo import JobRepo
from app.clients.openai_client import OpenAIClient
from app.core.errors.messages import messages
from app.db.db import SessionLocal

@celery_app.task(name="basket_generation_task")
def run_basket_generation(job_id, user_id):
    try:
        db = SessionLocal()
        jobs = JobRepo(db)
        job = jobs.get_job_by_id(job_id, user_id)
        jobs.update_running_job(job.id, user_id)
        user_id = job.user_id
        payload = json.loads(job.payload)
        user_prompt = payload["user_prompt"]
        
        ai_svc = AIService(OpenAIClient())
        basket_svc = BasketService(db, ai_svc)
        try:
            basket = basket_svc.generate_basket(user_prompt=user_prompt, user_id=user_id)
        except HTTPException as e:
            detail = e.detail.get("message") if isinstance(e.detail, dict) else str(e.detail)
            jobs.update_failed_job(job_id, user_id, detail)
            return
        jobs.update_succeeded_job(job_id, user_id)
    except:
        jobs.update_failed_job(job_id, user_id, messages.jobs_basket_generation_unexpected_error)
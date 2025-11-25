import json
from fastapi import HTTPException
from app.core.celery_app import celery_app
from app.investment_engine.services.basket_service import BasketService
from app.investment_engine.services.ai_service import AIService
from app.investment_engine.services.basket_suggestion_service import BasketSuggestionService
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

@celery_app.task(name="basket_regeneration_task")
def run_basket_regeneration(job_id, user_id):
    try:
        db = SessionLocal()
        jobs = JobRepo(db)
        job = jobs.get_job_by_id(job_id, user_id)
        print("HERE")
        payload = json.loads(job.payload)
        print("PAYLOAD:", payload)
        ai_svc = AIService(OpenAIClient())
        basket_svc = BasketService(db, ai_svc)
        try:
            regeneration = basket_svc.regenerate_basket(payload, user_id)
        except HTTPException as e:
            detail = e.detail.get("message") if isinstance(e.detail, dict) else str(e.detail)
            jobs.update_failed_job(job_id, user_id, detail)
            return
        jobs.update_succeeded_job(job_id, user_id)
    except:
        jobs.update_failed_job(job_id, user_id, messages.jobs_basket_regeneration_unexpected_error)

@celery_app.task(name="suggestions_generation_task")
def run_suggestions_generation(job_id, user_id):
    try:
        db = SessionLocal()
        jobs = JobRepo(db)
        job = jobs.get_job_by_id(job_id, user_id)
        jobs.update_running_job(job.id, user_id)
        user_id = job.user_id
        payload = json.loads(job.payload)
        basket_id = payload["basket_id"] or job.basket_id
        
        ai_svc = AIService(OpenAIClient())
        sug_svc = BasketSuggestionService(db, ai_svc)
        try:
            suggestions = sug_svc.generate_basket_suggestions(basket_id=basket_id, user_id=user_id)
        except HTTPException as e:
            detail = e.detail.get("message") if isinstance(e.detail, dict) else str(e.detail)
            jobs.update_failed_job(job_id, user_id, detail)
            return
        jobs.update_succeeded_job(job_id, user_id)
    except:
        jobs.update_failed_job(job_id, user_id, messages.jobs_basket_suggestions_unexpected_error)
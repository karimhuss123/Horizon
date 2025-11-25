import json
from pydantic import BaseModel
from fastapi import HTTPException, status
from app.tasks.repositories.job_repo import JobRepo
from app.investment_engine.repositories.basket_repo import BasketRepo
from app.tasks.basket_tasks import run_basket_generation, run_basket_regeneration, run_suggestions_generation
from app.core.errors.messages import messages

class JobService:
    def __init__(self, db):
        self.db = db
        self.jobs = JobRepo(db)
        self.baskets = BasketRepo(db)
        
    def enqueue_basket_generation(self, payload, user_id):
        if self.jobs.get_in_progress_basket_generation_job(user_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": messages.jobs_basket_generation_in_progress})
        normalized_payload = self.normalize_payload(payload)
        job = self.jobs.create_generation_job(normalized_payload, user_id)
        run_basket_generation.delay(job.id, user_id)
        return {"job_id": job.id, "status": job.status, "error_message": job.error_message}
    
    def enqueue_basket_regeneration(self, payload, user_id):
        print("BASKET ID", payload.basket_id)
        if self.jobs.get_in_progress_basket_regeneration_job(payload.basket_id, user_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": messages.jobs_basket_regeneration_in_progress})
        normalized_payload = self.normalize_payload(payload)
        job = self.jobs.create_regeneration_job(normalized_payload, payload.basket_id, user_id)
        run_basket_regeneration.delay(job.id, user_id)
        return {"job_id": job.id, "status": job.status, "error_message": job.error_message}

    def get_job_by_id(self, id, user_id):
        job = self.jobs.get_job_by_id(id, user_id)
        return {"job_id": job.id, "status": job.status, "error_message": job.error_message}
    
    def get_in_progress_basket_generation_job(self, user_id):
        job = self.jobs.get_in_progress_basket_generation_job(user_id)
        if not job:
            return None
        return {"job_id": job.id, "status": job.status, "error_message": job.error_message}
    
    def get_in_progress_basket_regeneration_job(self, basket_id, user_id):
        job = self.jobs.get_in_progress_basket_regeneration_job(basket_id, user_id)
        if not job:
            return None
        return {"job_id": job.id, "status": job.status, "error_message": job.error_message}
    
    def get_in_progress_suggestions_job(self, basket_id, user_id):
        basket = self.baskets.get(basket_id, user_id) # Verify basket validity
        job = self.jobs.get_in_progress_suggestions_job(basket_id, user_id)
        if not job:
            return None
        return {"job_id": job.id, "status": job.status, "error_message": job.error_message}
    
    def enqueue_suggestions_generation(self, payload, user_id):
        basket = self.baskets.get(payload.basket_id, user_id) # Verify basket validity
        normalized_payload = self.normalize_payload(payload)
        if self.jobs.get_in_progress_suggestions_job(payload.basket_id, user_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": messages.jobs_suggestions_in_progress})
        job = self.jobs.create_suggestions_job(normalized_payload, payload.basket_id, user_id)
        run_suggestions_generation.delay(job.id, user_id)
        return {"job_id": job.id, "status": job.status, "error_message": job.error_message}
    
    def normalize_payload(self, payload: BaseModel) -> str:
        raw = payload.model_dump()
        normalized = json.dumps(
            raw,
            sort_keys=True,
            separators=(",", ":") 
        )
        return normalized
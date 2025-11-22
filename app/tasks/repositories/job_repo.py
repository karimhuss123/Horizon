from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models import Job, JobType, JobStatus
from app.core.errors.messages import messages

class JobRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def create_generation_job(self, payload, user_id):
        job = Job(
            user_id=user_id,
            job_type=JobType.BASKET_GENERATION,
            status=JobStatus.PENDING,
            payload=payload
        )
        self.db.add(job)
        self.db.commit()
        return job
    
    def create_suggestions_job(self, payload, basket_id, user_id):
        job = Job(
            user_id=user_id,
            basket_id=basket_id,
            job_type=JobType.SUGGESTIONS_GENERATION,
            status=JobStatus.PENDING,
            payload=payload
        )
        self.db.add(job)
        self.db.commit()
        return job

    def get_job_by_id(self, job_id, user_id):
        job = self.db.query(Job).filter(Job.id==job_id, Job.user_id==user_id).first()
        if not job:
            raise HTTPException(status_code=404, detail=messages.job_not_found)
        return job
    
    def get_in_progress_basket_generation_job(self, user_id):
        return (
            self.db.query(Job)
            .filter(
                Job.user_id == user_id,
                Job.job_type == JobType.BASKET_GENERATION,
                Job.status.in_([JobStatus.PENDING, JobStatus.RUNNING])
            ).first()
        )
    
    def get_in_progress_suggestions_job(self, basket_id, user_id):
        return (
            self.db.query(Job)
            .filter(
                Job.user_id == user_id,
                Job.basket_id == basket_id,
                Job.job_type == JobType.SUGGESTIONS_GENERATION,
                Job.status.in_([JobStatus.PENDING, JobStatus.RUNNING])
            ).first()
        )

    def update_running_job(self, job_id, user_id):
        job = self.get_job_by_id(job_id, user_id)
        job.status = JobStatus.RUNNING
        job.error_message = None
        self.db.commit()
        return job
    
    def update_failed_job(self, job_id, user_id, detail):
        job = self.get_job_by_id(job_id, user_id)
        job.status = JobStatus.FAILED
        job.error_message = detail
        self.db.commit()
        return job

    def update_succeeded_job(self, job_id, user_id):
        job = self.get_job_by_id(job_id, user_id)
        job.status = JobStatus.SUCCEEDED
        job.error_message = None
        self.db.commit()
        return job

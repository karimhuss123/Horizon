from pydantic import BaseModel, Field
from app.db.models import JobStatus
from typing import Optional

class JobResponse(BaseModel):
    job_id: int = Field(..., gt=0)
    status: JobStatus
    error_message: Optional[str] = None
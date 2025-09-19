from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobCreate(BaseModel):
    problem_image_url: Optional[str] = None
    problem_text: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class JobResponse(BaseModel):
    id: str
    status: JobStatus
    problem_image_url: Optional[str] = None
    video_url: Optional[str] = None
    mni_file_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}

class JobList(BaseModel):
    jobs: list[JobResponse]
    total: int

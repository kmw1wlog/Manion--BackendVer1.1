from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: str  # "google" | "kakao"
    role: UserRole = UserRole.USER
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Job(BaseModel):
    id: str
    user_id: str
    status: JobStatus
    problem_image_url: Optional[str] = None
    mni_file_id: Optional[str] = None
    video_url: Optional[str] = None
    manim_code: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MNIFile(BaseModel):
    id: str
    job_id: str
    user_id: str
    content: Dict[str, Any]  # .mni JSON 내용
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class PostType(str, Enum):
    GENERAL = "general"  # 일반 게시판
    NOTICE = "notice"    # 공지사항
    ANONYMOUS = "anonymous"  # 익명 게시판

class Post(BaseModel):
    id: str
    title: str
    content: str
    user_id: str
    type: PostType
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    views: int = 0
    likes: int = 0
    comments_count: int = 0

class Comment(BaseModel):
    id: str
    post_id: str
    user_id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    likes: int = 0

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.core.security import get_current_user

router = APIRouter()

class ManimGenerateRequest(BaseModel):
    script: str

@router.post("/generate")
async def generate_manim(
    request: ManimGenerateRequest,
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Manim 스크립트를 기반으로 시각화 생성을 요청합니다.
    """
    # TODO: 실제 Manim 생성 로직 구현
    return {
        "message": "manim queued",
        "job_id": "dummy_job_id_12345", 
        "status": "pending"
    }

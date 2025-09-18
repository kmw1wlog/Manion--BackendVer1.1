from fastapi import APIRouter
import os
from datetime import datetime

router = APIRouter()

@router.get("/")
async def health_check():
    """
    시스템 상태 확인을 위한 헬스체크 엔드포인트
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
        "port": os.environ.get("PORT", "8000"),
        "environment": os.environ.get("ENVIRONMENT", "development")
    }
from fastapi import APIRouter, Response
import os
from datetime import datetime

router = APIRouter()

@router.get("/")
async def health_check(response: Response):
    """
    시스템 상태 확인을 위한 헬스체크 엔드포인트
    """
    # 리디렉션 없이 직접 응답하도록 설정
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
        "port": os.environ.get("PORT", "8000"),
        "environment": os.environ.get("ENVIRONMENT", "development")
    }

# 슬래시가 없는 경로도 동일하게 처리 (Railway 헬스체크용)
@router.get("")
async def health_check_no_slash(response: Response):
    """
    슬래시가 없는 헬스체크 엔드포인트 (Railway 헬스체크용)
    """
    return await health_check(response)
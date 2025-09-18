from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health_check():
    """
    시스템 상태 확인을 위한 헬스체크 엔드포인트
    """
    return {
        "ok": True
    }
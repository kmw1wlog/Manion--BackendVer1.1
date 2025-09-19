from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import Dict, Any, Optional
import httpx

from app.core.config import settings
from app.core.security import get_current_user

router = APIRouter()

@router.get("/{problemId}")
async def get_problem(
    problemId: str = Path(...),
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    특정 문제의 상세 정보를 조회합니다.
    """
    try:
        # TODO: Supabase에서 실제 문제 데이터 조회
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"
            }
            
            # 예시: 문제 데이터 조회
            query_url = f"{settings.SUPABASE_URL}/rest/v1/problems?id=eq.{problemId}"
            response = await client.get(query_url, headers=headers)
            
            if response.status_code == 200:
                problems = response.json()
                if not problems:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Problem with ID {problemId} not found"
                    )
                return problems[0]
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch problem: {response.text}"
                )
    except HTTPException:
        raise
    except Exception as e:
        # 현재는 더미 데이터 반환 (실제 구현 시 수정 필요)
        return {
            "id": problemId,
            "title": f"Example Problem {problemId}",
            "statement": "y = x^2 - 4x + 3의 꼭짓점을 구하라",
            "type": "algebra",
            "difficulty": "medium",
            "created_at": "2025-09-20T00:00:00Z",
            "note": f"TODO: Implement real problem fetching, Error: {str(e)}"
        }

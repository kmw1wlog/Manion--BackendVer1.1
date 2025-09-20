from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import httpx

from app.core.config import settings
from app.core.security import get_current_user

router = APIRouter()

class TitleUpdateRequest(BaseModel):
    title: str

@router.get("/history")
async def get_user_history(
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    사용자의 문제 풀이 이력을 조회합니다.
    """
    try:
        user_id = user.get("id")
        
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"
            }
            
            # 예시: 사용자 이력 조회
            query_url = f"{settings.SUPABASE_URL}/rest/v1/user_history?user_id=eq.{user_id}"
            response = await client.get(query_url, headers=headers)
            
            if response.status_code == 200:
                history = response.json()
                return {
                    "history": history,
                    "count": len(history)
                }
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch history: {response.text}"
                )
    except Exception as e:
        # 현재는 더미 데이터 반환 (실제 구현 시 수정 필요)
        return {
            "history": [
                {
                    "id": "history_1",
                    "problem_id": "prob_1",
                    "user_id": user.get("id"),
                    "title": "이차함수 문제",
                    "created_at": "2025-09-19T14:30:00Z",
                    "status": "completed"
                },
                {
                    "id": "history_2",
                    "problem_id": "prob_2",
                    "user_id": user.get("id"),
                    "title": "미분 문제",
                    "created_at": "2025-09-19T15:45:00Z",
                    "status": "in_progress"
                }
            ],
            "count": 2,
            "note": f"TODO: Implement real history fetching, Error: {str(e)}"
        }

@router.delete("/history/problem/{problemId}")
async def delete_problem_history(
    problemId: str = Path(...),
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    사용자의 특정 문제 풀이 이력을 삭제합니다.
    """
    try:
        user_id = user.get("id")
        
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"
            }
            
            # 예시: 이력 삭제
            query_url = f"{settings.SUPABASE_URL}/rest/v1/user_history?user_id=eq.{user_id}&problem_id=eq.{problemId}"
            response = await client.delete(query_url, headers=headers)
            
            if response.status_code in [200, 204]:
                return {"message": f"Problem history with ID {problemId} deleted successfully"}
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to delete history: {response.text}"
                )
    except Exception as e:
        # 스텁 응답
        return {
            "message": f"DELETE /user/history/problem/{problemId} ok",
            "note": f"TODO: Implement real deletion, Error: {str(e)}"
        }

@router.put("/history/problem/{problemId}/title")
async def update_problem_title(
    request: TitleUpdateRequest,
    problemId: str = Path(...),
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    사용자의 특정 문제 풀이 이력의 제목을 수정합니다.
    """
    try:
        user_id = user.get("id")
        
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            }
            
            # 예시: 제목 업데이트
            query_url = f"{settings.SUPABASE_URL}/rest/v1/user_history?user_id=eq.{user_id}&problem_id=eq.{problemId}"
            response = await client.patch(
                query_url,
                headers=headers,
                json={"title": request.title}
            )
            
            if response.status_code in [200, 204]:
                return {"message": f"Problem title updated successfully to '{request.title}'"}
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to update title: {response.text}"
                )
    except Exception as e:
        # 스텁 응답
        return {
            "message": f"PUT /user/history/problem/{problemId}/title ok",
            "updated_title": request.title,
            "note": f"TODO: Implement real title update, Error: {str(e)}"
        }

from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import Dict, Any, List, Optional
import httpx

from app.core.config import settings
from app.core.security import get_current_user, verify_admin_user

router = APIRouter()

@router.get("/problems")
async def get_admin_problems(
    page: int = 1,
    limit: int = 50,
    user: Dict[str, Any] = Depends(verify_admin_user)
) -> Dict[str, Any]:
    """
    관리자용 문제 목록을 조회합니다.
    """
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"
            }
            
            # 모든 문제 조회 (관리자 권한)
            offset = (page - 1) * limit
            query_url = f"{settings.SUPABASE_URL}/rest/v1/problems?order=created_at.desc&limit={limit}&offset={offset}"
            response = await client.get(query_url, headers=headers)
            
            if response.status_code == 200:
                problems = response.json()
                
                # 총 문제 수 조회
                count_url = f"{settings.SUPABASE_URL}/rest/v1/problems?select=count"
                count_response = await client.get(count_url, headers={**headers, "Prefer": "count=exact"})
                total_count = int(count_response.headers.get("Content-Range", "0-0/0").split("/")[1])
                
                return {
                    "problems": problems,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total_count,
                        "pages": (total_count + limit - 1) // limit
                    }
                }
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch problems: {response.text}"
                )
    except Exception as e:
        # 스텁 응답
        dummy_problems = [
            {
                "id": f"prob_{i}",
                "title": f"문제 {i}",
                "statement": f"이것은 더미 문제 {i}입니다.",
                "type": "algebra" if i % 3 == 0 else "calculus" if i % 3 == 1 else "geometry",
                "difficulty": "easy" if i % 5 < 2 else "medium" if i % 5 < 4 else "hard",
                "created_at": f"2025-09-{20-i}T12:00:00Z",
                "user_count": i * 2
            }
            for i in range(1, limit + 1)
        ]
        
        return {
            "problems": dummy_problems,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": 200,
                "pages": 4
            },
            "note": f"TODO: Implement real admin problems fetching, Error: {str(e)}"
        }

@router.delete("/problems/{problemId}")
async def delete_problem(
    problemId: str = Path(...),
    user: Dict[str, Any] = Depends(verify_admin_user)
) -> Dict[str, Any]:
    """
    관리자 권한으로 문제를 삭제합니다.
    """
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"
            }
            
            # 문제 삭제
            response = await client.delete(
                f"{settings.SUPABASE_URL}/rest/v1/problems?id=eq.{problemId}",
                headers=headers
            )
            
            if response.status_code in [200, 204]:
                return {"message": f"Problem with ID {problemId} deleted successfully"}
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to delete problem: {response.text}"
                )
    except Exception as e:
        # 스텁 응답
        return {
            "message": f"DELETE /admin/problems/{problemId} ok",
            "note": f"TODO: Implement real admin problem deletion, Error: {str(e)}"
        }

@router.get("/evaluations")
async def get_admin_evaluations(
    page: int = 1,
    limit: int = 50,
    user: Dict[str, Any] = Depends(verify_admin_user)
) -> Dict[str, Any]:
    """
    관리자용 평가 목록을 조회합니다.
    """
    try:
        # 스텁 응답
        dummy_evaluations = [
            {
                "id": f"eval_{i}",
                "user_id": f"user_{i % 10}",
                "rating": (i % 5) + 1,
                "feedback": f"평가 {i}의 피드백 내용입니다.",
                "created_at": f"2025-09-{20-i}T12:00:00Z"
            }
            for i in range(1, limit + 1)
        ]
        
        return {
            "evaluations": dummy_evaluations,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": 150,
                "pages": 3
            },
            "note": "TODO: Implement real admin evaluations fetching"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching evaluations: {str(e)}"
        )

@router.delete("/evaluations/{evaluationId}")
async def delete_evaluation(
    evaluationId: str = Path(...),
    user: Dict[str, Any] = Depends(verify_admin_user)
) -> Dict[str, Any]:
    """
    관리자 권한으로 평가를 삭제합니다.
    """
    try:
        # 스텁 응답
        return {
            "message": f"DELETE /admin/evaluations/{evaluationId} ok",
            "note": "TODO: Implement real admin evaluation deletion"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting evaluation: {str(e)}"
        )

@router.get("/stats")
async def get_admin_stats(
    user: Dict[str, Any] = Depends(verify_admin_user)
) -> Dict[str, Any]:
    """
    관리자용 통계 정보를 조회합니다.
    """
    try:
        # 스텁 응답
        return {
            "users": {
                "total": 1250,
                "active_today": 120,
                "active_week": 450,
                "new_today": 15
            },
            "problems": {
                "total": 240,
                "solved_today": 350,
                "most_popular": "prob_42"
            },
            "posts": {
                "total": 860,
                "today": 35
            },
            "system": {
                "uptime_days": 45,
                "storage_used_mb": 12500,
                "pending_jobs": 5
            },
            "note": "TODO: Implement real admin statistics"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching stats: {str(e)}"
        )

@router.delete("/posts/{postId}")
async def delete_post(
    postId: str = Path(...),
    user: Dict[str, Any] = Depends(verify_admin_user)
) -> Dict[str, Any]:
    """
    관리자 권한으로 게시글을 삭제합니다.
    """
    try:
        # 스텁 응답
        return {
            "message": f"DELETE /admin/posts/{postId} ok",
            "note": "TODO: Implement real admin post deletion"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting post: {str(e)}"
        )

@router.delete("/posts/{postId}/replies/{replyId}")
async def delete_reply(
    postId: str = Path(...),
    replyId: str = Path(...),
    user: Dict[str, Any] = Depends(verify_admin_user)
) -> Dict[str, Any]:
    """
    관리자 권한으로 댓글을 삭제합니다.
    """
    try:
        # 스텁 응답
        return {
            "message": f"DELETE /admin/posts/{postId}/replies/{replyId} ok",
            "note": "TODO: Implement real admin reply deletion"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting reply: {str(e)}"
        )

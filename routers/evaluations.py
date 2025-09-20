from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from pydantic import BaseModel
import httpx

from app.core.config import settings
from app.core.security import get_current_user

router = APIRouter()

class EvaluationRequest(BaseModel):
    rating: int
    feedback: str
    videoUrl: Optional[str] = None
    timestamp: Optional[str] = None

@router.post("")
async def create_evaluation(
    request: EvaluationRequest,
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    사용자 평가를 저장합니다.
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
            
            # 평가 데이터 저장
            evaluation_data = {
                "user_id": user_id,
                "rating": request.rating,
                "feedback": request.feedback,
                "video_url": request.videoUrl,
                "timestamp": request.timestamp or None
            }
            
            response = await client.post(
                f"{settings.SUPABASE_URL}/rest/v1/evaluations",
                headers=headers,
                json=evaluation_data
            )
            
            if response.status_code in [200, 201]:
                return {
                    "message": "Evaluation submitted successfully",
                    "evaluation_id": "eval_" + str(hash(str(evaluation_data)))[:8]
                }
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to submit evaluation: {response.text}"
                )
    except Exception as e:
        # 현재는 스텁 응답 반환
        return {
            "message": "POST /evaluations ok",
            "rating": request.rating,
            "feedback_length": len(request.feedback),
            "note": f"TODO: Implement real evaluation storage, Error: {str(e)}"
        }

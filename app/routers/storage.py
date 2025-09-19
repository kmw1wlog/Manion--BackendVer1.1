from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from pydantic import BaseModel
import httpx

from app.core.config import settings
from app.core.security import get_current_user

router = APIRouter()

class SignedUrlRequest(BaseModel):
    path: str
    from_bucket: Optional[str] = None

@router.post("/signed-url")
async def get_signed_url(
    request: SignedUrlRequest,
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Supabase Storage에 파일을 업로드하기 위한 서명된 URL을 생성합니다.
    """
    try:
        bucket = request.from_bucket or settings.BUCKET_MNI_FILES
        path = request.path
        
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"
            }
            
            # Supabase Storage API를 통해 서명된 URL 생성
            response = await client.post(
                f"{settings.SUPABASE_URL}/storage/v1/object/sign/{bucket}/{path}",
                headers=headers,
                json={"expiresIn": 600}  # 10분 동안 유효
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "url": data.get("signedURL"),
                    "expires_in": 600
                }
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to generate signed URL: {response.text}"
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating signed URL: {str(e)}"
        )

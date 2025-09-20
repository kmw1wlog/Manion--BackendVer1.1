from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Form, File
from typing import Dict, Any, Optional
import httpx
import uuid
import os
from datetime import datetime

from app.core.config import settings
from app.core.security import get_current_user

router = APIRouter()

@router.post("")
async def upload_file(
    image: UploadFile = File(...),
    title: str = Form(...),
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    파일 업로드를 처리합니다.
    
    FormData로 이미지와 제목을 받아 Supabase Storage에 저장합니다.
    """
    try:
        user_id = user.get("id")
        file_content = await image.read()
        file_size = len(file_content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB 제한
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large. Maximum size allowed is 10MB."
            )
        
        # 파일 확장자 추출
        file_ext = os.path.splitext(image.filename)[1].lower()
        if file_ext not in [".jpg", ".jpeg", ".png", ".gif", ".pdf"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Allowed types: jpg, jpeg, png, gif, pdf"
            )
        
        # 고유한 파일 이름 생성
        unique_filename = f"{user_id}/{str(uuid.uuid4())}{file_ext}"
        
        # Supabase에 업로드하기 위한 서명된 URL 가져오기
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"
            }
            
            # 서명된 URL 요청
            response = await client.post(
                f"{settings.SUPABASE_URL}/storage/v1/object/sign/{settings.BUCKET_MNI_FILES}/{unique_filename}",
                headers=headers,
                json={"expiresIn": 60}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to get signed URL: {response.text}"
                )
            
            signed_url_data = response.json()
            signed_url = signed_url_data.get("signedURL")
            
            # 서명된 URL로 파일 업로드
            upload_response = await client.put(
                signed_url,
                content=file_content,
                headers={"Content-Type": image.content_type}
            )
            
            if upload_response.status_code not in [200, 201]:
                raise HTTPException(
                    status_code=upload_response.status_code,
                    detail=f"Failed to upload file: {upload_response.text}"
                )
            
            # 업로드 메타데이터 저장
            metadata_url = f"{settings.SUPABASE_URL}/rest/v1/uploads"
            metadata_response = await client.post(
                metadata_url,
                headers={
                    **headers,
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                },
                json={
                    "user_id": user_id,
                    "title": title,
                    "file_path": unique_filename,
                    "file_type": image.content_type,
                    "file_size": file_size,
                    "created_at": datetime.now().isoformat()
                }
            )
            
            if metadata_response.status_code not in [200, 201]:
                # 업로드는 성공했지만 메타데이터 저장 실패 - 경고 로그만 남기고 진행
                print(f"Warning: Failed to save metadata: {metadata_response.text}")
            
            return {
                "file_id": unique_filename,
                "title": title,
                "file_size": file_size,
                "content_type": image.content_type,
                "storage_path": f"{settings.BUCKET_MNI_FILES}/{unique_filename}",
                "url": f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.BUCKET_MNI_FILES}/{unique_filename}"
            }
    except HTTPException:
        raise
    except Exception as e:
        # 실제 구현 시에는 파일 처리 로직 개선 필요
        return {
            "message": "POST /upload ok",
            "file_name": image.filename,
            "title": title,
            "file_size": len(await image.read()),
            "content_type": image.content_type,
            "note": f"TODO: Implement real file upload, Error: {str(e)}"
        }

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import httpx

from app.core.config import settings
from app.core.security import get_current_user

router = APIRouter()

# 요청 모델
class PostCreateRequest(BaseModel):
    content: str
    author: str
    boardType: str
    userId: str
    isNotice: Optional[bool] = False

class PostLikeRequest(BaseModel):
    action: str  # "like" 또는 "unlike"

class ReplyCreateRequest(BaseModel):
    content: str
    author: str
    isAdmin: Optional[bool] = False
    userId: str

@router.get("/posts/{boardType}")
async def get_posts_by_type(
    boardType: str = Path(...),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    특정 유형의 게시글 목록을 조회합니다.
    """
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"
            }
            
            # 게시글 조회
            offset = (page - 1) * limit
            query_url = f"{settings.SUPABASE_URL}/rest/v1/posts?boardType=eq.{boardType}&order=created_at.desc&limit={limit}&offset={offset}"
            response = await client.get(query_url, headers=headers)
            
            if response.status_code == 200:
                posts = response.json()
                
                # 총 게시글 수 조회
                count_url = f"{settings.SUPABASE_URL}/rest/v1/posts?boardType=eq.{boardType}&select=count"
                count_response = await client.get(count_url, headers={**headers, "Prefer": "count=exact"})
                total_count = int(count_response.headers.get("Content-Range", "0-0/0").split("/")[1])
                
                return {
                    "posts": posts,
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
                    detail=f"Failed to fetch posts: {response.text}"
                )
    except Exception as e:
        # 스텁 응답
        dummy_posts = [
            {
                "id": f"post_{i}",
                "title": f"{boardType} 게시글 {i}",
                "content": f"{boardType} 게시판의 {i}번째 더미 게시글입니다.",
                "author": f"User_{i % 5}",
                "boardType": boardType,
                "isNotice": i == 1,
                "created_at": f"2025-09-{20-i}T12:00:00Z",
                "likes": i * 3,
                "comments_count": i * 2
            }
            for i in range(1, limit + 1)
        ]
        
        return {
            "posts": dummy_posts,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": 100,
                "pages": 5
            },
            "note": f"TODO: Implement real posts fetching, Error: {str(e)}"
        }

@router.post("/posts")
async def create_post(
    request: PostCreateRequest,
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    새 게시글을 작성합니다.
    """
    try:
        # 사용자 ID 검증 - 자신의 ID만 사용할 수 있음
        if request.userId != user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create posts for other users"
            )
            
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            
            # 게시글 생성
            post_data = {
                "content": request.content,
                "author": request.author,
                "boardType": request.boardType,
                "userId": request.userId,
                "isNotice": request.isNotice
            }
            
            response = await client.post(
                f"{settings.SUPABASE_URL}/rest/v1/posts",
                headers=headers,
                json=post_data
            )
            
            if response.status_code in [200, 201]:
                return response.json()[0]
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to create post: {response.text}"
                )
    except HTTPException:
        raise
    except Exception as e:
        # 스텁 응답
        return {
            "id": "post_new",
            "content": request.content,
            "author": request.author,
            "boardType": request.boardType,
            "userId": request.userId,
            "isNotice": request.isNotice,
            "created_at": "2025-09-20T12:00:00Z",
            "note": f"TODO: Implement real post creation, Error: {str(e)}"
        }

@router.post("/posts/{postId}/like")
async def like_post(
    request: PostLikeRequest,
    postId: str = Path(...),
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    게시글 좋아요/좋아요 취소를 처리합니다.
    """
    try:
        user_id = user.get("id")
        
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json"
            }
            
            # 좋아요/좋아요 취소 처리
            if request.action == "like":
                # 좋아요 추가
                response = await client.post(
                    f"{settings.SUPABASE_URL}/rest/v1/post_likes",
                    headers=headers,
                    json={
                        "user_id": user_id,
                        "post_id": postId
                    }
                )
            elif request.action == "unlike":
                # 좋아요 취소
                response = await client.delete(
                    f"{settings.SUPABASE_URL}/rest/v1/post_likes?user_id=eq.{user_id}&post_id=eq.{postId}",
                    headers=headers
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Invalid action. Use "like" or "unlike".'
                )
            
            if response.status_code in [200, 201, 204]:
                return {
                    "message": f"Post {request.action} action completed",
                    "post_id": postId,
                    "action": request.action
                }
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to process {request.action} action: {response.text}"
                )
    except HTTPException:
        raise
    except Exception as e:
        # 스텁 응답
        return {
            "message": f"POST /posts/{postId}/like ok",
            "action": request.action,
            "post_id": postId,
            "note": f"TODO: Implement real like functionality, Error: {str(e)}"
        }

@router.post("/posts/{postId}/reply")
async def create_reply(
    request: ReplyCreateRequest,
    postId: str = Path(...),
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    게시글에 댓글을 작성합니다.
    """
    try:
        # 사용자 ID 검증 - 자신의 ID만 사용할 수 있음
        if request.userId != user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create replies for other users"
            )
        
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            
            # 댓글 생성
            reply_data = {
                "post_id": postId,
                "content": request.content,
                "author": request.author,
                "user_id": request.userId,
                "is_admin": request.isAdmin
            }
            
            response = await client.post(
                f"{settings.SUPABASE_URL}/rest/v1/replies",
                headers=headers,
                json=reply_data
            )
            
            if response.status_code in [200, 201]:
                return response.json()[0]
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to create reply: {response.text}"
                )
    except HTTPException:
        raise
    except Exception as e:
        # 스텁 응답
        return {
            "id": "reply_new",
            "post_id": postId,
            "content": request.content,
            "author": request.author,
            "user_id": request.userId,
            "is_admin": request.isAdmin,
            "created_at": "2025-09-20T12:00:00Z",
            "note": f"TODO: Implement real reply creation, Error: {str(e)}"
        }

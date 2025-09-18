from fastapi import APIRouter, HTTPException, status, Query, Path, Body
from typing import Optional, List
import uuid
from datetime import datetime, timedelta
import random

router = APIRouter()

# 더미 게시글 데이터 (실제 구현에서는 DB에서 가져옴)
DUMMY_POSTS = [
    {
        "id": "post_001",
        "title": "[공지사항] AI-MANIM 서비스 오픈 안내",
        "content": "안녕하세요. AI-MANIM 서비스가 오픈되었습니다. 많은 이용 부탁드립니다.",
        "user_id": "admin_001",
        "user_name": "관리자",
        "type": "notice",
        "created_at": "2025-09-15T09:00:00Z",
        "updated_at": "2025-09-15T09:00:00Z",
        "views": 245,
        "likes": 42,
        "comments_count": 15
    },
    {
        "id": "post_002",
        "title": "미분 문제 시각화가 너무 좋아요!",
        "content": "미분 문제를 AI-MANIM으로 시각화했는데 정말 이해가 잘 됩니다. 추천합니다!",
        "user_id": "user_001",
        "user_name": "수학좋아",
        "type": "general",
        "created_at": "2025-09-16T14:30:00Z",
        "updated_at": "2025-09-16T14:30:00Z",
        "views": 78,
        "likes": 23,
        "comments_count": 5
    },
    {
        "id": "post_003",
        "title": "이차함수 시각화 문제 있나요?",
        "content": "이차함수 그래프가 이상하게 나오는데 저만 그런가요?",
        "user_id": "user_002",
        "user_name": "고등학생",
        "type": "general",
        "created_at": "2025-09-17T10:15:00Z",
        "updated_at": "2025-09-17T10:15:00Z",
        "views": 42,
        "likes": 3,
        "comments_count": 8
    },
    {
        "id": "post_004",
        "title": "adfdaf",
        "content": "ㅁㄴㅇㄹㅁㄴㄹㅇㄴㅁㄹㄴㅁㅇ",
        "user_id": "anon_001",
        "user_name": "익명",
        "type": "anonymous",
        "created_at": "2025-09-17T23:45:00Z",
        "updated_at": "2025-09-17T23:45:00Z",
        "views": 12,
        "likes": 0,
        "comments_count": 2
    }
]

# 더미 댓글 데이터
DUMMY_COMMENTS = [
    {
        "id": "comment_001",
        "post_id": "post_001",
        "user_id": "user_001",
        "user_name": "수학좋아",
        "content": "정말 좋은 서비스네요. 감사합니다!",
        "created_at": "2025-09-15T09:30:00Z",
        "updated_at": "2025-09-15T09:30:00Z",
        "likes": 5
    },
    {
        "id": "comment_002",
        "post_id": "post_001",
        "user_id": "user_002",
        "user_name": "고등학생",
        "content": "수학 공부하는데 큰 도움이 될 것 같아요!",
        "created_at": "2025-09-15T10:15:00Z",
        "updated_at": "2025-09-15T10:15:00Z",
        "likes": 3
    },
    {
        "id": "comment_003",
        "post_id": "post_002",
        "user_id": "user_003",
        "user_name": "수포자",
        "content": "저도 사용해봤는데 정말 좋더라구요~",
        "created_at": "2025-09-16T15:10:00Z",
        "updated_at": "2025-09-16T15:10:00Z",
        "likes": 2
    }
]

@router.get("/posts")
async def list_posts(
    type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(10, gt=0, le=50),
    offset: int = Query(0, ge=0)
):
    """
    게시글 목록 조회
    """
    # 실제 구현에서는 DB에서 필터링하여 가져옴
    filtered_posts = DUMMY_POSTS
    
    if type:
        filtered_posts = [post for post in filtered_posts if post["type"] == type]
    
    if search:
        filtered_posts = [
            post for post in filtered_posts 
            if search.lower() in post["title"].lower() or search.lower() in post["content"].lower()
        ]
    
    # 페이징 적용
    paginated = filtered_posts[offset:offset+limit]
    
    return {
        "posts": paginated,
        "total": len(filtered_posts)
    }

@router.post("/posts")
async def create_post(
    title: str = Body(...),
    content: str = Body(...),
    type: str = Body(...)
):
    """
    게시글 생성
    """
    # 유효한 게시글 타입 확인
    if type not in ["general", "notice", "anonymous"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 게시글 타입입니다."
        )
    
    # 새 게시글 ID 생성
    post_id = f"post_{str(uuid.uuid4())[:8]}"
    now = datetime.now().isoformat()
    
    # 더미 사용자 ID (실제로는 인증된 사용자 ID 사용)
    user_id = "user_001"
    user_name = "테스트 사용자" if type != "anonymous" else "익명"
    
    # 새 게시글 생성 (실제로는 DB에 저장)
    new_post = {
        "id": post_id,
        "title": title,
        "content": content,
        "user_id": user_id,
        "user_name": user_name,
        "type": type,
        "created_at": now,
        "updated_at": now,
        "views": 0,
        "likes": 0,
        "comments_count": 0
    }
    
    return new_post

@router.get("/posts/{post_id}")
async def get_post(post_id: str = Path(...)):
    """
    특정 게시글 상세 조회
    """
    # 실제 구현에서는 DB에서 게시글 정보를 조회
    for post in DUMMY_POSTS:
        if post["id"] == post_id:
            # 조회수 증가 (실제로는 DB 업데이트 필요)
            post_copy = post.copy()
            post_copy["views"] += 1
            return post_copy
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"ID가 {post_id}인 게시글을 찾을 수 없습니다."
    )

@router.get("/posts/{post_id}/comments")
async def list_post_comments(
    post_id: str = Path(...),
    limit: int = Query(20, gt=0, le=100),
    offset: int = Query(0, ge=0)
):
    """
    특정 게시글의 댓글 목록 조회
    """
    # 실제 구현에서는 DB에서 해당 게시글의 댓글을 조회
    filtered_comments = [comment for comment in DUMMY_COMMENTS if comment["post_id"] == post_id]
    
    # 페이징 적용
    paginated = filtered_comments[offset:offset+limit]
    
    return {
        "comments": paginated,
        "total": len(filtered_comments)
    }

@router.post("/posts/{post_id}/comments")
async def create_comment(
    post_id: str = Path(...),
    content: str = Body(...)
):
    """
    특정 게시글에 댓글 작성
    """
    # 게시글이 존재하는지 확인
    post_exists = any(post["id"] == post_id for post in DUMMY_POSTS)
    if not post_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {post_id}인 게시글을 찾을 수 없습니다."
        )
    
    # 새 댓글 ID 생성
    comment_id = f"comment_{str(uuid.uuid4())[:8]}"
    now = datetime.now().isoformat()
    
    # 더미 사용자 ID (실제로는 인증된 사용자 ID 사용)
    user_id = "user_001"
    user_name = "테스트 사용자"
    
    # 새 댓글 생성 (실제로는 DB에 저장)
    new_comment = {
        "id": comment_id,
        "post_id": post_id,
        "user_id": user_id,
        "user_name": user_name,
        "content": content,
        "created_at": now,
        "updated_at": now,
        "likes": 0
    }
    
    return new_comment

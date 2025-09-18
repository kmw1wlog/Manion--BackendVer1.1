from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any

router = APIRouter()

# 실제 구현에서는 인증 로직이 들어가야 하지만, MVP에서는 더미 데이터 사용
@router.post("/login")
async def login():
    """
    더미 로그인 엔드포인트
    """
    return {
        "access_token": "dummy_token_12345",
        "token_type": "bearer",
        "user": {
            "id": "user_001",
            "name": "테스트 사용자",
            "email": "test@example.com",
            "avatar_url": "https://i.pravatar.cc/150?img=1"
        }
    }

@router.get("/google/authorize")
async def google_authorize():
    """
    구글 OAuth 인증 시작
    """
    # 실제 구현에서는 구글 OAuth 인증 URL로 리디렉션
    return {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?dummy_param=value"
    }

@router.get("/google/callback")
async def google_callback(code: str = None, error: str = None):
    """
    구글 OAuth 콜백 처리
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth 인증 오류: {error}"
        )
    
    # 실제 구현에서는 코드를 토큰으로 교환하고 사용자 정보를 가져옴
    return {
        "access_token": "dummy_google_token_12345",
        "token_type": "bearer",
        "user": {
            "id": "google_user_001",
            "name": "구글 사용자",
            "email": "google@example.com",
            "avatar_url": "https://i.pravatar.cc/150?img=2"
        }
    }

@router.get("/kakao/authorize")
async def kakao_authorize():
    """
    카카오 OAuth 인증 시작
    """
    # 실제 구현에서는 카카오 OAuth 인증 URL로 리디렉션
    return {
        "auth_url": "https://kauth.kakao.com/oauth/authorize?dummy_param=value"
    }

@router.get("/kakao/callback")
async def kakao_callback(code: str = None, error: str = None):
    """
    카카오 OAuth 콜백 처리
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth 인증 오류: {error}"
        )
    
    # 실제 구현에서는 코드를 토큰으로 교환하고 사용자 정보를 가져옴
    return {
        "access_token": "dummy_kakao_token_12345",
        "token_type": "bearer",
        "user": {
            "id": "kakao_user_001",
            "name": "카카오 사용자",
            "email": "kakao@example.com",
            "avatar_url": "https://i.pravatar.cc/150?img=3"
        }
    }

@router.get("/me")
async def get_current_user():
    """
    현재 로그인한 사용자 정보 반환
    """
    # 실제 구현에서는 토큰으로부터 사용자 정보를 가져옴
    return {
        "id": "user_001",
        "name": "테스트 사용자",
        "email": "test@example.com",
        "avatar_url": "https://i.pravatar.cc/150?img=1",
        "role": "user"
    }

@router.post("/logout")
async def logout():
    """
    로그아웃 처리
    """
    return {"message": "로그아웃 성공"}

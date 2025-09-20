from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import httpx
from pydantic import BaseModel, EmailStr

from app.core.config import settings
from app.core.security import get_current_user

router = APIRouter()
http_bearer = HTTPBearer()

# 요청 모델
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class SigninRequest(BaseModel):
    email: EmailStr
    password: str

class OAuthTokenRequest(BaseModel):
    token: str

# 응답 모델
class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

@router.post("/signup")
async def signup(request: SignupRequest) -> Dict[str, Any]:
    """
    사용자 회원가입 처리
    """
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            }
            
            # Supabase Auth API에 회원가입 요청
            response = await client.post(
                f"{settings.SUPABASE_URL}/auth/v1/signup",
                json={
                    "email": request.email,
                    "password": request.password,
                    "data": {"name": request.name}
                },
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "access_token": data.get("access_token"),
                    "token_type": "bearer",
                    "user": data.get("user", {})
                }
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Signup failed: {response.text}"
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup error: {str(e)}"
        )

@router.post("/signin")
async def signin(request: SigninRequest) -> Dict[str, Any]:
    """
    사용자 로그인 처리
    """
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            }
            
            # Supabase Auth API에 로그인 요청
            response = await client.post(
                f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password",
                json={
                    "email": request.email,
                    "password": request.password,
                },
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "access_token": data.get("access_token"),
                    "token_type": "bearer",
                    "user": data.get("user", {})
                }
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Login failed: {response.text}"
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )

@router.post("/google")
async def google_auth(request: OAuthTokenRequest) -> Dict[str, Any]:
    """
    구글 OAuth 인증 처리
    """
    try:
        # 실제 구현에서는 Google OAuth 토큰으로 Supabase 인증
        # 현재는 Supabase가 OAuth 처리를 담당
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            }
            
            # TODO: 실제 구현 완료 필요
            # Google ID 토큰을 Supabase로 전달하여 인증
            # 현재는 더미 데이터 반환
            return {
                "message": "Google OAuth 처리 구현 예정",
                "client_id": settings.GOOGLE_CLIENT_ID
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google OAuth 처리 중 오류 발생: {str(e)}"
        )

@router.post("/kakao")
async def kakao_auth(request: OAuthTokenRequest) -> Dict[str, Any]:
    """
    카카오 OAuth 인증 처리
    """
    try:
        # 실제 구현에서는 Kakao OAuth 토큰으로 Supabase 인증
        # 현재는 Supabase가 OAuth 처리를 담당
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            }
            
            # TODO: 실제 구현 완료 필요
            # Kakao 액세스 토큰을 Supabase로 전달하여 인증
            # 현재는 더미 데이터 반환
            return {
                "message": "Kakao OAuth 처리 구현 예정",
                "client_id": settings.KAKAO_CLIENT_ID
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kakao OAuth 처리 중 오류 발생: {str(e)}"
        )

@router.get("/me")
async def get_me(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    현재 로그인한 사용자 정보 반환
    """
    return user

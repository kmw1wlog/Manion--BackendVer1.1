from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime, timedelta
import logging
import secrets
import hashlib

from app.core.config import settings
from app.core.security import (
    get_current_user, 
    get_optional_user, 
    create_access_token,
    verify_token
)
from app.schemas.auth import (
    Token, 
    UserAuth, 
    UserCreate, 
    UserResponse,
    AuthResponse
)

logger = logging.getLogger("api")
router = APIRouter()
http_bearer = HTTPBearer(auto_error=False)

# 임시 사용자 스토리지 (실제 구현에서는 데이터베이스 사용)
USERS_DB = {
    "test@example.com": {
        "id": "user_001",
        "email": "test@example.com",
        "name": "테스트 사용자",
        "password": hashlib.sha256("password123".encode()).hexdigest(),  # 실제로는 더 안전한 해싱 사용
        "role": "user"
    },
    "admin@example.com": {
        "id": "admin_001",
        "email": "admin@example.com",
        "name": "관리자",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin"
    }
}

# FastAPI OAuth2 형식의 로그인 엔드포인트
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 호환 토큰 로그인 (JWT)
    """
    # 사용자 검증 (실제로는 데이터베이스에서 조회)
    user = USERS_DB.get(form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일을 확인해주세요.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 비밀번호 검증
    hashed_password = hashlib.sha256(form_data.password.encode()).hexdigest()
    if hashed_password != user["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비밀번호를 확인해주세요.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 액세스 토큰 생성
    extra_data = {
        "email": user["email"],
        "name": user["name"],
        "role": user["role"]
    }
    access_token = create_access_token(
        subject=user["id"],
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_data=extra_data
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/signup")
async def signup(request: UserCreate) -> AuthResponse:
    """
    1. 로컬 회원가입: JWT 토큰 사용
    2. Supabase 회원가입: 동시 지원
    """
    # 기존 사용자 확인
    if request.email in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )
    
    # 1. 로컬 사용자 생성
    user_id = f"user_{secrets.token_hex(4)}"
    hashed_password = hashlib.sha256(request.password.encode()).hexdigest()
    
    new_user = {
        "id": user_id,
        "email": request.email,
        "name": request.name,
        "password": hashed_password,
        "role": "user"
    }
    
    USERS_DB[request.email] = new_user
    
    # 토큰 생성
    extra_data = {
        "email": new_user["email"],
        "name": new_user["name"],
        "role": new_user["role"]
    }
    access_token = create_access_token(
        subject=user_id,
        extra_data=extra_data
    )
    
    try:
        # 2. Supabase 회원가입 시도 (선택 사항)
        if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
            async with httpx.AsyncClient() as client:
                headers = {
                    "apikey": settings.SUPABASE_ANON_KEY,
                    "Content-Type": "application/json"
                }
                
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
                    logger.info(f"Supabase 회원가입 성공: {request.email}")
                else:
                    logger.warning(f"Supabase 회원가입 실패: {response.text}")
    except Exception as e:
        logger.error(f"Supabase 회원가입 오류: {str(e)}")
        
    # 로컬 인증 결과 반환 (Supabase 실패해도 로컬은 성공)
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": new_user["id"],
            "email": new_user["email"],
            "name": new_user["name"],
            "role": new_user["role"]
        }
    )

@router.post("/signin")
async def signin(request: UserAuth) -> AuthResponse:
    """
    사용자 로그인 처리 (로컬 + Supabase)
    """
    # 1. 로컬 인증 시도
    user = USERS_DB.get(request.email)
    
    if user:
        hashed_password = hashlib.sha256(request.password.encode()).hexdigest()
        if hashed_password == user["password"]:
            # 로컬 인증 성공
            extra_data = {
                "email": user["email"],
                "name": user["name"],
                "role": user["role"]
            }
            access_token = create_access_token(
                subject=user["id"],
                extra_data=extra_data
            )
            
            return AuthResponse(
                access_token=access_token,
                token_type="bearer",
                user={
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "role": user["role"]
                }
            )
    
    # 2. Supabase 인증 시도
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            }
            
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
                return AuthResponse(
                    access_token=data.get("access_token"),
                    token_type="bearer",
                    user=data.get("user", {})
                )
            else:
                # 모든 인증 실패
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="이메일 또는 비밀번호를 확인해주세요."
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 오류: {str(e)}"
        )

# OAuth 관련 엔드포인트
@router.get("/google/authorize")
async def google_authorize():
    """
    구글 OAuth 인증 시작 URL 생성
    """
    google_client_id = settings.GOOGLE_CLIENT_ID
    redirect_uri = f"{settings.RAILWAY_BACKEND_URL or 'http://localhost:8000'}/api/auth/google/callback"
    
    # OAuth 2.0 파라미터 구성
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": google_client_id,
        "response_type": "code",
        "scope": "email profile",
        "redirect_uri": redirect_uri,
        "access_type": "offline",
        "prompt": "consent"
    }
    
    # URL 생성 (실제 구현에서는 urlencode 사용)
    param_str = "&".join([f"{k}={v}" for k, v in params.items()])
    final_url = f"{auth_url}?{param_str}"
    
    return {"auth_url": final_url}

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
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="인증 코드가 없습니다."
        )
    
    try:
        # 코드를 토큰으로 교환
        google_client_id = settings.GOOGLE_CLIENT_ID
        google_client_secret = settings.GOOGLE_CLIENT_SECRET
        redirect_uri = f"{settings.RAILWAY_BACKEND_URL or 'http://localhost:8000'}/api/auth/google/callback"
        
        async with httpx.AsyncClient() as client:
            # 1. 액세스 토큰 요청
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": google_client_id,
                    "client_secret": google_client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"토큰 교환 실패: {token_response.text}"
                )
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            # 2. 사용자 정보 요청
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"사용자 정보 요청 실패: {user_response.text}"
                )
            
            user_info = user_response.json()
            
            # 3. 로컬 토큰 생성
            google_user_id = f"google_{user_info.get('id')}"
            extra_data = {
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
                "provider": "google"
            }
            
            # 사용자가 없으면 자동 등록
            if not any(u.get("id") == google_user_id for u in USERS_DB.values()):
                USERS_DB[user_info.get("email")] = {
                    "id": google_user_id,
                    "email": user_info.get("email"),
                    "name": user_info.get("name"),
                    "password": secrets.token_hex(16),  # 랜덤 비밀번호
                    "role": "user"
                }
            
            jwt_token = create_access_token(
                subject=google_user_id,
                extra_data=extra_data
            )
            
            return {
                "access_token": jwt_token,
                "token_type": "bearer",
                "user": {
                    "id": google_user_id,
                    "email": user_info.get("email"),
                    "name": user_info.get("name"),
                    "avatar_url": user_info.get("picture")
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth 처리 오류: {str(e)}"
        )

@router.get("/kakao/authorize")
async def kakao_authorize():
    """
    카카오 OAuth 인증 시작 URL 생성
    """
    kakao_client_id = settings.KAKAO_CLIENT_ID
    redirect_uri = f"{settings.RAILWAY_BACKEND_URL or 'http://localhost:8000'}/api/auth/kakao/callback"
    
    # OAuth 2.0 파라미터 구성
    auth_url = "https://kauth.kakao.com/oauth/authorize"
    params = {
        "client_id": kakao_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code"
    }
    
    # URL 생성
    param_str = "&".join([f"{k}={v}" for k, v in params.items()])
    final_url = f"{auth_url}?{param_str}"
    
    return {"auth_url": final_url}

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
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="인증 코드가 없습니다."
        )
    
    try:
        # 코드를 토큰으로 교환
        kakao_client_id = settings.KAKAO_CLIENT_ID
        kakao_client_secret = settings.KAKAO_CLIENT_SECRET
        redirect_uri = f"{settings.RAILWAY_BACKEND_URL or 'http://localhost:8000'}/api/auth/kakao/callback"
        
        async with httpx.AsyncClient() as client:
            # 1. 액세스 토큰 요청
            token_response = await client.post(
                "https://kauth.kakao.com/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": kakao_client_id,
                    "client_secret": kakao_client_secret,
                    "redirect_uri": redirect_uri,
                    "code": code
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"토큰 교환 실패: {token_response.text}"
                )
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            # 2. 사용자 정보 요청
            user_response = await client.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"사용자 정보 요청 실패: {user_response.text}"
                )
            
            user_info = user_response.json()
            kakao_account = user_info.get("kakao_account", {})
            profile = kakao_account.get("profile", {})
            
            # 3. 로컬 토큰 생성
            kakao_user_id = f"kakao_{user_info.get('id')}"
            email = kakao_account.get("email", f"{kakao_user_id}@kakao.user")
            name = profile.get("nickname", "카카오 사용자")
            picture = profile.get("profile_image_url")
            
            extra_data = {
                "email": email,
                "name": name,
                "picture": picture,
                "provider": "kakao"
            }
            
            # 사용자가 없으면 자동 등록
            if not any(u.get("id") == kakao_user_id for u in USERS_DB.values()):
                USERS_DB[email] = {
                    "id": kakao_user_id,
                    "email": email,
                    "name": name,
                    "password": secrets.token_hex(16),  # 랜덤 비밀번호
                    "role": "user"
                }
            
            jwt_token = create_access_token(
                subject=kakao_user_id,
                extra_data=extra_data
            )
            
            return {
                "access_token": jwt_token,
                "token_type": "bearer",
                "user": {
                    "id": kakao_user_id,
                    "email": email,
                    "name": name,
                    "avatar_url": picture
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth 처리 오류: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_me(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    현재 로그인한 사용자 정보 반환
    """
    return UserResponse(
        id=user.get("id", ""),
        email=user.get("email", ""),
        name=user.get("name"),
        avatar_url=user.get("avatar_url"),
        role=user.get("role", "user")
    )

@router.post("/logout")
async def logout(response: Response):
    """
    로그아웃 처리 (클라이언트측에서 토큰 제거)
    """
    return {"message": "로그아웃 성공"}

@router.post("/validate-token")
async def validate_token(
    token: str = Body(..., embed=True)
) -> Dict[str, Any]:
    """
    토큰 유효성 검증
    """
    try:
        payload = await verify_token(token)
        return {
            "valid": True,
            "payload": payload
        }
    except HTTPException:
        return {
            "valid": False,
            "payload": None
        }

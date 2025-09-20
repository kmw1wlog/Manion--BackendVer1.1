from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union, List

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.auth import TokenPayload, UserResponse

# 인증 스킴 정의
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token", auto_error=False)
http_bearer = HTTPBearer(auto_error=False)

# JWT 관련 함수
def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None, extra_data: Dict = None) -> str:
    """
    JWT 액세스 토큰을 생성합니다.
    
    Args:
        subject: 토큰의 주체 (보통 사용자 ID)
        expires_delta: 만료 시간
        extra_data: 토큰에 추가할 데이터
        
    Returns:
        str: 인코딩된 JWT 토큰
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # 추가 데이터 병합
    if extra_data:
        to_encode.update(extra_data)
        
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# 로컬 JWT 토큰 검증 함수 추가
async def verify_token(token: str) -> Dict[str, Any]:
    """
    JWT 토큰을 검증하고 페이로드를 반환합니다.
    
    Args:
        token: JWT 토큰
        
    Returns:
        Dict[str, Any]: 토큰 페이로드
    """
    try:
        # JWT 토큰 디코딩
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        # 토큰 만료 확인
        if datetime.utcnow() > datetime.fromtimestamp(token_data.exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return payload
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_from_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    로컬 JWT 토큰으로부터 사용자 정보를 얻습니다.
    
    Args:
        token: JWT 토큰
        
    Returns:
        Dict[str, Any]: 사용자 정보
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        # 토큰 검증
        payload = await verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token payload"
            )
        
        # 사용자 ID로 데이터베이스 조회 (현재는 임시 구현)
        # TODO: 실제 데이터베이스 조회로 변경
        user_data = {
            "id": user_id,
            "email": payload.get("email", f"{user_id}@example.com"),
            "name": payload.get("name", "사용자"),
            "role": payload.get("role", "user"),
        }
        return user_data
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Supabase 인증 함수
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    request: Request = None
) -> Dict[str, Any]:
    """
    두 가지 방법으로 인증을 시도합니다:
    1. HTTP Bearer 토큰 사용 (Authorization 헤더)
    2. 쿠키의 access_token 사용
    
    Args:
        credentials: HTTP Authorization 헤더 내용
        request: 요청 객체
        
    Returns:
        Dict[str, Any]: 사용자 정보
        
    Raises:
        HTTPException: 인증에 실패한 경우
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # 1. 먼저 로컬 JWT 토큰 검증 시도
    try:
        payload = await verify_token(token)
        user_id = payload.get("sub")
        if user_id:
            # 로컬 JWT 토큰으로 성공
            return {
                "id": user_id,
                "email": payload.get("email", f"{user_id}@example.com"),
                "name": payload.get("name", "사용자"),
                "role": payload.get("role", "user"),
                "auth_type": "local_jwt"
            }
    except HTTPException:
        # 로컬 토큰 검증 실패 시 Supabase 검증 시도
        pass
    
    # 2. Supabase 토큰 검증 시도
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": settings.SUPABASE_ANON_KEY
            }
            response = await client.get(f"{settings.SUPABASE_URL}/auth/v1/user", headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Supabase token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user_data = response.json()
            user_data["auth_type"] = "supabase"
            return user_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    request: Request = None
) -> Optional[Dict[str, Any]]:
    """
    토큰이 제공된 경우 사용자 정보를 반환하고, 그렇지 않으면 None을 반환합니다.
    
    Args:
        credentials: HTTP Authorization 헤더 내용 (선택 사항)
        request: 요청 객체
        
    Returns:
        Optional[Dict[str, Any]]: 사용자 정보 또는 None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials=credentials, request=request)
    except HTTPException:
        return None

async def verify_admin_user(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    관리자 권한을 확인합니다.
    
    Args:
        user: 현재 사용자 정보
    
    Returns:
        Dict[str, Any]: 관리자 사용자 정보
        
    Raises:
        HTTPException: 관리자가 아닌 경우
    """
    # Supabase 및 로컬 JWT 모두 지원
    is_admin = user.get("is_admin", False)
    
    # 로컬 JWT의 경우 role 필드 확인
    if user.get("auth_type") == "local_jwt" and user.get("role") == "admin":
        is_admin = True
        
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다",
        )
    return user

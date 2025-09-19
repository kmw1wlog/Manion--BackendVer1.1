from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx

from app.core.config import settings

# OAuth2 Bearer 인증 스킴
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/signin")
http_bearer = HTTPBearer()

# JWT 관련 함수
def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    JWT 액세스 토큰을 생성합니다.
    
    Args:
        subject: 토큰의 주체 (보통 사용자 ID)
        expires_delta: 만료 시간
        
    Returns:
        str: 인코딩된 JWT 토큰
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)) -> Dict[str, Any]:
    """
    Supabase 토큰을 검증하고 현재 사용자 정보를 반환합니다.
    
    Args:
        credentials: HTTP Authorization 헤더 내용
    
    Returns:
        Dict[str, Any]: 사용자 정보
        
    Raises:
        HTTPException: 인증에 실패한 경우
    """
    token = credentials.credentials
    
    # Supabase Auth API를 통해 토큰 검증
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        response = await client.get(f"{settings.SUPABASE_URL}/auth/v1/user", headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_data = response.json()
        return user_data
    
async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer)) -> Optional[Dict[str, Any]]:
    """
    토큰이 제공된 경우 사용자 정보를 반환하고, 그렇지 않으면 None을 반환합니다.
    
    Args:
        credentials: HTTP Authorization 헤더 내용 (선택 사항)
    
    Returns:
        Optional[Dict[str, Any]]: 사용자 정보 또는 None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
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
    # TODO: Supabase의 실제 권한 필드에 따라 조정
    if not user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return user

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from functools import lru_cache


class Settings(BaseSettings):
    # API 설정
    API_VERSION: str = "v1"
    DEBUG: bool = False
    API_HOST: str = "0.0.0.0"
    API_PORT: int = int(os.environ.get("PORT", 8000))
    
    # Supabase 연결 정보
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # 외부 서비스 URL
    RAILWAY_BACKEND_URL: Optional[str] = None
    NETLIFY_SITE_URL: Optional[str] = None
    
    # OAuth 인증 설정
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    KAKAO_CLIENT_ID: str
    KAKAO_CLIENT_SECRET: str
    
    # JWT 설정
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS 설정
    FRONTEND_ORIGINS: str
    
    # Storage
    BUCKET_MNI_FILES: str = "mni-files"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        return self.FRONTEND_ORIGINS.split(',')
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
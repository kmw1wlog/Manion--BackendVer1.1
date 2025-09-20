import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException
from fastapi.responses import JSONResponse
import time
import logging
import json

# 라우터들을 임포트
from app.routers import (
    diag, auth, manim, storage, problem, user,
    upload, evaluations, community, admin
)
# API 모듈에서 jobs 라우터 임포트
from app.api import jobs
from app.core.config import settings

# 로거 설정
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("api")

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="AI-MANIM API",
    description="AI-MANIM 백엔드 API - 수학 문제 시각화 서비스",
    version="0.1.0",
    docs_url="/docs",  # 원래 "/api/docs"였으나 접근 문제로 변경
    redoc_url="/redoc", # 원래 "/api/redoc"였으나 접근 문제로 변경
    openapi_url="/openapi.json", # 원래 "/api/openapi.json"였으나 접근 문제로 변경
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로깅 미들웨어
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # 요청 로깅
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # 응답 처리
    response = await call_next(request)
    
    # 처리 시간 계산
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} (took {process_time:.2f}s)")
    
    # 응답 헤더에 처리 시간 추가
    response.headers["X-Process-Time"] = str(process_time)
    return response

# 전역 에러 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP exception: {exc.detail} ({exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )

# 기본 엔드포인트
@app.get("/")
async def root():
    """
    API 루트 엔드포인트
    """
    return {
        "name": "AI-MANIM API",
        "version": "0.1.0",
        "status": "active"
    }

# API 라우터 등록
app.include_router(diag.router, prefix="/api", tags=["Diagnostics"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(manim.router, prefix="/api/manim", tags=["Manim"])
app.include_router(storage.router, prefix="/api/storage", tags=["Storage"])
app.include_router(problem.router, prefix="/api/problem", tags=["Problems"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(evaluations.router, prefix="/api/evaluations", tags=["Evaluations"])
app.include_router(community.router, prefix="/api/community", tags=["Community"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])

# 직접 라우트 추가 (프록시 전송 문제 방지)
@app.get("/api/health")
async def health_check():
    """
    시스템 상태 확인을 위한 헬스체크 엔드포인트
    """
    return {"status": "ok"}

@app.get("/api/me")
async def get_me_direct():
    """
    현재 사용자 정보를 반환하는 엔드포인트 (auth.get_me로 리디렉션)
    """
    from app.routers.auth import get_me
    return await get_me()

# 앱 시작 이벤트
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting AI-MANIM API on port {settings.API_PORT}")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    logger.info(f"CORS origins: {settings.CORS_ORIGINS}")

# 앱 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AI-MANIM API")

# 직접 실행 시 서버 시작
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
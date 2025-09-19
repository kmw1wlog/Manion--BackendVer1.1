import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api import health, auth, uploads, jobs, community

# 환경 변수에서 PORT 가져오기 (Railway는 PORT 환경변수를 8080으로 설정)
port = int(os.environ.get("PORT", 8000))

app = FastAPI(
    title="AI-MANIM API",
    description="AI-MANIM 백엔드 API - 수학 문제 시각화 서비스",
    version="0.1.0",
    # 리디렉션 동작 비활성화
    redirect_slashes=False
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포에서는 프론트엔드 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기본 엔드포인트
@app.get("/")
async def root():
    return {
        "ok": True,
        "route": "/",
        "port": port,  # 현재 사용 중인 포트 반환
        "environment": os.environ.get("ENVIRONMENT", "development")
    }

# Railway 헬스체크를 위한 직접 라우트 추가
@app.get("/api/health")
async def direct_health_check():
    return {
        "status": "healthy",
        "timestamp": os.environ.get("RAILWAY_HEALTHCHECK_TIME", "unknown"),
        "version": "0.1.0"
    }

# API 라우터들 추가
app.include_router(health.router, prefix="/api/health", tags=["상태"])
app.include_router(auth.router, prefix="/api/auth", tags=["인증"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["업로드"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["작업"])
app.include_router(community.router, prefix="/api/community", tags=["커뮤니티"])

# 미들웨어 추가 - 로깅
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # 요청 경로 로깅
    path = request.url.path
    print(f"Request path: {path}")
    
    # 다음 미들웨어 또는 라우트 핸들러 호출
    response = await call_next(request)
    
    # 응답 상태 로깅
    print(f"Response status: {response.status_code}")
    
    return response

# 앱 시작 이벤트
@app.on_event("startup")
async def startup_event():
    # 초기화 작업 (DB 연결 등)
    print(f"AI-MANIM API 서버 시작 (포트: {port})")
    # 환경 변수 출력
    for key, value in os.environ.items():
        if key.startswith(("PORT", "RAILWAY", "ENVIRONMENT")):
            print(f"ENV: {key}={value}")

# 앱 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    # 종료 작업 (리소스 정리 등)
    print("AI-MANIM API 서버 종료")

# 직접 실행할 경우 uvicorn 서버 시작
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
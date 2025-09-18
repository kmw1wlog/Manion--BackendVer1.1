import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, auth, uploads, jobs, community

# 환경 변수에서 PORT 가져오기
port = int(os.environ.get("PORT", 8000))

app = FastAPI(
    title="AI-MANIM API",
    description="AI-MANIM 백엔드 API - 수학 문제 시각화 서비스",
    version="0.1.0"
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
        "port": port  # 현재 사용 중인 포트 반환
    }

# API 라우터들 추가
app.include_router(health.router, prefix="/api/health", tags=["상태"])
app.include_router(auth.router, prefix="/api/auth", tags=["인증"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["업로드"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["작업"])
app.include_router(community.router, prefix="/api/community", tags=["커뮤니티"])

# 앱 시작 이벤트
@app.on_event("startup")
async def startup_event():
    # 초기화 작업 (DB 연결 등)
    print(f"AI-MANIM API 서버 시작 (포트: {port})")

# 앱 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    # 종료 작업 (리소스 정리 등)
    print("AI-MANIM API 서버 종료")

# 직접 실행할 경우 uvicorn 서버 시작
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
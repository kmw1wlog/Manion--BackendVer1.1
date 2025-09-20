# 백엔드 테스트 가이드

이 디렉토리에는 FastAPI 백엔드 테스트를 위한 여러 스크립트가 포함되어 있습니다.

## 테스트 파일 목록

- **smoke.http**: HTTP 요청 파일 (VS Code REST Client 또는 IntelliJ HTTP Client로 실행)
- **smoke.sh**: 자동화된 API 테스트를 위한 쉘 스크립트
- **token-check.py**: Supabase 액세스 토큰의 유효성을 검증하는 Python 스크립트

## 테스트 실행 순서

### 1. 로컬 FastAPI 앱 테스트
```bash
# FastAPI 앱 실행
uvicorn app.main:app --reload --port 8000

# 다른 터미널에서 테스트 스크립트 실행
bash tests/smoke.sh local
```

### 2. Railway 배포 테스트
```bash
# 배포된 앱 테스트
bash tests/smoke.sh remote
```

### 3. Supabase 토큰 검증
```bash
# Supabase 액세스 토큰으로 검증
python tests/token-check.py <SUPABASE_ACCESS_TOKEN>

# 검증된 토큰으로 API 테스트
bash tests/smoke.sh local <SUPABASE_ACCESS_TOKEN>
bash tests/smoke.sh remote <SUPABASE_ACCESS_TOKEN>
```

### 4. 프론트엔드 프록시 테스트
프론트엔드 개발 서버(Vite)를 실행하고 `/api/*` 요청이 FastAPI 백엔드로 정상 프록시되는지 확인:
```bash
# 프론트엔드 레포지토리에서
npm run dev
```
브라우저에서 `http://localhost:3000`으로 접속하여 API 요청 테스트

### 5. Netlify 배포 테스트
배포된 Netlify 사이트에서 Railway 백엔드로의 요청이 CORS 없이 정상 작동하는지 확인합니다.

## 환경 변수 설정
테스트에 필요한 환경 변수는 `.env` 파일에 설정해야 합니다:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
SECRET_KEY=your-secret-key
FRONTEND_ORIGINS=http://localhost:3000,https://your-site.netlify.app
```

## 주의사항
- 토큰 테스트 시 실제 유효한 Supabase 액세스 토큰이 필요합니다.
- 프론트엔드 연동 테스트를 위해서는 Supabase 프로젝트 설정에서 적절한 CORS 오리진이 설정되어 있어야 합니다.


# AI-MANIM 백엔드 API

AI-MANIM은 수학 문제의 풀이 과정을 시각화해주는 서비스입니다. 이 저장소는 AI-MANIM의 백엔드 API를 제공합니다.

## 프로젝트 개요

AI-MANIM은 다음과 같은 기능을 제공합니다:

1. 수학 문제 이미지나 텍스트 입력
2. 문제의 구조화 및 분석
3. 검증된 풀이 과정 생성
4. 시각화 영상 제작 (Manim 기반)
5. 커뮤니티 공유

## API 엔드포인트

프론트엔드에서 사용하는 주요 엔드포인트는 다음과 같습니다:

### 인증
- `POST /api/auth/signup` - 회원가입
- `POST /api/auth/signin` - 로그인
- `POST /api/auth/google` - 구글 OAuth 인증
- `POST /api/auth/kakao` - 카카오 OAuth 인증

### 사용자/이력
- `GET /api/user/history` - 사용자 이력 목록
- `DELETE /api/user/history/problem/{problemId}` - 이력 내 문제 삭제
- `PUT /api/user/history/problem/{problemId}/title` - 제목 수정

### 문제
- `GET /api/problem/{problemId}` - 문제 상세

### 업로드
- `POST /api/upload` - 파일 업로드(이미지)

### 평가
- `POST /api/evaluations` - 평가 저장

### 커뮤니티
- `GET /api/community/posts/{boardType}` - 게시글 목록(일반/익명 등)
- `POST /api/community/posts` - 글 작성
- `POST /api/community/posts/{postId}/like` - 좋아요/취소
- `POST /api/community/posts/{postId}/reply` - 댓글 작성

### 관리자
- `GET /api/admin/problems` - 문제 관리 목록
- `DELETE /api/admin/problems/{problemId}` - 문제 삭제
- `GET /api/admin/evaluations` - 평가 목록
- `DELETE /api/admin/evaluations/{evaluationId}` - 평가 삭제
- `GET /api/admin/stats` - 통계 조회
- `DELETE /api/admin/posts/{postId}` - 게시글 삭제
- `DELETE /api/admin/posts/{postId}/replies/{replyId}` - 댓글 삭제

## 로컬 개발 환경 설정

### 필수 조건

- Python 3.11 이상
- pip

### 설치 및 실행

1. 저장소 복제
```bash
git clone https://github.com/kmw1wlog/Manion--BackendVer1.1.git
cd Manion--BackendVer1.1
```

2. 가상 환경 생성 및 활성화
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
```bash
cp env.example .env
# .env 파일을 편집하여 필요한 설정 추가
```

5. 개발 서버 실행
```bash
uvicorn app.main:app --reload --port 8080
```

서버가 `http://localhost:8080`에서 실행됩니다.

## 배포

### Railway 배포

1. Railway CLI 설치 및 로그인
2. 프로젝트 초기화
```bash
railway init
```

3. 프로젝트 배포
```bash
railway up
```

## 환경 변수

주요 환경 변수:

- `SUPABASE_URL`: Supabase 프로젝트 URL
- `SUPABASE_ANON_KEY`: Supabase 공개 키
- `SUPABASE_SERVICE_KEY`: Supabase 서비스 키 (비밀)
- `GOOGLE_CLIENT_ID`: Google OAuth 클라이언트 ID
- `KAKAO_CLIENT_ID`: Kakao OAuth 클라이언트 ID
- `FRONTEND_ORIGINS`: CORS 허용할 프론트엔드 도메인 (콤마로 구분)

## API 문서

API 문서는 다음 URL에서 확인할 수 있습니다:

- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`

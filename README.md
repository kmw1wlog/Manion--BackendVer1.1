# AI-MANIM 백엔드 API

AI-MANIM은 수학 문제의 풀이 과정을 시각화해주는 서비스입니다. 이 저장소는 AI-MANIM의 백엔드 API를 포함하고 있습니다.

## 프로젝트 개요

AI-MANIM은 다음과 같은 기능을 제공합니다:

1. 수학 문제 이미지나 텍스트 입력
2. 문제의 구조화 및 분석
3. 검증된 풀이 과정 생성
4. 시각화 영상 제작 (Manim 기반)
5. 커뮤니티 공유

## 기술 스택

- **백엔드**: FastAPI, Python 3.11
- **인증**: Supabase (구글/카카오 OAuth)
- **저장소**: Supabase PostgreSQL
- **배포**: Railway (백엔드), Netlify (프론트엔드)

## 시작하기

### 필수 조건

- Python 3.8 이상
- pip

### 로컬 개발 환경 설정

1. 저장소 복제
```bash
git clone https://github.com/your-username/ai-manim-backend.git
cd ai-manim-backend
```

2. 가상 환경 생성 및 활성화
```bash
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
```bash
# Linux/macOS
cp env.example .env
# Windows
copy env.example .env

# .env 파일을 편집하여 필요한 설정 추가
```

5. 서버 실행
```bash
# Linux/macOS
./run.sh

# Windows
run.bat
```

서버가 `http://localhost:8000`에서 실행됩니다.

## API 엔드포인트

### 기본 엔드포인트
- `GET /`: API 상태 및 버전 정보
- `GET /api/health`: 헬스체크

### 인증
- `POST /api/auth/login`: 로그인
- `GET /api/auth/google/authorize`: 구글 OAuth 인증 시작
- `GET /api/auth/google/callback`: 구글 OAuth 콜백
- `GET /api/auth/kakao/authorize`: 카카오 OAuth 인증 시작
- `GET /api/auth/kakao/callback`: 카카오 OAuth 콜백
- `GET /api/auth/me`: 현재 사용자 정보
- `POST /api/auth/logout`: 로그아웃

### 파일 업로드
- `POST /api/uploads/sign`: 업로드 URL 서명
- `POST /api/uploads/direct`: 직접 파일 업로드
- `GET /api/uploads/files/{file_id}`: 업로드된 파일 정보 조회

### 작업 관리
- `GET /api/jobs`: 작업 목록 조회
- `POST /api/jobs`: 새 작업 생성
- `GET /api/jobs/{job_id}`: 특정 작업 상세 조회
- `GET /api/jobs/{job_id}/video`: 작업 결과 영상 URL 조회
- `GET /api/jobs/{job_id}/mni`: 작업의 .mni 파일 내용 조회

### 커뮤니티
- `GET /api/community/posts`: 게시글 목록 조회
- `POST /api/community/posts`: 게시글 생성
- `GET /api/community/posts/{post_id}`: 특정 게시글 상세 조회
- `GET /api/community/posts/{post_id}/comments`: 특정 게시글의 댓글 목록 조회
- `POST /api/community/posts/{post_id}/comments`: 특정 게시글에 댓글 작성

## 배포

### Railway 배포
Railway.app을 통해 쉽게 배포할 수 있습니다:

1. Railway CLI 설치 및 로그인
2. 프로젝트 설정
```bash
railway init
```

3. 프로젝트 배포
```bash
railway up
```

## .mni 파일 형식

AI-MANIM은 `.mni` 파일 형식을 사용하여 문제, 풀이 과정, 시각화 정보를 저장합니다. 예시:

```json
{
  "schema_version": "1.0",
  "problem": {
    "id": "QF001",
    "statement": "함수 y = x^2 - 4x + 3의 꼭짓점을 구하라",
    "metadata": { "subject": "수학", "unit": "이차함수", "difficulty": "중간" }
  },
  "proof_tape": [
    {"step":1,"rule":"complete_square","expr_in":"x^2-4x+3","expr_out":"(x-2)^2-1"},
    {"step":2,"rule":"vertex","expr_in":"(x-2)^2-1","expr_out":"(2,-1)"}
  ],
  "visual": {
    "type": "ManimScene",
    "sections": [
      {
        "section_name": "Graph",
        "steps": [
          { "action": "CreateAxes", "x_range": [-2,6], "y_range": [-2,10] },
          { "action": "PlotFunction", "function": "x**2 - 4*x + 3" },
          { "action": "HighlightPoint", "point": [2, -1], "color": "yellow" }
        ]
      }
    ]
  },
  "verification": {
    "sympy": { "code":"...", "status":"pass", "artifacts":["vx=2","vy=-1"] }
  }
}
```

## 라이선스

이 프로젝트는 MIT 라이선스로 제공됩니다.

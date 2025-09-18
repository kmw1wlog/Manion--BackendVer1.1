@echo off

REM 필요한 디렉토리 생성
if not exist uploads mkdir uploads

REM 가상환경이 없는 경우 생성
if not exist venv (
  echo 가상환경을 생성합니다...
  python -m venv venv
)

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM 의존성 설치
echo 의존성을 설치합니다...
pip install -r requirements.txt

REM 서버 시작
echo FastAPI 서버를 시작합니다...
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

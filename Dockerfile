FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# start.sh에 실행 권한 부여를 위한 셸 스크립트 추가
COPY start.sh /app/
RUN chmod +x /app/start.sh

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 기본 포트 설정 (Railway에서 덮어씌워짐)
ENV PORT=8000

# 컨테이너 시작 시 실행할 명령
CMD ["/bin/bash", "/app/start.sh"]
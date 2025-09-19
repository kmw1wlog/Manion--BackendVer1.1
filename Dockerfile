FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# start.sh에 실행 권한 부여를 위한 셸 스크립트 추가
COPY start.sh /app/
# CRLF -> LF 변환 및 실행 권한 부여
RUN dos2unix /app/start.sh && \
    chmod +x /app/start.sh

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .
# 모든 sh 파일에 CRLF -> LF 변환
RUN find . -type f -name "*.sh" -exec dos2unix {} \;

# 기본 포트 설정 (Railway에서 덮어씌워짐)
ENV PORT=8000

# 컨테이너 시작 시 실행할 명령
CMD ["/bin/bash", "/app/start.sh"]
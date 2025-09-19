FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# 실행 스크립트 복사 및 권한 설정
COPY start.sh /app/
RUN dos2unix /app/start.sh && \
    chmod +x /app/start.sh

# 의존성 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 쉘 스크립트 줄 바꿈 문자 변환
RUN find . -name "*.sh" -exec dos2unix {} \;

# 환경 변수 설정
ENV PORT=8080
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1

# 실행 명령
CMD ["bash", "start.sh"]
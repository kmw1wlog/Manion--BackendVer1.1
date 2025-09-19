#!/bin/bash
# 이 스크립트는 줄 바꿈 문자(line endings)를 Unix 형식(LF)으로 변환합니다

# start.sh 파일의 줄 바꿈 문자를 변환
cat > start.sh << 'EOF'
#!/bin/bash

# 기본값 설정
export PORT="${PORT:-8000}"
export ENVIRONMENT="${ENVIRONMENT:-production}"
export RAILWAY_HEALTHCHECK_TIME="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

echo "Starting server on port $PORT"
echo "Environment: $ENVIRONMENT"
echo "Railway healthcheck time: $RAILWAY_HEALTHCHECK_TIME"

# FastAPI 애플리케이션 실행
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --no-access-log
EOF

echo "start.sh 파일의 줄 바꿈 문자가 Unix 형식(LF)으로 변환되었습니다."

# 필요한 경우 실행 권한 부여
chmod +x start.sh
echo "start.sh 파일에 실행 권한이 부여되었습니다."

echo "완료!"

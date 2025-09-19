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
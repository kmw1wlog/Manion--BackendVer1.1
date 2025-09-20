#!/bin/bash

# 오류 발생 시 스크립트 종료
set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 기본 변수 설정
MODE=${1:-"local"}
TOKEN=${2:-""}

if [ "$MODE" = "local" ]; then
  BASE_URL="http://localhost:8000"
  echo -e "${YELLOW}로컬 환경 테스트 시작 ($BASE_URL)${NC}"
else
  BASE_URL="https://manion-backendver11-production.up.railway.app"
  echo -e "${YELLOW}원격 환경 테스트 시작 ($BASE_URL)${NC}"
fi

echo "-------------------------------------"

# 헬스체크 테스트
echo -e "${YELLOW}헬스체크 테스트...${NC}"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/health")

if [ "$HEALTH_RESPONSE" = "200" ]; then
  echo -e "${GREEN}✓ 헬스체크 성공 (200)${NC}"
else
  echo -e "${RED}✗ 헬스체크 실패 ($HEALTH_RESPONSE)${NC}"
  exit 1
fi

# 인증 없는 /api/me 요청 (401 기대)
echo -e "${YELLOW}인증 없는 /api/me 테스트...${NC}"
NO_AUTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/me")

if [ "$NO_AUTH_RESPONSE" = "401" ]; then
  echo -e "${GREEN}✓ 인증 없는 /api/me 테스트 성공 (401)${NC}"
else
  echo -e "${RED}✗ 인증 없는 /api/me 테스트 실패 ($NO_AUTH_RESPONSE)${NC}"
  exit 1
fi

# 토큰이 제공된 경우 인증된 /api/me 요청
if [ -n "$TOKEN" ]; then
  echo -e "${YELLOW}인증된 /api/me 테스트...${NC}"
  AUTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/me")
  
  if [ "$AUTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ 인증된 /api/me 테스트 성공 (200)${NC}"
  else
    echo -e "${RED}✗ 인증된 /api/me 테스트 실패 ($AUTH_RESPONSE)${NC}"
    exit 1
  fi
fi

# Storage signed-url 요청 (토큰 있는 경우에만)
if [ -n "$TOKEN" ]; then
  echo -e "${YELLOW}스토리지 서명된 URL 테스트...${NC}"
  STORAGE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"path": "test/sample-image.jpg", "from_bucket": "mni-files"}' \
    "$BASE_URL/api/storage/signed-url")
  
  if [ "$STORAGE_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ 스토리지 서명된 URL 테스트 성공 (200)${NC}"
  elif [ "$STORAGE_RESPONSE" = "400" ]; then
    echo -e "${YELLOW}⚠ 스토리지 서명된 URL 테스트: 파라미터 문제 (400)${NC}"
  else
    echo -e "${RED}✗ 스토리지 서명된 URL 테스트 실패 ($STORAGE_RESPONSE)${NC}"
    exit 1
  fi
fi

# Jobs API 테스트
echo -e "${YELLOW}작업 목록 테스트...${NC}"
JOBS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/jobs")

if [ "$JOBS_RESPONSE" = "200" ]; then
  echo -e "${GREEN}✓ 작업 목록 테스트 성공 (200)${NC}"
else
  echo -e "${RED}✗ 작업 목록 테스트 실패 ($JOBS_RESPONSE)${NC}"
  exit 1
fi

echo "-------------------------------------"
echo -e "${GREEN}모든 테스트 성공!${NC}"


#!/usr/bin/env python3
import sys
import os
import requests
import json

# 색상 정의
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[0;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def check_token(token, supabase_url=None):
    """
    Supabase 액세스 토큰의 유효성을 체크합니다.
    
    Args:
        token (str): 체크할 Supabase 액세스 토큰
        supabase_url (str, optional): Supabase URL. 환경변수나 기본값에서 가져옵니다.
    
    Returns:
        bool: 토큰이 유효하면 True, 그렇지 않으면 False
    """
    # Supabase URL 결정
    if not supabase_url:
        supabase_url = os.environ.get('SUPABASE_URL')
        
    if not supabase_url:
        supabase_url = "https://pzyjcfkhdnczbfcpxjqb.supabase.co"  # 사용자가 제공한 Supabase URL
    
    # API 요청 헤더
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Supabase Auth API로 사용자 정보 요청
    url = f"{supabase_url}/auth/v1/user"
    print(f"{BLUE}Supabase 서버에 사용자 정보 요청 중...{NC}")
    print(f"{BLUE}URL: {url}{NC}")
    
    try:
        response = requests.get(url, headers=headers)
        status_code = response.status_code
        
        if status_code == 200:
            user_data = response.json()
            print(f"{GREEN}✓ 토큰 유효함 (200){NC}")
            print(f"{GREEN}✓ 사용자 ID: {user_data.get('id')}{NC}")
            print(f"{GREEN}✓ 이메일: {user_data.get('email')}{NC}")
            return True
        else:
            print(f"{RED}✗ 토큰 유효하지 않음 ({status_code}){NC}")
            print(f"{RED}✗ 응답: {response.text}{NC}")
            return False
    except Exception as e:
        print(f"{RED}✗ 오류 발생: {str(e)}{NC}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"{YELLOW}사용법: python token-check.py <SUPABASE_ACCESS_TOKEN> [SUPABASE_URL]{NC}")
        print(f"{YELLOW}예시: python token-check.py eyJhbGciOiJIUzI1NiIsInR5c... https://fycrkqrhrxcarllthqfl.supabase.co{NC}")
        sys.exit(1)
        
    token = sys.argv[1]
    supabase_url = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"{YELLOW}Supabase 토큰 검증 시작...{NC}")
    result = check_token(token, supabase_url)
    
    if result:
        print(f"{GREEN}토큰이 유효합니다. 백엔드에서 이 토큰으로 인증 가능합니다.{NC}")
        sys.exit(0)
    else:
        print(f"{RED}토큰이 유효하지 않습니다. 새로운 토큰을 발급받아야 합니다.{NC}")
        sys.exit(1)


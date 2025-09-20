from fastapi import APIRouter, HTTPException, status, Depends
import httpx
from typing import Dict, Any
from datetime import datetime
import json

from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    시스템 상태 확인을 위한 헬스체크 엔드포인트
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }

@router.get("/diag/supabase")
async def diagnose_supabase() -> Dict[str, Any]:
    """
    Supabase 연결 상태를 진단하는 엔드포인트
    """
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "count=exact"
            }
            
            # 간단한 쿼리로 Supabase 연결 테스트
            query_url = f"{settings.SUPABASE_URL}/rest/v1/rpc/test_connection"
            payload = json.dumps({})
            
            # TODO: 실제 테이블이나 함수로 변경 필요
            response = await client.post(
                query_url, 
                headers=headers, 
                content=payload,
                timeout=10.0
            )
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "message": "Successfully connected to Supabase",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to connect: {response.status_code}",
                    "details": response.text,
                    "timestamp": datetime.now().isoformat()
                }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Exception occurred: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

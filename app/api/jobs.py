from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
import uuid
from datetime import datetime, timedelta
import json
import random

router = APIRouter()

# 더미 작업 데이터 (실제 구현에서는 DB에서 가져옴)
DUMMY_JOBS = [
    {
        "id": "job_001",
        "status": "completed",
        "problem_image_url": "https://storage.ai-manim.example/uploads/img1.jpg",
        "video_url": "https://storage.ai-manim.example/videos/job_001.mp4",
        "mni_file_id": "mni_001",
        "created_at": "2025-09-18T09:30:00Z",
        "updated_at": "2025-09-18T09:35:00Z",
        "error_message": None,
        "metadata": {
            "problem": "함수 y = x^2 - 4x + 3의 꼭짓점을 구하라",
            "subject": "수학",
            "duration_sec": 42
        }
    },
    {
        "id": "job_002",
        "status": "completed",
        "problem_image_url": "https://storage.ai-manim.example/uploads/img2.jpg",
        "video_url": "https://storage.ai-manim.example/videos/job_002.mp4",
        "mni_file_id": "mni_002",
        "created_at": "2025-09-17T14:20:00Z",
        "updated_at": "2025-09-17T14:26:00Z",
        "error_message": None,
        "metadata": {
            "problem": "x^2 + y^2 = 16의 그래프를 그리고 넓이를 구하라",
            "subject": "수학",
            "duration_sec": 38
        }
    },
    {
        "id": "job_003",
        "status": "processing",
        "problem_image_url": "https://storage.ai-manim.example/uploads/img3.jpg",
        "video_url": None,
        "mni_file_id": None,
        "created_at": "2025-09-18T10:15:00Z",
        "updated_at": "2025-09-18T10:15:00Z",
        "error_message": None,
        "metadata": {
            "problem": "적분 ∫sin(x)dx의 과정을 보여주세요",
            "subject": "수학",
        }
    },
    {
        "id": "job_004",
        "status": "failed",
        "problem_image_url": "https://storage.ai-manim.example/uploads/img4.jpg",
        "video_url": None,
        "mni_file_id": None,
        "created_at": "2025-09-16T08:45:00Z",
        "updated_at": "2025-09-16T08:50:00Z",
        "error_message": "문제 이미지를 인식할 수 없습니다. 다른 이미지를 업로드해 주세요.",
        "metadata": {
            "attempt": 1
        }
    }
]

@router.get("/")
async def list_jobs(
    status: Optional[str] = None, 
    limit: int = Query(10, gt=0, le=100),
    offset: int = Query(0, ge=0)
):
    """
    작업 목록 조회
    """
    # 실제 구현에서는 DB에서 필터링하여 가져옴
    filtered_jobs = DUMMY_JOBS
    if status:
        filtered_jobs = [job for job in DUMMY_JOBS if job["status"] == status]
    
    # 페이징 적용
    paginated = filtered_jobs[offset:offset+limit]
    
    return {
        "jobs": paginated,
        "total": len(filtered_jobs)
    }

@router.post("/")
async def create_job(problem_image_url: Optional[str] = None, problem_text: Optional[str] = None):
    """
    새 작업 생성
    """
    if not problem_image_url and not problem_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="문제 이미지 URL이나 문제 텍스트 중 하나는 제공해야 합니다."
        )
    
    # 새 작업 ID 생성
    job_id = f"job_{str(uuid.uuid4())[:8]}"
    now = datetime.now().isoformat()
    
    # 더미 작업 생성 (실제로는 DB에 저장)
    new_job = {
        "id": job_id,
        "status": "pending",
        "problem_image_url": problem_image_url,
        "video_url": None,
        "mni_file_id": None,
        "created_at": now,
        "updated_at": now,
        "error_message": None,
        "metadata": {
            "problem_text": problem_text
        }
    }
    
    # 실제로는 이 시점에서 백그라운드 작업을 큐에 등록
    
    return new_job

@router.get("/{job_id}")
async def get_job(job_id: str):
    """
    특정 작업 상세 조회
    """
    # 실제 구현에서는 DB에서 작업 정보를 조회
    for job in DUMMY_JOBS:
        if job["id"] == job_id:
            return job
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"ID가 {job_id}인 작업을 찾을 수 없습니다."
    )

@router.get("/{job_id}/video")
async def get_job_video(job_id: str):
    """
    작업 결과 영상 URL 조회
    """
    # 실제 구현에서는 DB에서 작업 정보를 조회하고 영상 URL 반환
    for job in DUMMY_JOBS:
        if job["id"] == job_id:
            if job["status"] != "completed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="작업이 아직 완료되지 않았습니다."
                )
            
            if not job["video_url"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="영상이 존재하지 않습니다."
                )
                
            return {
                "video_url": job["video_url"],
                "duration_sec": job["metadata"].get("duration_sec", 30)
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"ID가 {job_id}인 작업을 찾을 수 없습니다."
    )

@router.get("/{job_id}/mni")
async def get_job_mni(job_id: str):
    """
    작업의 .mni 파일 내용 조회
    """
    # 실제 구현에서는 DB에서 작업 정보를 조회하고 .mni 파일 내용 반환
    for job in DUMMY_JOBS:
        if job["id"] == job_id:
            if job["status"] != "completed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="작업이 아직 완료되지 않았습니다."
                )
            
            # 더미 .mni 파일 내용 (실제로는 DB나 스토리지에서 가져와야 함)
            return {
                "schema_version": "1.0",
                "problem": {
                    "id": "QF001",
                    "statement": "함수 y = x^2 - 4x + 3의 꼭짓점을 구하라",
                    "metadata": { "subject": "수학", "unit": "이차함수", "difficulty": "중간", "time_estimate_min": 3 }
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
                    "sympy": { "code":"import sympy as sp\nx = sp.Symbol('x')\nf = x**2 - 4*x + 3\nf_expanded = sp.expand(f)\na = f_expanded.coeff(x, 2)\nb = f_expanded.coeff(x, 1)\nc = f_expanded.coeff(x, 0)\nvx = -b/(2*a)\nvy = f.subs(x, vx)\nprint(f'Vertex: ({vx}, {vy})')", "status":"pass", "artifacts":["vx=2","vy=-1"] }
                },
                "build": {
                    "options": { "fps": 30, "resolution": "1400x800", "theme":"dark" },
                    "hash_key": "QF001:9b7c...:v1",
                    "created_at": "2025-09-18T10:45:00Z"
                }
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"ID가 {job_id}인 작업을 찾을 수 없습니다."
    )
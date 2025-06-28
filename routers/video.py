from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from models.video import Video, VideoAnalysis, VideoAnalysisRequest, VideoRecommendation, VideoUploadRequest
from services.video_service import video_service

router = APIRouter(prefix="/videos", tags=["영상 관리"])

@router.post("/upload", response_model=Video, summary="영상 업로드")
async def upload_video(
    file: UploadFile = File(..., description="업로드할 영상 파일"),
    title: str = Form(..., description="영상 제목"),
    description: Optional[str] = Form(None, description="영상 설명"),
    sport_type: Optional[str] = Form(None, description="스포츠 종목"),
    match_date: Optional[datetime] = Form(None, description="경기 날짜"),
    teams: Optional[str] = Form(None, description="팀 정보 (쉼표로 구분)")
):
    """
    영상을 업로드하고 처리합니다.
    
    - **file**: 업로드할 영상 파일 (mp4, avi, mov, mkv, webm 지원)
    - **title**: 영상 제목
    - **description**: 영상 설명 (선택사항)
    - **sport_type**: 스포츠 종목 (선택사항)
    - **match_date**: 경기 날짜 (선택사항)
    - **teams**: 팀 정보, 쉼표로 구분 (선택사항)
    """
    
    # 팀 정보 파싱
    team_list = None
    if teams:
        team_list = [team.strip() for team in teams.split(",") if team.strip()]
    
    try:
        video = await video_service.upload_video(
            file=file,
            title=title,
            description=description,
            sport_type=sport_type,
            match_date=match_date,
            teams=team_list
        )
        return video
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Video], summary="영상 목록 조회")
async def list_videos(
    sport_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """
    영상 목록을 조회합니다. 필터링 파라미터가 없으면 전체 영상 목록을, 
    있으면 조건에 맞는 영상들만 반환합니다. 각 영상의 분석 결과도 함께 포함됩니다.
    
    - **sport_type**: 스포츠 종목으로 필터링 (선택사항)
    - **status**: 상태로 필터링 (선택사항) - uploading, processing, completed, failed
    - **limit**: 조회할 영상 개수 (기본값: 20)
    - **offset**: 건너뛸 영상 개수 (기본값: 0)
    
    예시:
    - 전체 목록: GET /videos/
    - 축구 영상만: GET /videos/?sport_type=soccer
    - 완료된 영상만: GET /videos/?status=completed
    - 축구 완료 영상: GET /videos/?sport_type=soccer&status=completed
    """
    videos = await video_service.get_video_history(limit=limit, offset=offset)
    
    # 필터링 적용
    if sport_type:
        videos = [v for v in videos if v.sport_type == sport_type]
    
    if status:
        videos = [v for v in videos if v.status.value == status]
    
    # 각 영상의 분석 결과를 포함하여 반환
    # Video 모델의 analyses 필드가 이미 포함되어 있으므로 그대로 반환
    return videos

@router.get("/{video_id}", response_model=Video, summary="영상 상세 정보 조회")
async def get_video(video_id: str):
    """
    특정 영상의 상세 정보를 조회합니다.
    
    - **video_id**: 조회할 영상의 ID
    """
    video = await video_service.get_video_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다.")
    return video

@router.post("/{video_id}/analyze", response_model=VideoAnalysis, summary="영상 분석 실행")
async def analyze_video(
    video_id: str,
    analysis_request: VideoAnalysisRequest
):
    """
    영상에 대한 AI 분석을 실행합니다.
    
    - **video_id**: 분석할 영상의 ID
    - **analysis_request**: 분석 요청 정보
    """
    try:
        analysis = await video_service.analyze_video(video_id, analysis_request)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{video_id}/analyses", response_model=List[VideoAnalysis], summary="영상 분석 결과 조회")
async def get_video_analyses(video_id: str):
    """
    영상의 모든 분석 결과를 조회합니다.
    
    - **video_id**: 조회할 영상의 ID
    """
    try:
        analyses = await video_service.get_video_analyses(video_id)
        return analyses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{video_id}/recommendations", response_model=List[VideoRecommendation], summary="관련 영상 추천")
async def get_video_recommendations(
    video_id: str,
    limit: int = 5
):
    """
    현재 영상과 관련된 다른 영상들을 추천합니다.
    
    - **video_id**: 기준이 될 영상의 ID
    - **limit**: 추천할 영상 개수 (기본값: 5)
    """
    try:
        recommendations = await video_service.get_video_recommendations(video_id, limit=limit)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{video_id}", summary="영상 삭제")
async def delete_video(video_id: str):
    """
    영상을 삭제합니다.
    
    - **video_id**: 삭제할 영상의 ID
    """
    try:
        success = await video_service.delete_video(video_id)
        if success:
            return {"message": "영상이 성공적으로 삭제되었습니다."}
        else:
            raise HTTPException(status_code=500, detail="영상 삭제에 실패했습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
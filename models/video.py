from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class VideoStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoAnalysis(BaseModel):
    id: str
    video_id: str
    analysis_type: str  # "goal_detection", "player_tracking", "tactical_analysis"
    result_data: dict
    confidence_score: float
    created_at: datetime

class Video(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    file_path: str
    file_size: int  # bytes
    duration: Optional[float] = None  # seconds
    status: VideoStatus
    sport_type: Optional[str] = None  # "soccer", "basketball", "baseball", etc.
    match_date: Optional[datetime] = None
    teams: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    analyses: Optional[List[VideoAnalysis]] = []

class VideoUploadRequest(BaseModel):
    title: str
    description: Optional[str] = None
    sport_type: Optional[str] = None
    match_date: Optional[datetime] = None
    teams: Optional[List[str]] = None

class VideoAnalysisRequest(BaseModel):
    analysis_type: str
    parameters: Optional[dict] = None

class VideoRecommendation(BaseModel):
    video_id: str
    title: str
    similarity_score: float
    reason: str 
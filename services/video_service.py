import os
import uuid
import shutil
from datetime import datetime
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from models.video import Video, VideoStatus, VideoAnalysis, VideoAnalysisRequest, VideoRecommendation

class VideoService:
    def __init__(self):
        self.upload_dir = "uploads"
        self.videos_db = {}  # 실제로는 데이터베이스를 사용해야 함
        self.analyses_db = {}
        
        # 업로드 디렉토리 생성
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def upload_video(self, file: UploadFile, title: str, description: str = None, 
                          sport_type: str = None, match_date: datetime = None, teams: List[str] = None) -> Video:
        """영상 업로드 및 저장"""
        
        # 파일 확장자 검증
        allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다.")
        
        # 파일 크기 검증 (100MB 제한)
        if file.size > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="파일 크기는 100MB를 초과할 수 없습니다.")
        
        # 고유 ID 생성
        video_id = str(uuid.uuid4())
        file_path = os.path.join(self.upload_dir, f"{video_id}{file_extension}")
        
        # 파일 저장
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"파일 저장 중 오류가 발생했습니다: {str(e)}")
        
        # 비디오 객체 생성
        video = Video(
            id=video_id,
            title=title,
            description=description,
            file_path=file_path,
            file_size=file.size,
            status=VideoStatus.UPLOADING,
            sport_type=sport_type,
            match_date=match_date,
            teams=teams,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # DB에 저장 (실제로는 데이터베이스에 저장)
        self.videos_db[video_id] = video
        
        # 비동기로 영상 처리 시작
        await self._process_video(video_id)
        
        return video
    
    async def _process_video(self, video_id: str):
        """영상 처리 (메타데이터 추출, 인덱싱 등)"""
        video = self.videos_db.get(video_id)
        if not video:
            return
        
        try:
            # 상태를 처리 중으로 변경
            video.status = VideoStatus.PROCESSING
            video.updated_at = datetime.now()
            
            # 여기서 실제 영상 처리 로직을 구현
            # - 영상 길이 추출
            # - 썸네일 생성
            # - 메타데이터 분석
            # - AI 모델을 통한 초기 분석 등
            
            # 임시로 3초 후 완료 처리
            import asyncio
            await asyncio.sleep(3)
            
            video.status = VideoStatus.COMPLETED
            video.updated_at = datetime.now()
            
        except Exception as e:
            video.status = VideoStatus.FAILED
            video.updated_at = datetime.now()
            print(f"영상 처리 중 오류: {str(e)}")
    
    async def get_video_history(self, limit: int = 20, offset: int = 0) -> List[Video]:
        """영상 히스토리 조회"""
        videos = list(self.videos_db.values())
        videos.sort(key=lambda x: x.created_at, reverse=True)
        return videos[offset:offset + limit]
    
    async def get_video_by_id(self, video_id: str) -> Optional[Video]:
        """ID로 영상 조회"""
        return self.videos_db.get(video_id)
    
    async def analyze_video(self, video_id: str, analysis_request: VideoAnalysisRequest) -> VideoAnalysis:
        """영상 분석 실행"""
        video = await self.get_video_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다.")
        
        if video.status != VideoStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="영상 처리가 완료되지 않았습니다.")
        
        # 분석 ID 생성
        analysis_id = str(uuid.uuid4())
        
        # 실제 분석 로직 구현
        # 여기서는 임시 결과를 반환
        result_data = {
            "analysis_type": analysis_request.analysis_type,
            "parameters": analysis_request.parameters or {},
            "results": {
                "detected_events": [],
                "statistics": {},
                "highlights": []
            }
        }
        
        analysis = VideoAnalysis(
            id=analysis_id,
            video_id=video_id,
            analysis_type=analysis_request.analysis_type,
            result_data=result_data,
            confidence_score=0.85,  # 임시 값
            created_at=datetime.now()
        )
        
        # DB에 저장
        self.analyses_db[analysis_id] = analysis
        
        # 비디오에 분석 결과 추가
        if not video.analyses:
            video.analyses = []
        video.analyses.append(analysis)
        
        return analysis
    
    async def get_video_analyses(self, video_id: str) -> List[VideoAnalysis]:
        """영상의 분석 결과 조회"""
        video = await self.get_video_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다.")
        
        return video.analyses or []
    
    async def get_video_recommendations(self, video_id: str, limit: int = 5) -> List[VideoRecommendation]:
        """관련 영상 추천"""
        current_video = await self.get_video_by_id(video_id)
        if not current_video:
            raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다.")
        
        recommendations = []
        
        # 간단한 추천 로직 (실제로는 더 복잡한 알고리즘 사용)
        for video in self.videos_db.values():
            if video.id == video_id:
                continue
            
            similarity_score = 0.0
            reason = ""
            
            # 같은 스포츠 타입
            if current_video.sport_type and video.sport_type == current_video.sport_type:
                similarity_score += 0.3
                reason += "같은 스포츠 종목, "
            
            # 같은 팀
            if current_video.teams and video.teams:
                common_teams = set(current_video.teams) & set(video.teams)
                if common_teams:
                    similarity_score += 0.4
                    reason += f"공통 팀: {', '.join(common_teams)}, "
            
            # 비슷한 날짜
            if current_video.match_date and video.match_date:
                date_diff = abs((current_video.match_date - video.match_date).days)
                if date_diff <= 30:
                    similarity_score += 0.2
                    reason += "비슷한 경기 날짜, "
            
            if similarity_score > 0.1:
                recommendations.append(VideoRecommendation(
                    video_id=video.id,
                    title=video.title,
                    similarity_score=similarity_score,
                    reason=reason.rstrip(", ")
                ))
        
        # 유사도 점수로 정렬
        recommendations.sort(key=lambda x: x.similarity_score, reverse=True)
        return recommendations[:limit]
    
    async def delete_video(self, video_id: str) -> bool:
        """영상 삭제"""
        video = await self.get_video_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다.")
        
        # 파일 삭제
        try:
            if os.path.exists(video.file_path):
                os.remove(video.file_path)
        except Exception as e:
            print(f"파일 삭제 중 오류: {str(e)}")
        
        # DB에서 삭제
        if video_id in self.videos_db:
            del self.videos_db[video_id]
        
        return True

# 전역 서비스 인스턴스
video_service = VideoService() 
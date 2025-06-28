from graphviz import Digraph
import os

def create_class_diagram():
    # Digraph 객체 생성
    dot = Digraph(comment='Sports Vision AI API Class Diagram')
    dot.attr(rankdir='TB')
    
    # 노드 스타일 설정
    dot.attr('node', shape='record', style='filled', fillcolor='lightblue')
    
    # VideoStatus Enum
    dot.node('VideoStatus', '''{VideoStatus (Enum)|+ UPLOADING: str\\n+ PROCESSING: str\\n+ COMPLETED: str\\n+ FAILED: str}''')
    
    # Video Model
    dot.node('Video', '''{Video (Model)|+ id: str\\n+ title: str\\n+ description: Optional[str]\\n+ file_path: str\\n+ file_size: int\\n+ duration: Optional[float]\\n+ status: VideoStatus\\n+ sport_type: Optional[str]\\n+ match_date: Optional[datetime]\\n+ teams: Optional[List[str]]\\n+ created_at: datetime\\n+ updated_at: datetime\\n+ analyses: Optional[List[VideoAnalysis]]}''')
    
    # VideoAnalysis Model
    dot.node('VideoAnalysis', '''{VideoAnalysis (Model)|+ id: str\\n+ video_id: str\\n+ analysis_type: str\\n+ result_data: dict\\n+ confidence_score: float\\n+ created_at: datetime}''')
    
    # VideoUploadRequest Model
    dot.node('VideoUploadRequest', '''{VideoUploadRequest (Model)|+ title: str\\n+ description: Optional[str]\\n+ sport_type: Optional[str]\\n+ match_date: Optional[datetime]\\n+ teams: Optional[List[str]]}''')
    
    # VideoAnalysisRequest Model
    dot.node('VideoAnalysisRequest', '''{VideoAnalysisRequest (Model)|+ analysis_type: str\\n+ parameters: Optional[dict]}''')
    
    # VideoRecommendation Model
    dot.node('VideoRecommendation', '''{VideoRecommendation (Model)|+ video_id: str\\n+ title: str\\n+ similarity_score: float\\n+ reason: str}''')
    
    # VideoService Class
    dot.node('VideoService', '''{VideoService (Service)|+ upload_dir: str\\n+ videos_db: dict\\n+ analyses_db: dict\\n\\n+ upload_video()\\n+ _process_video()\\n+ get_video_history()\\n+ get_video_by_id()\\n+ analyze_video()\\n+ get_video_analyses()\\n+ get_video_recommendations()\\n+ delete_video()}''')
    
    # Video Router
    dot.node('VideoRouter', '''{VideoRouter (Router)|\\n+ upload_video()\\n+ list_videos()\\n+ get_video()\\n+ analyze_video()\\n+ get_video_analyses()\\n+ get_video_recommendations()\\n+ delete_video()}''')
    
    # Main App
    dot.node('FastAPIApp', '''{FastAPI App (main.py)|\\n+ read_root()\\n+ read_item()\\n+ update_item()\\n+ health_check()}''')
    
    # 관계 정의
    # Video와 VideoAnalysis의 관계
    dot.edge('Video', 'VideoAnalysis', 'has many')
    
    # Video와 VideoStatus의 관계
    dot.edge('Video', 'VideoStatus', 'uses')
    
    # VideoService와 Video의 관계
    dot.edge('VideoService', 'Video', 'manages')
    dot.edge('VideoService', 'VideoAnalysis', 'creates')
    dot.edge('VideoService', 'VideoRecommendation', 'generates')
    
    # VideoRouter와 VideoService의 관계
    dot.edge('VideoRouter', 'VideoService', 'uses')
    
    # VideoRouter와 Request/Response Models의 관계
    dot.edge('VideoRouter', 'VideoUploadRequest', 'accepts')
    dot.edge('VideoRouter', 'VideoAnalysisRequest', 'accepts')
    dot.edge('VideoRouter', 'Video', 'returns')
    dot.edge('VideoRouter', 'VideoAnalysis', 'returns')
    dot.edge('VideoRouter', 'VideoRecommendation', 'returns')
    
    # FastAPI App과 VideoRouter의 관계
    dot.edge('FastAPIApp', 'VideoRouter', 'includes')
    
    # 파일로 저장
    dot.render('class_diagram', format='png', cleanup=True)
    print("클래스 다이어그램이 'class_diagram.png'로 생성되었습니다!")

if __name__ == "__main__":
    create_class_diagram() 
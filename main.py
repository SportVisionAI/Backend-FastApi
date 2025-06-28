from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from routers import video

app = FastAPI(
    title="Sports Vision AI API",
    description="이 API는 실시간 스포츠 경기 분석을 위한 백엔드 서버입니다.",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영에서는 특정 도메인만 허용해야 함
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(video.router)

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

@app.get("/", tags=["기본 테스트 기능"])
def read_root():
    return {
        "message": "Sports Vision AI API에 오신 것을 환영합니다!",
        "version": "1.0.0",
        "features": [
            "영상 업로드 및 처리",
            "영상 히스토리 관리",
            "AI 기반 영상 분석",
            "관련 영상 추천"
        ],
        "docs": "/docs"
    }

@app.get("/items/{item_id}", tags=["기본 테스트 기능"])
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}", tags=["기본 테스트 기능"])
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

@app.get("/health", tags=["시스템"])
def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
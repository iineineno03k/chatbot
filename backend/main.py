from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import traceback
from services.chat_service import ChatService

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# メッセージモデル
class Message(BaseModel):
    role: str  # "user" または "bot"
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    role: str
    content: str
    conversation_id: str

# アプリケーション起動時にサービスを初期化
chat_service = ChatService()

@app.get("/")
def read_root():
    return {"message": "チャットボットAPIへようこそ"}

@app.get("/api/chat/history")
def get_chat_history(conversation_id: Optional[str] = None):
    try:
        return chat_service.get_chat_history(conversation_id)
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"履歴の取得に失敗しました: {str(e)}")

@app.post("/api/chat/send", response_model=ChatResponse)
def send_message(request: ChatRequest):
    try:
        logger.info(f"Received message: '{request.message}', conversation_id: {request.conversation_id}")
        response = chat_service.send_message(request.message, request.conversation_id)
        return ChatResponse(**response)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"メッセージの処理に失敗しました: {str(e)}")

@app.post("/api/chat/new")
def create_new_chat():
    """新しい会話を作成する"""
    try:
        new_id = chat_service.create_new_chat()
        return {"conversation_id": new_id}
    except Exception as e:
        logger.error(f"Error creating new chat: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"新しい会話の作成に失敗しました: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # 注意: 開発環境では以下の方法でも動作しますが、
    # 本番環境ではコマンドラインから実行することを推奨します:
    # python -m uvicorn main:app --host 0.0.0.0 --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000) 
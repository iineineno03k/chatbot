from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import db  # 作成したDynamoDBモジュール

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

# 現在の会話IDを管理
current_conversation_id = None

def get_conversation_id(conversation_id: Optional[str] = None) -> str:
    """会話IDを取得または新規作成する"""
    global current_conversation_id
    
    # 指定された会話IDがある場合はそれを使用
    if conversation_id:
        current_conversation_id = conversation_id
        return conversation_id
        
    # 現在のセッションで既に会話IDがある場合はそれを使用
    if current_conversation_id:
        return current_conversation_id
        
    # 最新の会話があればそれを使用
    latest_conversation = db.get_latest_conversation()
    if latest_conversation:
        current_conversation_id = latest_conversation
        return latest_conversation
        
    # 新しい会話IDを作成
    new_conversation_id = db.create_new_conversation()
    current_conversation_id = new_conversation_id
    return new_conversation_id

@app.get("/")
def read_root():
    return {"message": "チャットボットAPIへようこそ"}

@app.get("/api/chat/history")
def get_chat_history(conversation_id: Optional[str] = None):
    # 会話IDを取得
    conv_id = get_conversation_id(conversation_id)
    
    # DynamoDBから会話履歴を取得
    history = db.get_conversation_history(conv_id)
    
    # フロントエンド用にフォーマット変換
    formatted_history = [
        {"role": item["role"], "content": item["content"]}
        for item in history
    ]
    
    return formatted_history

@app.post("/api/chat/send", response_model=ChatResponse)
def send_message(request: ChatRequest):
    # 会話IDを取得
    conv_id = get_conversation_id(request.conversation_id)
    
    # ユーザーメッセージを保存
    db.save_message(conv_id, "user", request.message)
    
    # 簡単な応答ロジック
    response_text = "こんにちは！あなたのメッセージを受け取りました: " + request.message
    
    # ボットの応答を保存
    db.save_message(conv_id, "bot", response_text)
    
    return ChatResponse(
        role="bot",
        content=response_text,
        conversation_id=conv_id
    )

@app.post("/api/chat/new")
def create_new_chat():
    """新しい会話を作成する"""
    global current_conversation_id
    new_id = db.create_new_conversation()
    current_conversation_id = new_id
    return {"conversation_id": new_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
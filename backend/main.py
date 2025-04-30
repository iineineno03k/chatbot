from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

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

# チャット履歴を保存するリスト
chat_history: List[Message] = []

@app.get("/")
def read_root():
    return {"message": "チャットボットAPIへようこそ"}

@app.get("/api/chat/history")
def get_chat_history():
    return chat_history

@app.post("/api/chat/send")
def send_message(request: ChatRequest):
    user_message = Message(role="user", content=request.message)
    chat_history.append(user_message)
    
    # 簡単な応答ロジック
    response_text = "こんにちは！あなたのメッセージを受け取りました: " + request.message
    bot_message = Message(role="bot", content=response_text)
    chat_history.append(bot_message)
    
    return bot_message

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
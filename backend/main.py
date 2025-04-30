from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import db  # 作成したDynamoDBモジュール
import logging
import traceback

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

# 現在の会話IDを管理
current_conversation_id = None

def get_conversation_id(conversation_id: Optional[str] = None) -> str:
    """会話IDを取得または新規作成する"""
    global current_conversation_id
    
    # 指定された会話IDがある場合はそれを使用
    if conversation_id:
        logger.info(f"Using provided conversation ID: {conversation_id}")
        current_conversation_id = conversation_id
        return conversation_id
        
    # 現在のセッションで既に会話IDがある場合はそれを使用
    if current_conversation_id:
        logger.info(f"Using current session conversation ID: {current_conversation_id}")
        return current_conversation_id
        
    # 最新の会話があればそれを使用
    try:
        latest_conversation = db.get_latest_conversation()
        if latest_conversation:
            logger.info(f"Using latest conversation ID: {latest_conversation}")
            current_conversation_id = latest_conversation
            return latest_conversation
    except Exception as e:
        logger.error(f"Error getting latest conversation: {str(e)}")
        # エラーが発生した場合は新しい会話を作成
        
    # 新しい会話IDを作成
    new_conversation_id = db.create_new_conversation()
    logger.info(f"Created new conversation ID: {new_conversation_id}")
    current_conversation_id = new_conversation_id
    return new_conversation_id

@app.get("/")
def read_root():
    return {"message": "チャットボットAPIへようこそ"}

@app.get("/api/chat/history")
def get_chat_history(conversation_id: Optional[str] = None):
    try:
        # 会話IDを取得
        conv_id = get_conversation_id(conversation_id)
        logger.info(f"Getting chat history for conversation ID: {conv_id}")
        
        # DynamoDBから会話履歴を取得
        history = db.get_conversation_history(conv_id)
        
        # フロントエンド用にフォーマット変換
        formatted_history = [
            {"role": item["role"], "content": item["content"]}
            for item in history
        ]
        
        logger.info(f"Retrieved {len(formatted_history)} messages from history")
        return formatted_history
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"履歴の取得に失敗しました: {str(e)}")

@app.post("/api/chat/send", response_model=ChatResponse)
def send_message(request: ChatRequest):
    try:
        logger.info(f"Received message: '{request.message}', conversation_id: {request.conversation_id}")
        
        # 会話IDを取得
        conv_id = get_conversation_id(request.conversation_id)
        
        # ユーザーメッセージを保存
        user_msg = db.save_message(conv_id, "user", request.message)
        logger.info(f"Saved user message with ID: {user_msg.get('message_id')}")
        
        # 簡単な応答ロジック
        response_text = "こんにちは！あなたのメッセージを受け取りました: " + request.message
        
        # ボットの応答を保存
        bot_msg = db.save_message(conv_id, "bot", response_text)
        logger.info(f"Saved bot response with ID: {bot_msg.get('message_id')}")
        
        response = ChatResponse(
            role="bot",
            content=response_text,
            conversation_id=conv_id
        )
        
        logger.info(f"Sending response: '{response_text}'")
        return response
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"メッセージの処理に失敗しました: {str(e)}")

@app.post("/api/chat/new")
def create_new_chat():
    """新しい会話を作成する"""
    try:
        global current_conversation_id
        new_id = db.create_new_conversation()
        current_conversation_id = new_id
        logger.info(f"Created new conversation with ID: {new_id}")
        return {"conversation_id": new_id}
    except Exception as e:
        logger.error(f"Error creating new chat: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"新しい会話の作成に失敗しました: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
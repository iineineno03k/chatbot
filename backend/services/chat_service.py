from typing import List, Dict, Optional
import logging
from database.dynamodb_repository import DynamoDBRepository

class ChatService:
    """チャットサービスクラス - ビジネスロジック層"""
    
    def __init__(self, repository: DynamoDBRepository = None):
        """初期化"""
        self.logger = logging.getLogger(__name__)
        self.repository = repository or DynamoDBRepository()
        self.current_conversation_id = None
    
    def get_conversation_id(self, conversation_id: Optional[str] = None) -> str:
        """会話IDを取得または新規作成する"""
        # 指定された会話IDがある場合はそれを使用
        if conversation_id:
            self.logger.info(f"Using provided conversation ID: {conversation_id}")
            self.current_conversation_id = conversation_id
            return conversation_id
            
        # 現在のセッションで既に会話IDがある場合はそれを使用
        if self.current_conversation_id:
            self.logger.info(f"Using current session conversation ID: {self.current_conversation_id}")
            return self.current_conversation_id
            
        # 最新の会話があればそれを使用
        try:
            latest_conversation = self.repository.get_latest_conversation()
            if latest_conversation:
                self.logger.info(f"Using latest conversation ID: {latest_conversation}")
                self.current_conversation_id = latest_conversation
                return latest_conversation
        except Exception as e:
            self.logger.error(f"Error getting latest conversation: {str(e)}")
            # エラーが発生した場合は新しい会話を作成
            
        # 新しい会話IDを作成
        new_conversation_id = self.repository.create_new_conversation()
        self.logger.info(f"Created new conversation ID: {new_conversation_id}")
        self.current_conversation_id = new_conversation_id
        return new_conversation_id
    
    def get_chat_history(self, conversation_id: Optional[str] = None) -> List[Dict]:
        """チャット履歴を取得する"""
        # 会話IDを取得
        conv_id = self.get_conversation_id(conversation_id)
        
        # リポジトリから会話履歴を取得
        history = self.repository.get_conversation_history(conv_id)
        
        # フロントエンド用にフォーマット変換
        formatted_history = [
            {"role": item["role"], "content": item["content"]}
            for item in history
        ]
        
        self.logger.info(f"Retrieved {len(formatted_history)} messages from history")
        return formatted_history
    
    def send_message(self, message: str, conversation_id: Optional[str] = None) -> Dict:
        """メッセージを送信し、ボットの応答を返す"""
        # 会話IDを取得
        conv_id = self.get_conversation_id(conversation_id)
        
        # ユーザーメッセージを保存
        user_msg = self.repository.save_message(conv_id, "user", message)
        self.logger.info(f"Saved user message with ID: {user_msg.get('message_id')}")
        
        # 簡単な応答ロジック
        response_text = self._generate_response(message)
        
        # ボットの応答を保存
        bot_msg = self.repository.save_message(conv_id, "bot", response_text)
        self.logger.info(f"Saved bot response with ID: {bot_msg.get('message_id')}")
        
        response = {
            "role": "bot",
            "content": response_text,
            "conversation_id": conv_id
        }
        
        self.logger.info(f"Sending response: '{response_text}'")
        return response
    
    def create_new_chat(self) -> str:
        """新しい会話を作成する"""
        new_id = self.repository.create_new_conversation()
        self.current_conversation_id = new_id
        self.logger.info(f"Created new conversation with ID: {new_id}")
        return new_id
    
    def _generate_response(self, message: str) -> str:
        """メッセージに対する応答を生成する"""
        # 実際のアプリケーションでは、ここにより複雑な応答生成ロジックが入る
        return f"こんにちは！あなたのメッセージを受け取りました: {message}" 
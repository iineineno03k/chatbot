import uuid
from datetime import datetime
from typing import List, Dict, Optional
import logging

class MockDynamoDBRepository:
    """テスト用モックDynamoDBリポジトリ"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conversations = {}  # 会話ID -> メッセージリスト
        self.latest_conversation_id = None
    
    def save_message(self, conversation_id: str, role: str, content: str) -> Dict:
        """メッセージをモックストアに保存する"""
        timestamp = datetime.utcnow().isoformat()
        message_id = str(uuid.uuid4())
        
        item = {
            'conversation_id': conversation_id,
            'timestamp': timestamp,
            'message_id': message_id,
            'role': role,
            'content': content
        }
        
        # 会話IDがなければ初期化
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        # メッセージを追加
        self.conversations[conversation_id].append(item)
        
        # 最新の会話IDを更新
        self.latest_conversation_id = conversation_id
        
        self.logger.info(f"[MOCK] Saved message to conversation: {conversation_id}")
        return item
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """指定された会話IDの全メッセージを取得する"""
        if conversation_id not in self.conversations:
            self.logger.info(f"[MOCK] No messages for conversation: {conversation_id}")
            return []
        
        messages = self.conversations[conversation_id]
        # タイムスタンプでソート
        sorted_messages = sorted(messages, key=lambda x: x['timestamp'])
        
        self.logger.info(f"[MOCK] Retrieved {len(sorted_messages)} messages")
        return sorted_messages
    
    def create_new_conversation(self) -> str:
        """新しい会話IDを生成する"""
        new_id = str(uuid.uuid4())
        self.conversations[new_id] = []
        self.latest_conversation_id = new_id
        
        self.logger.info(f"[MOCK] Created new conversation: {new_id}")
        return new_id
    
    def get_latest_conversation(self) -> Optional[str]:
        """最新の会話IDを取得する"""
        self.logger.info(f"[MOCK] Retrieved latest conversation: {self.latest_conversation_id}")
        return self.latest_conversation_id 
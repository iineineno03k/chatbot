import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import main
from services.chat_service import ChatService
from database.mock_repository import MockDynamoDBRepository

class TestChatAPI(unittest.TestCase):
    """チャットAPIのテスト"""
    
    def setUp(self):
        """各テスト前の準備"""
        # モックリポジトリを作成
        self.mock_repository = MockDynamoDBRepository()
        # モックサービスを作成
        self.mock_chat_service = ChatService(repository=self.mock_repository)
        # APIクライアントを作成
        self.client = TestClient(main.app)
        # mainモジュールのchat_serviceをモックに置き換え
        main.chat_service = self.mock_chat_service
    
    def test_read_root(self):
        """ルートエンドポイントのテスト"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "チャットボットAPIへようこそ"})
    
    def test_get_chat_history_empty(self):
        """空のチャット履歴取得テスト"""
        # 新しい会話を作成
        conversation_id = self.mock_repository.create_new_conversation()
        
        # API呼び出し
        response = self.client.get(f"/api/chat/history?conversation_id={conversation_id}")
        
        # 検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
    
    def test_get_chat_history(self):
        """チャット履歴取得テスト"""
        # 会話とメッセージを作成
        conversation_id = self.mock_repository.create_new_conversation()
        self.mock_repository.save_message(conversation_id, "user", "APIテスト")
        self.mock_repository.save_message(conversation_id, "bot", "応答テスト")
        
        # API呼び出し
        response = self.client.get(f"/api/chat/history?conversation_id={conversation_id}")
        
        # 検証
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["role"], "user")
        self.assertEqual(data[0]["content"], "APIテスト")
    
    def test_send_message(self):
        """メッセージ送信テスト"""
        # 会話を作成
        conversation_id = self.mock_repository.create_new_conversation()
        
        # API呼び出し
        message = "APIからのメッセージ"
        response = self.client.post(
            "/api/chat/send",
            json={"message": message, "conversation_id": conversation_id}
        )
        
        # 検証
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["role"], "bot")
        self.assertIn(message, data["content"])
        self.assertEqual(data["conversation_id"], conversation_id)
        
        # データが保存されていることを確認
        history = self.mock_repository.get_conversation_history(conversation_id)
        self.assertEqual(len(history), 2)
    
    def test_create_new_chat(self):
        """新しい会話作成テスト"""
        # API呼び出し
        response = self.client.post("/api/chat/new")
        
        # 検証
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("conversation_id", data)
        self.assertIsNotNone(data["conversation_id"])
        
        # 作成された会話IDがサービスに設定されていることを確認
        self.assertEqual(self.mock_chat_service.current_conversation_id, data["conversation_id"])
    
    def test_error_handling(self):
        """エラーハンドリングテスト"""
        # get_chat_historyでエラーが発生するようにモック
        with patch.object(self.mock_chat_service, 'get_chat_history', side_effect=Exception("テストエラー")):
            response = self.client.get("/api/chat/history")
            self.assertEqual(response.status_code, 500)
            self.assertIn("detail", response.json())
            self.assertIn("テストエラー", response.json()["detail"])

if __name__ == "__main__":
    unittest.main() 
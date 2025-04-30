import unittest
from unittest.mock import patch, MagicMock
from services.chat_service import ChatService
from database.mock_repository import MockDynamoDBRepository

class TestChatService(unittest.TestCase):
    """チャットサービスのテスト"""
    
    def setUp(self):
        """各テスト前の準備"""
        self.mock_repository = MockDynamoDBRepository()
        self.chat_service = ChatService(repository=self.mock_repository)
    
    def test_get_conversation_id_provided(self):
        """指定された会話IDが使われるか確認"""
        provided_id = "test-conversation-id"
        result = self.chat_service.get_conversation_id(provided_id)
        self.assertEqual(result, provided_id)
        self.assertEqual(self.chat_service.current_conversation_id, provided_id)
    
    def test_get_conversation_id_from_session(self):
        """セッションの会話IDが使われるか確認"""
        # 事前に会話IDを設定
        self.chat_service.current_conversation_id = "session-conversation-id"
        result = self.chat_service.get_conversation_id()
        self.assertEqual(result, "session-conversation-id")
    
    def test_get_conversation_id_from_latest(self):
        """最新の会話IDが使われるか確認"""
        # 最新の会話IDを設定
        latest_id = self.mock_repository.create_new_conversation()
        # current_conversation_idをリセット
        self.chat_service.current_conversation_id = None
        
        result = self.chat_service.get_conversation_id()
        self.assertEqual(result, latest_id)
        self.assertEqual(self.chat_service.current_conversation_id, latest_id)
    
    def test_get_conversation_id_new(self):
        """新しい会話IDが作成されるか確認"""
        # リポジトリをモック化して最新の会話IDをNoneに設定
        with patch.object(self.mock_repository, 'get_latest_conversation', return_value=None):
            # 現在の会話IDもNoneに設定
            self.chat_service.current_conversation_id = None
            # 新しい会話IDを取得
            result = self.chat_service.get_conversation_id()
            # IDがNoneでないことを確認
            self.assertIsNotNone(result)
            # 現在の会話IDが更新されていることを確認
            self.assertEqual(self.chat_service.current_conversation_id, result)
    
    def test_get_chat_history(self):
        """チャット履歴取得のテスト"""
        # 会話を作成してメッセージを追加
        conversation_id = self.mock_repository.create_new_conversation()
        self.mock_repository.save_message(conversation_id, "user", "テストメッセージ")
        self.mock_repository.save_message(conversation_id, "bot", "テスト応答")
        
        # 履歴を取得
        history = self.chat_service.get_chat_history(conversation_id)
        
        # 検証
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "テストメッセージ")
        self.assertEqual(history[1]["role"], "bot")
        self.assertEqual(history[1]["content"], "テスト応答")
    
    def test_send_message(self):
        """メッセージ送信のテスト"""
        # 会話IDを取得
        conversation_id = self.mock_repository.create_new_conversation()
        
        # メッセージを送信
        user_message = "こんにちは、テストです"
        response = self.chat_service.send_message(user_message, conversation_id)
        
        # 検証
        self.assertEqual(response["role"], "bot")
        self.assertIn(user_message, response["content"])
        self.assertEqual(response["conversation_id"], conversation_id)
        
        # 会話履歴に保存されていることを確認
        history = self.mock_repository.get_conversation_history(conversation_id)
        self.assertEqual(len(history), 2)  # ユーザーとボットのメッセージ
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], user_message)
        self.assertEqual(history[1]["role"], "bot")
    
    def test_create_new_chat(self):
        """新しい会話作成のテスト"""
        # 新しい会話を作成
        new_id = self.chat_service.create_new_chat()
        
        # 検証
        self.assertIsNotNone(new_id)
        self.assertEqual(self.chat_service.current_conversation_id, new_id)
    
    def test_generate_response(self):
        """応答生成のテスト"""
        message = "テストメッセージ"
        response = self.chat_service._generate_response(message)
        self.assertIn(message, response)

if __name__ == "__main__":
    unittest.main() 
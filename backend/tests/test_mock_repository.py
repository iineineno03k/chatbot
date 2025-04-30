import unittest
from database.mock_repository import MockDynamoDBRepository

class TestMockDynamoDBRepository(unittest.TestCase):
    """モックDynamoDBリポジトリのテスト"""
    
    def setUp(self):
        """各テスト前の準備"""
        self.repository = MockDynamoDBRepository()
    
    def test_create_new_conversation(self):
        """新しい会話作成のテスト"""
        conversation_id = self.repository.create_new_conversation()
        self.assertIsNotNone(conversation_id)
        self.assertEqual(conversation_id, self.repository.latest_conversation_id)
        self.assertIn(conversation_id, self.repository.conversations)
        self.assertEqual(len(self.repository.conversations[conversation_id]), 0)
    
    def test_save_message(self):
        """メッセージ保存のテスト"""
        conversation_id = self.repository.create_new_conversation()
        
        # ユーザーメッセージを保存
        user_message = "こんにちは"
        item = self.repository.save_message(conversation_id, "user", user_message)
        
        # 検証
        self.assertEqual(item["conversation_id"], conversation_id)
        self.assertEqual(item["role"], "user")
        self.assertEqual(item["content"], user_message)
        self.assertIn("timestamp", item)
        self.assertIn("message_id", item)
        
        # 会話履歴に追加されていることを確認
        self.assertEqual(len(self.repository.conversations[conversation_id]), 1)
    
    def test_get_conversation_history_empty(self):
        """空の会話履歴取得テスト"""
        conversation_id = self.repository.create_new_conversation()
        history = self.repository.get_conversation_history(conversation_id)
        self.assertEqual(len(history), 0)
    
    def test_get_conversation_history(self):
        """会話履歴取得テスト"""
        conversation_id = self.repository.create_new_conversation()
        
        # メッセージを保存
        self.repository.save_message(conversation_id, "user", "こんにちは")
        self.repository.save_message(conversation_id, "bot", "こんにちは！")
        
        # 履歴を取得
        history = self.repository.get_conversation_history(conversation_id)
        
        # 検証
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "こんにちは")
        self.assertEqual(history[1]["role"], "bot")
        self.assertEqual(history[1]["content"], "こんにちは！")
    
    def test_get_latest_conversation(self):
        """最新の会話ID取得テスト"""
        # 初期状態では最新の会話IDはNone
        self.assertIsNone(self.repository.get_latest_conversation())
        
        # 新しい会話を作成
        conversation_id1 = self.repository.create_new_conversation()
        self.assertEqual(self.repository.get_latest_conversation(), conversation_id1)
        
        # 別の会話を作成
        conversation_id2 = self.repository.create_new_conversation()
        self.assertEqual(self.repository.get_latest_conversation(), conversation_id2)
    
    def test_multiple_conversations(self):
        """複数の会話管理テスト"""
        # 2つの会話を作成
        conversation_id1 = self.repository.create_new_conversation()
        self.repository.save_message(conversation_id1, "user", "会話1のメッセージ")
        
        conversation_id2 = self.repository.create_new_conversation()
        self.repository.save_message(conversation_id2, "user", "会話2のメッセージ")
        
        # 各会話の履歴を確認
        history1 = self.repository.get_conversation_history(conversation_id1)
        self.assertEqual(len(history1), 1)
        self.assertEqual(history1[0]["content"], "会話1のメッセージ")
        
        history2 = self.repository.get_conversation_history(conversation_id2)
        self.assertEqual(len(history2), 1)
        self.assertEqual(history2[0]["content"], "会話2のメッセージ")

if __name__ == "__main__":
    unittest.main() 
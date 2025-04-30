import unittest
import boto3
import uuid
from moto import mock_aws
from database.dynamodb_repository import DynamoDBRepository
from datetime import datetime, UTC
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDynamoDBWithMoto(unittest.TestCase):
    """motoライブラリを使用したDynamoDBリポジトリのテスト"""
    
    def _setup_dynamodb(self):
        """各テストで共通のDynamoDBセットアップを行うヘルパーメソッド"""
        # DynamoDBリソースの初期化（motoによってモック化される）
        dynamodb = boto3.resource(
            'dynamodb',
            region_name='us-west-2'
        )
        
        # テスト用テーブルの作成
        table_name = "TestChatMessages"
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'conversation_id', 'KeyType': 'HASH'},  # パーティションキー
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}  # ソートキー
            ],
            AttributeDefinitions=[
                {'AttributeName': 'conversation_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # テーブルが作成されるまで待機
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        logger.info(f"Created test table: {table_name}")
        
        # リポジトリの作成
        repository = DynamoDBRepository(
            table_name=table_name,
            region_name='us-west-2',
            endpoint_url=None
        )
        
        return dynamodb, table, repository
    
    @mock_aws
    def test_create_new_conversation(self):
        """新しい会話作成のテスト"""
        # DynamoDBとテーブルをセットアップ
        _, _, repository = self._setup_dynamodb()
        
        # 新しい会話IDを作成
        conversation_id = repository.create_new_conversation()
        
        # 検証
        self.assertIsNotNone(conversation_id)
        # UUIDv4の形式チェック (簡易版)
        self.assertEqual(len(conversation_id), 36)
        self.assertEqual(conversation_id.count('-'), 4)
    
    @mock_aws
    def test_save_message(self):
        """メッセージ保存のテスト"""
        # DynamoDBとテーブルをセットアップ
        _, table, repository = self._setup_dynamodb()
        
        # テストデータ
        conversation_id = str(uuid.uuid4())
        role = "user"
        content = "これはmotoを使ったテストメッセージです"
        
        # メッセージを保存
        result = repository.save_message(conversation_id, role, content)
        
        # 結果の検証
        self.assertEqual(result["conversation_id"], conversation_id)
        self.assertEqual(result["role"], role)
        self.assertEqual(result["content"], content)
        self.assertIn("timestamp", result)
        self.assertIn("message_id", result)
        
        # 保存されたデータを直接取得して検証
        response = table.get_item(
            Key={
                'conversation_id': conversation_id,
                'timestamp': result['timestamp']
            }
        )
        item = response.get('Item')
        self.assertIsNotNone(item)
        self.assertEqual(item['content'], content)
    
    @mock_aws
    def test_get_conversation_history(self):
        """会話履歴取得のテスト"""
        # DynamoDBとテーブルをセットアップ
        _, _, repository = self._setup_dynamodb()
        
        # 会話IDを生成
        conversation_id = str(uuid.uuid4())
        
        # 複数のメッセージを保存
        repository.save_message(conversation_id, "user", "こんにちは")
        repository.save_message(conversation_id, "bot", "こんにちは！お手伝いできることはありますか？")
        repository.save_message(conversation_id, "user", "DynamoDBについて教えてください")
        
        # 会話履歴を取得
        history = repository.get_conversation_history(conversation_id)
        
        # 検証
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "こんにちは")
        self.assertEqual(history[1]["role"], "bot")
        self.assertEqual(history[2]["role"], "user")
        self.assertEqual(history[2]["content"], "DynamoDBについて教えてください")
    
    @mock_aws
    def test_multiple_conversations(self):
        """複数の会話管理テスト"""
        # DynamoDBとテーブルをセットアップ
        _, _, repository = self._setup_dynamodb()
        
        # 2つの会話を作成
        conversation_id1 = repository.create_new_conversation()
        conversation_id2 = repository.create_new_conversation()
        
        # それぞれの会話にメッセージを追加
        repository.save_message(conversation_id1, "user", "会話1のメッセージ")
        repository.save_message(conversation_id2, "user", "会話2のメッセージ")
        
        # 会話履歴を取得して検証
        history1 = repository.get_conversation_history(conversation_id1)
        self.assertEqual(len(history1), 1)
        self.assertEqual(history1[0]["content"], "会話1のメッセージ")
        
        history2 = repository.get_conversation_history(conversation_id2)
        self.assertEqual(len(history2), 1)
        self.assertEqual(history2[0]["content"], "会話2のメッセージ")

if __name__ == "__main__":
    unittest.main() 
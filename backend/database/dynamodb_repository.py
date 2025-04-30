import os
import boto3
import uuid
from datetime import datetime, UTC
from typing import List, Dict, Optional
import logging

class DynamoDBRepository:
    """DynamoDBリポジトリクラス - データアクセス層"""
    
    def __init__(self, 
                 region_name: str = "us-west-2",
                 endpoint_url: str = "http://localhost:8002",
                 table_name: str = "ChatMessages",
                 aws_access_key_id: str = "local",
                 aws_secret_access_key: str = "local"):
        """初期化"""
        self.logger = logging.getLogger(__name__)
        self.table_name = table_name
        
        # DynamoDBリソースの初期化
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=region_name,
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        
        # テーブルを初期化
        self.table = self._create_table_if_not_exists()
        
    def _create_table_if_not_exists(self):
        """テーブルが存在しない場合は作成する"""
        table_names = [table.name for table in self.dynamodb.tables.all()]
        
        if self.table_name not in table_names:
            self.logger.info(f"Creating table: {self.table_name}")
            table = self.dynamodb.create_table(
                TableName=self.table_name,
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
            table.meta.client.get_waiter('table_exists').wait(TableName=self.table_name)
            self.logger.info(f"Table created: {self.table_name}")
        else:
            self.logger.info(f"Table already exists: {self.table_name}")
            table = self.dynamodb.Table(self.table_name)
        
        return table
    
    def save_message(self, conversation_id: str, role: str, content: str) -> Dict:
        """メッセージをDynamoDBに保存する"""
        timestamp = datetime.now(UTC).isoformat()
        message_id = str(uuid.uuid4())
        
        item = {
            'conversation_id': conversation_id,
            'timestamp': timestamp,
            'message_id': message_id,
            'role': role,
            'content': content
        }
        
        self.table.put_item(Item=item)
        self.logger.info(f"Saved message with ID: {message_id} to conversation: {conversation_id}")
        return item
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """指定された会話IDの全メッセージを取得する"""
        self.logger.info(f"Getting history for conversation: {conversation_id}")
        response = self.table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('conversation_id').eq(conversation_id),
            ScanIndexForward=True  # タイムスタンプで昇順ソート
        )
        
        items = response.get('Items', [])
        self.logger.info(f"Retrieved {len(items)} messages from conversation: {conversation_id}")
        return items
    
    def create_new_conversation(self) -> str:
        """新しい会話IDを生成する"""
        new_id = str(uuid.uuid4())
        self.logger.info(f"Created new conversation with ID: {new_id}")
        return new_id
    
    def get_latest_conversation(self) -> Optional[str]:
        """最新の会話IDを取得する（存在する場合）"""
        # 簡易的な実装として全件スキャンを使用
        # 注意: 実際の運用では非効率なため、別のインデックスやメタデータテーブルを検討すべき
        response = self.table.scan(Limit=1)
        items = response.get('Items', [])
        
        if items:
            conversation_id = items[0].get('conversation_id')
            self.logger.info(f"Retrieved latest conversation ID: {conversation_id}")
            return conversation_id
        
        self.logger.info("No latest conversation found")
        return None 
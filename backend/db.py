import os
import boto3
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
import json

# 環境変数の読み込み
load_dotenv('config.env')

# DynamoDB 設定
AWS_REGION = os.getenv('AWS_REGION', 'us-west-2')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'local')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'local')
DYNAMODB_ENDPOINT = os.getenv('DYNAMODB_ENDPOINT', 'http://localhost:8000')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME', 'ChatMessages')

# DynamoDBリソースの初期化
dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    endpoint_url=DYNAMODB_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def create_table_if_not_exists():
    """テーブルが存在しない場合は作成する"""
    table_names = [table.name for table in dynamodb.tables.all()]
    
    if DYNAMODB_TABLE_NAME not in table_names:
        print(f"Creating table: {DYNAMODB_TABLE_NAME}")
        table = dynamodb.create_table(
            TableName=DYNAMODB_TABLE_NAME,
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
        table.meta.client.get_waiter('table_exists').wait(TableName=DYNAMODB_TABLE_NAME)
        print(f"Table created: {DYNAMODB_TABLE_NAME}")
    else:
        print(f"Table already exists: {DYNAMODB_TABLE_NAME}")
    
    return dynamodb.Table(DYNAMODB_TABLE_NAME)

# テーブルを取得または作成
table = create_table_if_not_exists()

def save_message(conversation_id: str, role: str, content: str) -> Dict:
    """メッセージをDynamoDBに保存する"""
    timestamp = datetime.utcnow().isoformat()
    
    item = {
        'conversation_id': conversation_id,
        'timestamp': timestamp,
        'message_id': str(uuid.uuid4()),
        'role': role,
        'content': content
    }
    
    table.put_item(Item=item)
    return item

def get_conversation_history(conversation_id: str) -> List[Dict]:
    """指定された会話IDの全メッセージを取得する"""
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('conversation_id').eq(conversation_id),
        ScanIndexForward=True  # タイムスタンプで昇順ソート
    )
    
    return response.get('Items', [])

def create_new_conversation() -> str:
    """新しい会話IDを生成する"""
    return str(uuid.uuid4())

def get_latest_conversation() -> Optional[str]:
    """最新の会話IDを取得する（存在する場合）"""
    # 簡易的な実装として全件スキャンを使用
    # 注意: 実際の運用では非効率なため、別のインデックスやメタデータテーブルを検討すべき
    response = table.scan(Limit=1)
    items = response.get('Items', [])
    
    if items:
        return items[0].get('conversation_id')
    return None 
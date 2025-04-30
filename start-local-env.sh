#!/bin/bash

# DynamoDBローカル環境を起動
echo "Starting DynamoDB local environment..."
docker-compose up -d

# DynamoDBが起動するまで少し待機
echo "Waiting for DynamoDB to initialize..."
sleep 5

# バックエンドを起動
echo "Starting backend server..."
cd backend
source venv/bin/activate
pip install -r requirements.txt

# バックエンドのポートが8000の場合、DynamoDBのポートと競合する可能性があるので
# DynamoDBのポートは8002に変更済み（docker-compose.ymlとconfig.envで設定）
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 
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
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 
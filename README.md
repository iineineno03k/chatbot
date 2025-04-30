# シンプルチャットボット

React (TypeScript) とFastAPI (Python) を使用した簡単なチャットボットアプリケーション。データ保存にはAmazon DynamoDBを使用しています。

## プロジェクト構成

- `frontend/`: React (TypeScript) フロントエンド
- `backend/`: FastAPI (Python) バックエンド
- `docker-compose.yml`: DynamoDBローカル環境の設定

## 前提条件

- Docker と Docker Compose がインストールされていること
- Python 3.8以上
- Node.js 14以上
- npm 6以上

## セットアップ方法

### ローカル環境のワンステップセットアップ

全てのサービス（DynamoDB, バックエンド）を一度に起動するには：

```bash
./start-local-env.sh
```

そして別のターミナルで：

```bash
cd frontend
npm install
npm start
```

### 個別セットアップ

#### DynamoDBローカル

```bash
# DynamoDBローカルとDynamoDB管理UIを起動
docker-compose up -d
```

- DynamoDBローカルは http://localhost:8000 で動作します
- DynamoDB管理UIは http://localhost:8001 でアクセスできます

#### バックエンド

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
./run.sh  # Windows: uvicorn main:app --reload
```

バックエンドサーバーは http://localhost:8000 で実行されます。

#### フロントエンド

```bash
cd frontend
npm install
npm start
```

フロントエンドアプリケーションは http://localhost:3000 で実行されます。

## 機能

- ユーザーはチャットボットにメッセージを送信できます
- チャットボットはシンプルな応答を返します
- チャット履歴はDynamoDBに保存され、セッション間で保持されます
- 複数の会話を作成し管理できます

## API エンドポイント

- `GET /api/chat/history`: チャット履歴を取得
- `POST /api/chat/send`: メッセージを送信
- `POST /api/chat/new`: 新しい会話を作成

## DynamoDBデータモデル

チャットメッセージは次の構造でDynamoDBに保存されます：

- `conversation_id`: (パーティションキー) 会話のユニークID
- `timestamp`: (ソートキー) メッセージのタイムスタンプ
- `message_id`: メッセージのユニークID
- `role`: メッセージの送信者 ("user" または "bot")
- `content`: メッセージの内容

## ライセンス

MIT 
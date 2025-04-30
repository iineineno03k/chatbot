# シンプルチャットボット

React (TypeScript) とFastAPI (Python) を使用した簡単なチャットボットアプリケーション。

## プロジェクト構成

- `frontend/`: React (TypeScript) フロントエンド
- `backend/`: FastAPI (Python) バックエンド

## セットアップ方法

### バックエンド

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
./run.sh  # Windows: uvicorn main:app --reload
```

バックエンドサーバーは http://localhost:8000 で実行されます。

### フロントエンド

```bash
cd frontend
npm install
npm start
```

フロントエンドアプリケーションは http://localhost:3000 で実行されます。

## 機能

- ユーザーはチャットボットにメッセージを送信できます
- チャットボットはシンプルな応答を返します
- チャット履歴はセッション中に保存されます

## API エンドポイント

- `GET /api/chat/history`: チャット履歴を取得
- `POST /api/chat/send`: メッセージを送信

## ライセンス

MIT 
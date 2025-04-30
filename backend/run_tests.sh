#!/bin/bash

# テスト実行スクリプト
echo "Running Chatbot Backend Tests"
echo "=============================="

# テスト依存関係を確認
if ! pip list | grep -q "fastapi"; then
  echo "Installing test dependencies..."
  pip install pytest pytest-cov fastapi httpx
fi

# すべてのテストを実行
python -m unittest discover -s tests

# カバレッジレポートを生成（オプション）
echo "Generating coverage report..."
python -m pytest --cov=database --cov=services tests/ 
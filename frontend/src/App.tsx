import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

interface Message {
  role: string;
  content: string;
}

interface ChatResponse {
  role: string;
  content: string;
  conversation_id: string;
}

// APIの基本URL
const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // メッセージが追加されたら自動スクロール
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    // チャット履歴を取得
    const fetchChatHistory = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log('履歴を取得中...');
        const response = await axios.get(`${API_BASE_URL}/api/chat/history`);
        console.log('履歴取得レスポンス:', response.data);
        
        if (Array.isArray(response.data)) {
          setMessages(response.data);
        }
        
        // 会話IDが存在しない場合は新しい会話を作成
        if (!conversationId) {
          const newChatResponse = await axios.post(`${API_BASE_URL}/api/chat/new`);
          console.log('新しい会話ID:', newChatResponse.data.conversation_id);
          setConversationId(newChatResponse.data.conversation_id);
        }
      } catch (error) {
        console.error('チャット履歴の取得に失敗しました:', error);
        setError('サーバー接続エラー：チャット履歴の取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    fetchChatHistory();
  }, []);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || loading) return;
    
    setLoading(true);
    setError(null);
    
    // ユーザーメッセージをUIに追加
    const userMessage: Message = { role: 'user', content: input };
    const currentInput = input; // 入力内容をキャプチャ
    
    // UIを即座に更新
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    
    try {
      console.log('メッセージ送信:', currentInput, '会話ID:', conversationId);
      
      // バックエンドにメッセージを送信
      const response = await axios.post<ChatResponse>(`${API_BASE_URL}/api/chat/send`, {
        message: currentInput,
        conversation_id: conversationId
      });
      
      console.log('送信レスポンス:', response.data);
      
      // ボットの応答をUIに追加
      if (response.data && response.data.content) {
        setMessages(prev => [...prev, { 
          role: response.data.role, 
          content: response.data.content 
        }]);
        
        // 会話IDを保存
        if (response.data.conversation_id) {
          setConversationId(response.data.conversation_id);
        }
      } else {
        throw new Error('無効なレスポンス形式');
      }
    } catch (error) {
      console.error('メッセージの送信に失敗しました:', error);
      setError('メッセージの送信に失敗しました。もう一度お試しください。');
      
      // エラーの場合、ユーザーの入力を復元
      setInput(currentInput);
      
      // エラーの場合、ユーザーメッセージをUIから削除
      setMessages(prev => prev.filter((_, i) => i !== prev.length - 1));
    } finally {
      setLoading(false);
    }
  };

  const startNewConversation = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('新しい会話を作成中...');
      const response = await axios.post(`${API_BASE_URL}/api/chat/new`);
      console.log('新しい会話レスポンス:', response.data);
      
      if (response.data && response.data.conversation_id) {
        setConversationId(response.data.conversation_id);
        setMessages([]);
      } else {
        throw new Error('会話IDが取得できませんでした');
      }
    } catch (error) {
      console.error('新しい会話の作成に失敗しました:', error);
      setError('新しい会話の作成に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>シンプルチャットボット</h1>
        <button 
          className="new-chat-button" 
          onClick={startNewConversation}
          disabled={loading}
        >
          新しい会話を開始
        </button>
      </header>
      
      {error && <div className="error-message">{error}</div>}
      
      <main className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="welcome-message">
              メッセージを送信して会話を始めましょう！
            </div>
          ) : (
            <>
              {messages.map((msg, index) => (
                <div key={index} className={`message ${msg.role}`}>
                  <div className="message-content">{msg.content}</div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
        <form onSubmit={sendMessage} className="input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="メッセージを入力..."
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            {loading ? '送信中...' : '送信'}
          </button>
        </form>
      </main>
    </div>
  );
}

export default App;

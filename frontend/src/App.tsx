import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

interface Message {
  role: string;
  content: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // チャット履歴を取得
    const fetchChatHistory = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/chat/history');
        setMessages(response.data);
      } catch (error) {
        console.error('チャット履歴の取得に失敗しました:', error);
      }
    };

    fetchChatHistory();
  }, []);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    setLoading(true);
    
    // ユーザーメッセージをUIに追加
    const userMessage: Message = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    
    try {
      // バックエンドにメッセージを送信
      const response = await axios.post('http://localhost:8000/api/chat/send', {
        message: input
      });
      
      // ボットの応答をUIに追加
      setMessages(prev => [...prev, response.data]);
    } catch (error) {
      console.error('メッセージの送信に失敗しました:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>シンプルチャットボット</h1>
      </header>
      <main className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="welcome-message">
              メッセージを送信して会話を始めましょう！
            </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className={`message ${msg.role}`}>
                <div className="message-content">{msg.content}</div>
              </div>
            ))
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
            送信
          </button>
        </form>
      </main>
    </div>
  );
}

export default App;

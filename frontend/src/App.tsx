import React, { useState, useEffect } from 'react';
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

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  useEffect(() => {
    // チャット履歴を取得
    const fetchChatHistory = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:8000/api/chat/history');
        setMessages(response.data);
        
        // レスポンスに会話IDが含まれている場合は保存
        const chatResponse = response.data.find((msg: any) => msg.conversation_id);
        if (chatResponse && chatResponse.conversation_id) {
          setConversationId(chatResponse.conversation_id);
        }
      } catch (error) {
        console.error('チャット履歴の取得に失敗しました:', error);
      } finally {
        setLoading(false);
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
      const response = await axios.post<ChatResponse>('http://localhost:8000/api/chat/send', {
        message: input,
        conversation_id: conversationId
      });
      
      // ボットの応答をUIに追加
      setMessages(prev => [...prev, { 
        role: response.data.role, 
        content: response.data.content 
      }]);
      
      // 会話IDを保存
      if (response.data.conversation_id) {
        setConversationId(response.data.conversation_id);
      }
    } catch (error) {
      console.error('メッセージの送信に失敗しました:', error);
    } finally {
      setLoading(false);
    }
  };

  const startNewConversation = async () => {
    try {
      setLoading(true);
      const response = await axios.post('http://localhost:8000/api/chat/new');
      setConversationId(response.data.conversation_id);
      setMessages([]);
    } catch (error) {
      console.error('新しい会話の作成に失敗しました:', error);
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

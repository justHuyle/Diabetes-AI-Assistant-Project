// frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import HealthBanner from './components/HealthBanner';
import ConsultForm from './components/ConsultForm';
import ChatPanel from './components/ChatPanel';
import { fetchHealth, sendConsultation } from './services/api';
import './App.css';

export default function App() {
  const [health, setHealth] = useState(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);

  // Tải trạng thái các mô hình từ backend
  const loadHealth = async () => {
    setHealthLoading(true);
    try {
      const data = await fetchHealth();
      setHealth(data);
    } catch (err) {
      console.warn('Lỗi khi kiểm tra health backend:', err);
      setHealth(null);
    } finally {
      setHealthLoading(false);
    }
  };

  useEffect(() => {
    loadHealth();
  }, []);

  // Xử lý gửi yêu cầu tư vấn tới API
  const handleConsultSubmit = async (payload) => {
    setLoading(true);

    const now = new Date();
    const timeStr = now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });

    // Tạo tin nhắn của người bệnh
    const userMsg = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: payload.message || 'Gửi hồ sơ chỉ số xét nghiệm lâm sàng',
      metrics: payload.metrics || null,
      timestamp: timeStr,
    };

    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await sendConsultation(payload);
      const assistantMsg = {
        id: `assistant-${Date.now()}`,
        sender: 'assistant',
        result: res,
        timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Lỗi khi gọi API consult:', err);
      const errorMsg = {
        id: `error-${Date.now()}`,
        sender: 'error',
        error: err,
        timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleSendChatMessage = (text) => {
    handleConsultSubmit({ message: text });
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  const handleRetryError = () => {
    const lastUserMsg = [...messages].reverse().find((m) => m.sender === 'user');
    if (lastUserMsg) {
      handleConsultSubmit({
        message: lastUserMsg.text,
        metrics: lastUserMsg.metrics,
      });
    }
  };

  return (
    <div className="app-container">
      <Header
        health={health}
        healthLoading={healthLoading}
        onRefreshHealth={loadHealth}
      />

      <main>
        {/* Dải kiểm tra thành phần mô hình */}
        <HealthBanner health={health} />

        {/* Bố cục hai cột bất đối xứng */}
        <div className="clinical-layout">
          {/* Cột trái hẹp: Hồ sơ chỉ số lâm sàng */}
          <aside className="layout-sidebar">
            <ConsultForm onSubmit={handleConsultSubmit} loading={loading} />
          </aside>

          {/* Cột phải rộng: Khung hội thoại tư vấn lâm sàng (Chatbot) */}
          <section className="layout-content">
            <ChatPanel
              messages={messages}
              loading={loading}
              onSendMessage={handleSendChatMessage}
              onClearChat={handleClearChat}
              onRetryError={handleRetryError}
            />
          </section>
        </div>
      </main>
    </div>
  );
}

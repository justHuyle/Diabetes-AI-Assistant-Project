// frontend/src/components/ChatPanel.jsx
import React, { useState, useRef, useEffect } from 'react';
import ResultsPanel from './ResultsPanel';
import ErrorState from './ErrorState';

export default function ChatPanel({
  messages = [],
  loading = false,
  onSendMessage,
  onClearChat,
  onRetryError,
}) {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);

  // Tự động cuộn xuống tin nhắn mới nhất
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim() || loading) return;
    onSendMessage(inputText.trim());
    setInputText('');
  };

  const handleQuickQuestion = (qText) => {
    if (loading) return;
    onSendMessage(qText);
  };

  return (
    <div className="chat-panel-wrapper">
      {/* 1. Thanh tiêu đề khung hội thoại */}
      <div className="chat-panel-header">
        <div className="chat-header-title-group">
          <h2 className="chat-panel-title">Hội Thoại Tư Vấn Lâm Sàng</h2>
          <span className="chat-assistant-status">
            <span className="status-indicator ready" /> 4 Tác tử sẵn sàng
          </span>
        </div>
        {messages.length > 0 && (
          <button
            type="button"
            className="btn-clear-chat"
            onClick={onClearChat}
            title="Xóa toàn bộ lịch sử hội thoại"
          >
            Làm mới hội thoại
          </button>
        )}
      </div>

      {/* 2. Luồng tin nhắn hội thoại */}
      <div className="chat-messages-stream">
        {messages.length === 0 ? (
          <div className="chat-welcome-card">
            <div className="welcome-badge">Trợ lý AI Đa Tác Tử (Clinical Multi-Agent)</div>
            <h3 className="welcome-title">Xin chào! Tôi là Trợ lý Hội chẩn &amp; Tư vấn Đái tháo đường.</h3>
            <p className="welcome-desc">
              Hệ thống kết hợp 4 tác tử chuyên môn: <strong>Dự báo nguy cơ (MLP ONNX)</strong>,{' '}
              <strong>Tri thức y khoa (RAG ADA/BYT)</strong>, <strong>Đề xuất lối sống (RL Q-Table)</strong> và{' '}
              <strong>Thẩm định an toàn lâm sàng (Rule-based)</strong> có quyền phủ quyết VETO.
            </p>

            <div className="welcome-guide-box">
              <div className="guide-heading">Cách thức tương tác:</div>
              <ul className="guide-list">
                <li>
                  <strong>Cách 1:</strong> Nhập các chỉ số xét nghiệm ở cột <em>"Hồ sơ chỉ số lâm sàng"</em> bên trái rồi bấm <strong>"Gửi Phiếu Tư Vấn"</strong> để nhận phân tích toàn diện.
                </li>
                <li>
                  <strong>Cách 2:</strong> Đặt câu hỏi trực tiếp vào ô chat bên dưới để tra cứu tiêu chuẩn và phác đồ y khoa.
                </li>
              </ul>
            </div>

            <div className="quick-suggestions-block">
              <div className="quick-suggestions-label">Gợi ý câu hỏi nhanh:</div>
              <div className="quick-chips-group">
                <button
                  type="button"
                  className="quick-chip-btn"
                  onClick={() =>
                    handleQuickQuestion(
                      'Tiêu chuẩn chẩn đoán đái tháo đường theo ADA (đường huyết lúc đói và HbA1c)'
                    )
                  }
                >
                  📖 Tiêu chuẩn chẩn đoán theo ADA
                </button>
                <button
                  type="button"
                  className="quick-chip-btn"
                  onClick={() =>
                    handleQuickQuestion(
                      'Cần xử trí khẩn cấp như thế nào khi đường huyết giảm sâu dưới 70 mg/dL?'
                    )
                  }
                >
                  🚨 Xử trí hạ đường huyết cấp cứu (&lt; 70 mg/dL)
                </button>
                <button
                  type="button"
                  className="quick-chip-btn"
                  onClick={() =>
                    handleQuickQuestion(
                      'Chế độ ăn giảm tinh bột và vận động thể lực cho người có nguy cơ tiền tiểu đường'
                    )
                  }
                >
                  🥗 Lối sống cho người tiền đái tháo đường
                </button>
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg) => {
            if (msg.sender === 'user') {
              return (
                <div key={msg.id} className="chat-message-row user-row">
                  <div className="chat-bubble user-bubble">
                    <div className="bubble-meta">
                      <span className="sender-badge user-badge">Người bệnh</span>
                      <span className="message-time">{msg.timestamp}</span>
                    </div>

                    {msg.text && <div className="user-message-text">{msg.text}</div>}

                    {msg.metrics && Object.keys(msg.metrics).length > 0 && (
                      <div className="user-metrics-summary-card">
                        <div className="metrics-card-header">Chỉ số xét nghiệm gửi kèm:</div>
                        <div className="metrics-tags-row">
                          {msg.metrics.age && (
                            <span className="metric-tag">Tuổi: {msg.metrics.age}</span>
                          )}
                          {msg.metrics.bmi && (
                            <span className="metric-tag">BMI: {msg.metrics.bmi}</span>
                          )}
                          {msg.metrics.hbA1c_level && (
                            <span className="metric-tag">HbA1c: {msg.metrics.hbA1c_level}%</span>
                          )}
                          {msg.metrics.blood_glucose_level && (
                            <span className="metric-tag highlight">
                              Đường huyết: {msg.metrics.blood_glucose_level}{' '}
                              {msg.metrics.glucose_unit || 'mg/dL'}
                            </span>
                          )}
                          {msg.metrics.hypertension === 1 && (
                            <span className="metric-tag alert">Tăng huyết áp</span>
                          )}
                          {msg.metrics.heart_disease === 1 && (
                            <span className="metric-tag alert">Bệnh tim</span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            }

            if (msg.sender === 'assistant' && msg.result) {
              const isChitchat = msg.result.intent === 'chitchat';
              const chitchatText =
                msg.result.knowledge_response?.content?.answer ||
                msg.result.summary;

              return (
                <div key={msg.id} className="chat-message-row assistant-row">
                  <div className="chat-bubble assistant-bubble">
                    <div className="bubble-meta">
                      <span className="sender-badge assistant-badge">
                        {isChitchat
                          ? 'Trợ Lý AI Lâm Sàng'
                          : 'Hệ Thống Hội Chẩn Đa Tác Tử'}
                      </span>
                      <span className="message-time">{msg.timestamp}</span>
                    </div>

                    {isChitchat ? (
                      <div className="chitchat-bubble-content">
                        <div className="chitchat-text-body">
                          {chitchatText.split('\n\n').map((paragraph, pIdx) => (
                            <p key={pIdx} style={{ margin: '0 0 10px 0' }}>
                              {paragraph}
                            </p>
                          ))}
                        </div>
                        <div className="chitchat-guide-footer">
                          <span className="hint-icon">💡</span>
                          <span>
                            Gợi ý: Bạn có thể nhập các chỉ số xét nghiệm ở cột bên trái hoặc hỏi về tiêu chuẩn đái tháo đường ADA/BYT để nhận phân tích chuyên sâu.
                          </span>
                        </div>
                      </div>
                    ) : (
                      /* Nhúng toàn bộ kết quả phân tích đa tác tử */
                      <ResultsPanel result={msg.result} isChat={true} />
                    )}
                  </div>
                </div>
              );
            }

            if (msg.sender === 'error') {
              return (
                <div key={msg.id} className="chat-message-row error-row">
                  <div className="chat-bubble error-bubble">
                    <div className="bubble-meta">
                      <span className="sender-badge error-badge">Lỗi hệ thống</span>
                      <span className="message-time">{msg.timestamp}</span>
                    </div>
                    <ErrorState error={msg.error} onRetry={onRetryError} />
                  </div>
                </div>
              );
            }

            return null;
          })
        )}

        {/* Trạng thái đang tải phản hồi của bot */}
        {loading && (
          <div className="chat-message-row assistant-row">
            <div className="chat-bubble assistant-bubble loading-bubble">
              <div className="bubble-meta">
                <span className="sender-badge assistant-badge">Hệ Thống Hội Chẩn Đa Tác Tử</span>
                <span className="message-time">Đang xử lý...</span>
              </div>
              <div className="chat-loading-content">
                <div className="loading-spinner-dots">
                  <span className="dot" />
                  <span className="dot" />
                  <span className="dot" />
                </div>
                <div className="loading-status-text">
                  Đang phân luồng và điều phối 4 tác tử chuyên môn (Prediction, Knowledge, Recommendation, Safety)...
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 3. Khung nhập liệu tin nhắn trò chuyện ở đáy */}
      <form className="chat-input-bar-form" onSubmit={handleSubmit}>
        <div className="chat-input-row">
          <input
            type="text"
            className="chat-input-field"
            placeholder="Nhập câu hỏi y khoa hoặc hướng dẫn cần tra cứu..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            className="btn-chat-send"
            disabled={loading || !inputText.trim()}
          >
            {loading ? 'Đang gửi...' : 'Gửi câu hỏi'}
          </button>
        </div>
        <div className="chat-disclaimer-footnote">
          Hệ thống hỗ trợ tư vấn dựa trên hướng dẫn ADA và Bộ Y tế. Không tự ý thay đổi phác đồ điều trị khi chưa có ý kiến của bác sĩ chuyên khoa.
        </div>
      </form>
    </div>
  );
}

// frontend/src/components/Header.jsx
import React from 'react';

export default function Header({ health, healthLoading, onRefreshHealth }) {
  const isHealthy = health?.status === 'healthy';
  const hasError = health && !isHealthy;

  return (
    <header className="app-header">
      <div className="container">
        <div className="header-top">
          <div className="app-title-group">
            <h1>Hệ Đa Agent Hỗ Trợ Tư Vấn Cho Bệnh Nhân Tiểu Đường</h1>
            <p>Học viện Công nghệ Bưu chính Viễn thông (PTIT) • Phát triển các hệ thống thông minh</p>
          </div>

          <div className="health-bar" title="Trạng thái hệ thống mô hình AI">
            <span
              className={`health-dot ${
                healthLoading ? 'warning' : isHealthy ? 'ready' : 'error'
              }`}
            />
            <span>
              {healthLoading
                ? 'Đang kết nối backend...'
                : isHealthy
                ? 'Hệ thống AI sẵn sàng'
                : 'Mô hình chưa sẵn sàng (503)'}
            </span>
            <button
              onClick={onRefreshHealth}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--color-primary)',
                cursor: 'pointer',
                fontSize: '12px',
                textDecoration: 'underline',
              }}
            >
              Làm mới
            </button>
          </div>
        </div>

        <div className="priority-badge-banner">
          ⚖️ Nguyên tắc phân giải xung đột: An toàn (Safety) &gt; Tri thức (Knowledge) &gt; Đề xuất (Recommendation) &gt; Dự đoán (Prediction)
        </div>
      </div>
    </header>
  );
}

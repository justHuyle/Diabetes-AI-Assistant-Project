// frontend/src/components/HealthBanner.jsx
import React from 'react';

export default function HealthBanner({ health }) {
  if (!health || !health.models) return null;

  const { models } = health;
  const modelLabels = {
    risk_model: 'Mô hình Dự đoán (ONNX MLP)',
    knowledge_base: 'Cơ sở Tri thức (MiniLM RAG)',
    rl_recommendation: 'Chính sách Đề xuất (RL Q-Table)',
    safety_rules: 'Hệ luật An toàn (Rules Engine)',
    gemini_api: 'Gemini API Sinh văn bản',
  };

  const hasMissingModel = Object.values(models).some(
    (status) => status !== 'ready' && status !== 'extractive_mode'
  );

  return (
    <div className="health-details-panel">
      <div>
        <strong style={{ fontSize: '13px', color: '#1e293b' }}>
          Trạng thái kiểm tra mô hình:
        </strong>
        {hasMissingModel && (
          <span style={{ color: 'var(--color-danger)', fontSize: '12px', marginLeft: '8px' }}>
            ⚠️ Phát hiện thành phần chưa sẵn sàng! Các yêu cầu liên quan sẽ trả HTTP 503.
          </span>
        )}
      </div>

      <div className="model-badges">
        {Object.entries(models).map(([key, status]) => {
          const isReady = status === 'ready';
          const isExtractive = status === 'extractive_mode';
          const className = isReady
            ? 'model-tag ready'
            : isExtractive
            ? 'model-tag extractive'
            : 'model-tag error';

          const label = modelLabels[key] || key;
          const statusText = isReady
            ? 'Sẵn sàng'
            : isExtractive
            ? 'Trích xuất (No Key)'
            : `Chưa nạp (${status})`;

          return (
            <span key={key} className={className} title={`${label}: ${statusText}`}>
              {label}: {statusText}
            </span>
          );
        })}
      </div>
    </div>
  );
}

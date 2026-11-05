// frontend/src/components/HealthBanner.jsx
import React from 'react';

export default function HealthBanner({ health }) {
  if (!health || !health.models) return null;

  const { models } = health;
  const labels = {
    risk_model: 'Dự báo nguy cơ (ONNX)',
    knowledge_base: 'Cơ sở tri thức (MiniLM RAG)',
    rl_recommendation: 'Chính sách lối sống (Q-Table)',
    safety_rules: 'Luật an toàn lâm sàng',
    gemini_api: 'Mô hình sinh câu trả lời',
  };

  const hasMissing = Object.entries(models).some(
    ([key, st]) => {
      if (key === 'gemini_api') {
        return st !== 'configured' && st !== 'extractive_mode' && st !== 'ready';
      }
      return st !== 'ready';
    }
  );

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '8px',
        padding: '6px 10px',
        background: '#FAF8F5',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-sm)',
        fontSize: '11px',
        marginBottom: '16px',
      }}
    >
      <div>
        <strong style={{ color: 'var(--color-text)' }}>Kiểm tra thành phần:</strong>{' '}
        {hasMissing && (
          <span style={{ color: 'var(--color-accent)' }}>
            [Lưu ý: Phát hiện thành phần chưa nạp, API sẽ trả HTTP 503 khi được gọi]
          </span>
        )}
      </div>

      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        {Object.entries(models).map(([key, st]) => {
          const isOk =
            st === 'ready' || st === 'configured' || st === 'extractive_mode';
          const txt =
            st === 'ready'
              ? 'Sẵn sàng'
              : st === 'configured'
              ? 'Gemini LLM (Sẵn sàng)'
              : st === 'extractive_mode'
              ? 'Trích xuất (No Key)'
              : `Lỗi (${st})`;
          return (
            <span
              key={key}
              style={{
                padding: '1px 5px',
                border: '1px solid',
                borderColor: isOk ? 'var(--color-border-dark)' : 'var(--color-accent)',
                borderRadius: 'var(--radius-sm)',
                background: isOk ? 'var(--color-surface)' : 'var(--color-accent-bg)',
                color: isOk ? 'var(--color-text)' : 'var(--color-accent)',
              }}
            >
              {labels[key] || key}: {txt}
            </span>
          );
        })}
      </div>
    </div>
  );
}

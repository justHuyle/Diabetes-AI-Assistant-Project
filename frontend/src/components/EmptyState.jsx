// frontend/src/components/EmptyState.jsx
import React from 'react';

export default function EmptyState() {
  return (
    <div className="empty-state">
      <div style={{ fontSize: '40px', marginBottom: '12px' }}>🩺</div>
      <h3>Chưa Có Yêu Cầu Tư Vấn Nào</h3>
      <p style={{ marginBottom: '16px' }}>
        Hệ thống tích hợp 4 tác tử AI chuyên biệt để hỗ trợ toàn diện:
      </p>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '12px',
          textAlign: 'left',
          marginTop: '16px',
        }}
      >
        <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
          <strong>🛡️ Agent An Toàn (Safety):</strong>
          <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>
            Nắm quyền phủ quyết VETO tuyệt đối. Giám sát hạ đường huyết &lt; 70 mg/dL, toan ceton &gt; 250 mg/dL, và chặn mọi yêu cầu kê đơn thuốc.
          </div>
        </div>

        <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
          <strong>📚 Agent Tri Thức (Knowledge):</strong>
          <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>
            Truy xuất thông tin y khoa chính thống từ tài liệu chuẩn Bộ Y tế Việt Nam và ADA (Extractive RAG).
          </div>
        </div>

        <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
          <strong>💡 Agent Đề Xuất (Recommendation):</strong>
          <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>
            Học tăng cường (RL Q-Table) gợi ý can thiệp lối sống (dinh dưỡng, vận động, đo đường huyết). Tuyệt đối không can thiệp thuốc.
          </div>
        </div>

        <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
          <strong>📊 Agent Dự Đoán (Prediction):</strong>
          <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>
            Mô hình phân loại Deep Learning MLP (ONNX) dự báo nguy cơ đái tháo đường với ngưỡng F1 tối ưu 0.87.
          </div>
        </div>
      </div>

      <div style={{ marginTop: '20px', fontSize: '13px', color: 'var(--color-primary)' }}>
        👉 <strong>Mẹo:</strong> Bạn có thể bấm vào một trong các <em>Kịch bản kiểm thử nhanh</em> ở cột bên trái để trải nghiệm ngay luồng hoạt động!
      </div>
    </div>
  );
}

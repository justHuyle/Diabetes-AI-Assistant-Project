// frontend/src/components/EmptyState.jsx
import React from 'react';

export default function EmptyState() {
  return (
    <div className="empty-sheet-view">
      <h3>Phiếu Tư Vấn Chưa Được Khởi Tạo</h3>
      <p style={{ fontSize: '13px', color: 'var(--color-text-muted)' }}>
        Nhập chỉ số của bệnh nhân tại cột bên trái hoặc chọn một trong các mẫu dữ liệu kiểm thử để tạo phiếu tư vấn.
      </p>

      <div style={{ marginTop: '16px', borderTop: '1px solid var(--color-border)', paddingTop: '12px' }}>
        <strong style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--color-text-dim)' }}>
          Quy trình tiếp nhận và phân giải:
        </strong>
        <ol className="empty-guide-list">
          <li>
            <strong>SafetyAgent (An toàn):</strong> Kiểm tra ngưỡng cấp cứu (đường huyết &lt; 70 mg/dL hoặc &gt; 250 mg/dL) và chặn yêu cầu kê đơn thuốc. Có quyền phủ quyết VETO cao nhất.
          </li>
          <li>
            <strong>KnowledgeAgent (Tri thức):</strong> Truy xuất nguyên văn từ Quyết định 5481/QĐ-BYT và ADA Standards. Mọi kết luận đều dẫn kèm nguồn và đoạn trích.
          </li>
          <li>
            <strong>RecommendationAgent (Lối sống):</strong> Tra cứu chính sách tối ưu (Q-table) về khẩu phần carbohydrate, vận động và lịch đo đường huyết.
          </li>
          <li>
            <strong>PredictionAgent (Dự báo nguy cơ):</strong> Mạng MLP (ONNX) dự báo xác suất đái tháo đường với ngưỡng F1 tối ưu 87%.
          </li>
        </ol>
      </div>

      <div style={{ marginTop: '14px', fontSize: '12px', fontStyle: 'italic', color: 'var(--color-text-muted)' }}>
        Lưu ý: Mọi số liệu và trích dẫn được trích xuất trực tiếp từ mô hình và cơ sở tri thức đã huấn luyện, không sử dụng dữ liệu giả định.
      </div>
    </div>
  );
}

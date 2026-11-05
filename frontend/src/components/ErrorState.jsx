// frontend/src/components/ErrorState.jsx
import React from 'react';

export default function ErrorState({ error, onRetry }) {
  if (!error) return null;

  const is503 = error.status === 503;
  const isConnectionRefused = error.status === 0;

  return (
    <div className="error-sheet-box">
      <h3>
        {is503
          ? 'Lỗi hệ thống: Mô hình AI chưa sẵn sàng (HTTP 503 Service Unavailable)'
          : isConnectionRefused
          ? 'Không thể kết nối đến máy chủ backend (Port 8000)'
          : `Lỗi xử lý yêu cầu (HTTP ${error.status || 'Chưa xác định'})`}
      </h3>

      <p>{error.message}</p>

      {is503 && (
        <div className="instruction-block">
          <strong>Căn cứ quy tắc docs/PROJECT_RULES.md:</strong>
          <ul style={{ paddingLeft: '18px', marginTop: '4px' }}>
            <li>Hệ thống từ chối sinh dữ liệu giả khi thiếu file trọng số mô hình hoặc cơ sở tri thức.</li>
            <li>Kiểm tra thư mục <code>models/</code> để xác nhận các tệp: <code>risk_model.onnx</code>, <code>scaler.json</code>, <code>feature_schema.json</code>, <code>kb_index/</code>, <code>rl_policy.npy</code>, <code>discretization.json</code>, <code>rules.yaml</code>.</li>
            <li>Theo dõi dòng kiểm tra thành phần ở đầu trang để biết module bị thiếu.</li>
          </ul>
        </div>
      )}

      {isConnectionRefused && (
        <div className="instruction-block">
          <strong>Quy trình khởi động dịch vụ:</strong>
          <ul style={{ paddingLeft: '18px', marginTop: '4px' }}>
            <li>Khởi động backend bằng lệnh: <code>uvicorn backend.app.main:app --port 8000</code></li>
            <li>Sau khi tiến trình backend hoàn tất nạp mô hình, nhấn nút [Thử lại] bên dưới.</li>
          </ul>
        </div>
      )}

      {onRetry && (
        <div style={{ marginTop: '12px' }}>
          <button type="button" className="btn-secondary-action" onClick={onRetry}>
            Thử lại
          </button>
        </div>
      )}
    </div>
  );
}

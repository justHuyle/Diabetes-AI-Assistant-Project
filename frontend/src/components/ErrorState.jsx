// frontend/src/components/ErrorState.jsx
import React from 'react';

export default function ErrorState({ error, onRetry }) {
  if (!error) return null;

  const is503 = error.status === 503;
  const isConnectionRefused = error.status === 0;

  return (
    <div className="error-card">
      <h3>
        {is503
          ? '⚠️ Lỗi 503: Hệ Thống Mô Hình Chưa Sẵn Sàng (Service Unavailable)'
          : isConnectionRefused
          ? '🔌 Không Thể Kết Nối Tới Máy Chủ Backend'
          : `❌ Lỗi Xử Lý (Mã HTTP ${error.status || 'Unknown'})`}
      </h3>

      <p>{error.message}</p>

      {is503 && (
        <div style={{ fontSize: '13px', background: '#fff', padding: '10px', borderRadius: '4px', border: '1px solid #fca5a5' }}>
          <strong>Hướng dẫn khắc phục:</strong>
          <ul style={{ paddingLeft: '18px', marginTop: '6px' }}>
            <li>Theo quy tắc <code>docs/PROJECT_RULES.md</code>, hệ thống tuyệt đối không sinh dữ liệu giả khi thiếu file mô hình hoặc checkpoint.</li>
            <li>Vui lòng kiểm tra thư mục <code>models/</code> để chắc chắn các tệp <code>risk_model.onnx</code>, <code>scaler.json</code>, <code>feature_schema.json</code>, <code>kb_index/</code>, <code>rl_policy.npy</code>, <code>discretization.json</code>, <code>rules.yaml</code> đã tồn tại đầy đủ.</li>
            <li>Xem thông báo chi tiết tại thanh trạng thái mô hình trên đầu trang để biết chính xác module nào gặp sự cố.</li>
          </ul>
        </div>
      )}

      {isConnectionRefused && (
        <div style={{ fontSize: '13px', background: '#fff', padding: '10px', borderRadius: '4px', border: '1px solid #fca5a5' }}>
          <strong>Hướng dẫn khởi động Backend:</strong>
          <ul style={{ paddingLeft: '18px', marginTop: '6px' }}>
            <li>Mở một cửa sổ dòng lệnh tại thư mục gốc của dự án.</li>
            <li>Kích hoạt môi trường ảo: <code>.\.venv\Scripts\Activate.ps1</code></li>
            <li>Chạy lệnh uvicorn: <code>uvicorn backend.app.main:app --port 8000</code></li>
            <li>Sau khi backend khởi động xong, bấm nút "Thử lại" bên dưới.</li>
          </ul>
        </div>
      )}

      {onRetry && (
        <button
          type="button"
          className="btn-secondary"
          onClick={onRetry}
          style={{ marginTop: '12px' }}
        >
          🔄 Thử lại
        </button>
      )}
    </div>
  );
}

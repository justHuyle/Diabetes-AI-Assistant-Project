// frontend/src/components/LoadingState.jsx
import React from 'react';

export default function LoadingState() {
  return (
    <div className="loading-state">
      <div className="spinner" />
      <h3>Đang Điều Phối Các Tác Tử AI...</h3>
      <p>
        Điều phối viên đang phân loại ý định, truy xuất cơ sở tri thức (RAG), tra cứu chính sách lối sống (RL Q-Table) và tính toán nguy cơ (MLP ONNX). Agent An toàn sẽ kiểm duyệt lần cuối trước khi trả kết quả.
      </p>
    </div>
  );
}

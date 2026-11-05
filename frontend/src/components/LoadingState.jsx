// frontend/src/components/LoadingState.jsx
import React from 'react';

export default function LoadingState() {
  return (
    <div className="loading-sheet-view">
      <div className="loading-simple-text">Đang phân tích và điều phối dữ liệu...</div>
      <p style={{ fontSize: '13px', marginTop: '6px' }}>
        Tác tử điều phối đang đối chiếu các quy tắc an toàn lâm sàng, tra cứu tài liệu Bộ Y tế và tính toán chỉ số rủi ro.
      </p>
    </div>
  );
}

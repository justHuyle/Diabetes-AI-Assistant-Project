// frontend/src/components/Header.jsx
import React, { useState } from 'react';
import DoctorContactModal from './DoctorContactModal';

export default function Header({ health, healthLoading, onRefreshHealth }) {
  const [doctorModalOpen, setDoctorModalOpen] = useState(false);
  const isHealthy = health?.status === 'healthy';

  return (
    <header className="clinic-header">
      <div className="clinic-header-top">
        <div className="clinic-title-row">
          <h1 className="clinic-title">Hồ Sơ Tư Vấn Lâm Sàng Bệnh Nhân Đái Tháo Đường</h1>
          <span className="clinic-meta">
            Phần mềm ghi nhận chỉ số &amp; hỗ trợ quyết định lâm sàng đa tác tử • PTIT
          </span>
        </div>

        <div className="clinic-header-actions-group">
          <button
            type="button"
            className="btn-header-doctor-contact"
            onClick={() => setDoctorModalOpen(true)}
            title="Xem danh bạ và kết nối Bác sĩ chuyên khoa"
          >
            👨‍⚕️ Danh bạ Bác sĩ
          </button>

          <div className="clinic-health-status">
            <span
              className={`status-indicator ${
                healthLoading ? 'error' : isHealthy ? 'ready' : 'error'
              }`}
            />
            <span>
              {healthLoading
                ? 'Đang kiểm tra kết nối...'
                : isHealthy
                ? 'Hệ thống: Sẵn sàng'
                : 'Hệ thống: Chưa sẵn sàng (HTTP 503)'}
            </span>
            <button
              type="button"
              className="btn-link-action"
              onClick={onRefreshHealth}
              title="Kiểm tra lại trạng thái các module"
            >
              [Kiểm tra lại]
            </button>
          </div>
        </div>
      </div>

      <div className="priority-rule-bar">
        <span>
          <strong>Nguyên tắc phân giải xung đột:</strong> An toàn lâm sàng &gt; Tri thức chuẩn &gt; Đề xuất lối sống &gt; Dự báo nguy cơ
        </span>
        <span className="clinic-meta">Quy định y khoa số 5481/QĐ-BYT &amp; ADA Standards</span>
      </div>

      <DoctorContactModal
        isOpen={doctorModalOpen}
        onClose={() => setDoctorModalOpen(false)}
      />
    </header>
  );
}

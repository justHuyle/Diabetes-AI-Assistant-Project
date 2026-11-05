// frontend/src/components/DoctorContactModal.jsx
import React, { useState, useEffect } from 'react';

const FALLBACK_DOCTORS = [
  {
    id: 'doc_bm_01',
    name: 'PGS. TS. BS. Nguyễn Khoa Diệu Vân',
    title: 'Nguyên Trưởng khoa Nội tiết - Đái tháo đường',
    facility: 'Khoa Nội tiết - Đái tháo đường, Bệnh viện Bạch Mai (Hà Nội)',
    phone: '024.3869.3731',
    available_hours: '07:30 - 17:00 (Thứ 2 - Thứ 6)',
  },
  {
    id: 'doc_dhy_02',
    name: 'PGS. TS. BS. Đỗ Trung Quân',
    title: 'Chủ tịch Hội Nội tiết & Đái tháo đường Hà Nội, Bệnh viện ĐHY Hà Nội',
    facility: 'Phòng khám Đa khoa, Bệnh viện Đại học Y Hà Nội',
    phone: '1900.6422',
    available_hours: '07:00 - 16:30 (Thứ 2 - Thứ 7)',
  },
  {
    id: 'doc_cr_03',
    name: 'TS. BS. Lâm Văn Hoàng',
    title: 'Trưởng khoa Nội tiết, Bệnh viện Chợ Rẫy',
    facility: 'Khoa Nội tiết, Bệnh viện Chợ Rẫy (TP. Hồ Chí Minh)',
    phone: '028.3855.4137',
    available_hours: '07:00 - 16:00 (Thứ 2 - Thứ 6)',
  },
  {
    id: 'emergency_hotline',
    name: 'Tổng đài Cấp cứu Y tế Ngoại viện',
    title: 'Trực ban Cấp cứu 24/7 (Đường huyết <70 mg/dL hoặc >250 mg/dL)',
    facility: 'Mạng lưới Cấp cứu Y tế 115 Toàn quốc',
    phone: '115',
    available_hours: '24/24h hàng ngày',
  },
];

export default function DoctorContactModal({
  isOpen,
  onClose,
  consultResult,
  userMetrics = null,
}) {
  const [doctors, setDoctors] = useState(FALLBACK_DOCTORS);
  const [selectedFacility, setSelectedFacility] = useState(FALLBACK_DOCTORS[0].facility);
  const [patientName, setPatientName] = useState('');
  const [patientPhone, setPatientPhone] = useState('');
  const [patientNotes, setPatientNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState(null);
  const [copied, setCopied] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Nạp danh bạ bác sĩ từ backend nếu có
  useEffect(() => {
    fetch('/api/doctors')
      .then((res) => res.json())
      .then((data) => {
        if (data && data.doctors && data.doctors.length > 0) {
          setDoctors(data.doctors);
          setSelectedFacility(data.doctors[0].facility);
        }
      })
      .catch(() => {
        // Fallback đã có sẵn
      });
  }, []);

  if (!isOpen) return null;

  const isEmergency = Boolean(
    consultResult?.emergency_detected ||
    consultResult?.safety_review?.status === 'VETO'
  );

  // Tạo nội dung tóm tắt lâm sàng
  const buildClinicalSummary = () => {
    const lines = [];
    if (consultResult?.consultation_id) {
      lines.push(`Mã phiên tư vấn AI: ${consultResult.consultation_id}`);
    }
    if (userMetrics) {
      const parts = [];
      if (userMetrics.age) parts.push(`Tuổi: ${userMetrics.age}`);
      if (userMetrics.gender) parts.push(`Giới: ${userMetrics.gender}`);
      if (userMetrics.bmi) parts.push(`BMI: ${userMetrics.bmi}`);
      if (userMetrics.blood_glucose_level) {
        parts.push(`Đường huyết: ${userMetrics.blood_glucose_level} ${userMetrics.glucose_unit || 'mg/dL'}`);
      }
      if (userMetrics.hbA1c_level) parts.push(`HbA1c: ${userMetrics.hbA1c_level}%`);
      if (parts.length > 0) lines.push(`Chỉ số xét nghiệm: ${parts.join(' | ')}`);
    }
    if (consultResult?.prediction_response?.content?.risk_category) {
      lines.push(`Dự báo rủi ro: ${consultResult.prediction_response.content.risk_category} (Xác suất: ${(consultResult.prediction_response.content.risk_probability * 100).toFixed(1)}%)`);
    }
    if (consultResult?.summary) {
      lines.push(`Tóm tắt thẩm định AI: ${consultResult.summary}`);
    }
    return lines.join('\n');
  };

  const clinicalSummaryText = buildClinicalSummary();

  const handleCopySummary = () => {
    navigator.clipboard.writeText(clinicalSummaryText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!patientPhone.trim() || patientPhone.trim().length < 8) {
      setErrorMsg('Vui lòng nhập số điện thoại liên hệ hợp lệ (tối thiểu 8 số).');
      return;
    }
    setErrorMsg('');
    setSubmitting(true);

    try {
      const payload = {
        consultation_id: consultResult?.consultation_id || null,
        patient_name: patientName.trim() || 'Bệnh nhân',
        patient_phone: patientPhone.trim(),
        facility_or_doctor: selectedFacility,
        patient_notes: patientNotes.trim(),
        clinical_summary: clinicalSummaryText,
        is_emergency: isEmergency,
      };

      const res = await fetch('/api/doctor/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Không thể gửi yêu cầu liên hệ.');
      }

      const data = await res.json();
      setSubmitResult(data);
    } catch (err) {
      setErrorMsg(err.message || 'Đã xảy ra lỗi khi gửi yêu cầu.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-backdrop-overlay" onClick={onClose}>
      <div className="doctor-contact-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header Modal */}
        <div className="modal-header-bar">
          <div className="modal-title-group">
            <h3 className="modal-main-title">Chuyển Tiếp Hồ Sơ &amp; Liên Hệ Bác Sĩ Chuyên Khoa</h3>
            <span className="modal-subtitle">
              Kết nối trực tiếp chuyên môn y tế • Bệnh viện Bạch Mai &amp; Bệnh viện ĐHY
            </span>
          </div>
          <button type="button" className="btn-close-modal" onClick={onClose} title="Đóng">
            &times;
          </button>
        </div>

        {/* Nội dung Modal */}
        <div className="modal-body-content">
          {/* Cảnh báo cấp cứu nếu có VETO */}
          {isEmergency && (
            <div className="modal-emergency-banner">
              <div className="banner-alert-title">🚨 CẢNH BÁO TÌNH HUỐNG CẤP CỨU LÂM SÀNG!</div>
              <p>
                Chỉ số đường huyết của bạn đang ở ngưỡng đe dọa sinh mạng (&lt; 70 mg/dL hoặc &gt; 250 mg/dL).
                Người nhà cần <strong>GỌI NGAY CẤP CỨU 115</strong> hoặc đưa người bệnh đến khoa Cấp cứu gần nhất!
              </p>
              <div style={{ marginTop: '8px' }}>
                <a href="tel:115" className="btn-call-emergency">
                  📞 Gọi Ngay Cấp Cứu 115
                </a>
              </div>
            </div>
          )}

          {submitResult ? (
            <div className="contact-success-card">
              <div className="success-icon-badge">✓</div>
              <h4 className="success-heading">{submitResult.message}</h4>
              <p className="success-instruction">{submitResult.instructions}</p>
              <div className="referral-code-box">
                Mã tiếp nhận hồ sơ bệnh án:{' '}
                <strong className="numeral">{submitResult.referral_id}</strong>
              </div>
              <div style={{ marginTop: '16px', display: 'flex', gap: '8px', justifyContent: 'center' }}>
                <button type="button" className="btn-primary-action" onClick={onClose}>
                  Đã hiểu &amp; Đóng cửa sổ
                </button>
                <button type="button" className="btn-secondary-action" onClick={handleCopySummary}>
                  {copied ? '✓ Đã sao chép bệnh án' : 'Sao chép tóm tắt bệnh án'}
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              {/* Thẻ tóm tắt lâm sàng đã lập */}
              <div className="clinical-summary-preview">
                <div className="preview-header-row">
                  <strong>Tóm tắt hồ sơ đính kèm gửi Bác sĩ:</strong>
                  <button
                    type="button"
                    className="btn-link-action"
                    onClick={handleCopySummary}
                    title="Sao chép toàn bộ tóm tắt để dán vào Zalo/Email"
                  >
                    {copied ? '✓ Đã sao chép' : '📋 Sao chép tóm tắt'}
                  </button>
                </div>
                <div className="preview-text-box">{clinicalSummaryText}</div>
              </div>

              {/* Lựa chọn bác sĩ / cơ sở tiếp nhận */}
              <div className="form-item" style={{ marginTop: '12px' }}>
                <label htmlFor="doctor-select">Đơn vị / Chuyên gia Nội tiết tiếp nhận:</label>
                <select
                  id="doctor-select"
                  className="input-box"
                  value={selectedFacility}
                  onChange={(e) => setSelectedFacility(e.target.value)}
                >
                  {doctors.map((doc) => (
                    <option key={doc.id} value={doc.facility}>
                      {doc.facility} — {doc.name} ({doc.phone})
                    </option>
                  ))}
                </select>
              </div>

              {/* Thông tin liên hệ bệnh nhân */}
              <div className="form-grid-two-cols" style={{ marginTop: '10px' }}>
                <div className="form-item">
                  <label htmlFor="patient-name">Họ và tên người bệnh:</label>
                  <input
                    id="patient-name"
                    type="text"
                    className="input-box"
                    placeholder="Ví dụ: Nguyễn Văn A"
                    value={patientName}
                    onChange={(e) => setPatientName(e.target.value)}
                  />
                </div>
                <div className="form-item">
                  <label htmlFor="patient-phone">
                    Số điện thoại liên hệ <span className="req">*</span>:
                  </label>
                  <input
                    id="patient-phone"
                    type="tel"
                    className="input-box numeral"
                    placeholder="Ví dụ: 0912345678"
                    value={patientPhone}
                    onChange={(e) => setPatientPhone(e.target.value)}
                    required
                  />
                </div>
              </div>

              {/* Lời nhắn / Triệu chứng bổ sung */}
              <div className="form-item" style={{ marginTop: '10px' }}>
                <label htmlFor="patient-notes">Lời nhắn / Triệu chứng muốn hỏi thêm Bác sĩ:</label>
                <textarea
                  id="patient-notes"
                  rows={2}
                  className="input-box"
                  placeholder="Ví dụ: Tôi thấy chóng mặt và đói cồn cào từ lúc sáng, nhờ bác sĩ tư vấn giúp..."
                  value={patientNotes}
                  onChange={(e) => setPatientNotes(e.target.value)}
                />
              </div>

              {errorMsg && <div className="field-error-text" style={{ marginTop: '8px' }}>{errorMsg}</div>}

              {/* Hàng nút gửi */}
              <div className="modal-actions-row">
                <button type="submit" className="btn-primary-action" disabled={submitting}>
                  {submitting ? 'Đang chuyển hồ sơ...' : 'Gửi Hồ Sơ Tới Bác Sĩ'}
                </button>
                <button type="button" className="btn-secondary-action" onClick={onClose}>
                  Hủy bỏ
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

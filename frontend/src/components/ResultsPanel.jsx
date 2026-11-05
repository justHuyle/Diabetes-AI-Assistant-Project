// frontend/src/components/ResultsPanel.jsx
import React, { useState } from 'react';

// Dải tham chiếu đường huyết lâm sàng bằng SVG phẳng
function GlucoseRangeBar({ glucoseMgDl }) {
  if (!glucoseMgDl || isNaN(glucoseMgDl)) return null;

  // Giới hạn hiển thị trên trục từ 40 đến 320 mg/dL
  const minVal = 40;
  const maxVal = 320;
  const clamped = Math.max(minVal, Math.min(maxVal, glucoseMgDl));
  const posX = ((clamped - minVal) / (maxVal - minVal)) * 500;

  // Tọa độ các mốc
  const x70 = ((70 - minVal) / (maxVal - minVal)) * 500;
  const x130 = ((130 - minVal) / (maxVal - minVal)) * 500;
  const x180 = ((180 - minVal) / (maxVal - minVal)) * 500;
  const x250 = ((250 - minVal) / (maxVal - minVal)) * 500;

  return (
    <div className="visual-metric-wrapper">
      <div className="visual-metric-title">
        Vị trí đường huyết đo được ({glucoseMgDl.toFixed(1)} mg/dL) trên dải tham chiếu lâm sàng:
      </div>
      <svg className="svg-horizontal-bar" viewBox="0 0 500 52" preserveAspectRatio="none">
        {/* Vùng < 70 (Hạ đường huyết) */}
        <rect x="0" y="12" width={x70} height="12" fill="#FDF3F0" stroke="#DDD8CE" strokeWidth="1" />
        {/* Vùng 70-130 (Mục tiêu lúc đói) */}
        <rect x={x70} y="12" width={x130 - x70} height="12" fill="#F1F6F2" stroke="#DDD8CE" strokeWidth="1" />
        {/* Vùng 130-180 (Sau ăn chấp nhận) */}
        <rect x={x130} y="12" width={x180 - x130} height="12" fill="#FAF8F5" stroke="#DDD8CE" strokeWidth="1" />
        {/* Vùng 180-250 (Tăng cao) */}
        <rect x={x180} y="12" width={x250 - x180} height="12" fill="#FFF9E6" stroke="#DDD8CE" strokeWidth="1" />
        {/* Vùng > 250 (Nguy cơ toan ceton) */}
        <rect x={x250} y="12" width={500 - x250} height="12" fill="#FDF3F0" stroke="#DDD8CE" strokeWidth="1" />

        {/* Nhãn khoảng trực tiếp */}
        <text x="4" y="34" fontSize="9" fill="#575D58" fontFamily="IBM Plex Sans">Hạ (&lt;70)</text>
        <text x={x70 + 4} y="34" fontSize="9" fill="#4A6B53" fontFamily="IBM Plex Sans" fontWeight="600">Mục tiêu (70-130)</text>
        <text x={x130 + 4} y="34" fontSize="9" fill="#575D58" fontFamily="IBM Plex Sans">Sau ăn (130-180)</text>
        <text x={x180 + 4} y="34" fontSize="9" fill="#575D58" fontFamily="IBM Plex Sans">Cao (180-250)</text>
        <text x={x250 + 4} y="34" fontSize="9" fill="#B4472A" fontFamily="IBM Plex Sans" fontWeight="600">Toan ceton (&gt;250)</text>

        {/* Điểm chỉ thị của bệnh nhân */}
        <line x1={posX} y1="4" x2={posX} y2="30" stroke="#1F2421" strokeWidth="2" />
        <polygon points={`${posX-4},4 ${posX+4},4 ${posX},10`} fill="#1F2421" />
        <text
          x={Math.max(10, Math.min(430, posX - 20))}
          y="46"
          fontSize="10"
          fill="#1F2421"
          fontWeight="700"
          fontFamily="IBM Plex Sans"
        >
          {glucoseMgDl.toFixed(1)} mg/dL
        </text>
      </svg>
    </div>
  );
}

// Thanh ngang SVG phân vị xác suất nguy cơ đái tháo đường
function RiskProbabilityBar({ probability, threshold = 0.87 }) {
  if (probability === undefined || probability === null) return null;

  const p = Math.max(0, Math.min(1, probability));
  const posX = p * 500;
  const threshX = threshold * 500;
  const isHigh = p >= threshold;

  return (
    <div className="visual-metric-wrapper">
      <div className="visual-metric-title">
        Thang đo xác suất mô hình MLP ({ (p * 100).toFixed(1) }%):
      </div>
      <svg className="svg-horizontal-bar" viewBox="0 0 500 48" preserveAspectRatio="none">
        {/* Nền thanh đo */}
        <rect x="0" y="10" width="500" height="10" fill="#FAF8F5" stroke="#DDD8CE" strokeWidth="1" />
        {/* Vùng nguy cơ cao sau ngưỡng */}
        <rect x={threshX} y="10" width={500 - threshX} height="10" fill="#FDF3F0" stroke="#DDD8CE" strokeWidth="1" />

        {/* Vạch chia ngưỡng quyết định 87% */}
        <line x1={threshX} y1="6" x2={threshX} y2="24" stroke="#B4472A" strokeWidth="1.5" strokeDasharray="2 2" />
        <text x={threshX - 45} y="32" fontSize="9" fill="#B4472A" fontWeight="600" fontFamily="IBM Plex Sans">
          Ngưỡng F1 (87%)
        </text>

        {/* Vị trí xác suất của bệnh nhân */}
        <circle cx={posX} cy="15" r="5" fill={isHigh ? '#B4472A' : '#4A6B53'} stroke="#1F2421" strokeWidth="1.5" />
        <text
          x={Math.max(4, Math.min(420, posX - 25))}
          y="42"
          fontSize="10"
          fill="#1F2421"
          fontWeight="700"
          fontFamily="IBM Plex Sans"
        >
          Xác suất: {(p * 100).toFixed(1)}%
        </text>
      </svg>
    </div>
  );
}

export default function ResultsPanel({ result, isChat = false }) {
  const [showTrace, setShowTrace] = useState(false);
  const [expandedSidenotes, setExpandedSidenotes] = useState({});

  if (!result) return null;

  const {
    consultation_id,
    intent,
    status,
    priority_order,
    emergency_detected,
    emergency_alert,
    summary,
    safety_review,
    knowledge_response,
    recommendation_response,
    prediction_response,
    trace,
  } = result;

  const toggleSidenote = (idx) => {
    setExpandedSidenotes((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  const glucoseVal =
    recommendation_response?.content?.state_mapping?.glucose_evaluated_mg_dl ??
    prediction_response?.content?.clinical_metrics_evaluated?.blood_glucose_level_mg_dl;

  return (
    <div className={`consult-sheet ${isChat ? 'in-chat' : ''}`}>
      {/* 1. ĐẦU PHIẾU TƯ VẤN */}
      <div className="sheet-header">
        <div className="sheet-header-top">
          <h2 className="sheet-title">Phiếu Ghi Nhận &amp; Quyết Định Tư Vấn Lâm Sàng</h2>
          <span
            className={`status-text-badge ${
              status === 'VETO' ? 'veto' : status === 'MODIFY' ? 'modify' : 'pass'
            }`}
          >
            Trạng thái: {status}
          </span>
        </div>

        <div className="sheet-meta-row">
          <span>
            Mã lưu vết: <code className="numeral">{consultation_id}</code>
          </span>
          <span>Phân loại ý định: {intent}</span>
        </div>

        <div className="sheet-disclaimer-inline">
          Lưu ý nghiệp vụ: Phiếu tư vấn có tính chất hỗ trợ chuyên môn, không thay thế chẩn đoán và chỉ định trực tiếp của bác sĩ điều trị.
        </div>
      </div>

      {/* 2. CẢNH BÁO AN TOÀN / CẤP CỨU (XUẤT HIỆN NGAY TRÊN ĐẦU PHIẾU) */}
      {emergency_detected && (
        <div className="clinical-alert-box">
          <div className="alert-heading">Cảnh báo cấp cứu y tế: Hạ đường huyết nguy hiểm</div>
          <div className="alert-body">
            {emergency_alert ||
              'Nồng độ glucose huyết ở mức đe dọa sinh mạng. Bệnh nhân cần được xử trí cấp cứu theo Quy tắc 15-15 ngay lập tức.'}
          </div>
        </div>
      )}

      {/* 3. MỤC: AGENT AN TOÀN (SAFETY REVIEW) */}
      <div className="sheet-section">
        <div className="section-label-bar">
          <div className="section-agent-title">1. Thẩm định An toàn Lâm sàng (SafetyAgent)</div>
          <span
            className={`status-text-badge ${
              safety_review?.status === 'VETO'
                ? 'veto'
                : safety_review?.status === 'MODIFY'
                ? 'modify'
                : 'pass'
            }`}
          >
            Kết quả: {safety_review?.status || (emergency_detected ? 'VETO' : 'PASS')}
          </span>
        </div>

        <div style={{ fontSize: '13px', lineHeight: '1.6' }}>
          {safety_review?.status === 'VETO' ? (
            <p style={{ color: 'var(--color-accent)', fontWeight: '600' }}>
              Quyền phủ quyết VETO đã kích hoạt. Hệ thống chặn hoặc đình chỉ can thiệp để bảo đảm an toàn sinh mạng.
            </p>
          ) : safety_review?.status === 'MODIFY' ? (
            <p style={{ color: '#8C5300', fontWeight: '500' }}>
              Phát hiện chống chỉ định y khoa. Các đề xuất lối sống đã được hiệu chỉnh tự động trước khi xuất phiếu.
            </p>
          ) : (
            <p style={{ color: 'var(--color-olive)' }}>
              Đạt tiêu chuẩn an toàn lâm sàng theo Quyết định 5481/QĐ-BYT. Không có chống chỉ định nguy hiểm.
            </p>
          )}

          {safety_review?.triggered_rules?.length > 0 && (
            <div style={{ marginTop: '6px' }}>
              <strong>Luật y khoa kích hoạt:</strong>{' '}
              {safety_review.triggered_rules.map((rule, idx) => (
                <span
                  key={idx}
                  style={{
                    display: 'inline-block',
                    background: '#FAF8F5',
                    border: '1px solid var(--color-border)',
                    padding: '1px 5px',
                    fontSize: '11px',
                    marginRight: '4px',
                    borderRadius: '2px',
                    fontFamily: 'monospace',
                  }}
                >
                  {rule}
                </span>
              ))}
            </div>
          )}

          {safety_review?.modifications_made?.length > 0 && (
            <div style={{ marginTop: '6px' }}>
              <strong>Hiệu chỉnh bắt buộc từ Agent An toàn:</strong>
              <ul style={{ paddingLeft: '18px', marginTop: '2px', color: 'var(--color-accent)' }}>
                {safety_review.modifications_made.map((mod, idx) => (
                  <li key={idx}>{mod}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Dải tham chiếu đường huyết nếu có số liệu */}
          {glucoseVal && <GlucoseRangeBar glucoseMgDl={glucoseVal} />}
        </div>
      </div>

      {/* 4. MỤC: AGENT TRI THỨC (KNOWLEDGE AGENT & SIDENOTES) */}
      {knowledge_response && (
        <div className="sheet-section">
          <div className="section-label-bar">
            <div className="section-agent-title">2. Căn cứ Tri thức Y khoa (KnowledgeAgent)</div>
            <span className="clinic-meta numeral">
              Độ tương đồng: {((knowledge_response.confidence ?? 0) * 100).toFixed(1)}%
            </span>
          </div>

          <div className="knowledge-section-layout">
            {/* Cột nội dung trích xuất chính */}
            <div className="knowledge-main-content">
              {knowledge_response.content?.answer ||
                knowledge_response.content?.message ||
                'Chưa có nội dung phản hồi từ tài liệu chuẩn.'}
            </div>

            {/* Cột chú thích lề phải (sidenotes) */}
            <div className="marginalia-sidenotes">
              <div className="sidenote-header">Tài liệu dẫn chiếu:</div>
              {knowledge_response.content?.citations?.length > 0 ? (
                knowledge_response.content.citations.map((cite, idx) => (
                  <div key={idx} className="sidenote-item">
                    <div className="sidenote-title">
                      [{idx + 1}] {cite.source_file || cite.doc_id}
                    </div>
                    {cite.section_or_page && (
                      <div style={{ fontSize: '10px', color: 'var(--color-text-dim)' }}>
                        {cite.section_or_page}
                      </div>
                    )}
                    <span className="sidenote-score numeral">
                      Cosine: {(cite.similarity_score ?? 0).toFixed(4)}
                    </span>

                    <div>
                      <button
                        type="button"
                        className="btn-link-action"
                        onClick={() => toggleSidenote(idx)}
                      >
                        {expandedSidenotes[idx] ? '[Thu gọn đoạn gốc]' : '[Xem đoạn gốc]'}
                      </button>
                    </div>

                    {expandedSidenotes[idx] && (
                      <div className="sidenote-excerpt-box">
                        "{cite.excerpt || cite.chunk_text || cite.text}"
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div style={{ fontStyle: 'italic' }}>Không có trích dẫn bổ sung.</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 5. MỤC: AGENT ĐỀ XUẤT LỐI SỐNG (RECOMMENDATION AGENT) */}
      {recommendation_response && (
        <div className="sheet-section">
          <div className="section-label-bar">
            <div className="section-agent-title">3. Đề xuất Can thiệp Lối sống (RecommendationAgent)</div>
            <span className="clinic-meta numeral">
              Độ tin cậy Q-table: {((recommendation_response.confidence ?? 0) * 100).toFixed(1)}%
            </span>
          </div>

          {recommendation_response.content?.lifestyle_plan ? (
            <div>
              <table className="lifestyle-plan-table">
                <thead>
                  <tr>
                    <th>Trụ cột can thiệp</th>
                    <th>Chỉ định cụ thể</th>
                    <th>Căn cứ lâm sàng &amp; Lý do giải thích</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="pillar-name">Dinh dưỡng (Carbohydrate)</td>
                    <td>
                      <strong>
                        {recommendation_response.content.lifestyle_plan.nutrition?.label ||
                          recommendation_response.content.lifestyle_plan.nutrition?.level}
                      </strong>
                    </td>
                    <td>
                      {recommendation_response.content.lifestyle_plan.nutrition?.rationale}
                    </td>
                  </tr>
                  <tr>
                    <td className="pillar-name">Vận động thể lực</td>
                    <td>
                      <strong>
                        {recommendation_response.content.lifestyle_plan.exercise?.label ||
                          recommendation_response.content.lifestyle_plan.exercise?.level}
                      </strong>
                    </td>
                    <td>
                      {recommendation_response.content.lifestyle_plan.exercise?.rationale}
                    </td>
                  </tr>
                  <tr>
                    <td className="pillar-name">Theo dõi đường huyết</td>
                    <td>
                      <strong>
                        {recommendation_response.content.lifestyle_plan.monitoring?.required
                          ? 'Bắt buộc đo lại'
                          : 'Định kỳ thông thường'}
                      </strong>
                    </td>
                    <td>
                      {recommendation_response.content.lifestyle_plan.monitoring?.rationale}
                    </td>
                  </tr>
                </tbody>
              </table>

              <div
                style={{
                  marginTop: '8px',
                  fontSize: '11px',
                  color: 'var(--color-text-muted)',
                  fontStyle: 'italic',
                }}
              >
                Giới hạn nghiệp vụ: {recommendation_response.content.disclaimer}
              </div>
            </div>
          ) : (
            <p style={{ color: 'var(--color-text-muted)', fontSize: '13px' }}>
              Chưa có đường huyết lúc đói. Nhập ở cột trái để luật an toàn kiểm tra và mô hình đề xuất lối sống.
            </p>
          )}
        </div>
      )}

      {/* 6. MỤC: AGENT DỰ ĐOÁN NGUY CƠ (PREDICTION AGENT) */}
      {prediction_response && (
        <div className="sheet-section">
          <div className="section-label-bar">
            <div className="section-agent-title">4. Đánh giá Nguy cơ Đái tháo đường (PredictionAgent)</div>
            <span
              className={`status-text-badge ${
                prediction_response.content?.is_high_risk ? 'veto' : 'pass'
              }`}
            >
              {prediction_response.content?.is_high_risk ? 'Nguy cơ cao' : 'Nguy cơ thấp'}
            </span>
          </div>

          <div style={{ fontSize: '13px', lineHeight: '1.6' }}>
            <p>
              Mô hình mạng nơ-ron đa tầng MLP (ONNX) ước lượng xác suất mắc bệnh là{' '}
              <strong className="numeral">
                {(
                  (prediction_response.content?.risk_probability ??
                    prediction_response.content?.probability ??
                    prediction_response.confidence) * 100
                ).toFixed(2)}
                %
              </strong>
              , so với ngưỡng phân loại F1 tối ưu{' '}
              <code className="numeral">
                {(
                  (prediction_response.content?.decision_threshold ?? 0.87) * 100
                ).toFixed(0)}
                %
              </code>
              .
            </p>

            {/* Thanh ngang SVG phân vị xác suất */}
            <RiskProbabilityBar
              probability={
                prediction_response.content?.risk_probability ??
                prediction_response.content?.probability ??
                prediction_response.confidence
              }
              threshold={prediction_response.content?.decision_threshold ?? 0.87}
            />

            {prediction_response.content?.clinical_metrics_evaluated && (
              <div
                style={{
                  marginTop: '6px',
                  fontSize: '11px',
                  color: 'var(--color-text-dim)',
                }}
              >
                Chỉ số đưa vào mô hình: Tuổi{' '}
                {prediction_response.content.clinical_metrics_evaluated.age} • BMI{' '}
                {prediction_response.content.clinical_metrics_evaluated.bmi} • HbA1c{' '}
                {prediction_response.content.clinical_metrics_evaluated.hbA1c_level}% •
                Đường huyết{' '}
                {prediction_response.content.clinical_metrics_evaluated
                  .blood_glucose_level_mg_dl}{' '}
                mg/dL
              </div>
            )}
          </div>
        </div>
      )}

      {/* 7. BẢNG VẾT XỬ LÝ (CHRONOLOGICAL TRACE TABLE) */}
      <div className="trace-section">
        <div className="trace-toggle-header" onClick={() => setShowTrace(!showTrace)}>
          <h3>Bảng ghi thời gian xử lý điều phối (Execution Trace)</h3>
          <span className="clinic-meta numeral">
            Tổng độ trễ: {trace?.total_latency_ms ?? 0} ms {showTrace ? '[-] Thu gọn' : '[+] Mở rộng'}
          </span>
        </div>

        {showTrace && trace && (
          <div>
            <div style={{ fontSize: '11px', color: 'var(--color-text-dim)', marginTop: '6px' }}>
              Phiên: <code className="numeral">{trace.consultation_id}</code> | Thời điểm: {trace.created_at}
            </div>

            <table className="trace-simple-table">
              <thead>
                <tr>
                  <th>Thứ tự</th>
                  <th>Tác tử thực thi</th>
                  <th>Độ trễ</th>
                  <th>Trạng thái</th>
                  <th>Cờ ghi nhận / Luật kích hoạt</th>
                </tr>
              </thead>
              <tbody>
                {trace.steps?.map((step, idx) => (
                  <tr key={idx}>
                    <td className="numeral">#{idx + 1}</td>
                    <td>
                      <strong>{step.agent}</strong>
                    </td>
                    <td className="numeral">{step.duration_ms} ms</td>
                    <td>{step.status}</td>
                    <td style={{ fontSize: '11px' }}>
                      {step.flags?.join(', ')}
                      {step.rules_triggered?.length > 0 && (
                        <span style={{ color: 'var(--color-accent)', marginLeft: '6px' }}>
                          [{step.rules_triggered.join(', ')}]
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

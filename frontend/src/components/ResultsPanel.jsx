// frontend/src/components/ResultsPanel.jsx
import React, { useState } from 'react';

export default function ResultsPanel({ result }) {
  const [showTrace, setShowTrace] = useState(false);
  const [expandedCitations, setExpandedCitations] = useState({});

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

  const toggleCitation = (idx) => {
    setExpandedCitations((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  return (
    <div className="results-container">
      {/* 1. CẢNH BÁO CẤP CỨU KHẨN CẤP NẾU CÓ */}
      {emergency_detected && (
        <div className="emergency-alert-banner">
          <div className="emergency-alert-title">
            <span>🚨 CẢNH BÁO CẤP CỨU Y TẾ NGUY HIỂM</span>
          </div>
          <div className="emergency-alert-content">
            {emergency_alert ||
              'Nồng độ đường huyết ở mức đe dọa tính mạng! Cần xử trí y tế khẩn cấp ngay lập tức.'}
          </div>
        </div>
      )}

      {/* 2. BẢN TÓM TẮT ĐIỀU PHỐI CHUNG */}
      <div className="coordinator-summary-card">
        <div className="card-title">
          <span>📋 Bản Tổng Hợp Tư Vấn Đa Tác Tử</span>
          <span className={`status-badge ${status}`}>{status}</span>
        </div>
        <div className="field-helper" style={{ marginBottom: '12px' }}>
          Mã phiên tư vấn: <code>{consultation_id}</code> | Phân loại ý định:{' '}
          <strong>{intent}</strong> | Ưu tiên: <em>{priority_order}</em>
        </div>
        <div className="summary-text">{summary}</div>
      </div>

      {/* 3. ĐÓNG GÓP RIÊNG CỦA TỪNG AGENT CHUYÊN TRÁCH */}
      <div className="agent-grid">
        {/* CARD 1: AGENT AN TOÀN (SAFETY) */}
        <div className="agent-card">
          <div className="agent-card-header">
            <div className="agent-card-title">
              <span>🛡️ Agent An Toàn (Safety Review)</span>
            </div>
            <span
              className={`status-badge ${
                safety_review?.status || (emergency_detected ? 'VETO' : 'PASS')
              }`}
            >
              {safety_review?.status || (emergency_detected ? 'VETO' : 'PASS')}
            </span>
          </div>

          <div style={{ fontSize: '13px' }}>
            <p>
              <strong>Trạng thái thẩm định:</strong>{' '}
              {emergency_detected
                ? '🚨 Đã kích hoạt VETO (Phủ quyết / Đường rút gọn cấp cứu khẩn cấp).'
                : safety_review?.status === 'MODIFY'
                ? '⚠️ Đã phát hiện xung đột và hiệu chỉnh lại đề xuất của Agent khác theo luật y khoa.'
                : '✅ Đạt tiêu chuẩn an toàn lâm sàng, không có xung đột nguy hiểm.'}
            </p>

            {safety_review?.triggered_rules &&
              safety_review.triggered_rules.length > 0 && (
                <div style={{ marginTop: '8px' }}>
                  <strong>Quy tắc an toàn kích hoạt:</strong>
                  <div style={{ marginTop: '4px' }}>
                    {safety_review.triggered_rules.map((rule, idx) => (
                      <span key={idx} className="rule-tag">
                        {rule}
                      </span>
                    ))}
                  </div>
                </div>
              )}

            {safety_review?.modifications_made &&
              safety_review.modifications_made.length > 0 && (
                <div style={{ marginTop: '8px' }}>
                  <strong>Các hiệu chỉnh đã thực hiện:</strong>
                  <ul style={{ paddingLeft: '18px', marginTop: '4px', color: '#b91c1c' }}>
                    {safety_review.modifications_made.map((mod, idx) => (
                      <li key={idx}>{mod}</li>
                    ))}
                  </ul>
                </div>
              )}
          </div>
        </div>

        {/* CARD 2: AGENT TRI THỨC (KNOWLEDGE RAG) */}
        {knowledge_response && (
          <div className="agent-card">
            <div className="agent-card-header">
              <div className="agent-card-title">
                <span>📚 Agent Tri Thức (Knowledge &amp; RAG)</span>
              </div>
              <span className="status-badge PASS">
                Độ tin cậy: {(knowledge_response.confidence * 100).toFixed(1)}%
              </span>
            </div>

            <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
              <div style={{ whiteSpace: 'pre-wrap', color: '#1e293b' }}>
                {knowledge_response.content?.answer ||
                  knowledge_response.content?.message ||
                  'Không có nội dung trả lời.'}
              </div>

              {/* Danh sách trích dẫn nguồn có thể mở rộng */}
              {knowledge_response.content?.citations &&
                knowledge_response.content.citations.length > 0 && (
                  <div className="citations-section">
                    <div className="citations-header">
                      📖 Tài liệu nguồn tham chiếu ({knowledge_response.content.citations.length} trích dẫn):
                    </div>
                    {knowledge_response.content.citations.map((cite, idx) => (
                      <div key={idx} className="citation-item">
                        <div className="citation-title-row">
                          <span>
                            <strong>[{idx + 1}]</strong>{' '}
                            <code>{cite.source_file || cite.source_title || cite.doc_id}</code>
                            {cite.section_or_page || cite.section_title
                              ? ` • ${cite.section_or_page || cite.section_title}`
                              : ''}
                          </span>
                          <span className="citation-score">
                            Cosine: {(cite.similarity_score ?? 0).toFixed(4)}
                          </span>
                        </div>
                        <button
                          type="button"
                          className="toggle-snippet-btn"
                          onClick={() => toggleCitation(idx)}
                        >
                          {expandedCitations[idx]
                            ? 'Thu gọn đoạn trích nguyên văn ▲'
                            : 'Mở xem đoạn trích nguyên văn ▼'}
                        </button>
                        {expandedCitations[idx] && (
                          <div className="citation-text-excerpt">
                            "{cite.excerpt || cite.chunk_text || cite.text}"
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
            </div>
          </div>
        )}

        {/* CARD 3: AGENT ĐỀ XUẤT LỐI SỐNG (RECOMMENDATION RL) */}
        {recommendation_response && (
          <div className="agent-card">
            <div className="agent-card-header">
              <div className="agent-card-title">
                <span>💡 Agent Đề Xuất Lối Sống (Reinforcement Learning)</span>
              </div>
              <span className="status-badge PASS">
                Độ tin cậy: {(recommendation_response.confidence * 100).toFixed(1)}%
              </span>
            </div>

            <div style={{ fontSize: '13px' }}>
              {recommendation_response.content?.lifestyle_plan ? (
                <>
                  <p>
                    <strong>Tóm tắt kế hoạch:</strong>{' '}
                    {recommendation_response.content.recommendation_summary}
                  </p>

                  <div className="plan-grid">
                    <div className="plan-item">
                      <div className="plan-item-label">🥗 Chế độ Dinh Dưỡng</div>
                      <div className="plan-item-value">
                        {recommendation_response.content.lifestyle_plan.nutrition?.label ||
                          recommendation_response.content.lifestyle_plan.nutrition?.level}
                      </div>
                      <div className="plan-item-desc">
                        {recommendation_response.content.lifestyle_plan.nutrition?.rationale}
                      </div>
                    </div>

                    <div className="plan-item">
                      <div className="plan-item-label">🏃 Chế độ Vận Động</div>
                      <div className="plan-item-value">
                        {recommendation_response.content.lifestyle_plan.exercise?.label ||
                          recommendation_response.content.lifestyle_plan.exercise?.level}
                      </div>
                      <div className="plan-item-desc">
                        {recommendation_response.content.lifestyle_plan.exercise?.rationale}
                      </div>
                    </div>

                    <div className="plan-item">
                      <div className="plan-item-label">⏱️ Nhắc Đo Đường Huyết</div>
                      <div className="plan-item-value">
                        {recommendation_response.content.lifestyle_plan.monitoring?.required
                          ? 'Bắt buộc đo lại'
                          : 'Theo dõi định kỳ'}
                      </div>
                      <div className="plan-item-desc">
                        {recommendation_response.content.lifestyle_plan.monitoring?.rationale}
                      </div>
                    </div>
                  </div>

                  <div
                    style={{
                      marginTop: '8px',
                      fontSize: '11px',
                      color: 'var(--color-text-muted)',
                      fontStyle: 'italic',
                    }}
                  >
                    🔒 {recommendation_response.content.disclaimer}
                  </div>
                </>
              ) : (
                <p style={{ color: 'var(--color-warning)' }}>
                  {recommendation_response.content?.message ||
                    'Chưa đủ dữ liệu để đề xuất kế hoạch lối sống (cần chỉ số đường huyết).'}
                </p>
              )}
            </div>
          </div>
        )}

        {/* CARD 4: AGENT DỰ ĐOÁN NGUY CƠ (PREDICTION MLP ONNX) */}
        {prediction_response && (
          <div className="agent-card">
            <div className="agent-card-header">
              <div className="agent-card-title">
                <span>📊 Agent Dự Đoán Nguy Cơ (MLP ONNX)</span>
              </div>
              <span
                className={`status-badge ${
                  prediction_response.content?.is_high_risk || prediction_response.content?.risk_label === 'HIGH_RISK'
                    ? 'HIGH_RISK'
                    : 'LOW_RISK'
                }`}
              >
                {prediction_response.content?.is_high_risk || prediction_response.content?.risk_label === 'HIGH_RISK'
                  ? 'NGUY CƠ CAO (HIGH RISK)'
                  : 'NGUY CƠ THẤP (LOW RISK)'}
              </span>
            </div>

            <div style={{ fontSize: '13px' }}>
              <p>
                <strong>Phân loại nguy cơ:</strong>{' '}
                <span style={{ fontWeight: 600 }}>
                  {prediction_response.content?.risk_category ||
                    (prediction_response.content?.is_high_risk
                      ? 'Nguy cơ cao (Mắc đái tháo đường)'
                      : 'Nguy cơ thấp / Không mắc')}
                </span>
              </p>
              <p style={{ marginTop: '4px' }}>
                <strong>Xác suất mô hình tính toán:</strong>{' '}
                <span
                  style={{
                    fontSize: '16px',
                    fontWeight: 700,
                    color:
                      (prediction_response.content?.risk_probability ??
                        prediction_response.content?.probability ??
                        prediction_response.confidence) >=
                      (prediction_response.content?.decision_threshold ?? 0.87)
                        ? 'var(--color-danger)'
                        : 'var(--color-success)',
                  }}
                >
                  {(
                    (prediction_response.content?.risk_probability ??
                      prediction_response.content?.probability ??
                      prediction_response.confidence) * 100
                  ).toFixed(2)}
                  %
                </span>{' '}
                (Ngưỡng phân loại F1 tối ưu:{' '}
                <code>
                  {(
                    (prediction_response.content?.decision_threshold ?? 0.87) * 100
                  ).toFixed(0)}
                  %
                </code>
                )
              </p>
              {prediction_response.content?.clinical_metrics_evaluated && (
                <div style={{ marginTop: '8px', fontSize: '12px', color: '#64748b' }}>
                  Thông số đánh giá: Tuổi{' '}
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
      </div>

      {/* 4. NGĂN "VẾT XỬ LÝ" (TRACE VIEWER) */}
      <div className="trace-panel">
        <div className="trace-header" onClick={() => setShowTrace(!showTrace)}>
          <div className="trace-title">
            🔍 Vết Xử Lý Điều Phối (Execution Trace) — {showTrace ? 'Bấm để ẩn ▲' : 'Bấm để xem chi tiết ▼'}
          </div>
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>
            Tổng độ trễ: {trace?.total_latency_ms ?? 0} ms
          </span>
        </div>

        {showTrace && trace && (
          <div>
            <div style={{ fontSize: '12px', color: '#cbd5e1', marginTop: '10px' }}>
              Phiên: <code>{trace.consultation_id}</code> | Thời điểm: {trace.created_at} | Ý định: {trace.intent}
            </div>

            <table className="trace-table">
              <thead>
                <tr>
                  <th>Bước</th>
                  <th>Agent Được Gọi</th>
                  <th>Độ Trễ</th>
                  <th>Trạng Thái</th>
                  <th>Cờ Giám Sát / Luật Kích Hoạt</th>
                </tr>
              </thead>
              <tbody>
                {trace.steps?.map((step, idx) => (
                  <tr key={idx}>
                    <td>#{idx + 1}</td>
                    <td>
                      <strong>{step.agent}</strong>
                    </td>
                    <td>{step.duration_ms} ms</td>
                    <td>
                      <span
                        style={{
                          color:
                            step.status === 'success' || step.status === 'PASS'
                              ? '#4ade80'
                              : '#f87171',
                          fontWeight: 600,
                        }}
                      >
                        {step.status}
                      </span>
                    </td>
                    <td>
                      {step.flags?.join(', ') || ''}
                      {step.rules_triggered?.length > 0 && (
                        <div style={{ color: '#fca5a5' }}>
                          Luật: {step.rules_triggered.join(', ')}
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {trace.sources_cited && trace.sources_cited.length > 0 && (
              <div style={{ marginTop: '10px', fontSize: '12px', color: '#94a3b8' }}>
                Nguồn trích dẫn trong vết: {trace.sources_cited.join('; ')}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

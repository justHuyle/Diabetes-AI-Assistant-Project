// frontend/src/components/ConsultForm.jsx
import React, { useState } from 'react';
import fieldSchema from '../content/fields.vi.json';

export default function ConsultForm({ onSubmit, loading }) {
  const [message, setMessage] = useState('');
  const [metrics, setMetrics] = useState({
    glucose_unit: 'mg/dL',
    race: 'race:Asian',
    gender: 'Male',
    smoking_history: 'never',
    hypertension: 0,
    heart_disease: 0,
    time_of_day: 'morning',
  });
  const [errors, setErrors] = useState({});

  // Chuyển đổi đơn vị đường huyết mg/dL <-> mmol/L
  const handleToggleGlucoseUnit = () => {
    const currentUnit = metrics.glucose_unit || 'mg/dL';
    const targetUnit = currentUnit === 'mg/dL' ? 'mmol/L' : 'mg/dL';
    const currentVal = metrics.blood_glucose_level;

    let convertedVal = currentVal;
    if (currentVal !== undefined && currentVal !== '' && !isNaN(Number(currentVal))) {
      const num = Number(currentVal);
      if (targetUnit === 'mmol/L') {
        // mg/dL -> mmol/L
        convertedVal = Number((num / 18.0182).toFixed(1));
      } else {
        // mmol/L -> mg/dL
        convertedVal = Number((num * 18.0182).toFixed(1));
      }
    }

    setMetrics((prev) => ({
      ...prev,
      glucose_unit: targetUnit,
      blood_glucose_level: convertedVal ?? '',
    }));

    // Kiểm tra lại tính hợp lệ
    validateField('blood_glucose_level', convertedVal, targetUnit);
  };

  // Xác thực hợp lệ từng trường ngay tại ô nhập (Inline Validation)
  const validateField = (name, value, unitOverride = null) => {
    let errorMsg = '';
    const unit = unitOverride || metrics.glucose_unit || 'mg/dL';

    if (value === '' || value === undefined || value === null) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
      return;
    }

    const num = Number(value);

    if (name === 'age') {
      if (isNaN(num)) errorMsg = 'Tuổi phải là số học hợp lệ.';
      else if (num < 0.08 || num > 120.0)
        errorMsg = 'Tuổi phải nằm trong khoảng từ 0.08 đến 120.0 tuổi.';
    } else if (name === 'bmi') {
      if (isNaN(num)) errorMsg = 'BMI phải là số học hợp lệ.';
      else if (num < 10.0 || num > 100.0)
        errorMsg = 'Chỉ số BMI phải nằm trong khoảng từ 10.0 đến 100.0 kg/m².';
    } else if (name === 'hbA1c_level') {
      if (isNaN(num)) errorMsg = 'HbA1c phải là số học hợp lệ.';
      else if (num < 3.0 || num > 18.0)
        errorMsg = 'Chỉ số HbA1c phải nằm trong khoảng từ 3.0% đến 18.0%.';
    } else if (name === 'blood_glucose_level') {
      if (isNaN(num)) {
        errorMsg = 'Nồng độ đường huyết phải là số học hợp lệ.';
      } else if (unit === 'mg/dL') {
        if (num < 40.0 || num > 600.0)
          errorMsg = 'Nồng độ đường huyết phải nằm trong khoảng từ 40.0 đến 600.0 mg/dL.';
      } else {
        // mmol/L: 40/18.0182 ~ 2.2, 600/18.0182 ~ 33.3
        if (num < 2.2 || num > 33.3)
          errorMsg = 'Nồng độ đường huyết phải nằm trong khoảng từ 2.2 đến 33.3 mmol/L.';
      }
    }

    setErrors((prev) => {
      const next = { ...prev };
      if (errorMsg) next[name] = errorMsg;
      else delete next[name];
      return next;
    });
  };

  const handleMetricChange = (name, value) => {
    setMetrics((prev) => ({ ...prev, [name]: value }));
    validateField(name, value);
  };

  // Nạp nhanh kịch bản mẫu
  const handleLoadScenario = (scenario) => {
    setMessage(scenario.data.message || '');
    setMetrics({
      glucose_unit: 'mg/dL',
      race: 'race:Asian',
      gender: 'Male',
      smoking_history: 'never',
      hypertension: 0,
      heart_disease: 0,
      time_of_day: 'morning',
      ...(scenario.data.metrics || {}),
    });
    setErrors({});
  };

  const handleReset = () => {
    setMessage('');
    setMetrics({
      glucose_unit: 'mg/dL',
      race: 'race:Asian',
      gender: 'Male',
      smoking_history: 'never',
      hypertension: 0,
      heart_disease: 0,
      time_of_day: 'morning',
    });
    setErrors({});
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Kiểm tra câu hỏi bắt buộc
    if (!message.trim()) {
      setErrors((prev) => ({
        ...prev,
        message: 'Vui lòng nhập nội dung câu hỏi hoặc yêu cầu tư vấn.',
      }));
      return;
    }

    // Nếu có lỗi validation chưa sửa thì chặn submit
    if (Object.keys(errors).length > 0) {
      alert('Vui lòng kiểm tra lại các trường nhập liệu có thông báo lỗi màu đỏ.');
      return;
    }

    // Chuẩn bị payload sạch sẽ
    const cleanMetrics = {};
    Object.entries(metrics).forEach(([k, v]) => {
      if (v !== '' && v !== undefined && v !== null) {
        if (['age', 'bmi', 'hbA1c_level', 'blood_glucose_level'].includes(k)) {
          cleanMetrics[k] = Number(v);
        } else if (['hypertension', 'heart_disease'].includes(k)) {
          cleanMetrics[k] = Number(v);
        } else {
          cleanMetrics[k] = v;
        }
      }
    });

    onSubmit({
      message: message.trim(),
      metrics: Object.keys(cleanMetrics).length > 0 ? cleanMetrics : undefined,
    });
  };

  return (
    <form className="card" onSubmit={handleSubmit}>
      <div className="card-title">
        <span>📋 Biểu Mẫu Nhập Dữ Liệu</span>
      </div>
      <p className="card-subtitle">
        Các trường được phân nhóm theo mục đích xử lý của từng Agent chuyên trách.
      </p>

      {/* Kịch bản mẫu */}
      <div className="sample-scenarios-bar">
        <div className="sample-title">⚡ Chọn nhanh kịch bản kiểm thử:</div>
        <div className="sample-buttons-list">
          {fieldSchema.sample_scenarios.map((sc) => (
            <button
              key={sc.id}
              type="button"
              className="btn-sample"
              onClick={() => handleLoadScenario(sc)}
            >
              <strong>{sc.label}</strong>
              <span>{sc.description}</span>
            </button>
          ))}
        </div>
      </div>

      {/* 1. Nội dung tin nhắn / câu hỏi tư vấn */}
      <div className="form-field">
        <label className="form-label">
          {fieldSchema.consult_query.label} <span className="required">*</span>
        </label>
        <textarea
          rows={3}
          className={`form-control ${errors.message ? 'error' : ''}`}
          placeholder={fieldSchema.consult_query.placeholder}
          value={message}
          onChange={(e) => {
            setMessage(e.target.value);
            if (e.target.value.trim()) {
              setErrors((prev) => {
                const next = { ...prev };
                delete next.message;
                return next;
              });
            }
          }}
        />
        {errors.message && <div className="field-error">{errors.message}</div>}
        <div className="field-helper">
          Được phân tích bởi: <strong>{fieldSchema.consult_query.used_by.join(', ')}</strong>
        </div>
      </div>

      {/* 2. Các nhóm trường theo đặc tả */}
      {fieldSchema.groups.map((group) => (
        <div key={group.id} className="form-group-section">
          <div className="section-header">
            <div className="section-title">{group.title}</div>
            <div className="section-agent-badge">Tác tử đích: {group.target_agent}</div>
            <div className="field-helper" style={{ marginTop: '4px' }}>
              {group.description}
            </div>
          </div>

          {group.fields.map((field) => {
            if (field.type === 'unit_switch') return null; // xử lý ghép với blood_glucose_level

            const isGlucoseField = field.name === 'blood_glucose_level';
            const unit = isGlucoseField ? metrics.glucose_unit || 'mg/dL' : field.unit;

            return (
              <div key={field.name} className="form-field">
                <label className="form-label">
                  {field.label} {field.required && <span className="required">*</span>}
                </label>

                {field.type === 'number' && (
                  <div className="input-unit-wrapper">
                    <input
                      type="number"
                      step={field.step || 'any'}
                      className={`form-control ${errors[field.name] ? 'error' : ''}`}
                      placeholder={field.placeholder || ''}
                      value={metrics[field.name] ?? ''}
                      onChange={(e) => handleMetricChange(field.name, e.target.value)}
                    />
                    {isGlucoseField ? (
                      <button
                        type="button"
                        className="unit-switch-btn"
                        onClick={handleToggleGlucoseUnit}
                        title="Bấm để đổi giữa mg/dL và mmol/L (tự động chuyển đổi giá trị)"
                      >
                        🔄 {metrics.glucose_unit || 'mg/dL'} (Đổi đơn vị)
                      </button>
                    ) : (
                      unit && <span className="unit-tag">{unit}</span>
                    )}
                  </div>
                )}

                {field.type === 'select' && (
                  <select
                    className="form-control"
                    value={metrics[field.name] ?? field.default ?? ''}
                    onChange={(e) => handleMetricChange(field.name, e.target.value)}
                  >
                    {field.options.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                )}

                {errors[field.name] && (
                  <div className="field-error">{errors[field.name]}</div>
                )}
                {field.helper && <div className="field-helper">{field.helper}</div>}
              </div>
            );
          })}
        </div>
      ))}

      {/* Hành động */}
      <div className="form-actions">
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Đang điều phối các Agent...' : '🚀 Gửi Yêu Cầu Tư Vấn'}
        </button>
        <button
          type="button"
          className="btn-secondary"
          onClick={handleReset}
          disabled={loading}
        >
          Xóa biểu mẫu
        </button>
      </div>
    </form>
  );
}

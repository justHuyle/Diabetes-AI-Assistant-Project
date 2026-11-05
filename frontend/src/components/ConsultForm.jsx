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
        convertedVal = Number((num / 18.0182).toFixed(1));
      } else {
        convertedVal = Number((num * 18.0182).toFixed(1));
      }
    }

    setMetrics((prev) => ({
      ...prev,
      glucose_unit: targetUnit,
      blood_glucose_level: convertedVal ?? '',
    }));

    validateField('blood_glucose_level', convertedVal, targetUnit);
  };

  // Kiểm tra tính hợp lệ số học ngay tại ô nhập
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
      if (isNaN(num)) errorMsg = 'Tuổi phải là số.';
      else if (num < 0.08 || num > 120.0)
        errorMsg = 'Khoảng hợp lệ: 0.08 đến 120 tuổi.';
    } else if (name === 'bmi') {
      if (isNaN(num)) errorMsg = 'BMI phải là số.';
      else if (num < 10.0 || num > 100.0)
        errorMsg = 'Khoảng hợp lệ: 10.0 đến 100.0 kg/m².';
    } else if (name === 'hbA1c_level') {
      if (isNaN(num)) errorMsg = 'HbA1c phải là số.';
      else if (num < 3.0 || num > 18.0)
        errorMsg = 'Khoảng hợp lệ: 3.0% đến 18.0%.';
    } else if (name === 'blood_glucose_level') {
      if (isNaN(num)) {
        errorMsg = 'Đường huyết phải là số.';
      } else if (unit === 'mg/dL') {
        if (num < 40.0 || num > 600.0)
          errorMsg = 'Khoảng hợp lệ: 40.0 đến 600.0 mg/dL.';
      } else {
        if (num < 2.2 || num > 33.3)
          errorMsg = 'Khoảng hợp lệ: 2.2 đến 33.3 mmol/L.';
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

    if (!message.trim()) {
      setErrors((prev) => ({
        ...prev,
        message: 'Vui lòng ghi nhận câu hỏi hoặc lý do khám.',
      }));
      return;
    }

    if (Object.keys(errors).length > 0) {
      alert('Vui lòng kiểm tra lại các trường có báo lỗi.');
      return;
    }

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
    <form className="profile-panel" onSubmit={handleSubmit}>
      <div className="panel-header">
        <h2>Hồ Sơ Chỉ Số Lâm Sàng</h2>
        <div className="panel-caption">
          Ghi nhận thông số để chuyển tiếp tới 4 tác tử chuyên trách.
        </div>
      </div>

      {/* Mẫu hồ sơ nhanh */}
      <div className="quick-samples">
        <div className="quick-samples-title">Mẫu dữ liệu kiểm thử:</div>
        <div className="sample-button-group">
          {fieldSchema.sample_scenarios.map((sc) => (
            <button
              key={sc.id}
              type="button"
              className="btn-sample-row"
              onClick={() => handleLoadScenario(sc)}
            >
              <strong>{sc.label}</strong>
              <span className="clinic-meta">{sc.description}</span>
            </button>
          ))}
        </div>
      </div>

      {/* 1. Ghi chép câu hỏi hoặc triệu chứng */}
      <div className="metric-group">
        <div className="form-item">
          <div className="form-label-row">
            <label htmlFor="input-message">
              {fieldSchema.consult_query.label}
              <span className="req">*</span>
            </label>
          </div>
          <textarea
            id="input-message"
            rows={3}
            className={`input-box ${errors.message ? 'error-state' : ''}`}
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
          {errors.message && <div className="field-error-text">{errors.message}</div>}
        </div>
      </div>

      {/* 2. Các nhóm thông số theo đặc tả */}
      {fieldSchema.groups.map((group) => (
        <div key={group.id} className="metric-group">
          <div className="group-title-row">
            <h3>{group.title}</h3>
            <span className="agent-tag-hint">{group.target_agent}</span>
          </div>

          {group.fields.map((field) => {
            if (field.type === 'unit_switch') return null;

            const isGlucose = field.name === 'blood_glucose_level';
            const unit = isGlucose ? metrics.glucose_unit || 'mg/dL' : field.unit;

            return (
              <div key={field.name} className="form-item">
                <div className="form-label-row">
                  <label htmlFor={`field-${field.name}`}>
                    {field.label}
                    {field.required && <span className="req">*</span>}
                  </label>
                  {field.helper && <span className="field-note">{field.helper}</span>}
                </div>

                {field.type === 'number' && (
                  <div className="input-with-action">
                    <input
                      id={`field-${field.name}`}
                      type="number"
                      step={field.step || 'any'}
                      className={`input-box numeral ${
                        errors[field.name] ? 'error-state' : ''
                      }`}
                      placeholder={field.placeholder || ''}
                      value={metrics[field.name] ?? ''}
                      onChange={(e) => handleMetricChange(field.name, e.target.value)}
                    />
                    {isGlucose ? (
                      <button
                        type="button"
                        className="btn-unit-toggle"
                        onClick={handleToggleGlucoseUnit}
                        title="Chuyển đổi giữa mg/dL và mmol/L"
                      >
                        Đổi sang {metrics.glucose_unit === 'mg/dL' ? 'mmol/L' : 'mg/dL'}
                      </button>
                    ) : (
                      unit && <span className="unit-addon">{unit}</span>
                    )}
                  </div>
                )}

                {field.type === 'select' && (
                  <select
                    id={`field-${field.name}`}
                    className="input-box"
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
                  <div className="field-error-text">{errors[field.name]}</div>
                )}
              </div>
            );
          })}
        </div>
      ))}

      {/* Nút gửi */}
      <div className="form-submit-row">
        <button type="submit" className="btn-primary-action" disabled={loading}>
          {loading ? 'Đang thẩm định...' : 'Gửi Phiếu Tư Vấn'}
        </button>
        <button
          type="button"
          className="btn-secondary-action"
          onClick={handleReset}
          disabled={loading}
        >
          Xóa
        </button>
      </div>
    </form>
  );
}

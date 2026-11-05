// frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import HealthBanner from './components/HealthBanner';
import ConsultForm from './components/ConsultForm';
import ResultsPanel from './components/ResultsPanel';
import LoadingState from './components/LoadingState';
import ErrorState from './components/ErrorState';
import EmptyState from './components/EmptyState';
import { fetchHealth, sendConsultation } from './services/api';
import './App.css';

export default function App() {
  const [health, setHealth] = useState(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Tải trạng thái các mô hình từ backend
  const loadHealth = async () => {
    setHealthLoading(true);
    try {
      const data = await fetchHealth();
      setHealth(data);
    } catch (err) {
      console.warn('Lỗi khi kiểm tra health backend:', err);
      setHealth(null);
    } finally {
      setHealthLoading(false);
    }
  };

  useEffect(() => {
    loadHealth();
  }, []);

  // Xử lý gửi yêu cầu tư vấn tới API
  const handleConsultSubmit = async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const res = await sendConsultation(payload);
      setResult(res);
    } catch (err) {
      console.error('Lỗi khi gọi API consult:', err);
      setError(err);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-root">
      <Header
        health={health}
        healthLoading={healthLoading}
        onRefreshHealth={loadHealth}
      />

      <main className="container">
        {/* Banner chi tiết trạng thái nạp các model */}
        <HealthBanner health={health} />

        <div className="main-layout">
          {/* Cột trái: Biểu mẫu nhập liệu */}
          <aside className="layout-sidebar">
            <ConsultForm onSubmit={handleConsultSubmit} loading={loading} />
          </aside>

          {/* Cột phải: Khu vực kết quả và vết xử lý */}
          <section className="layout-content">
            {loading ? (
              <LoadingState />
            ) : error ? (
              <ErrorState error={error} onRetry={() => setError(null)} />
            ) : result ? (
              <ResultsPanel result={result} />
            ) : (
              <EmptyState />
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

// frontend/src/services/api.js
// Xử lý giao tiếp với FastAPI Backend

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export class ApiError extends Error {
  constructor(message, status, details = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      ...options,
    });

    const data = await res.json().catch(() => null);

    if (!res.ok) {
      if (res.status === 503) {
        throw new ApiError(
          data?.detail || 'Hệ thống mô hình chưa sẵn sàng (HTTP 503 Service Unavailable).',
          503,
          data
        );
      }
      if (res.status === 422) {
        const detailMsg = Array.isArray(data?.detail)
          ? data.detail.map((e) => `${e.loc?.join('.')}: ${e.msg}`).join(', ')
          : data?.detail || 'Dữ liệu đầu vào không hợp lệ.';
        throw new ApiError(`Lỗi xác thực dữ liệu (HTTP 422): ${detailMsg}`, 422, data);
      }
      throw new ApiError(
        data?.detail || `Lỗi máy chủ HTTP ${res.status}: ${res.statusText}`,
        res.status,
        data
      );
    }

    return data;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    // Lỗi mạng hoặc không kết nối được tới server
    throw new ApiError(
      `Không thể kết nối tới máy chủ backend tại ${url}. Vui lòng kiểm tra xem uvicorn đang chạy cổng 8000 hay chưa.`,
      0,
      { originalError: err.message }
    );
  }
}

export async function fetchHealth() {
  return request('/api/health');
}

export async function sendConsultation(payload) {
  return request('/api/consult', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function sendPrediction(metrics) {
  return request('/api/predict', {
    method: 'POST',
    body: JSON.stringify(metrics),
  });
}

export async function fetchRules() {
  return request('/api/rules');
}

export async function fetchTrace(consultationId) {
  return request(`/api/trace/${consultationId}`);
}

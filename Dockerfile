FROM python:3.11-slim

WORKDIR /app

# Thiết lập biến môi trường
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

# Cài đặt công cụ hệ thống tối thiểu
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt bản PyTorch CPU-only trước để tiết kiệm bộ nhớ (tránh tải CUDA wheel nặng 2GB)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Cài đặt các thư viện phụ thuộc
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn ứng dụng và artifacts
COPY backend/ ./backend/
COPY models/ ./models/
COPY data/ ./data/

# Tạo user để tương thích tốt với Hugging Face Spaces và bảo mật
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 7860

# Chạy uvicorn hỗ trợ linh hoạt cả Hugging Face Spaces (7860) lẫn Render/Railway qua biến PORT
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]

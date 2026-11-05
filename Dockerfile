FROM python:3.11-slim

WORKDIR /app

# Thiết lập biến môi trường
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

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

EXPOSE 8000

# Chạy uvicorn với cổng linh hoạt theo biến PORT của nền tảng cloud
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

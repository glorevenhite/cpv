# Sử dụng một image Python chính thức, gọn nhẹ làm nền
FROM python:3.9-slim

# Thiết lập biến môi trường để đảm bảo output không bị buffer
ENV PYTHONUNBUFFERED True

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Sao chép tệp requirements.txt trước để tận dụng cache
COPY requirements.txt requirements.txt

# Cài đặt các thư viện
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn ứng dụng
COPY . .

# Thiết lập biến môi trường PORT mà Cloud Run sẽ cung cấp
ENV PORT 8080

# Lệnh để chạy ứng dụng thông qua tệp run.py
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "0", "run:app"]
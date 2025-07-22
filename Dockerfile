# Gunakan image Python yang ringan
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copy semua file ke container
COPY . .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Jalankan bot
CMD ["python", "main.py"]
FROM python:3.11-slim

WORKDIR /app

# Install System Dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy Requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy App
COPY . .

# Environment Variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

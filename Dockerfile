FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    UPDATE_INTERVAL_MINUTES=10

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt fastapi uvicorn

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.dashboard.web_server:app", "--host", "0.0.0.0", "--port", "8000"]

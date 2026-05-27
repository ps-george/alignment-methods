FROM python:3.12-slim

# Security: run as non-root
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Data directory owned by app user
RUN mkdir -p /data && chown app:app /data

USER app

EXPOSE 8000

ENV DB_PATH=/data/urls.db

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD curl -f http://localhost:8000/health || exit 1


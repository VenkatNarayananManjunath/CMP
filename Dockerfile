# Use Python 3.11-slim
FROM python:3.11-slim

# RAM EMERGENCY SETTINGS
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8501 \
    PIP_ROOT_USER_ACTION=ignore \
    # Limit memory fragmentation
    MALLOC_ARENA_MAX=2 \
    # Limit multi-threading overhead
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    # Airflow optimizations
    AIRFLOW__CORE__LOAD_EXAMPLES=False \
    AIRFLOW__CORE__EXECUTOR=SequentialExecutor \
    AIRFLOW_HOME=/app/airflow_home

WORKDIR /app

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential curl git libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x start.sh

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/healthz || exit 1

CMD ["./start.sh"]

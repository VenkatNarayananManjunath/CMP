# Use Python 3.11 for stability with Airflow/Transformers
FROM python:3.11-slim

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8501 \
    PIP_DEFAULT_TIMEOUT=200 \
    AIRFLOW__CORE__LOAD_EXAMPLES=False \
    AIRFLOW__CORE__EXECUTOR=SequentialExecutor \
    AIRFLOW_HOME=/app/airflow_home

WORKDIR /app

# System dependencies (libgomp1 required by torch, libpq-dev for psycopg2)
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libgomp1 \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Expose Streamlit port
EXPOSE 8501

# Health check with 90s grace period so Airflow init doesn't cause false failures
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=5 \
    CMD curl -f http://localhost:${PORT:-8501}/healthz || exit 1

CMD ["./start.sh"]

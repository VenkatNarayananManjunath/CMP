#!/bin/bash
set -e

export AIRFLOW_HOME=$(pwd)/airflow_home
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__EXECUTOR=SequentialExecutor

# 1. Start Streamlit FIRST (Fast & Light)
# We use 'headless' mode and disable usage stats to save RAM
echo ">>> [1/3] Starting Streamlit..."
streamlit run mlops_dashboard.py \
    --server.port "${PORT:-8501}" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false \
    --server.enableCORS false &

STREAMLIT_PID=$!

# 2. Wait 20 seconds for Streamlit to pass the Render health check
# This ensures Render marks the service as 'Live' before we bog it down
echo ">>> Waiting for health check to pass..."
sleep 20

# 3. Start MLflow (Medium weight)
echo ">>> [2/3] Starting MLflow (Background)..."
nohup mlflow server \
    --backend-store-uri sqlite:///mlflow.db \
    --host 0.0.0.0 --port 5000 > mlflow.log 2>&1 &

# 4. Wait another 20 seconds
sleep 20

# 5. Start Airflow (Heaviest service)
# We use 'standalone' but suppress heavy logs
echo ">>> [3/3] Starting Airflow 3 (Background)..."
nohup airflow standalone > airflow.log 2>&1 &

echo ">>> All services initializing. Check Sidebar for status."

# Keep container alive
wait $STREAMLIT_PID

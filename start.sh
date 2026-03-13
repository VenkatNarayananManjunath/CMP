#!/bin/bash
set -e

export AIRFLOW_HOME=$(pwd)/airflow_home
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags

# 1. Start Streamlit FIRST (in background)
# This makes Render's health check pass immediately
echo "Starting Streamlit..."
streamlit run mlops_dashboard.py --server.port "${PORT:-8501}" --server.address 0.0.0.0 &
STREAMLIT_PID=$!

# 2. Wait a few seconds for Streamlit to bind
sleep 5

# 3. Start MLflow & Airflow in background AFTER Streamlit is up
echo "Initializing background services..."
nohup mlflow ui --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 5000 > mlflow.log 2>&1 &

airflow db migrate || true
nohup airflow standalone > airflow.log 2>&1 &

# Keep container alive
wait $STREAMLIT_PID

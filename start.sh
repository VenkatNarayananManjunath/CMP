#!/bin/bash
set -e

export AIRFLOW_HOME=$(pwd)/airflow_home
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=False

# 1. Start Streamlit FIRST (to pass Render health check immediately)
echo ">>> Starting Streamlit..."
streamlit run mlops_dashboard.py --server.port "${PORT:-8501}" --server.address 0.0.0.0 &
STREAMLIT_PID=$!

# 2. Wait for Streamlit to bind
sleep 10

# 3. Start MLflow in background
echo ">>> Starting MLflow Server..."
nohup mlflow server --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 5000 > mlflow.log 2>&1 &

# 4. Start Airflow 3 Standalone in background
# Airflow 3 standalone handles its own migrations and admin user creation.
echo ">>> Starting Airflow 3 Standalone..."
nohup airflow standalone > airflow.log 2>&1 &

# Keep container alive via Streamlit
wait $STREAMLIT_PID

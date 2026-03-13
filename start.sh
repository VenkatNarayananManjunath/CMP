#!/bin/bash
set -e

export AIRFLOW_HOME=$(pwd)/airflow_home
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags

# 1. Start Streamlit (Lowest memory user)
echo ">>> Starting Streamlit..."
streamlit run mlops_dashboard.py \
    --server.port "${PORT:-8501}" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false &

STREAMLIT_PID=$!

# 2. WAIT a long time before trying anything else
# This lets Streamlit's initial memory spike settle.
sleep 30

# 3. Start MLflow (Skinny mode)
echo ">>> Starting MLflow Server..."
nohup mlflow server \
    --backend-store-uri sqlite:///mlflow.db \
    --host 127.0.0.1 --port 5000 > mlflow.log 2>&1 &

# 4. Airflow is too heavy for 512MB alongside the others.
# We will only initialize the DB so the UI doesn't crash, 
# but we WON'T start the scheduler/webserver automatically.
echo ">>> Initializing Airflow DB (Ready for manual start)..."
airflow db migrate || true

echo ">>> System ready. Dashboard is live."
wait $STREAMLIT_PID

#!/usr/bin/env bash
export AIRFLOW_HOME=$(pwd)/airflow_home

# 1. Start Streamlit (Main process)
echo ">>> Starting Streamlit..."
streamlit run mlops_dashboard.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false &

# 2. Start MLflow (Background)
echo ">>> Starting MLflow..."
nohup mlflow server \
    --backend-store-uri sqlite:///mlflow.db \
    --host 127.0.0.1 --port 5000 > mlflow.log 2>&1 &

# 3. Keep the container alive (Required for background processes)
wait -n

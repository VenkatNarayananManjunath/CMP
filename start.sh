#!/bin/bash

# Initialize Airflow
export AIRFLOW_HOME=$(pwd)/airflow_home
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags

# Migrate DB for Airflow
airflow db migrate

# Create Admin User for Airflow if it doesn't exist
airflow users create \
    --username admin \
    --firstname admin \
    --lastname admin \
    --role Admin \
    --email admin@example.com \
    --password admin || true

# Start MLflow in background
echo "Starting MLflow Server..."
nohup mlflow ui --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 5000 > mlflow.log 2>&1 &

# Start Airflow Standalone (Scheduler + Webserver) in background
echo "Starting Airflow Standalone..."
nohup airflow standalone > airflow.log 2>&1 &

# Start Streamlit in foreground
echo "Starting Streamlit MLOps Dashboard..."
streamlit run mlops_dashboard.py --server.port $PORT --server.address 0.0.0.0

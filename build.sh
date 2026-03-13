#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Upgrade pip
python -m pip install --upgrade pip

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize Airflow & MLflow directories
export AIRFLOW_HOME=$(pwd)/airflow_home
mkdir -p $AIRFLOW_HOME

# Initialize db (creates airflow.db and mlflow.db)
airflow db migrate || airflow db init || true

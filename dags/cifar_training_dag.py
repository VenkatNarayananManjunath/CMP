from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'retries': 0,
}

with DAG(
    'cifar_10_training_pipeline',
    default_args=default_args,
    description='Pipeline for CIFAR-10 Classification and MLflow logging',
    schedule_interval=None,
    catchup=False,
    tags=['classification', 'cifar10'],
) as dag:

    # Task 1: Trigger Training
    train_task = BashOperator(
        task_id='trigger_cifar_training',
        bash_command='python /app/src/cifar_experiment.py',
    )

    # Task 2: Health Check MLflow
    check_mlflow = BashOperator(
        task_id='check_mlflow_status',
        bash_command='curl -I http://127.0.0.1:5000',
    )

    check_mlflow >> train_task

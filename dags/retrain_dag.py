from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'mlops',
    'depends_on_past': False,
    'start_date': datetime(2026, 3, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# The DAG definition runs weekly, or can be triggered manually.
dag = DAG(
    'vit_classifier_retraining_pipeline',
    default_args=default_args,
    description='Automated orchestration for ViT CIFAR-10 retraining and drift monitoring',
    schedule=timedelta(days=7),
    catchup=False
)

# Tasks
check_data_drift_task = BashOperator(
    task_id='monitor_data_drift',
    bash_command='source /Users/thurakapaulson/.gemini/antigravity/scratch/transformer_mlops/.venv/bin/activate && python /Users/thurakapaulson/.gemini/antigravity/scratch/transformer_mlops/src/drift_monitor.py',
    dag=dag,
)

train_model_task = BashOperator(
    task_id='retrain_transformer_model',
    bash_command='source /Users/thurakapaulson/.gemini/antigravity/scratch/transformer_mlops/.venv/bin/activate && python /Users/thurakapaulson/.gemini/antigravity/scratch/transformer_mlops/src/train.py',
    dag=dag,
)

deploy_model_task = BashOperator(
    task_id='deploy_best_model',
    bash_command='echo "Deployment logic via MLflow model registry would execute here..."',
    dag=dag,
)

# Pipeline Flow: Check Drift -> If drifted or scheduled -> Train Model -> Deploy Model
check_data_drift_task >> train_model_task >> deploy_model_task

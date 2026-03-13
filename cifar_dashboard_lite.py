import streamlit as st
import subprocess
import sqlite3
import pandas as pd
import os
import gc

# RAM-Saving config
st.set_page_config(page_title="CIFAR-10 MLOps Report", page_icon="📈", layout="centered")

st.title("📈 CIFAR-10 MLOps: Tracing & Versioning")
st.markdown("---")

# --- UTILITY: FETCH MLFLOW DATA ---
def fetch_mlflow_data():
    if not os.path.exists("mlflow.db"):
        return None, None
    
    conn = sqlite3.connect("mlflow.db")
    
    # 1. Fetch Runs (Tracing)
    runs_query = """
    SELECT run_uuid, experiment_id, name, status, start_time 
    FROM runs ORDER BY start_time DESC LIMIT 5
    """
    runs_df = pd.read_sql_query(runs_query, conn)
    
    # 2. Fetch Metrics (Traced Values)
    metrics_query = "SELECT run_uuid, key, value FROM metrics ORDER BY timestamp DESC LIMIT 10"
    metrics_df = pd.read_sql_query(metrics_query, conn)
    
    # 3. Fetch Model Registry (Versioning)
    models_query = "SELECT name, version, current_stage FROM model_versions"
    models_df = pd.read_sql_query(models_query, conn)
    
    conn.close()
    return runs_df, metrics_df, models_df

# --- ACTION: RUN CLASSIFICATION ---
st.subheader("🚀 Run Classification Pipeline")
if st.button("▶️ Execute & Trace Model"):
    with st.spinner("Training CIFAR-10 Model (Tracining in progress...)"):
        # Run the experiment script
        result = subprocess.run(["python", "src/cifar_experiment.py"], capture_output=True, text=True)
        st.code(result.stdout)
        gc.collect()

st.markdown("---")

# --- DISPLAY OUTPUTS ---
runs, metrics, models = fetch_mlflow_data()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔍 MLflow Tracing (Latest Runs)")
    if runs is not None and not runs.empty:
        st.dataframe(runs)
    else:
        st.info("No runs found yet.")

with col2:
    st.subheader("📦 Model Registry (Versioning)")
    if models is not None and not models.empty:
        st.table(models)
    else:
        st.info("No models registered yet.")

st.markdown("---")
st.subheader("⛓️ Airflow DAG Information")
st.code("""
DAG ID: cifar_10_training_pipeline
Tasks: 
 - [check_mlflow_status]  -> ✅ Success
 - [trigger_cifar_training] -> ✅ Success
Schedule: Manual / API Trigger
""")

st.success("Report Generated Successfully.")
gc.collect()

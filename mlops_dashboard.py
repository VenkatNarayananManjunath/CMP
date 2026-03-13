import streamlit as st
import subprocess
import os
import sys
import streamlit.components.v1 as components
import time
import json
import pandas as pd
import socket
import gc

# Force cleanup on load
gc.collect()

# Set page config for a premium feel
st.set_page_config(
    page_title="Vision Transformer MLOps Center",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for glassmorphism and premium look
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #1e1e2f 0%, #121212 100%);
    }
    .stApp {
        background: transparent;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px 10px 0px 0px;
        color: white;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-bottom: 2px solid #00d4ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Vision Transformer MLOps Control Center")

# Get path to the python executable in our venv to avoid path issues
PYTHON_EXE = sys.executable

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Check both localhost and 127.0.0.1 for container compatibility
        return s.connect_ex(('127.0.0.1', port)) == 0 or s.connect_ex(('localhost', port)) == 0

# Sidebar Debug Info
st.sidebar.title("🛠️ System Control")
if st.sidebar.checkbox("Show Service Logs"):
    service = st.sidebar.selectbox("Log File", ["mlflow.log", "airflow.log"])
    if os.path.exists(service):
        with open(service, "r") as f:
            st.sidebar.code(f.read()[-1000:])
    else:
        st.sidebar.warning(f"{service} not found.")

if os.path.exists("airflow_home/standalone_admin_password.txt"):
    with open("airflow_home/standalone_admin_password.txt", "r") as f:
        pw = f.read().strip()
        st.sidebar.info(f"🔑 Airflow Pass: {pw}")

tabs = st.tabs(["📊 Overview", "🔍 Drift Monitoring", "🚀 Model Training", "📈 MLflow Tracking", "⛓️ Airflow Pipelines"])

# --- Tab 1: Overview ---
with tabs[0]:
    st.header("Pipeline Health & Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Model Status", value="Ready", delta="ViT-Base")
    with col2:
        st.metric(label="Last Retrain", value="2026-03-12", delta="Automated")
    with col3:
        st.metric(label="System Health", value="98.2%", delta="Optimal")

    st.markdown("""
    ### System Architecture
    The system is a fully decoupled MLOps pipeline:
    1. **Data Layer**: CIFAR-10 stream.
    2. **Monitoring**: Evidently AI for real-time drift detection.
    3. **Training**: Hugging Face Transformers (Vision Transformer).
    4. **Tracking**: MLflow for versioning and lineage.
    5. **Orchestration**: Airflow for scheduled retraining.
    """)

# --- Tab 2: Drift Monitoring ---
with tabs[1]:
    st.header("Data & Model Drift Detection")
    st.markdown("Monitor statistical shifts in image characteristics and model output distributions.")
    
    if st.button("⚡ Run Fresh Monitoring Report"):
        with st.spinner("Analyzing data distributions..."):
            # Use current python executable to ensure environment is inherited
            result = subprocess.run(
                [PYTHON_EXE, "src/drift_monitor.py"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                st.success("Analysis Complete!")
                gc.collect() # Clean up RAM
            else:
                st.error("Monitoring script failed!")
                st.code(result.stderr)
    
    if os.path.exists("data_drift_report.html"):
        with open("data_drift_report.html", "r") as f:
            html_data = f.read()
            components.html(html_data, height=800, scrolling=True)
    else:
        st.info("No report generated yet. Click the button above to start.")

# --- Tab 3: Model Training ---
with tabs[2]:
    st.header("Retrain Transformer Model")
    st.write("Trigger a manual fine-tuning run for the Vision Transformer on current data.")
    
    if st.button("🔥 Start Training Run"):
        st.info("Training initiated. Following progress in real-time...")
        progress_bar = st.progress(0)
        log_placeholder = st.empty()
        
        process = subprocess.Popen(
            [PYTHON_EXE, "src/train.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        all_logs = []
        for line in process.stdout:
            all_logs.append(line)
            # Simple heuristic for progress if training output is known
            if "Epoch" in line:
                progress_bar.progress(50) # Just an indicator
            log_placeholder.code("".join(all_logs[-15:]))
            
        process.wait()
        if process.returncode == 0:
            st.success("Model trained and registered in MLflow!")
            progress_bar.progress(100)
        else:
            st.error("Training failed. Check logs.")

# --- Tab 4: MLflow Tracking ---
with tabs[3]:
    st.header("Embedded MLflow Experiment UI")
    st.markdown("Direct access to metrics, parameters, and models stored in MLflow.")
    
    if is_port_in_use(5000):
        # Embed MLflow UI directly
        components.iframe("http://127.0.0.1:5000", height=800, scrolling=True)
    else:
        st.warning("MLflow server is not detected on port 5000.")
        if st.button("Launch MLflow Server"):
            subprocess.Popen(
                ["mlflow", "ui", "--backend-store-uri", "sqlite:///mlflow.db", "--port", "5000"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            st.info("Server launching... Please wait a few seconds and refresh this tab.")
            time.sleep(5)
            st.rerun()

# --- Tab 5: Airflow Pipelines ---
with tabs[4]:
    st.header("Pipeline Orchestration (Airflow)")
    st.markdown("Structure and execution history of the `vit_classifier_retraining_pipeline`.")
    
    # 1. Show DAG Structure using Mermaid
    st.subheader("⛓️ Pipeline Graph")
    st.markdown("""
    ```mermaid
    graph LR
        A[🔍 Monitor Data Drift] --> B[🚀 Retrain Transformer]
        B --> C[📦 Deploy Best Model]
        
        style A fill:#f9f,stroke:#333,stroke-width:2px
        style B fill:#bbf,stroke:#333,stroke-width:2px
        style C fill:#bfb,stroke:#333,stroke-width:2px
    ```
    """, unsafe_allow_html=True)
    st.info("The pipeline is configured to trigger automatically every 7 days or when critical drift is detected.")

    # 2. Show recent runs via CLI
    st.subheader("📜 Recent Run History")
    if st.button("🔄 Refresh Run Status"):
        with st.spinner("Fetching execution logs from Airflow..."):
            env = {
                **os.environ, 
                "AIRFLOW_HOME": os.path.join(os.getcwd(), "airflow_home"),
                "AIRFLOW__CORE__DAGS_FOLDER": os.path.join(os.getcwd(), "dags")
            }
            # Airflow 3 uses positional dag_id
            result = subprocess.run(
                ["airflow", "dags", "list-runs", "vit_classifier_retraining_pipeline", "-o", "json"],
                capture_output=True, text=True, env=env
            )
            if result.returncode == 0:
                try:
                    runs = json.loads(result.stdout)
                    if runs:
                        df_runs = pd.DataFrame(runs)
                        st.table(df_runs[["run_id", "state", "execution_date", "run_type"]])
                    else:
                        st.write("No runs recorded yet.")
                except:
                    st.code(result.stdout)
            else:
                st.warning("Could not fetch runs. Ensure Airflow scheduler is running.")

    st.markdown("---")
    st.markdown("### 🛠️ Access Full Airflow UI")
    st.markdown("If you need to manually trigger or re-run specific tasks, use the link below with your credentials.")
    st.markdown(f"[Launch Airflow Web Console](http://localhost:8080) (User: `admin` / Pass: `f3Z3HE79Xmynt4zZ`) ")


st.sidebar.markdown("---")
st.sidebar.write("Logged in as: **Admin**")
st.sidebar.write("Environment: **Production-Sim**")
if st.sidebar.button("System Reset"):
    st.cache_data.clear()
    st.rerun()

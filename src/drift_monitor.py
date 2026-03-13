import json
import numpy as np
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from evidently.metrics import ColumnDriftMetric

def generate_drift_report():
    print("Simulating dataset predictions for drift detection...")
    
    # Reference data (e.g., training distribution)
    np.random.seed(42)
    reference_data = pd.DataFrame({
        "confidence_score": np.random.normal(0.8, 0.1, 1000),
        "predicted_class": np.random.choice([0,1,2,3,4,5,6,7,8,9], 1000, p=[0.1]*10),
        "ground_truth": np.random.choice([0,1,2,3,4,5,6,7,8,9], 1000, p=[0.1]*10),
        "brightness": np.random.normal(120, 20, 1000)
    })
    
    # Current data containing clear drift
    current_data = pd.DataFrame({
        "confidence_score": np.random.normal(0.6, 0.2, 500), # Drifted
        "predicted_class": np.random.choice([0,1,2,3,4,5,6,7,8,9], 500, p=[0.3, 0.1, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.1, 0.15]), # Skewed drift
        "ground_truth": np.random.choice([0,1,2,3,4,5,6,7,8,9], 500, p=[0.1]*10),
        "brightness": np.random.normal(90, 15, 500) # Drifted image characteristic
    })
    
    print("Generating Evidently Drift Report (v0.4.x+ API)...")
    # Initialize Report
    report = Report(metrics=[
        DataDriftPreset(),
        ColumnDriftMetric(column_name="confidence_score"),
        ColumnDriftMetric(column_name="brightness")
    ])
    
    # Run the report
    report.run(reference_data=reference_data, current_data=current_data)
    
    # Save results
    report.save_html("data_drift_report.html")
    report.save_json("data_drift_report.json")
    
    print(f"Drift detection completed. Reports generated: data_drift_report.html, data_drift_report.json")
    
if __name__ == "__main__":
    generate_drift_report()

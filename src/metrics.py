import os
import time
from functools import wraps
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    push_to_gateway,
)

# --- Configuration ---

# Flag to enable/disable metrics collection
METRICS_ENABLED = os.environ.get("METRICS_ENABLED", "true").lower() == "true"
# URL for the Pushgateway
PUSHGATEWAY_URL = os.environ.get("PUSHGATEWAY_URL", "http://localhost:9091")
# Job name for Prometheus
JOB_NAME = "ai_robo_advisor_cli"

# Create a central registry
registry = CollectorRegistry()

# --- Metric Definitions for a CLI Job ---

workflow_runs_total = Counter(
    "workflow_runs_total",
    "Total number of workflow runs",
    ["status"],  # 'success' or 'failure'
    registry=registry
)

workflow_duration_seconds = Histogram(
    "workflow_duration_seconds",
    "Duration of workflow execution in seconds",
    registry=registry
)

workflow_last_run_timestamp = Gauge(
    "workflow_last_run_timestamp",
    "Timestamp of the last successful workflow run",
    registry=registry
)

model_inference_duration_seconds = Histogram(
    "model_inference_duration_seconds",
    "Model inference duration in seconds",
    ["model_name"], # e.g., 'investment_agent', 'analyst_agent'
    registry=registry
)

# --- Decorator for Model Inference ---
# (This was previously at the wrong indentation)
def track_inference_duration(model_name: str):
    """
    Decorator to track inference time for a specific model.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not METRICS_ENABLED:
                return func(*args, **kwargs)
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                model_inference_duration_seconds.labels(
                    model_name=model_name
                ).observe(duration)
        return wrapper
    return decorator

# --- Utility Functions ---

def setup_metrics():
    if METRICS_ENABLED:
        print(f"Metrics collection enabled. Will push to {PUSHGATEWAY_URL}")
    else:
        print("Metrics collection is disabled.")

def push_metrics():
    """
    Push all collected metrics to the Pushgateway.
    """
    if not METRICS_ENABLED:
        return

    try:
        push_to_gateway(
            PUSHGATEWAY_URL, 
            job=JOB_NAME, 
            registry=registry
        )
        print("Successfully pushed metrics to Pushgateway.")
    except Exception as e:
        print(f"❌ Error: Could not push metrics to Pushgateway: {e}")
        print("Please ensure the Pushgateway is running at " + PUSHGATEWAY_URL)
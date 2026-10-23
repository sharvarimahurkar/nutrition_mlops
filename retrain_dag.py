"""Airflow DAG (PLANNED / optional): daily drift check -> retrain when drift is found.
Copy into your Airflow dags/ folder. Needs `pip install apache-airflow`."""
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG("nutrition_retrain", start_date=datetime(2026, 1, 1), schedule="@daily", catchup=False) as dag:
    ingest = BashOperator(task_id="ingest_validate", bash_command="cd /app && python -m src.data_gen")
    drift = BashOperator(task_id="drift_check", bash_command="cd /app && python -c 'from src.drift import drift_report as d; r=d(); print(r); exit(1 if r[\"status\"]==\"drift_detected\" else 0)'")
    train = BashOperator(task_id="retrain", bash_command="cd /app && python -m src.train", trigger_rule="all_done")
    ingest >> drift >> train

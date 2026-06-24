from __future__ import annotations 

import pendulum 
from airflow import DAG 
from airflow.providers.standard.operators.bash import BashOperator 
from airflow.providers.standard.operators.python import PythonOperator

STUDENT_SCHEMA = "student14" 
PAIR_NAME = "student14_pair" 
DAG_ID = "week7_student14_weather_pipeline"

def print_student_context(student_schema: str, pair_name: str) -> None: 
    print("Student schema:", student_schema) 
    print("Pair name:", pair_name) 
    print("This DAG contains one real task that writes one log row to Azure SQL.")

with DAG( 
    dag_id=DAG_ID, 
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"), 
    schedule=None, 
    catchup=False, 
    tags=["week7", "student", STUDENT_SCHEMA], 
) as dag:
    
    start = BashOperator( 
        task_id="start", 
        bash_command=f'echo "Starting {DAG_ID}"', 
    )

    show_context = PythonOperator( 
        task_id="show_student_context", 
        python_callable=print_student_context, 
        op_kwargs={ 
            "student_schema": STUDENT_SCHEMA, 
            "pair_name": PAIR_NAME, 
        }, 
    )

    write_airflow_log = BashOperator( 
        task_id="write_airflow_run_log_to_azure_sql", 
        bash_command=( 
            "/opt/airflow/venv/bin/python " 
            "/opt/airflow/repos/week7_etl_starter/airflow/scripts/write_airflow_run_log.py " 
            f"--student-schema {STUDENT_SCHEMA} " 
            f"--pair-name {PAIR_NAME} " 
            "--dag-id '{{ dag.dag_id }}' " 
            "--run-id '{{ run_id }}'" 
        ), 
    )

    simulate_python_validation = BashOperator( 
        task_id="simulate_python_validation", 
        bash_command=f'echo "Would run Python validation for {STUDENT_SCHEMA}"', 
    )
    simulate_dbt_run = BashOperator( 
        task_id="simulate_dbt_run", 
        bash_command=f'echo "Would run dbt models for {STUDENT_SCHEMA}"', 
    )
    end = BashOperator( 
        task_id="end", 
        bash_command=f'echo "Finished {DAG_ID}"', 
    )

    start >> show_context >> write_airflow_log >> simulate_python_validation >> simulate_dbt_run >> end

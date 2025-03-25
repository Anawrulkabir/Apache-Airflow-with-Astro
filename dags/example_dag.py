
from airflow import DAG  # DAG is used to define the workflow structure
from airflow.operators.python import PythonOperator  # PythonOperator allows execution of Python functions as tasks
import pandas as pd  
from datetime import datetime 

# Define the DAG (Directed Acyclic Graph) for the workflow
with DAG(
    dag_id="weather_etl", 
    start_date=datetime(year=2024, month=1, day=1, hour=9, minute=0),  
    schedule="@daily",  
    catchup=True, 
    max_active_runs=1,  
    render_template_as_native_obj=True 
) as dag:
    
    #  ETL - Extract Transform Load

    # 1. Extract 
    def extract_data_callable():

        print("Extracting data from a weather API")
        return {
            "date": "2023-01-01",  
            "location": "NYC",  
            "weather": {
                "temp": 33,  
                "conditions": "Light snow and wind"  
            }
        }
    
    extract_data = PythonOperator(
        dag=dag, 
        task_id="extract_data", 
        python_callable=extract_data_callable  
    )


    
    # 2. Transform
    def transform_data_callable(raw_data):
        transformed_data = [
            [
                raw_data.get("date"), 
                raw_data.get("location"),  
                raw_data.get("weather").get("temp"),  
                raw_data.get("weather").get("conditions") 
            ]
        ]
        return transformed_data  

    transform_data = PythonOperator(
        dag=dag,  
        task_id="transform_data",  
        python_callable=transform_data_callable, 
        op_kwargs={"raw_data": "{{ ti.xcom_pull(task_ids='extract_data') }}"}  # Pass the output of "extract_data" as input
    )

    # 3. Load
    def load_data_callable(transformed_data):
        # Load the transformed data into a Pandas DataFrame
        loaded_data = pd.DataFrame(transformed_data)
        loaded_data.columns = [
            "date", 
            "location",  
            "weather_temp",  
            "weather_conditions"  
        ]
        print(loaded_data)

    load_data = PythonOperator(
        dag=dag,  
        task_id="load_data",  
        python_callable=load_data_callable, 
        op_kwargs={"transformed_data": "{{ ti.xcom_pull(task_ids='transform_data') }}"}  # Pass the output of "transform_data" as input
    )

    # Define the task dependencies (execution order)
    extract_data >> transform_data >> load_data  # "extract_data" runs first, followed by "transform_data", then "load_data"

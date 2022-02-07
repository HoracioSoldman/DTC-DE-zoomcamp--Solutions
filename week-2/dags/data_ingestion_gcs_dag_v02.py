import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
from pendulum import datetime
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'trips_data_all')

dataset_base_url = 'https://s3.amazonaws.com/nyc-tlc/trip+data'
dataset_file = 'yellow_tripdata_{{execution_date.strftime(\'%Y-%m\')}}.csv'
dataset_url = f'{dataset_base_url}/{dataset_file}'
path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")

dataset_output_file = 'yellow_tripdata_output_{{execution_date.strftime(\'%Y-%m\')}}.csv'
parquet_file = dataset_output_file.replace('.csv', '.parquet')



def format_to_parquet(src_file):
    if not src_file.endswith('.csv'):
        logging.error("Can only accept source files in CSV format, for the moment")
        return
    table = pv.read_csv(src_file)
    pq.write_table(table, src_file.replace('.csv', '.parquet'))


# NOTE: takes 20 mins, at an upload speed of 800kbps. Faster if your internet has a better upload speed
def upload_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    # check if the environment vars are here..
    print('Bucket: ',BUCKET, ' -- Project_id', PROJECT_ID)

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)


default_args = {
    "owner": "airflow",
    "start_date": datetime(2019, 1, 1),
    "end_date": datetime(2021, 1, 1),
    "depends_on_past": False,
    "retries": 1,
}

# NOTE: DAG declaration - using a Context Manager (an implicit way)
with DAG(
    dag_id="data_ingestion_gcs_dag_v02",
    description="""
        This dag retrieves monthly NY Yellow taxi data from January 2019 to December 2020.
    """, 
    schedule_interval="0 8 1 * *",
    default_args=default_args,
    catchup=True,
    max_active_runs=3,
    tags=['dtc-de', 'yellow taxi', '2019', '2020', 'NY taxi'],
) as dag:

    download_dataset_task = BashOperator(
        task_id="download_dataset_task",
        # bash_command=f"cp /opt/airflow/downloaded_data/yellow_tripdata_2021-01.csv {path_to_local_home}/{dataset_file}"
        bash_command=f"curl -sSLf {dataset_url} > {path_to_local_home}/{dataset_output_file}"
    )

    format_to_parquet_task = PythonOperator(
        task_id="format_to_parquet_task",
        python_callable=format_to_parquet,
        op_kwargs={
            "src_file": f"{path_to_local_home}/{dataset_output_file}",
        },
    )

    # TODO: Homework - research and try XCOM to communicate output values between 2 tasks/operators
    local_to_gcs_task = PythonOperator(
        task_id="local_to_gcs_task",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f"raw/{parquet_file}",
            "local_file": f"{path_to_local_home}/{parquet_file}",
        },
    )

  
    cleanup_local_storage_task = BashOperator(
        task_id="cleanup_local_storage_task",
        bash_command=f"rm {path_to_local_home}/{dataset_output_file} {path_to_local_home}/{parquet_file}"
    )


    download_dataset_task >> format_to_parquet_task >> local_to_gcs_task >> cleanup_local_storage_task
from datetime import datetime, timedelta
import pandas as pd
import tempfile

from airflow.models import DAG, Variable
from airflow.utils import dates
from airflow.settings import AIRFLOW_HOME
from airflow.operators.python import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.google.cloud.transfers.postgres_to_gcs import PostgresToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_local import GCSToLocalFilesystemOperator
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocSubmitPySparkJobOperator,
    DataprocDeleteClusterOperator,
)



CSV_FILENAME            = 'user_purchase.csv'
PROJECT_ID              = 'data-bootcamp-76724'
USER_PURCHASE_TABLE_NAME = 'user_purchase'
DATAPROC_TEMP_BUCKET    = 'dev-dataproc-temp-martin-denton-b6uf7'
DATAPROC_CLUSTER_NAME   = 'dev-dataproc-cluster-martin-denton-c7vg8'
DATAPROC_REGION         = 'us-west3'
MOVIE_REVIEWS_SCRIPT    = 'movie_reviews.py'
MOVIES_REVIEWS_INPUT    = 'movie_review.csv'
MOVIES_REVIEWS_OUTPUT   = 'movie_review_stage.csv'
LOGS_REVIEWS_SCRIPT     = 'log_reviews.py'
LOGS_REVIEWS_INPUT      = 'log_ewviews.csv'
LOGS_REVIEWS_OUTPUT     = 'ovie_review_stage.csv'
RAW_BUCKET              = 'dev-raw-martin-denton-a5te6'
STAGING_BUCKET          = 'dev-staging-martin-denton-a5te6'
STAGING_USER_PURCHASE_FILE = 'staging_user_purchase.csv'


# Default arguments
default_args = {
    "owner": "roberto.mendoza",
    'depends_on_past': False,
    "email": "ultrainla3@gmail.com",
    'start_date': dates.days_ago(1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=20),
}

def fecth_user_purchase_csv():
    url = 'https://'
    response = requests.get(url)



def load_user_purchase_data(csv_file):
    # data reading and minor transformations
    df = pd.read_csv(csv_file)
    df = df.dropna(subset=["CustomerID"]).copy()
    df["CustomerID"] = df["CustomerID"].apply(int)


    with tempfile.TemporaryDirectory() as tempdir:
        df.to_csv(f"{tempdir}/temp.csv", index=False, header=False)

        sql = f"""
        COPY {USER_PURCHASE_TABLE_NAME}
        FROM STDIN
        DELIMITER ',' 
        CSV;
        """

        pg_hook = PostgresHook(postgres_conn_id="postgres_default")
        pg_hook.copy_expert(sql=sql, filename=f"{tempdir}/temp.csv")


# Instantiate the DAG
with DAG(
    "user_purchase_pipeline",
    schedule_interval=None,
    start_date=datetime(2022, 4, 13),
    default_args=default_args,
    catchup=False,
) as dag:
    
    # Tasks
    task_create_user_purchase_table = PostgresOperator(
        task_id="create_user_purchase_table",
        postgres_conn_id="postgres_default",
        sql=f"""
            CREATE TABLE IF NOT EXISTS {USER_PURCHASE_TABLE_NAME} (
            invoice_number varchar(10),
            stock_code varchar(20),
            detail varchar(1000),
            quantity int,
            invoice_date timestamp,
            unit_price numeric(8,3),
            customer_id int,
            country varchar(20));
          """,
    )

    task_user_purchase_csv_to_local = GCSToLocalFilesystemOperator(
        task_id="user_purchase_file_to_local",
        gcp_conn_id="google_cloud_default",
        object_name=CSV_FILENAME,
        bucket=RAW_BUCKET,
        filename=f'{AIRFLOW_HOME}/user_purchase.csv',
    )

    # Save to Postgres
    task_user_purchase_local_to_postgres = PythonOperator(
        task_id="load_user_purchase_data_to_db",
        python_callable=load_user_purchase_data,
        op_kwargs={"csv_file": f'{AIRFLOW_HOME}/user_purchase.csv'},
    )

    task_user_purchase_postgres_to_csv_in_bucket = PostgresToGCSOperator(
        task_id="user_purchase_postgres_to_csv_in_bucet",
        postgres_conn_id="postgres_default",
        google_cloud_storage_conn_id="google_cloud_default",
        sql=f"select customer_id, quantity, unit_price from {USER_PURCHASE_TABLE_NAME};",
        bucket=STAGING_BUCKET,
        filename=STAGING_USER_PURCHASE_FILE,
        export_format="CSV",
        gzip=False,
        use_server_side_cursor=True,
    )

    task_create_dataproc_cluster = DataprocCreateClusterOperator(
        task_id="create_dataproc_cluster",
        project_id=PROJECT_ID,
        cluster_config={
            "temp_bucket": DATAPROC_TEMP_BUCKET,
            "software_config": {"image_version": "2.0"},
            "master_config": {
                "num_instances": 1,
                "machine_type_uri": "n1-standard-2",
                "disk_config": {
                    "boot_disk_type": "pd-standard",
                    "boot_disk_size_gb": 300,
                },
            },
            "worker_config": {
                "num_instances": 2,
                "machine_type_uri": "n1-standard-2",
                "disk_config": {
                    "boot_disk_type": "pd-standard",
                    "boot_disk_size_gb": 300,
                },
            },
        },
        region=DATAPROC_REGION,
        cluster_name=DATAPROC_CLUSTER_NAME,
        gcp_conn_id="google_cloud_default",
    )

    task_spark_movie_reviews_job = DataprocSubmitPySparkJobOperator(
        task_id="spark_movie_reviews_job",
        main=MOVIE_REVIEWS_SCRIPT,
        gcp_conn_id="google_cloud_default",
        cluster_name=DATAPROC_CLUSTER_NAME,
        job_name="movie_reviews_job",
        dataproc_jars=[
            "https://repo1.maven.org/maven2/org/apache/spark/spark-avro_2.12/3.1.1/spark-avro_2.12-3.1.1.jar"
        ],
        arguments=[
            "--input_file",
            MOVIES_REVIEWS_INPUT,
            "--output_path",
            MOVIES_REVIEWS_OUTPUT,
        ],
        region=DATAPROC_REGION,
        project_id=PROJECT_ID,
    )

    task_spark_log_reviews_job = DataprocSubmitPySparkJobOperator(
        task_id="spark_log_reviews_job",
        main=LOGS_REVIEWS_SCRIPT,
        gcp_conn_id="google_cloud_default",
        cluster_name=DATAPROC_CLUSTER_NAME,
        job_name="log_reviews_job",
        dataproc_jars=[
            "https://repo1.maven.org/maven2/org/apache/spark/spark-avro_2.12/3.1.1/spark-avro_2.12-3.1.1.jar"
        ],
        arguments=[
            "--input_file",
            LOGS_REVIEWS_INPUT,
            "--output_path",
            LOGS_REVIEWS_OUTPUT,
        ],
        region=DATAPROC_REGION,
        project_id=PROJECT_ID,
    )

    task_delete_dataproc_cluster = DataprocDeleteClusterOperator(
        task_id="delete_dataproc_cluster",
        project_id=PROJECT_ID,
        region=DATAPROC_REGION,
        cluster_name=DATAPROC_CLUSTER_NAME,
        gcp_conn_id="google_cloud_default",
        trigger_rule="all_done",
    )


    # Setting up dependencies
    # User purchase file
    (task_create_user_purchase_table >> task_user_purchase_csv_to_local >> task_user_purchase_local_to_postgres >>
     task_user_purchase_postgres_to_csv_in_bucket)

    # Movie and logs reviews files
    (task_create_dataproc_cluster >> [task_spark_movie_reviews_job, task_spark_log_reviews_job] >> task_delete_dataproc_cluster)


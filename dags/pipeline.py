from datetime import datetime, timedelta
import pandas as pd
import tempfile

from airflow.models import DAG
from airflow.models import Variable
from airflow.utils import dates
from airflow.operators.python import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.google.cloud.transfers.postgres_to_gcs import PostgresToGCSOperator
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocSubmitPySparkJobOperator,
    DataprocDeleteClusterOperator,
)



CSV_FILENAME = Variable.get("USER_PURCHASE_CSV")
PROJECT_ID = Variable.get("PROJECT_ID")
USER_PURCHASE_TABLE_NAME = Variable.get("USER_PURCHASE_TABLE")
DATAPROC_TEMP_BUCKET = Variable.get("DATAPROC_TEMP_BUCKET")
DATAPROC_CLUSTER_NAME = Variable.get("DATAPROC_CLUSTER_NAME")
DATAPROC_REGION = Variable.get("DATAPROC_REGION")


# Default arguments
default_args = {
    "owner": "roberto.mendoza",
    'depends_on_past': False,
    "email": "ultrainla3@gmail.com",
    'start_date': airflow.utils.dates.days_ago(1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=20),
}


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

    # Save to Postgres
    task_load_user_purchase_data_to_db = PythonOperator(
        task_id="load_user_purchase_data_to_db",
        python_callable=transform_and_load_user_purchase_data,
        op_kwargs={"csv_file": CSV_FILENAME},
    )

    task_user_purchase_postgres_to_csv_in_bucket = PostgresToGCSOperator(
        task_id="user_purchase_postgres_to_csv_in_bucet",
        postgres_conn_id="postgres_default",
        google_cloud_storage_conn_id="google_default",
        sql=f"select customer_id, quantity, unit_price from {USER_PURCHASE_TABLE_NAME};",
        bucket="{{var.value.STAGING_BUCKET}}",
        filename="{{var.value.CLEAN_USER_PURCHASE_FILE}}",
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
                    "boot_disk_size_gb": 500,
                },
            },
            "worker_config": {
                "num_instances": 2,
                "machine_type_uri": "n1-standard-2",
                "disk_config": {
                    "boot_disk_type": "pd-standard",
                    "boot_disk_size_gb": 500,
                },
            },
        },
        region=DATAPROC_REGION,
        cluster_name=DATAPROC_CLUSTER_NAME,
        gcp_conn_id="google_default",
    )

    task_spark_movie_reviews_job = DataprocSubmitPySparkJobOperator(
        task_id="spark_movie_reviews_job",
        main=MOVIE_REVIEWS_SCRIPT,
        gcp_conn_id="google_default",
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
        gcp_conn_id="google_default",
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
        gcp_conn_id="google_default",
        trigger_rule="all_done",
    )


    # Setting up dependencies
    # User purchase file
    (task_create_user_purchase_table >> task_load_user_purchase_data_to_db >> task_user_purchase_postgres_to_csv_in_bucket)

    # Movie and logs reviews files
    (task_create_dataproc_cluster >> [task_spark_movie_reviews_job, task_spark_log_reviews_job])

from datetime import datetime

import pandas as pd
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.utils import dates

from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator


CSV_FILE = Variable.get("USER_PURCHASE_CSV")
PROJECT_ID = Variable.get("PROJECT_ID")
USER_PURCHASE_TABLE_NAME = Variable.get("USER_PURCHASE_TABLE")


default_args = {
    "owner": "roberto.mendoza",
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(1),
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "ultrainla3@gmail.com",
    "retries": 1,
    "retry_delay": timedelta(minutes=15),
    "on_failure_callback": _send_fail_notification,
    "on_success_callback": _send_success_notification,
}

def transform_and_load_user_purchase_data(csv_file):
    df = pd.read_csv(csv_file)
    df = df.dropna(subset=["CustomerID"]).copy()
    df["CustomerID"] = df["CustomerID"].apply(int)

    with tempfile.TemporaryDirectory() as tempdir:
        df.to_csv(f"{tempdir}/temp.csv", index=False, header=False)

        sql = f"""
        COPY {USER_PURCHASE_TABLE}
        FROM STDIN
        DELIMITER ',' 
        CSV;
        """

        pg_hook = PostgresHook(postgres_conn_id="postgres_default")
        pg_hook.copy_expert(sql=sql, filename=f"{tempdir}/temp.csv")

with DAG(
    "user_purchase_pipeline",
    schedule_interval=None,
    start_date=datetime(2022, 4, 13),
    default_args=default_args,
    catchup=False,
) as dag:
    
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
    task_load_user_purchase_data = PythonOperator(
        task_id="load_user_purchase_data",
        python_callable=transform_and_load_user_purchase_data,
        op_kwargs={"csv_file": CSV_FILE},
    )


    task_create_user_purchase_table>> task_load_user_purchase_data




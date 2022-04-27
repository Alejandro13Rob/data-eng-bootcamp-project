import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.utils import dates
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.base_hook import BaseHook

logging.basicConfig(format="%(name)s-%(levelname)s-%(asctime)s-%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

default_args = {
    "owner": "roberto.mendoza",
    "description": (
            "print the airflow connections in URI format"
        ),
    'depends_on_past': False,
    'start_date': dates.days_ago(1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "provide_context": True,
}


def print_uris():
    conn = BaseHook.get_connection('google_cloud_default')
    print(f"AIRFLOW_CONN_{conn.conn_id.upper()}='{conn.get_uri()}'")

    conn2 = BaseHook.get_connection('postgres_default')
    print(f"AIRFLOW_CONN_{conn2.conn_id.upper()}='{conn2.get_uri()}'")


with DAG(
    "print_uris",
    schedule_interval=None,
    start_date=datetime(2022, 4, 13),
    default_args=default_args,
    catchup=False,
) as dag:

    task_print_uris = PythonOperator(
        task_id="print_uris",
        python_callable=print_uris,
    )

    task_print_uris

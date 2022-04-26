from airflow.hooks.base_hook import BaseHook

conn = BaseHook.get_connection('google_cloud_default')
print(f"AIRFLOW_CONN_{conn.conn_id.upper()}='{conn.get_uri()}'")

conn2 = BaseHook.get_connection('postgres_default')
print(f"AIRFLOW_CONN_{conn2.conn_id.upper()}='{conn2.get_uri()}'")

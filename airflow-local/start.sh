echo "Initializing database"
airflow db init

echo "creating user for airflow..."
airflow users create -e "admin@airflow.com" -f "airflow" -l "airflow" -p "airflow" -r "Admin" -u "airflow"

# Run the scheduler in background
airflow scheduler &> /dev/null &

exec airflow webserver
echo "webserver running"

exec /entrypoint "${@}"

from airflow import DAG
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from src.interface.import_user import ImportUser

from datetime import datetime

with DAG(dag_id='importer_user_to_db',
         start_date=datetime(2022, 5, 28),
         tags = ['database','users'],
         schedule_interval=None) as dag:

    start_task = EmptyOperator(task_id='start')

    @task.branch(task_id="import")
    def import_user_to_db():
        importer = ImportUser()
        importer.import_entity()
    
    import_user = import_user_to_db()

    end_task = EmptyOperator(task_id='end')

start_task >> import_user
import_user >> end_task

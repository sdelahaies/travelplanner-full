"""
   DAG to load datatourisme into mongo

   DB: itinerary
   collection: point_of_interest
   
   TODO: 
    - index_processed.json lacks an index!
      need to import the original datatoursime
      index, or create a new one.
   
    should the following tasks be considered
    as distinct DAGS or should we write one?
    - add the possibility to update the POIs, 
      could be scheduled to add new entries or 
      update entries regularly
    - add collections for each API/scraping we 
      gather data from : opentripmap, geoapify,
      mapbox, tripadvisor, ... 
"""

from airflow import DAG
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from src.interface.importer import Importer

from datetime import datetime

with DAG(dag_id='importer_datatourism_to_db',
          tags=['mongo','DB'],
         start_date=datetime(2022, 5, 28),
         schedule_interval=None) as dag:

    
    @task.branch(task_id="import")
    def import_datatourism_to_db():
        importer = Importer()
        importer.import_entity()
    
    import_datatourism = import_datatourism_to_db()

    

import_datatourism


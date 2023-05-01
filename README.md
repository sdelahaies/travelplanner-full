Final project for the Data Engineer @ DataScientest, jan2023 Bootcamp training

Authors S. Delahaies, A. Boutier, I. Noui, H. Elmi Ali
 
**Travel planning**: design, implement, deploy a travel planning web application

A brief overview of the project can be found in the post [Travel Planning Web App](https://sdelahaies.github.io/travelplanner.html).

---
# Install

```
# download the repo and enter the folder
git clone https://github.com/sdelahaies/travelplanner-full.git
cd travelplanner-full

docker compose up -d

# change ownership for the datalake folder if not already owned
sudo chown $USER:$USER datalake

# download the index_processed.json 
cd datalake
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1wPf55Bl9ObDQlxeN4kJDKqiYVZFRQrFT' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1wPf55Bl9ObDQlxeN4kJDKqiYVZFRQrFT" -O index_processed.json && rm -rf /tmp/cookies.txt
```
The next step consists in initializing the databases. Go to airflow UI at `http://localhost:8080` with the following credentials:
  - login: airflow
  - password: airflow

and run the dags `importer_datatourism_to_db` and `importer_user_to_db` to import the data into mongoDB.

Go to mongo-express at `http://localhost:8111` and check that the itinerary DB exists and that it contains the two collections `point_of_interest`  and `user`.

You can then access the web app at `http://localhost:8181/login` with the credentials:
  - login: travel
  - password: planner

and test the planner and auto-planner modes.

Note: the search bar is using the geolocation API adresse.data.gouv.fr it is therefore limited to France, the same goes for DATAtourisme data... Feel free to plug any worldwide geolocation API together with opentripmap to enable global travel planning. 

![image app](assets/auto-planner-opt.gif)
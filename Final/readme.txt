frontend files:
1. floorplan_images
2. templates
3. dash_test
4. heatmap.py
5. heatmap_debug

backend files:
1. data_cleaning
2. libDB
3. predictive_model
4. predDB

shared files:
1. datasets
2. config
3. DSA3101-2310-04-lib.pem
4. requirements

note:
* to run the application: 
	- cd to dir of this local repo 
	- execute docker compose up -d in terminal 
	- go to http://localhost:5050/home.html
* 1 container running all operations:
	- dash_test.py is dash application that provides user with data visualisation of library volume at different time and day. dash_test also allow user to upload a csv file that will help improve the 	prediction.
	- If valid file is uploaded, data_cleaning.py is triggered to clean the csv file, outputing a cleaned csv file at the end.
	- Which in turn trigger libDB.sh to input the cleaned csv file into sql.
	- predictive_model.py is then triggered to get data from sql and output a predicted csv.
	- Finally predDB will start up and store predicted csv into another database in SQL to be used by dash_test.py to show the visualisation of the prediction.


EXTRA: agent based simulation folder contains (work in progress)
* not part of our website but is what we plan to implement to improve our visualisation
* to see how it works cd to dir, docker compose up -d, go to containers of docker desktop and manually start netlogo container, go to http://localhost:10000/index.html?password=111
* folder contains:
1. agent_based-simulation_model
2. agent_based_simulation_model.nlogo
3. docker-compose
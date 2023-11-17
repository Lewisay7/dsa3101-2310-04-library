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
* for security reasons we uploaded the pem file and the datasets folder to sharepoint. Download datasets folder and DSA3101-2310-04-lib.pem from there and put it in the folder named 'Shared' and 'agent_based_simulation'. This is the link:
https://nusu.sharepoint.com/sites/Section_2310_1390/Shared%20Documents/Forms/AllItems.aspx?csf=1&web=1&e=hbllTP&cid=4c74dee9-5a67-4b25-a88d-a4c6b2b79f43&FolderCTID=0x012000BA950ECCC4DBF0438F37E82EEB2251D1&id=%2Fsites%2FSection_2310_1390%2FShared%20Documents%2FGeneral%2FVideo%20Submissions%2F04-library&viewid=bd5e0aee-4e23-43f5-9177-06817d4333d7

* the SSH_HOST in config.sh has to be changed manually if server is restarted

* the datasets folder contains 6 csv files:
	1. actual_seat_count.csv - count of different types of seats in library
	2. chair.csv - visitor's preference of chairs. This is from survey results
	3. clean_df.csv - a cleaned version of data provided by client
	4. dsa_data.csv - raw data provided by client
	5. floor.csv - visitor's preference of floors. This is from survey results
	6. model_output.csv - prediction data

* to run the application: 
	- cd to Final dir 
	- execute docker compose up -d in terminal 
	- go to http://localhost:5050/home.html

* when uploading a file on the website:
	1. the web will take some time to load. This is normal as the website will only be functional after backend scripts finished making prediction allowing frontend visualisation to present latest update.
	2. we assume the client will upload files similar to the data they provide us with so the file format (number of columns, name of columns, format & type of values, etc.) should be the same as dsa_data.csv.

* 1 container running all operations:
	- dash_test.py is dash application that provides user with data visualisation of library volume at different time and day. dash_test also allow user to upload a csv file that will help improve the prediction.
	- If valid file is uploaded, data_cleaning.py is triggered to clean the csv file, outputing a cleaned csv file at the end.
	- This will trigger libDB.sh to input the cleaned csv file into sql.
	- predictive_model.py is then triggered to get data from sql and output a predicted csv.
	- Finally predDB will start up and store predicted csv into another table in SQL to be used by dash_test.py to show the visualisation of the prediction.


EXTRA: agent based simulation folder contains (work in progress)
* not part of our website but is what we plan to implement in the future to improve our visualisation
* to see how it works cd to agent_based_simulation dir, docker compose up -d, go to http://localhost:10000/index.html?password=111
* folder contains:
1. agent_based-simulation_model
2. agent_based_simulation_model.nlogo
3. docker-compose

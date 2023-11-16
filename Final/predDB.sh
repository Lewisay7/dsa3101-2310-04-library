#!/bin/bash

source ./config.sh
PORT=3309
TABLE='PredictionTable'

# File to import
FILE_PATH='./datasets/model_output.csv'

# Start the SSH tunnel
ssh -4 -o StrictHostKeyChecking=no -i $SSH_KEY_PATH -N -L $PORT:$HOST:3306 $SSH_USER@$SSH_HOST &
SSH_PID=$!

# Give the SSH tunnel a moment to establish
sleep 5

# Use MySQL command line tool to import the CSV into the database
mysql --local-infile=1 -h $HOST -P $PORT -u $USER -p$PASSWORD $DATABASE -e "
    LOAD DATA LOCAL INFILE '$FILE_PATH' 
    INTO TABLE $TABLE 
    FIELDS TERMINATED BY ',' 
    OPTIONALLY ENCLOSED BY '\"' 
    LINES TERMINATED BY '\n' 
    IGNORE 1 LINES;
"

kill $SSH_PID





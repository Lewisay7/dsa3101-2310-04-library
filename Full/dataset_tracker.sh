#!/bin/bash

while inotifywait -e modify,create,delete,move -r app/datasets/dsa_data.csv; do

    docker-compose up -d
done
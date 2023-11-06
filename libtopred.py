import os
import pandas as pd
import sshtunnel
from sshtunnel import SSHTunnelForwarder
import mysql.connector

config_path = './config.sh'
config_vars = {}

with open(config_path, 'r') as file:
    for line in file:
        if line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        config_vars[key] = value

ssh_host = config_vars['SSH_HOST']
ssh_username = config_vars['SSH_USER']
ssh_key_path = config_vars['SSH_KEY_PATH']
mysql_host = config_vars['HOST']
mysql_user = config_vars['USER']
mysql_password = config_vars['PASSWORD']
mysql_db = config_vars['DATABASE']
local_bind_port = 5000
mysql_port = 3306
remote_bind_port = mysql_port

try:
    tunnel = SSHTunnelForwarder(
        (ssh_host, 22),
        ssh_username=ssh_username,
        ssh_private_key=ssh_key_path,
        remote_bind_address=(mysql_host, remote_bind_port),
        local_bind_address=('127.0.0.1', local_bind_port)
    )
    tunnel.start()
except Exception as e:
    exit(1)

try:
    connection = mysql.connector.connect(
        user=mysql_user,
        password=mysql_password,
        host='127.0.0.1',
        port=local_bind_port,
        database=mysql_db,
        use_pure=True
    )
    if connection.is_connected():
        cursor = connection.cursor()
        sample_query = "SELECT * FROM LibraryRecords LIMIT 5;"
        cursor.execute(sample_query)
        result = cursor.fetchall()
        print(result)
        cursor.close()
except mysql.connector.Error:
    pass
finally:
    if 'connection' in locals() or 'connection' in globals() and connection.is_connected():
        connection.close()
    tunnel.stop()

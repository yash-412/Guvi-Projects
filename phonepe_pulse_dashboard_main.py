import os
import json
import pandas as pd
import mysql.connector
from mysql.connector import Error

state_folder_path = 'D:/VSCodium/Guvi-Projects/pulse/data/aggregated/transaction/country/india/state/'

all_data = []

# Use os.listdir() to get a list of all folders inside the "state" folder
state_subfolders = [folder for folder in os.listdir(state_folder_path) if os.path.isdir(os.path.join(state_folder_path, folder))]

# Loop through each state's folder
for state_subfolder in state_subfolders:
    state_subfolder_path = os.path.join(state_folder_path, state_subfolder)
    
    year_subfolders = [folder for folder in os.listdir(state_subfolder_path) if os.path.isdir(os.path.join(state_subfolder_path, folder))]
    
    #print(f"State: {state_subfolder}")
    
    for year_subfolder in year_subfolders:
        year_subfolder_path = os.path.join(state_subfolder_path, year_subfolder)
        
        json_files = [file for file in os.listdir(year_subfolder_path) if file.endswith('.json')]
        
        #print(f"  Year: {year_subfolder}")
        
        for json_file in json_files:
            #print(f"    JSON File: {json_file}")
            
            json_file_path = os.path.join(year_subfolder_path, json_file)
            
            with open(json_file_path, 'r') as json_file:
                data = json.load(json_file)
                
                year = int(year_subfolder)
                state_name = state_subfolder
                
                for transaction in data['data']['transactionData']:
                    transaction_name = transaction['name']
                    payment_instrument = transaction['paymentInstruments'][0]
                    
                    row = {
                        'year': year,
                        'state': state_name,
                        'transaction_name': transaction_name,
                        'payment_instrument_type': payment_instrument['type'],
                        'payment_instrument_count': payment_instrument['count'],
                        'payment_instrument_amount': payment_instrument['amount']
                    }
                    all_data.append(row)

df = pd.DataFrame(all_data)

# Define your MySQL connection parameters
host = 'localhost'
database = 'phonepe_pulse'
user = 'root'
password = '+91naveen'

try:
    # Establish a connection to the MySQL database
    connection = mysql.connector.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )

    if connection.is_connected():
        cursor = connection.cursor()

        # Create a table to store the DataFrame data
        create_table_query = """
        CREATE TABLE IF NOT EXISTS india_states (
            year INT,
            state VARCHAR(255),
            transaction_name VARCHAR(255),
            payment_instrument_type VARCHAR(255),
            payment_instrument_count INT,
            payment_instrument_amount FLOAT
        )
        """
        cursor.execute(create_table_query)

        # Insert the DataFrame data into the MySQL table
        for index, row in df.iterrows():
            insert_query = """
            INSERT INTO india_states (year, state, transaction_name, payment_instrument_type, payment_instrument_count, payment_instrument_amount)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            data_tuple = (row['year'], row['state'], row['transaction_name'], row['payment_instrument_type'], row['payment_instrument_count'], row['payment_instrument_amount'])
            cursor.execute(insert_query, data_tuple)

        # Commit the changes and close the cursor and connection
        connection.commit()
        cursor.close()
        connection.close()
        print("Data inserted successfully!")

except Error as e:
    print(f"Error: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
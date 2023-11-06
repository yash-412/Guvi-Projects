'''pip install streamlit
pip install pandas
pip install mysql-connector-python
pip install plotly
pip install gitpython'''

import streamlit as st
import os
import json
import pandas as pd
import mysql.connector
from mysql.connector import Error
import plotly.express as px
import plotly.graph_objects as go
import io
import git
import shutil
from plotly.subplots import make_subplots

st.title("PhonePe Pulse Dashboard")

repo_url = 'https://github.com/PhonePe/pulse.git'
local_directory = 'D:/VSCodium/Guvi-Projects'

if os.path.exists(local_directory):
    # If it exists, update the existing repository
    repo = git.Repo(local_directory)
    origin = repo.remotes.origin
    origin.pull()
else:
    # If it doesn't exist, clone the repository
    git.Repo.clone_from(repo_url, local_directory)

host = 'localhost'
database = 'phonepe_pulse'
user = 'root'
password = '+91naveen'

state_mapping = {
    'andaman-&-nicobar-islands': 'Andaman and Nicobar',
    'andhra-pradesh': 'Andhra Pradesh',
    'arunachal-pradesh': 'Arunachal Pradesh',
    'assam': 'Assam',
    'bihar': 'Bihar',
    'chandigarh': 'Chandigarh',
    'chhattisgarh': 'Chhattisgarh',
    'dadra-&-nagar-haveli-&-daman-&-diu': 'Dadra and Nagar Haveli',
    'delhi': 'Delhi',
    'goa': 'Goa',
    'gujarat': 'Gujarat',
    'haryana': 'Haryana',
    'himachal-pradesh': 'Himachal Pradesh',
    'jammu-&-kashmir': 'Jammu & Kashmir',
    'jharkhand': 'Jharkhand',
    'karnataka': 'Karnataka',
    'kerala': 'Kerala',
    'ladakh': 'Ladakh',
    'lakshadweep': 'Lakshadweep',
    'madhya-pradesh': 'Madhya Pradesh',
    'maharashtra': 'Maharashtra',
    'manipur': 'Manipur',
    'meghalaya': 'Meghalaya',
    'mizoram': 'Mizoram',
    'nagaland': 'Nagaland',
    'odisha': 'Odisha',
    'puducherry': 'Puducherry',
    'punjab': 'Punjab',
    'rajasthan': 'Rajasthan',
    'sikkim': 'Sikkim',
    'tamil-nadu': 'Tamil Nadu',
    'telangana': 'Telangana',
    'tripura': 'Tripura',
    'uttar-pradesh': 'Uttar Pradesh',
    'uttarakhand': 'Uttaranchal',
    'west-bengal': 'West Bengal'
}

def load_transaction_data(state_folder_path_transaction):
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
                
                quarter = json_file.split('.')[0]
                
                with open(json_file_path, 'r') as json_file:
                    data = json.load(json_file)
                    
                    year = int(year_subfolder)
                    state_name = state_subfolder
                    
                    for transaction in data['data']['transactionData']:
                        transaction_name = transaction['name']
                        payment_instrument = transaction['paymentInstruments'][0]
                        
                        row = {
                            'year': year,
                            'quarter': quarter,
                            'state': state_name,
                            'transaction_name': transaction_name,
                            'payment_instrument_type': payment_instrument['type'],
                            'payment_instrument_count': payment_instrument['count'],
                            'payment_instrument_amount': payment_instrument['amount']
                        }
                        all_data.append(row)

    df = pd.DataFrame(all_data)
    df['state_code'] = df['state'].map(state_mapping)
    return df

def load_user_data(state_folder_path):

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
                
                quarter = json_file.split('.')[0]
                
                with open(json_file_path, 'r') as json_file:
                    data = json.load(json_file)
                    
                    year = int(year_subfolder)
                    state_name = state_subfolder
                    
                    user_data = data['data']['usersByDevice']

                    if user_data is None:
                        continue

                    for user in user_data:
                        brand = user['brand']
                        count = user['count']
                        
                        row = {
                            'year': year,
                            'quarter': quarter,
                            'state': state_name,
                            'brand': brand,
                            'count': count,
                        }
                        all_data.append(row)

    df_user = pd.DataFrame(all_data)
    df_user['state_code'] = df_user['state'].map(state_mapping)

    return df_user

custom_purples = ["#f2f0f7", "#dadaeb", "#bcbddc", "#9e9ac8", "#756bb1", "#54278f"]

def transactions_map(selected_data, year, quarter):
    fig = go.Figure(data=go.Choropleth(
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locationmode='geojson-id',
        locations=selected_data['state_code'],
        z=selected_data['payment_instrument_amount'],


        autocolorscale=False,
        colorscale=custom_purples,  # Choose an appropriate color scale
        zmin=194000,  # Set the minimum value in your data
        zmax=506000000,  # Set the maximum value in your data
        marker_line_color='peachpuff',

        colorbar=dict(
            title={'text': "Transactions"},
            title_font={'family': 'Arial', 'size': 18, 'color': 'black'},
            thickness=15,
            len=0.35,
            bgcolor='rgba(255,255,255,0.6)',
            nticks=10,
            tick0=0,
            dtick=50000000,  # Adjust the tick interval
        )
    ))

    fig.update_geos(
        visible=False,
        projection=dict(
            type='conic conformal',
            parallels=[12.472944444, 35.172805555556],
            rotation={'lat': 24, 'lon': 80}
        ),
        lonaxis={'range': [68, 98]},
        lataxis={'range': [6, 38]}
    )

    fig.update_layout(
        title=dict(
            text=f"PhonePe Pulse {year} Q{quarter}",
            xanchor='center',
            x=0.5,
            yref='paper',
            yanchor='bottom',
            y=1,
            pad={'b': 10},
            font={'family': 'Arial', 'size': 24, 'color': 'black'}
        ),
        margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
        height=550,
        width=550
    )

    return fig

def user_map(selected_data, year, quarter):
    fig = go.Figure(data=go.Choropleth(
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locationmode='geojson-id',
        locations=selected_data['state_code'],
        z=selected_data['count'],


        autocolorscale=False,
        colorscale=custom_purples,  # Choose an appropriate color scale
        zmin=500,  # Set the minimum value in your data
        zmax=1000000,  # Set the maximum value in your data
        marker_line_color='peachpuff',

        colorbar=dict(
            title={'text': "Users by brand"},
            title_font={'family': 'Arial', 'size': 18, 'color': 'black'},
            thickness=15,
            len=0.35,
            bgcolor='rgba(255,255,255,0.6)',
            nticks=10,
            tick0=selected_data['count'].min(),
            dtick=(selected_data['count'].max() - selected_data['count'].min()) / 10,  # Adjust the tick interval
        )
    ))

    fig.update_geos(
        visible=False,
        projection=dict(
            type='conic conformal',
            parallels=[12.472944444, 35.172805555556],
            rotation={'lat': 24, 'lon': 80}
        ),
        lonaxis={'range': [68, 98]},
        lataxis={'range': [6, 38]}
    )

    fig.update_layout(
        title=dict(
            text=f"PhonePe Pulse {year} Q{quarter}",
            xanchor='center',
            x=0.5,
            yref='paper',
            yanchor='bottom',
            y=1,
            pad={'b': 10},
            font={'family': 'Arial', 'size': 24, 'color': 'black'}
        ),
        margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
        height=550,
        width=550
    )

    return fig

def insert_data_transaction(df,host,database,user,password):
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

def insert_data_users(df, host, database, user, password):
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

            # Create a table to store the data
            create_table_query = """
            CREATE TABLE IF NOT EXISTS user_data (
                year INT,
                quarter VARCHAR(255),
                state VARCHAR(255),
                brand VARCHAR(255),
                count INT
            )
            """
            cursor.execute(create_table_query)

            # Insert the data into the MySQL table
            for index, row in df.iterrows():
                insert_query = """
                INSERT INTO user_data (year, quarter, state, brand, count)
                VALUES (%s, %s, %s, %s, %s)
                """
                data_tuple = (row['year'], row['quarter'], row['state'], row['brand'], row['count'])
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

def data_from_mysql_transaction(host, database, user, password):
    try:
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )

        if connection.is_connected():
            # Replace 'your_query' with your SQL query to fetch the data
            query = "SELECT * FROM transaction_data"
            df = pd.read_sql(query, connection)
            return df

    except Exception as e:
        st.error(f"Error: {e}")
        return None

def data_from_mysql_user(host, database, user, password):
    try:
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )

        if connection.is_connected():
            # Replace 'your_query' with your SQL query to fetch the data
            query = "SELECT * FROM user_data"
            df = pd.read_sql(query, connection)
            return df

    except Exception as e:
        st.error(f"Error: {e}")
        return None

tab1, tab2, tab3 = st.tabs(["Transaction","Users","Database Connection"])

with tab1:
    
    option = st.selectbox("Select an Option:", ["Explore Transaction Data", "Transaction Type Analysis"])

    state_folder_path = 'D:/VSCodium/Guvi-Projects/pulse/data/aggregated/transaction/country/india/state/' # for transaction
    df = load_transaction_data(state_folder_path)

    if option == "Explore Transaction Data":
        st.header("Transactions Data")
        column1, column2, column3 = st.columns([2,3,1],gap="small")

        with column1:
            years = df['year'].unique()
            selected_year = st.selectbox("Select Year (Transactions):", years)

            quarter = df['quarter'].unique()
            selected_quarter = st.selectbox("Select Quarter (Transactions):", quarter)

            selected_data = df[(df['year'] == selected_year) & (df['quarter'] == selected_quarter)]
            
            states = selected_data['state_code'].unique()
            selected_state = st.selectbox("State (Transactions):", states)
            state = selected_data[selected_data['state_code'] == selected_state]

        with column2:
            if selected_data is not None:
                fig = transactions_map(selected_data, selected_year, selected_quarter)
                st.plotly_chart(fig)
        
        drop_columns = ['year','quarter','state', 'payment_instrument_type','state_code']
        state = state.drop(columns=drop_columns)
        st.dataframe(state, height=213, width=1220, use_container_width=True)

        with column3:
            st.subheader('Total transactions in India')
            
            total_transactions = df['payment_instrument_amount'].sum()
            st.markdown(total_transactions)

            st.subheader(f'Total transactions in {selected_state}')

            total_transactions_state = state['payment_instrument_amount'].sum().round(2)
            st.markdown(total_transactions_state)

    if option == "Transaction Type Analysis":

        st.title("Transaction Type Analysis")

        # Dropdowns for filtering data
        selected_state = st.selectbox("Select State:", df['state_code'].unique())
        selected_transaction_type = st.selectbox("Select Transaction Type:", df['transaction_name'].unique())

        # Filter the data based on dropdown selections
        filtered_df = df[(df['state_code'] == selected_state) &
                        (df['transaction_name'] == selected_transaction_type)]

        # Create a line chart for Payment Instrument Count using Plotly
        fig_count = px.line(
            filtered_df,
            x='year',
            y='payment_instrument_count',
            labels={'year': 'Year', 'payment_instrument_count': 'Payment Instrument Count'},
            title=f'Payment Instrument Count Growth',
        )

        # Add quarters between years
        quarters = [f'Q{q}' for q in filtered_df['quarter']]
        fig_count.update_xaxes(type='category', categoryarray=quarters)

        # Create a line chart for Payment Instrument Amount using Plotly
        fig_amount = px.line(
            filtered_df,
            x='year',
            y='payment_instrument_amount',
            labels={'year': 'Year', 'payment_instrument_amount': 'Payment Instrument Amount'},
            title=f'Payment Instrument Amount Growth',
        )

        # Add quarters between years
        fig_amount.update_xaxes(type='category', categoryarray=quarters)

        # Display the charts side by side using st.columns()
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(fig_count)

        with col2:
            st.plotly_chart(fig_amount)

        col_a, col_b = st.columns(2)

        with col_b:
            st.title("Payment Instrument Analysis")
            # Dropdowns for filtering data
            selected_state = st.selectbox("Select State :", df['state_code'].unique())
            selected_year = st.selectbox("Select Year :", df['year'].unique())

            # Filter the data based on the selected state and year
            filtered_df = df[(df['state_code'] == selected_state) & (df['year'] == selected_year)]

        with col_a:
            # Create a pie chart for Payment Instrument Amount using Plotly
            fig = px.pie(
                filtered_df,
                names='transaction_name',
                values='payment_instrument_amount',
                title=f'Payment Instrument Amount Distribution in {selected_state} - {selected_year}',
            )

            # Show the pie chart
            st.plotly_chart(fig)

with tab2:
    
    option = st.selectbox("Select an Option:", ["Explore User Data", "Diversity of Users by Brand", "Detailed Statistics"])

    if option == "Explore User Data":
        st.header("Explore User Data")
        state_folder_path = 'D:/VSCodium/Guvi-Projects/pulse/data/aggregated/user/country/india/state/' # for user
        df = load_user_data(state_folder_path)

        column1, column2, column3 = st.columns([2,3,1],gap="small")

        with column1:
            years = df['year'].unique()
            selected_year = st.selectbox("Select Year (Users):", years)

            quarter = df['quarter'].unique()
            selected_quarter = st.selectbox("Select Quarter (Users):", quarter)

            selected_data = df[(df['year'] == selected_year) & (df['quarter'] == selected_quarter)]

            states = selected_data['state_code'].unique()
            selected_state = st.selectbox("State (Users):", states)
            state = selected_data[selected_data['state_code'] == selected_state]   


        with column2:
            if selected_data is not None:
                fig = user_map(selected_data, selected_year, selected_quarter)
                st.plotly_chart(fig)
        
        drop_columns = ['year','quarter','state','state_code']
        state = state.drop(columns=drop_columns)
        st.dataframe(state, height=213, width=1200, use_container_width=True)

        with column3:
            st.subheader('Total users in India')
            
            total_count = df['count'].sum()
            st.markdown(total_count)

            st.subheader(f'Total users in {selected_state}')

            total_count_state = state['count'].sum()
            st.markdown(total_count_state)
    
    elif option == "Diversity of Users by Brand":

        state_folder_path = 'D:/VSCodium/Guvi-Projects/pulse/data/aggregated/user/country/india/state/' # for user
        df = load_user_data(state_folder_path)
        grouped_df = df.groupby(['year','brand'])['count'].sum().reset_index()

        fig = px.bar(
        grouped_df,
        x='year',
        y='count',
        color='brand',
        labels={'year': 'Year', 'count': 'Total Count'},
        title='Diversity of Users by Brand'
        )
        fig.update_layout(height=800)
        st.plotly_chart(fig, use_container_width=True)

    elif option == "Detailed Statistics":
        st.header("Detailed Statistics")
        
        state_folder_path = 'D:/VSCodium/Guvi-Projects/pulse/data/aggregated/user/country/india/state/' # for user
        df = load_user_data(state_folder_path)
        left_column, right_column = st.columns([2, 1])

        with right_column:
            year = st.selectbox("Select Year  :", df['year'].unique())
            quarter = st.selectbox("Select Quarter  :", df['quarter'].unique())
            state = st.selectbox("Select State  :", df['state_code'].unique())

            # Filter data based on selected values
            filtered_data = df[(df['year'] == year) & (df['quarter'] == quarter) & (df['state_code'] == state)]

        with left_column:
            if not filtered_data.empty:
                # Create a pie chart
                fig = px.pie(filtered_data, values='count', names='brand', title='Brand Distribution')

                # Display the pie chart
                st.plotly_chart(fig)
            else:
                st.write("No data available for the selected filters.")

    with tab3:
        st.title("Data In SQL Database")

        st.header("Transactions Data Table")
        state_folder_path = 'D:/VSCodium/Guvi-Projects/pulse/data/aggregated/transaction/country/india/state/'
        df = load_transaction_data(state_folder_path)
        insert_data_transaction(df,host,database,user,password)
        df_got = data_from_mysql_transaction(host, database, user, password)

        st.dataframe(df_got)
        info_buffer = io.StringIO()
        df_got.info(buf=info_buffer)
        info_text = info_buffer.getvalue()
        st.text(info_text)

        st.header("Users Data Table")
        state_folder_path = 'D:/VSCodium/Guvi-Projects/pulse/data/aggregated/user/country/india/state/'
        df = load_user_data(state_folder_path)
        insert_data_users(df, host, database, user, password)
        df_got = data_from_mysql_user(host, database, user, password)

        st.dataframe(df_got)
        info_buffer = io.StringIO()
        df_got.info(buf=info_buffer)
        info_text = info_buffer.getvalue()
        st.text(info_text)

# streamlit run D:\VSCodium\Guvi-Projects\phonepe_pulse_dashboard.py
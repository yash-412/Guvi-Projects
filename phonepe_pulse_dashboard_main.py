import streamlit as st
import os
import json
import pandas as pd
import mysql.connector
from mysql.connector import Error
import plotly.express as px
import plotly.graph_objects as go

st.title("PhonePe Pulse")

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

state_folder_path = 'D:/VSCodium/Guvi-Projects/pulse/data/aggregated/transaction/country/india/state/' # for transaction

def load_transaction_data(state_folder_path):
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

df = load_transaction_data(state_folder_path)

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

tab1, tab2 = st.tabs(["Transaction","Users"])

with tab1:
    st.header("Transactions Data")

    left_column, right_column = st.columns([2,2],gap="large")

    with left_column:
        years = df['year'].unique()
        selected_year = st.selectbox("Select Year:", years)

        quarter = df['quarter'].unique()
        selected_quarter = st.selectbox("Select Quarter:", quarter)

        selected_data = df[(df['year'] == selected_year) & (df['quarter'] == selected_quarter)]
        
        states = selected_data['state_code'].unique()
        selected_state = st.selectbox("State:", states)
        state = selected_data[selected_data['state_code'] == selected_state]

    with right_column:
        if selected_data is not None:
            fig = transactions_map(selected_data, selected_year, selected_quarter)
            st.plotly_chart(fig)
    
    drop_columns = ['year','quarter','state', 'payment_instrument_type','state_code']
    state = state.drop(columns=drop_columns)
    st.dataframe(state, height=213, width=1220, use_container_width=True)

with tab2:
    st.header("Users Data")

# streamlit run C:\Users\Yash\Desktop\phonepe_pulse_dashboard.py
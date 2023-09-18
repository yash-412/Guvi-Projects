# Guvi-Projects-streamlit_yt2_active

Project Name: YouTube Data Migration and Query Tool

Description:

This Python script is designed to fetch data from YouTube channels, store it in a MongoDB database, migrate that data to a PostgreSQL SQL database, and provide various options for querying the stored data. The script uses several Python libraries and APIs to accomplish these tasks.

Project Structure:

The code is divided into several sections, each with specific functionality:

Data Extraction from YouTube:

The script uses the Google API Client Library to interact with the YouTube Data API. It fetches data such as channel details, playlists, playlist items, videos, and comments related to a specified YouTube channel.
Loading Data into MongoDB:

The extracted data is stored in a MongoDB database. It establishes a connection to MongoDB using pymongo and stores data in the "guvi" database and the "book" collection.
Migrate Data Option:

This section includes a function (migrate_data) that migrates data from MongoDB to a PostgreSQL SQL database. It structures the data and inserts it into SQL tables for channel, playlists, videos, and comments.
SQL Database Configuration:

The script establishes a connection to the PostgreSQL SQL database using the SQLAlchemy library. It sets up the database URL and creates SQLAlchemy session objects for interacting with the database.
Streamlit User Interface:

The user interface is built using the Streamlit library. Users can select various options:
"Insert Data" to fetch YouTube data and store it in MongoDB.
"Migrate Data" to migrate data from MongoDB to SQL and display the migrated data.
"Query Data" to run predefined SQL queries on the SQL database and display the query results.
"Show Data" to view selected YouTube data.
Predefined SQL Queries:

The script includes predefined SQL queries that users can select and run. These queries cover various aspects of the stored data, such as video views, likes, comments, playlists, and more.
Instructions for Running:

Install the required Python libraries using pip install google-api-python-client streamlit sqlalchemy psycopg2 pymongo pandas isodate.

Obtain a YouTube Data API key and replace api_key in the code with your API key.

Configure MongoDB and PostgreSQL database connections by replacing database URLs and credentials in the code.

Execute the script using Python.

Use the Streamlit web interface to interact with the application, fetch data, migrate data, query data, and view data.

Dependencies:

Google API Client Library
Streamlit
SQLAlchemy
psycopg2
pymongo
pandas
isodate

Notes:

Ensure that you have the necessary API keys and credentials for YouTube Data API, MongoDB, and PostgreSQL.
Before running the code, set up the database structures (tables) in the PostgreSQL database as required by the code.
Always handle API keys and database credentials securely.
The script offers flexibility in terms of data retrieval and querying YouTube data. You can further customize it to meet your specific requirements.
Take caution when migrating or querying data as it may affect the contents of your databases.
Disclaimer:

This code is provided as a sample and should be used responsibly and in accordance with YouTube's terms of service and API usage policies.

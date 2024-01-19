import os
import googleapiclient.errors
import json
import streamlit as st
import psycopg2
from googleapiclient.discovery import build
import pymongo
from pymongo.mongo_client import MongoClient
from googleapiclient.errors import HttpError
from streamlit_webrtc import webrtc_streamer
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer, BigInteger, Text, MetaData, create_engine, Table, cast, text, DateTime, TIMESTAMP, select, func, Interval
from sqlalchemy.ext.declarative import declarative_base
import isodate

api_key = 'AIzaSyCiH_CF2iTOAP3NyGf88Tb1bC1780bK9x4'
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

m = pymongo.MongoClient("mongodb://guvi_1:guvi1234@ac-qdjuliv-shard-00-00.t5ahkrs.mongodb.net:27017,ac-qdjuliv-shard-00-01.t5ahkrs.mongodb.net:27017,ac-qdjuliv-shard-00-02.t5ahkrs.mongodb.net:27017/?ssl=true&replicaSet=atlas-117bl4-shard-0&authSource=admin&retryWrites=true&w=majority")
db=m['guvi']
col=db['book']

db_url = "postgresql://postgres:+91naveen@localhost/Youtube Exp"
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

conn = psycopg2.connect(
    host="localhost",
    dbname="Youtube Exp",
    password="+91naveen",
    user="postgres"
)
cursor = conn.cursor()

def channel_id(channel_name):
    channel_id = ""
    channel_search = youtube.search().list(
        part="id",
        q=channel_name,
        type="channel",
        maxResults=1
    )
    channel_search_response = channel_search.execute()

    if 'items' in channel_search_response:
        channel_id = channel_search_response['items'][0]['id']['channelId']

    return channel_id

def channel_details(channel_id):
    channel_details = {}
    channel_search = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    )
    channel_search_response = channel_search.execute()

    if 'items' in channel_search_response:
        channel_data = channel_search_response['items']
        channel_details = channel_data
    return channel_details

def playlist_details(channel_id):
    playlist_ids = []
    playlists_detail = []
    playlist_search = youtube.playlists().list(
        part="contentDetails,id,snippet",
        channelId=channel_id,
        maxResults=50
    )
    playlist_search_response = playlist_search.execute()
    playlist_detail = playlist_search_response['items']
    playlists_detail.append(playlist_detail)

    if 'items' in playlist_search_response:
        for item in playlist_search_response['items']:
            playlist_id = item['id']
            playlist_ids.append(playlist_id)

    return playlist_ids, playlists_detail  

def playlist_items(playlist_ids):
    playlist_items = []
    video_ids = [] 

    for playlist_id in playlist_ids:
        next_page_token = None
        while True:
            playlist_items_request = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            playlist_items_response = playlist_items_request.execute()

            if 'items' in playlist_items_response:
                for item in playlist_items_response['items']:
                    playlist_items.append(item['snippet'])
                    if 'resourceId' in item['snippet'] and 'videoId' in item['snippet']['resourceId']:
                        video_id = item['snippet']['resourceId']['videoId']
                        video_ids.append(video_id)

            next_page_token = playlist_items_response.get('nextPageToken')
            if not next_page_token:
                break

    return video_ids, playlist_items

def video_details(video_ids):
    video_details = []

    for video_id in video_ids:
        video_request = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id
        )
        video_response = video_request.execute()

        if 'items' in video_response:
            video_details.append(video_response['items'])

    return video_details

def comments(video_ids):
    video_comments = []

    for video_id in video_ids:
        try:
            comment_request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=10
            )
            comment_response = comment_request.execute()
            video_comments.append(comment_response)
        except Exception as e:
            print(f"{video_id}")
            continue  
    return video_comments

def main(channel_names):
    c_id = channel_id(channel_names)
    c = channel_details(c_id)
    p = playlist_details(c_id)
    p_i = playlist_items(p[0])
    v = video_details(p_i[0])
    cm = comments(p_i[0])

    data = {
            "channel": c,
            "playlists": p[1],
            "playlist_items": p_i[1],
            "videos": v,
            "comments": cm
            }
    
    
    return data

def migrate_data(col, engine):
    channel_data = []
    channel = col.find_one({}).get("channel", {})
    channel_info = channel[0]['snippet']
    channel_statistics = channel[0]['statistics']
    channel_id = channel[0]['id']
    channel_title = channel_info['title']
    channel_description = channel_info['description']
    channel_published_date = channel_info['publishedAt']
    channel_views = channel_statistics['viewCount']
    channel_subscribers = channel_statistics['subscriberCount']
    channel_videos = channel_statistics['videoCount']

    channel_data.append({
        "id": channel_id,
        "title": channel_title,
        "description": channel_description,
        "publishedAt": channel_published_date,
        "viewCount": channel_views,
        "subscriberCount": channel_subscribers,
        "videoCount": channel_videos
    })

    playlist_data = []
    playlist_list = col.find_one({}).get("playlists", {})
    for playlist in playlist_list[0]:
        playlist_title = playlist['snippet']['title']
        playlist_kind = playlist['kind']
        playlist_id = playlist['id']
        playlist_channel_id = playlist['snippet']['channelId']
        playlist_description = playlist['snippet']['description']
        playlist_thumbnails = playlist['snippet']['thumbnails']['default']['url']
        playlist_channel_title = playlist['snippet']['channelTitle']
        playlist_item_count = playlist['contentDetails']['itemCount']
        playlist_data.append({
            "title": playlist_title,
            "kind": playlist_kind,
            "id": playlist_id,
            "channelID": playlist_channel_id,
            "description": playlist_description,
            "thumbnails": playlist_thumbnails,
            "channelTitle": playlist_channel_title,
            "itemCount": playlist_item_count
        })

    video_data = []
    video_list = col.find_one({}).get("videos", {})
    for video in video_list:
        if video and video[0]:  # Check if the video is not empty
            snippet = video[0]['snippet']
            channel_id = snippet['channelId']
            title = snippet['title']
            description = snippet['description']
            channel_title = snippet['channelTitle']
            try:
                tags = snippet['tags']
            except KeyError:
                tags = None
            video_id = video[0]['id']
            statistics = video[0]['statistics']
            view_count = statistics['viewCount']
            like_count = statistics['likeCount']
            favorite_count = statistics['favoriteCount']
            comment_count = statistics['commentCount']
            content_details = video[0]['contentDetails']
            duration = content_details['duration']

            video_info = {
                "id": video_id,
                "channelId": channel_id,
                "title": title,
                "description": description,
                "channelTitle": channel_title,
                "tags": tags,
                "viewCount": view_count,
                "likeCount": like_count,
                "favoriteCount": favorite_count,
                "commentCount": comment_count,
                "duration": duration
            }
            video_data.append(video_info)

    comment_data = []
    comment_list = col.find_one({}).get("comments", {})   
    for comment in comment_list:
        comment_thread_id = comment['items'][0]['id']
        comment_id = comment['items'][0]['snippet']['topLevelComment']['id']
        channel_id = comment['items'][0]['snippet']['topLevelComment']['snippet']['channelId']
        video_id = comment['items'][0]['snippet']['topLevelComment']['snippet']['videoId']
        comment_text     = comment['items'][0]['snippet']['topLevelComment']['snippet']['textOriginal']
        comment_author = comment['items'][0]['snippet']['topLevelComment']['snippet']['authorDisplayName']
        like_count = comment['items'][0]['snippet']['topLevelComment']['snippet']['likeCount']
        published_at = comment['items'][0]['snippet']['topLevelComment']['snippet']['publishedAt']
        comment_details = {
            "id": comment_id,
            "threadId": comment_thread_id,
            "channelId": channel_id,
            "videoId": video_id,
            "commentText": comment_text,
            "commentAuthor": comment_author,
            "likeCount": like_count,
            "publishedAt": published_at
        }
        comment_data.append(comment_details)

    channel_df = pd.DataFrame(channel_data)
    playlist_df = pd.DataFrame(playlist_data)
    video_df = pd.DataFrame(video_data)
    comment_df = pd.DataFrame(comment_data)
    #Change datatypes of columns
    channel_df['id'] = channel_df['id'].astype('string')
    channel_df['viewCount'] = channel_df['viewCount'].astype('int64')
    channel_df['subscriberCount'] = channel_df['subscriberCount'].astype('int64')
    channel_df['publishedAt'] = pd.to_datetime(channel_df['publishedAt'], utc=True)
    channel_df['videoCount'] = channel_df['videoCount'].astype('int32')

    playlist_df['itemCount'] = playlist_df['itemCount'].astype('int32')

    video_df['viewCount'] = video_df['viewCount'].astype('int64')
    video_df['likeCount'] = video_df['likeCount'].astype('int32')
    video_df['commentCount'] = video_df['commentCount'].astype('int32')
    def iso8601_to_seconds(duration_str):
        duration = isodate.parse_duration(duration_str)
        return duration.total_seconds()
    video_df['duration'] = video_df['duration'].apply(iso8601_to_seconds).astype(int)

    comment_df['likeCount'] = comment_df['likeCount'].astype('int32')
    comment_df['publishedAt'] = pd.to_datetime(comment_df['publishedAt'], utc=True)
    
    channel_df.to_sql('channel', engine, if_exists='replace', index=False)    
    playlist_df.to_sql('playlists', engine, if_exists='replace', index=False)
    video_df.to_sql('videos', engine, if_exists='replace', index=False)
    comment_df.to_sql('comments', engine, if_exists='replace', index=False)

playlist_selectbox_key = "playlist_selectbox"
video_selectbox_key = "video_selectbox"

selected_option = st.sidebar.selectbox("Select an option", ["Insert Data", "Migrate Data", "Query Data", "Show Data"])

st.title("YouTube Data Fetcher")

if selected_option == "Insert Data":
    channel_name = st.text_input("Enter YouTube channel names (separated by space):")

    if st.button("Fetch Data"):
        data = main(channel_name)

        col.delete_many({})
        col.insert_one(data)
    pass

elif selected_option == "Migrate Data":
    if st.button("Migrate Data"):
        migrate_data(col, engine)
        st.subheader("Migrated Data")

        st.subheader("Channel Data")
        channel_data = pd.read_sql_query("SELECT * FROM channel;", conn)
        st.dataframe(channel_data.head())

        st.subheader("Playlists Data")
        playlists_data = pd.read_sql_query("SELECT * FROM playlists;", conn)
        st.dataframe(playlists_data.head())

        st.subheader("Videos Data")
        videos_data = pd.read_sql_query("SELECT * FROM videos;", conn)
        st.dataframe(videos_data.head())

        st.subheader("Comments Data")
        comments_data = pd.read_sql_query("SELECT * FROM comments;", conn)
        st.dataframe(comments_data.head())
    pass

elif selected_option == "Query Data":
    
    queries = {
        "Videos with views > 20000000": 'SELECT * FROM videos WHERE "viewCount" > 2000000;',
        "Videos with likes > 1000000": 'SELECT * FROM videos WHERE "likeCount" > 1000000;',
        "Videos with > 50000 comments": 'SELECT * FROM videos WHERE "commentCount" > 50000;',
        "Comments with > 10000 likes": 'SELECT * FROM comments WHERE "likeCount" > 10000;',
        "Playlist with > 50 videos": 'SELECT * FROM playlists WHERE "itemCount" > 50;',
        "Videos with views between 4000000 and 20000000": 'SELECT * FROM videos WHERE "viewCount" BETWEEN 4000000 AND 20000000;',
        "Sorted Videos by views in descending order": 'SELECT * FROM videos ORDER BY "viewCount" DESC;',
        "Videos with electronics and smartphone in tags": 'SELECT * FROM videos WHERE tags LIKE \'%electronics%\' OR tags LIKE \'%smartphone%\';',
        "Videos with keyword space in title": 'SELECT * FROM videos WHERE title ILIKE \'%space%\';',
        "Comments that were published at 2023-01-01": 'SELECT * FROM comments WHERE "publishedAt" > \'2023-01-01\';',
        "Sort playlist by video count in ascending order": 'SELECT * FROM playlists ORDER BY "itemCount" ASC;',
        "Videos with least and highest views": 'SELECT * FROM videos WHERE "viewCount" = (SELECT MIN("viewCount") FROM videos) UNION ALL SELECT * FROM videos WHERE "viewCount" = (SELECT MAX("viewCount") FROM videos);'
    }
    
    selected_query = st.selectbox("Select a Query", list(queries.keys()))

    if st.button("Run Query"):
        try:
            cursor.execute(queries[selected_query])

            query_result = cursor.fetchall()

            df = pd.DataFrame(query_result, columns=[desc[0] for desc in cursor.description])
            st.dataframe(df)

        except (Exception, psycopg2.Error) as error:
            st.error(f"Error executing the query: {error}")
    pass

elif selected_option == "Show Data":
    document = col.find_one({})
    if document:
        channels_data = []
        channel = col.find_one({}).get("channel", {})
        channel_info = channel[0]['snippet']
        channel_statistics = channel[0]['statistics']
        channel_id = channel[0]['id']
        channel_title = channel_info['title']
        channel_description = channel_info['description']
        channel_published_date = channel_info['publishedAt']
        channel_views = channel_statistics['viewCount']
        channel_subscribers = channel_statistics['subscriberCount']
        channel_videos = channel_statistics['videoCount']
    
        channels_data.append({
            "id": channel_id,
            "title": channel_title,
            "description": channel_description,
            "publishedAt": channel_published_date,
            "viewCount": channel_views,
            "subscriberCount": channel_subscribers,
            "videoCount": channel_videos
        })
        channel_df = pd.DataFrame(channels_data)
        st.write("Channel Data:")
        st.write(channel_df)
        
    playlists_data = []
    playlist_items_data = []
    videos_data = []
    for document in col.find({}):
        playlists_data.extend(document.get("playlists", []))
        playlist_items_data.extend(document.get("playlist_items", []))
        videos_data.extend(document.get("videos", []))

    playlist_names = list(set(playlist_item["snippet"]["title"] for playlist_data in playlists_data for playlist_item in playlist_data))
    video_titles = list(set(video_item["snippet"]["title"] for video_data in videos_data for video_item in video_data))

    playlist_video_dict = {}
    for item in playlist_items_data:
        playlist_id = item['playlistId']
        video_id = item['resourceId']['videoId']

        if playlist_id in playlist_video_dict:
            playlist_video_dict[playlist_id].append(video_id)
        else:
            playlist_video_dict[playlist_id] = [video_id]

    playlist_names_ids = {}
    for playlist_data in playlists_data[0]:
        playlist_id = playlist_data['id']
        playlist_name = playlist_data['snippet']['title']
        playlist_names_ids[playlist_name] = playlist_id

    video_names_ids = {}
    for video_data in videos_data:
        if video_data and video_data[0]:
            snippet = video_data[0]['snippet']
            video_id = video_data[0]['id']
            if 'title' in snippet and video_id:
                video_name = snippet['title']
                video_names_ids[video_id] = video_name

    selected_playlist_name = st.selectbox("Select a playlist", list(playlist_names_ids.keys()), key=playlist_selectbox_key)

    if selected_playlist_name:
        selected_playlist_id = playlist_names_ids[selected_playlist_name]

        st.write(f"You selected: {selected_playlist_name}")

        if selected_playlist_id in playlist_video_dict:
            video_ids_for_selected_playlist = playlist_video_dict[selected_playlist_id]

            video_names_for_selected_playlist = [video_names_ids.get(video_id, "") for video_id in video_ids_for_selected_playlist]

            selected_video_name = st.selectbox("Select a video", video_names_for_selected_playlist, key=video_selectbox_key)
            if selected_video_name:
                st.write(f"You selected: {selected_playlist_name} - {selected_video_name}")
    pass

#streamlit run c:\Users\Yash\Desktop\streamlitexp.py

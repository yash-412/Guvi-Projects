import os
import googleapiclient.discovery
import googleapiclient.errors
import json
import streamlit as st
import psycopg2
from googleapiclient.discovery import build
import pymongo
import pandas as pd
from googleapiclient.errors import HttpError
from typing import List

api_key = 'AIzaSyDh12-HTXwBoHkwDdXd7DKQUSsEON2t1mY'
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

def channel_ids(channel_names):
    channel_ids = []
    for channel_name in channel_names:
        channel_search = youtube.search().list(
            part="id",
            q=channel_name,
            type="channel",
            maxResults=1
        )
        channel_search_response = channel_search.execute()

        if 'items' in channel_search_response:
            channel_id = channel_search_response['items'][0]['id']['channelId']
            channel_ids.append(channel_id)

    return channel_ids

def channel_details(channel_ids):
    channel_details = []
    for channel_id in channel_ids:
        channel_search = youtube.channels().list(
            part="snippet",
            id=channel_id
        )
        channel_search_response = channel_search.execute()

        if 'items' in channel_search_response:
            channel_data = channel_search_response['items'][0]['snippet']
            channel_details.append(channel_data)

    return channel_details

def playlist_details(channel_ids):
    playlist_ids = []
    playlists_detail = []
    for channel_id in channel_ids:
        playlist_search = youtube.playlists().list(
            part="id,snippet",
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
                maxResults=100
            )
            comment_response = comment_request.execute()
            video_comments.append(comment_response)
        except Exception as e:
            print(f"{video_id}")
            continue  
    return video_comments

def main(channel_names):
    c_ids = channel_ids(channel_names)
    c = channel_details(c_ids)
    p = playlist_details(c_ids)
    p_i = playlist_items(p[0])
    v = video_details(p_i[0])
    cm = comments(p_i[0])

    data = {"channels": c,
            "playlists": p[1],
            "videos": v,
            "comments": cm}
    
    return data

selected_channel = None
selected_playlist = None
selected_video_title = None

st.title("YouTube Data Fetcher")

channel_names = st.text_input("Enter YouTube channel names (separated by space):")

if st.button("Fetch Data"):
    channel_names = channel_names.split()
    data = main(channel_names)

    m = pymongo.MongoClient("mongodb+srv://guvi_1:guvi1234@mongoguvi.t5ahkrs.mongodb.net/?retryWrites=true&w=majority")
    db = m['guvi']
    col = db['book']

    col.delete_many({})
    col.insert_one(data)
    
    channel_names = set()

    for document in col.find({}):
        channels_data = document.get("channels", [])
        for channel_data in channels_data:
            channel_name = channel_data.get("title")
            if channel_name:
                channel_names.add(channel_name)

    selected_channel = st.selectbox("Select a channel", sorted(list(channel_names)))

if selected_channel:
    playlist_names = set()
    playlist_ids = []
    playlist_info = {}

    for document in col.find({}):
        playlists_data = document.get("playlists", [])
        for playlist_data in playlists_data:
            for playlist_item in playlist_data:
                if "channelTitle" in playlist_item["snippet"]:
                    channel_title = playlist_item["snippet"]["channelTitle"]
                    if channel_title == selected_channel:
                        playlist_name = playlist_item["snippet"]["title"]
                        playlist_id = playlist_item["id"]
                        if playlist_name:
                            playlist_info[playlist_name] = playlist_id
                            playlist_names.add(playlist_name)
                            playlist_ids.append(playlist_id)

    if playlist_names:
        selected_playlist = st.selectbox(f"Select a playlist", sorted(list(playlist_names)))

if selected_playlist:
    selected_playlist_video_ids = []

    if selected_playlist:
        playlist_id = playlist_info.get(selected_playlist)
        
        if playlist_id:
            playlist_video_ids, _ = playlist_items([playlist_id])
            
        selected_playlist_video_ids.extend(playlist_video_ids)

    video_details = []

    for document in col.find({}):
        videos_data = document.get("videos", [])
        for video_data in videos_data:
            for video_item in video_data:
                if video_item.get("id") in selected_playlist_video_ids:
                    video_details.append(video_item)

    video_titles = [video["snippet"]["title"] for video in video_details]

    if video_titles:
        selected_video_title = st.selectbox("Select a video", sorted(video_titles))

#streamlit run C:\Users\Yash\Desktop\streamlit_yt_2.py
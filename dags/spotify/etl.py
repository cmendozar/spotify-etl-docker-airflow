from genericpath import exists
import os
import logging
import datetime
from xmlrpc.client import DateTime 

import pandas as pd

import sqlite3
from sqlalchemy import create_engine

import spotipy 
import spotipy.util as util 


cid = 'c9c1a716270c4838aab105a27a474d4c'
secret = '7ce85b565f334d8da88fb4bba530dd64'
username = 'recomendacion-v1'
redirect_uri = 'http://localhost:8081'

scope = 'user-top-read'


DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"


def song_etl(day = datetime.datetime.now(), **kwargs) -> None: 
    print(" JAJAJAJA STARTINNNNNNN JAJAJAJAJJAJA")
    cid = 'c9c1a716270c4838aab105a27a474d4c'
    secret = '7ce85b565f334d8da88fb4bba530dd64'
    username = 'recomendacion-v1'
    redirect_uri = 'http://localhost:8081'

    scope = 'user-read-recently-played'#'user-top-read'

    token = util.prompt_for_user_token(
        username = username, 
        scope = scope,
        client_id = cid,
        client_secret = secret,
        redirect_uri = redirect_uri
    )

    sp = spotipy.Spotify(auth = token)
    

    #day = datetime.datetime(kwargs.get('ds')) #datetime.datetime(year = 2022, month = 9, day = 6)

    yesterday = day - datetime.timedelta(days = 1)

    yesterday_unix_timestamp = int(datetime.datetime.timestamp(yesterday) *1000)
    day_unix_timestamp = int(datetime.datetime.timestamp(day) *1000) 

    logging.info("Starting process at day:")
    data = sp.current_user_recently_played(limit = 50, before = yesterday_unix_timestamp)
    
    song_names = []
    artist_names = []
    other_artists = []
    played_at_list = []
    timestamps = []

    logging.info("Transforming Data")

    for item in data['items']:
        song_names.append(item['track']['name'])
        artist_names.append( item['track']['artists'][0]['name'] )
        artist_involved   = []
        if len(item['track']['artists']) > 1: 
            for artist in item['track']['artists']: 
                artist_involved.append(artist['name'])
        else: 
            artist_involved.append("")

        other_artists.append(str(artist_involved[1:]))
        played_at_list.append( item['played_at'] )
        timestamps.append(item['played_at'][0:10])

    song_dict = {
        "song_name" : song_names,
        "artist_name": artist_names,
        "other_artist": other_artists,
        "played_at" : played_at_list,
        "timestamp" : timestamps
    }

    df_song = pd.DataFrame(song_dict, columns = song_dict.keys())

    conn = sqlite3.connect('my_played_tracks.sqlite')
    cursor = conn.cursor()
    engine = create_engine(DATABASE_LOCATION)


    create_table_query ="""
        CREATE TABLE IF NOT EXISTS my_played_tracks(
        song_name VARCHAR(200),
        artist_name VARCHAR(200),
        other_artist VARCHAR(200),
        played_at VARCHAR(200),
        timestamp VARCHAR(200),
        CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
    )"""

    cursor.execute(create_table_query)
    logging.info("Opened database successfully")

    try: 
        df_song.to_sql("my_played_tracks", con = engine, index = False, if_exists='replace')
    except: 
        logging.ERROR("Something happened with load process!!")
    
    cursor.close()
    logging.info("Finished procees at day{} loading succesfully {} rows".format(str(yesterday),len(df_song)))

if __name__ == '__main__':

    song_etl()

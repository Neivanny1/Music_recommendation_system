import numpy as np
import pandas as pd
import pickle

"""
Loading model for song recommendation
"""
df = pickle.load(open('df.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

"""
Builds a list of songs recommended to user
"""
def recommendation(song_df):
    idx = df[df['song'] == song_df].index[0]
    distances = sorted(list(enumerate(similarity[idx])), reverse=True, key=lambda x: x[1])

    # Use list comprehension to get the song names
    songs = [df.iloc[m_id[0]].song for m_id in distances[1:21]]
    return songs


'''
Populate drop down list
'''
def dropdown():
    names = list(df['song'].values)
    return names

"""
YouTube search function
Takes in song name and gets song id from youtube
"""
def search_youtube(song):
    video_search = VideosSearch(song, limit=1)
    results = video_search.result()
    if 'result' in results and len(results['result']) > 0:
        return results['result'][0]['id']
    return None

# print(len(dropdown()))
# #print(recommendation('Bang'))
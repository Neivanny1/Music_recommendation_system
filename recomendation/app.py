from flask import Flask,request,render_template
import numpy as np
import pandas as pd
import pickle
from youtubesearchpython import VideosSearch
from pytube import YouTube

# laoding models
df = pickle.load(open('df.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))

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

def recommendation(song_df):
    idx = df[df['song'] == song_df].index[0]
    distances = sorted(list(enumerate(similarity[idx])), reverse=True, key=lambda x: x[1])

    songs = []
    for m_id in distances[1:21]:
        songs.append(df.iloc[m_id[0]].song)

    return songs


# flask app
app = Flask(__name__)
# paths
@app.route('/')
def index():
    names = list(df['song'].values)
    return render_template('index.html',name = names)
@app.route('/recom/',methods=['POST'])
def mysong():
    user_song = request.form['names']
    songs = recommendation(user_song)

    return render_template('index.html',songs=songs)

"""
Gets event clicks from song clicked
Then passes the song name to search_youtube
"""
@app.route('/process_song_click', methods=['POST'])
def process_song_click():
    data = request.get_json()
    clicked_song = data.get('clicked_song')
    video_id = search_youtube(clicked_song)
    return video_id
"""
Plays song after geting the song id
"""
@app.route('/play/<video_id>')
def play(video_id):
    return render_template('yt.html', video_id=video_id)


# python
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7000, debug=True)
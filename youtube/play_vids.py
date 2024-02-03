from flask import Flask, render_template, request, redirect, url_for
from youtubesearchpython import VideosSearch
from pytube import YouTube

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        song_name = request.form['song_name']

        # Get video ID
        videos_search = VideosSearch(song_name, limit=1)
        results = videos_search.result()
        
        if results['result']:
            video_id = results['result'][0]['id']
            
            return redirect(url_for('play', video_id=video_id))

        else:
            return "No results found for the given song name."

@app.route('/play/<video_id>')
def play(video_id):
    return render_template('play.html', video_id=video_id)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

#!/usr/bin/python3
"""
Imports all necessary modules to run the app
"""
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from youtubesearchpython import VideosSearch
import pickle
import os
from dotenv import load_dotenv
from flask_mysqldb import MySQL
import MySQLdb.cursors
from dbprepare import db_init

"""
Loads db creds to the app
"""
load_dotenv()

"""
Initializing the Flask app
"""
# Loading models
df = pickle.load(open('df.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
app = Flask(__name__)

"""
Unpacking db creds
"""
app.config['MYSQL_HOST'] = os.environ.get('HOST')
app.config['MYSQL_USER'] = os.environ.get('USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('Databasename')
app.config['MYSQL_PORT'] = int(os.environ.get('PORT'))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# Secret key for hashing
app.secret_key = os.environ.get('SECRET')

"""
Initialize MySQL
"""
mysql = MySQL(app)

"""
Handles logins to app
"""
@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account and check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return render_template('home.html', msg='Logged in successfully!')
        else:
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)

"""
Handles logouts
"""
@app.route('/logout/')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

"""
Home redirection
"""
@app.route('/home/')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

"""
Registers favorite user artists to db
"""
@app.route('/artists/', methods=['POST', 'GET'])
def artists():
    user_id = session.get('id')
    username = session.get('username')
    if request.method == 'POST':
        if user_id:
            try:
                cursor = mysql.connection.cursor()
                for i in range(1, 6):
                    artist_name = request.form.get(f'artist{i}')
                    if artist_name:
                        cursor.execute("INSERT INTO my_artists (user_id, artist_name) VALUES (%s, %s)",
                                       (user_id, artist_name))
                mysql.connection.commit()
                cursor.close()
                msg = 'Artists submitted successfully!'
                return render_template('home.html', msg=msg)
            except MySQLdb.Error as e:
                print(f"Error submitting artists: {e}")
                msg = 'An error occurred while submitting artists.'
                return render_template('artists.html', msg=msg, username=username)
        else:
            return 'User not logged in.'
    else:
        return render_template('artists.html', username=username)

"""
History
"""
@app.route('/activity/')
def activity():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT song_id FROM user_history WHERE user_id = %s', (session['id'],))
        rows = cursor.fetchall()
        print("Query Result:", rows)  # Debugging: print the query result
        song_ids = [row['song_id'] for row in rows]
        cursor.close()
        return render_template('activity.html', song_ids=song_ids)
    except Exception as e:
        return render_template('error.html', error=str(e))


"""
Profile details
"""
@app.route('/profile/')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.execute('SELECT song_id FROM user_history WHERE user_id = %s', (session['id'],))
        rows = cursor.fetchall()
        song_ids = [row['song_id'] for row in rows]
        cursor.close()
        return render_template('profile.html', account=account, song_ids=song_ids)
    return redirect(url_for('login'))



"""
Render searched song
"""
@app.route('/search/', methods=['POST'])
def search():
    if request.method == 'POST':
        song_name = request.form['song_name']
        videos_search = VideosSearch(song_name, limit=1)
        results = videos_search.result()
        if results['result']:
            video_id = results['result'][0]['id']
            user_id = session.get('id')
            if user_id:
                cursor = mysql.connection.cursor()
                cursor.execute("SELECT * FROM user_history WHERE user_id = %s AND song_id = %s", (user_id, video_id))
                existing_song = cursor.fetchone()
                if not existing_song:
                    cursor.execute("INSERT INTO user_history (user_id, song_id, song_name) VALUES (%s, %s, %s)",
                                   (user_id, video_id, song_name))
                    mysql.connection.commit()
                    cursor.close()
                    print('This is ID:', video_id)
                    return render_template('dashboard.html', video_id=video_id)
                else:
                    cursor.close()
                    return render_template('dashboard.html', msg1='oops song not found')
            else:
                msg = "User not logged in."
                return render_template('index.html', msg=msg)
        else:
            msg = "No results found for the given song name."
            return render_template('dashboard.html', msg=msg)

"""
Plays videos
"""
@app.route('/dashboard/<video_id>')
def play_to_dash(video_id):
    return render_template('dashboard.html', video_id=video_id)

"""
Adds and route to register users to the system
"""
@app.route('/register/', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Hashing the password using Werkzeug
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        try:
            # Establish a connection to the database
            cursor = mysql.connection.cursor()
            print(email, username, hashed_password)
            # Insert user data into the database
            cursor.execute("INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)",
                           (username, hashed_password, email))
            mysql.connection.commit()
            cursor.close()
            msg = 'You have successfully registered!'
        except MySQLdb.Error as e:
            print(f"Error during registration: {e}")
            msg = 'An error occurred during registration. Please try again.'
    return render_template('register.html', msg=msg)

"""
Dashboard
"""
@app.route('/dashboard/')
def dashboard():
    return render_template('dashboard.html')

"""
YouTube search function
Takes in song name and gets song id from YouTube
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

@app.route('/songsrecommendations/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        names = list(df['song'].values)
        return render_template('recom.html', name=names)
    elif request.method == 'POST':
        user_song = request.form['names']
        songs = recommendation(user_song)
        return render_template('recom.html', songs=songs)

"""
Gets event clicks from song clicked
Then passes the song name to search_youtube
"""
@app.route('/process_song_click/', methods=['POST'])
def process_song_click():
    data = request.get_json()
    clicked_song = data.get('clicked_song')
    video_id = search_youtube(clicked_song)
    return video_id

"""
Plays song after getting the song id
"""
@app.route('/play/<video_id>')
def play(video_id):
    return render_template('yt.html', video_id=video_id)

"""
Start Flask app
"""
if __name__ == '__main__':
    with app.app_context():
        db_init()
    app.run(host='0.0.0.0', port=5000)

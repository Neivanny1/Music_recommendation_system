#/usr/bin/python3
"""
Imports all necesary modules to run the app
"""
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors, re, hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from handle import get_db_uri
from youtubesearchpython import VideosSearch
from pytube import YouTube
import numpy as np
import pandas as pd
import pickle

"""
Loads db creds to the app
"""
creds = get_db_uri()

"""
Intiliazing the flask app
"""
app = Flask(__name__)

"""
Unpacking db creds
"""
app.config['MYSQL_HOST'] = creds[0]
app.config['MYSQL_USER'] = creds[1]
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = creds[1]
# secret key for hashing
app.secret_key = creds[3]

"""
Intialize MySQL
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
home redirection
"""
@app.route('/home/')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

"""
Registers favorite user artsits to db
"""
@app.route('/artists/', methods=['POST', 'GET'])
def artists():
    user_id = session.get('id')
    username = session.get('username')    
    if request.method == 'POST':
        if user_id:
            try:
                with mysql.connection.cursor() as cursor:
                    for i in range(1, 6):
                        artist_name = request.form.get(f'artist{i}')
                        if artist_name:
                            cursor.execute("INSERT INTO my_artists (user_id, artist_name) VALUES (%s, %s)",
                                           (user_id, artist_name))
                            mysql.connection.commit()
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
@app.route('/activity')
def activity():
    with mysql.connection.cursor() as cursor:
        cursor.execute('SELECT song_id FROM user_history WHERE user_id = %s', (session['id'],))
        song_ids = [row[0] for row in cursor.fetchall()]
    return render_template('activity.html', song_ids=song_ids)

"""
Profiles details
"""
@app.route('/profile/')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        with mysql.connection.cursor() as cursor:
            cursor.execute('SELECT song_id FROM user_history WHERE user_id = %s', (session['id'],))
            song_ids = [row[0] for row in cursor.fetchall()]
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
                with mysql.connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM user_history WHERE user_id = %s AND song_id = %s", (user_id, video_id))
                    existing_song = cursor.fetchone()

                    if not existing_song:
                        cursor.execute("INSERT INTO user_history (user_id, song_id, song_name) VALUES (%s, %s, %s)",
                                       (user_id, video_id, song_name))
                        mysql.connection.commit()
                        print('This is ID:', video_id)
                        return render_template('dashboard.html', video_id=video_id)
                    else:
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
        # pushing user data into the db
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)",
                       (username, hashed_password, email))
        mysql.connection.commit()
        msg = 'You have successfully registered!'
        return render_template('index.html', msg=msg)
    return render_template('register.html', msg=msg)

'''
Dashboard
'''
@app.route('/dashboard/')
def dashboard():
    return render_template('dashboard.html')


"""
start flask app
"""
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)
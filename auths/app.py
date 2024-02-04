from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors, re, hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from handle import get_db_uri
from youtubesearchpython import VideosSearch
from pytube import YouTube

app = Flask(__name__)

creds = get_db_uri()
# secret key for hashing
app.secret_key = creds[3]

# database connection details
app.config['MYSQL_HOST'] = creds[0]
app.config['MYSQL_USER'] = creds[1]
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = creds[1]

# Intialize MySQL
mysql = MySQL(app)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Hash the password using Werkzeug
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Insert user data into the 'accounts' table
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)",
                       (username, hashed_password, email))
        mysql.connection.commit()
        msg = 'You have successfully registered!'
        return render_template('index.html', msg=msg)

    return render_template('register.html', msg=msg)

# login in
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
            return render_template('artists.html', msg='Logged in successfully!')
        else:
            msg = 'Incorrect username/password!'

    return render_template('index.html', msg=msg)

# logout
@app.route('/logout/')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# home redirection
@app.route('/home')
def home():
    # Check if the user is logged in
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
@app.route('/submit_artists', methods=['POST'])
def submit_artists():
    if request.method == 'POST':
        user_id = session.get('id')  # Assuming you are using user sessions
        if user_id:
            try:
                with mysql.connection.cursor() as cursor:
                    for i in range(1, 21):
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
                return render_template('artists.html', msg=msg)
        else:
            return 'User not logged in.'
    else:
        return redirect(url_for('artists'))



@app.route('/profile/')
def profile():
    # Check if the user is logged in
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not logged in redirect to login page
    return redirect(url_for('login'))
@app.route('/search/', methods=['POST'])
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
            msg = "No results found for the given song name."
            return render_template('home.html', msg=msg)

@app.route('/home/<video_id>')
def play(video_id):
    return render_template('home.html', video_id=video_id)

# start flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
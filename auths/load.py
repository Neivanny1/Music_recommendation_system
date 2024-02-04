from flask import Flask
from flask_mysqldb import MySQL
import MySQLdb.cursors
from handle import get_db_uri

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

def load_to_dash(user_id):
    with app.app_context():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM my_artists WHERE user_id = %s", (user_id,))
        existing_artists = cursor.fetchone()
        count = existing_artists[0]
    return count
count = load_to_dash
# Assuming you have a user_id value
# user_id = 1  # Replace with the actual user_id
print(load_to_dash(1))
# print(len(load_to_dash(user_id)))
import pymysql
import os
from dotenv import load_dotenv
load_dotenv()


create_acounts = '''CREATE TABLE IF NOT EXISTS accounts (
  id INT NOT NULL AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
)'''
create_user_history = '''CREATE TABLE IF NOT EXISTS user_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    song_id VARCHAR(50),
    song_name VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES accounts(id),
    INDEX fk_user_history_user_id (user_id),
    INDEX fk_user_history_song_id (song_id)
)'''
create_my_artists = '''CREATE TABLE IF NOT EXISTS my_artists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    artist_name VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES accounts(id),
    INDEX fk_my_artists_user_id (user_id)
)'''

def connector():
    timeout = 10
    connection = pymysql.connect(
    charset="utf8mb4",
    connect_timeout=timeout,
    cursorclass=pymysql.cursors.DictCursor,
    db=os.environ.get("Databasename"),
    host=os.environ.get('HOST'),
    password=os.environ.get('PASSWORD'),
    read_timeout=timeout,
    port=int(os.environ.get('PORT')),
    user=os.environ.get("USER"),
    write_timeout=timeout,
    )
    return connection
def db_init():
    connection = connector()   
    try:
        cursor = connection.cursor()
        cursor.execute(create_acounts)
        cursor.execute(create_user_history)
        cursor.execute(create_my_artists)
    finally:
        connection.close()

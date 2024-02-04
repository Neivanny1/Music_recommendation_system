from youtubesearchpython import VideosSearch

def get_youtube_video_id(song_name):
    try:
        # Search for the song on YouTube
        videos_search = VideosSearch(song_name, limit = 1)
        results = videos_search.result()

        # Get the video ID of the first result
        if results['result']:
            video_id = results['result'][0]['id']
            return video_id
        else:
            return "No results found for the given song name."

    except Exception as e:
        return f"An error occurred: {str(e)}"
def write_song_to_history(user_id, song_id, song_name):
    try:
        # Connect to MySQL and insert song information into the 'user_history' table
        with mysql.connection.cursor() as cursor:
            cursor.execute("INSERT INTO user_history (user_id, song_id, song_name) VALUES (%s, %s, %s)",
                           (user_id, song_id, song_name))
            mysql.connection.commit()
    except MySQLdb.Error as e:
        print(f"Error writing song to history: {e}")

if __name__ == "__main__":
    song_name = input("Enter the name of the song: ")
    video_id = get_youtube_video_id(song_name)
    write_song_to_history(user_id, video_id_id, song_name)
    print(f"Video ID for '{song_name}': {video_id}")

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

if __name__ == "__main__":
    song_name = input("Enter the name of the song: ")
    video_id = get_youtube_video_id(song_name)

    print(f"Video ID for '{song_name}': {video_id}")

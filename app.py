from flask import Flask, request, render_template, redirect, url_for
from lyricsgenius import Genius
import random

app = Flask(__name__)
genius = Genius('WgL88zDw74vN0BHApKBu4Mfoz_EObXEFHKgxUlfdIhUcgZFvp5Vi7RcL0hs8J3rL', timeout=10)

sorted_songs = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    artist_name = request.args.get('artist')
    if artist_name:
        sorted_songs = get_artist_songs_by_pop(artist_name)
        if sorted_songs:
            song_titles = [song['title'] for song in sorted_songs]
            # Return URL of results page
            return redirect(url_for('results', artist=artist_name))
    return 'No Songs Found for artist'
    


@app.route('/results/<artist>')
def results(artist):
        song_lyrics = {}
        for song in sorted_songs:
            song_title = song['title']
            song_obj = genius.search_song(song_title, artist)
            if song_obj:
                song_lyrics[song_title] = random.choice(song_obj.lyrics.lyrics.split('\n'))
            else:
                 song_lyrics[song_title] = "Lyrics not found"
        return render_template('results.html', artist=artist, song_lyrics=song_lyrics)

    

def get_artist_songs_by_pop(artist_name, max_songs=2):#change max song to none later only at 2 for test speed
    try:
        artist = genius.search_artist(artist_name, max_songs=max_songs)
        if artist:
            songs = []
            page = 1
            while page:
                request = genius.artist_songs(artist.id, sort='popularity', per_page=50, page=page)
                if 'next_page' not in request or len(request['songs']) == 0:
                    break
                songs.extend(request['songs'])
                page = request['next_page']

            # Sort the songs
            sorted_songs = sorted(songs, key=lambda x: x.get('popularity', 0), reverse=True)
            return sorted_songs
    except Exception as e:
        print(f"An error occurred while fetching songs: {e}")
        return None


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, render_template, redirect, url_for
from lyricsgenius import Genius
import random
import json

app = Flask(__name__)
genius = Genius('WgL88zDw74vN0BHApKBu4Mfoz_EObXEFHKgxUlfdIhUcgZFvp5Vi7RcL0hs8J3rL', timeout=10)

sorted_songs = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    artist_name = request.form.get('artist')
    if artist_name:
        sorted_songs = get_artist_songs_by_pop(artist_name)
        if sorted_songs:
            # Return URL of results page
            song_lyrics = {}
            for song in sorted_songs:
                song_title = song.get('title')
                song_obj = genius.search_song(song_title, artist_name)
                if song_obj:
                    song_lyrics[song_title] = random.choice(song_obj.lyrics.split('\n')) 
                else:
                    song_lyrics[song_title] = "Lyrics not found"
            return render_template('results.html', artist=artist_name, song_lyrics=song_lyrics)
    return 'No Songs Found for artist'
    
@app.route('/check_lyric/<artist>', methods=['POST'])
def check_lyric(artist):
    submitted_song = request.form.get('guessedSong')
    actual_lyric = request.form.get('actualLyric')
    actual_song = request.form.get('actualSong')

    if submitted_song and actual_song:
        if submitted_song.lower() == actual_song.lower():
            return "Correct! The guessed song is correct."
        else:
            return "Incorrect! The guessed song is incorrect. The actual song is: " + actual_song
    else:
        return "Skipping. Missing data. Please provide a guessed song."

  

def get_artist_songs_by_pop(artist_name, max_songs=None):#change max song to none later 2 for test speed
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

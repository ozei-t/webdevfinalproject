from flask import Flask, request, render_template, redirect, url_for
from lyricsgenius import Genius
import random
import json
import re
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' 

genius = Genius(
    access_token="WgL88zDw74vN0BHApKBu4Mfoz_EObXEFHKgxUlfdIhUcgZFvp5Vi7RcL0hs8J3rL",
    timeout=50,
    verbose=True,
    remove_section_headers=True,
    skip_non_songs=True,
    excluded_terms=["(Remix)", "(Live)"],
    replace_default_terms=True,
    retries=3
)
#



   # for row in cursor.execute("select * from leaderboard"):
    #    print(row)

   # cursor.execute("select * from leaderboard where artist_name =: a", {"a": })
   # leaderboard_search =cursor.fetch()

    #for i in leaderboard_search:

#

sorted_songs = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    artist_name = request.form.get('artist')
    if artist_name:
        sorted_songs = get_artist_songs_by_pop(artist_name, 2)
        if sorted_songs:
            # Return URL of results page
            song_lyrics = {}
            for song in sorted_songs:
                id = song.id;
                song_title = song.title
                print("Processing song:", song_title)  
                lyrics = genius.lyrics(song_id=id, remove_section_headers=True)
                if lyrics:
                    lyrics_lines = lyrics.split('\n')
                    chosen_line = re.sub(r'\u2028|\u2029|\u200B', '', random.choice(lyrics_lines))
                    
                    while len(re.sub(r'\s', '', chosen_line)) == 0:
                        chosen_line = re.sub(r'\u2028|\u2029|\u200B', '', random.choice(lyrics_lines))
                    song_lyrics[song_title] = chosen_line
                else:
                    song_lyrics[song_title] = "Lyrics not found"
            return render_template('results.html', artist=artist_name, song_lyrics=song_lyrics)
    return 'No Songs Found for artist'
    


    

def get_artist_songs_by_pop(artist_name, max_songs=None):#change max song to none later 2 for test speed
    try:
        artist = genius.search_artist(artist_name, max_songs=max_songs)
        if artist:
            print(artist.songs)
            songs = artist.songs
            # Sort the songs
            # sorted_songs = sorted(songs, key=lambda x: x.get('popularity', 0), reverse=True)
            return songs
    except Exception as e:
        print(f"An error occurred while fetching songs: {e}")
        return None

@app.route('/submit-score', methods=['POST'])
def submit_score():
    try:
        connection = sqlite3.connect("leaderboard.db")
        print("Connected to database successfully")
        cursor = connection.cursor()
        
        cursor.execute("CREATE TABLE IF NOT EXISTS leaderboard(artist_name TEXT, user TEXT, score INTEGER)")
        
        print("Form data:", request.form)
        
        artist_name = request.form.get('artist')
        name = request.form.get('playerName')
        score = request.form.get('score')
        
        print("Received data:", artist_name, name, score)  # Debug statement
        
        cursor.execute("INSERT INTO leaderboard VALUES (?, ?, ?)", (artist_name, name, score))
        connection.commit()
        
        connection.close()  
        
        return redirect(url_for('leaderboard'))
    except Exception as e:
        print("An error occurred:", e)  # Debug statement
        return "An error occurred while submitting the score.", 500


@app.route('/leaderboard')
def leaderboard():
    connection = sqlite3.connect("leaderboard.db")
    cursor = connection.cursor()
    
    
    cursor.execute("SELECT * FROM leaderboard ORDER BY score DESC")
    leaderboard_data = cursor.fetchall()
    
    connection.close()  
    
    return render_template('leaderboard.html', leaderboard_data=leaderboard_data)


if __name__ == '__main__':
    app.run(debug=True)
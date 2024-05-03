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

connection= sqlite3.connect("leaderboard.db")
print("connect to db success")
cursor =connection.cursor()
cursor.execute("create table leaderboard(artist_name text, user text, score integer)")
print("created db success")
#
cursor.execute("insert into leaderboard values(?,?,?)")
for row in cursor.execute("select * from leaderboard"):
    print(row)

cursor.execute("select * from leaderboard where artist_name =: a", {"c": })
leaderboard_search =cursor.fetch()

for i in leaderboard_search:

#

sorted_songs = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    artist_name = request.form.get('artist')
    if artist_name:
        sorted_songs = get_artist_songs_by_pop(artist_name, 10)
        if sorted_songs:
            # Return URL of results page
            song_lyrics = {}
            for song in sorted_songs:
                id = song.id;
                song_title = song.title
                print("Processing song:", song_title)  # Add this line to print the song title
                # Using Genius.lyrics instead of scraping the lyrics manually
                lyrics = genius.lyrics(song_id=id, remove_section_headers=True)
                if lyrics:
                    lyrics_lines = lyrics.split('\n')
                    chosen_line = re.sub(r'\u2028|\u2029|\u200B', '', random.choice(lyrics_lines))
                    # Check if the chosen line becomes empty after stripping all whitespace characters
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
    name = request.form.get('playerName')
    total_score = int(request.form.get('totalScore'))

    new_score = Score(name=name, total_score=total_score)
    db.session.add(new_score)
    db.session.commit()

    return redirect(url_for('leaderboard'))


@app.route('/leaderboard')
def leaderboard():
    scores = Score.query.order_by(Score.total_score.asc()).all()
    return render_template('leaderboard.html', scores=scores)


connection.close

if __name__ == '__main__':
    app.run(debug=True)
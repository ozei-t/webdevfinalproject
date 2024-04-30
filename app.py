from flask import Flask, request, render_template, redirect, url_for
from lyricsgenius import Genius
import random
import json
import re
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
genius = Genius('WgL88zDw74vN0BHApKBu4Mfoz_EObXEFHKgxUlfdIhUcgZFvp5Vi7RcL0hs8J3rL', timeout=10)
genius.remove_section_headers = True
genius.excluded_terms = ["(Remix)", "(Live)"] 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' 
db = SQLAlchemy(app)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    total_score = db.Column(db.Integer, nullable=False)

with app.app_context(): db.create_all()

sorted_songs = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    artist_name = request.form.get('artist')
    if artist_name:
        # Get the sorted songs
        sorted_songs = get_artist_songs_by_pop(artist_name, 2)
        if sorted_songs:
            # Return URL of results page
            return render_template('results.html', artist=artist_name, sorted_songs=sorted_songs)
    return 'No Songs Found for artist'
    


@app.route('/results/<artist>', methods=['POST'])
def results(artist):
    sorted_songs_json = request.form.get('sorted_songs')
    if sorted_songs_json:
        sorted_songs = json.loads(sorted_songs_json)
        song_lyrics = {}
        for song in sorted_songs:
            song_title = song.get('title')
            song_obj = genius.search_song(song_title, artist, get_full_info=False)
            if song_obj:
                lyrics_lines = song_obj.lyrics.split('\n')
                chosen_line = random.choice(lyrics_lines)
                # Check if the chosen line becomes empty after stripping all whitespace characters
                while not re.sub(r'\s+', '', chosen_line):
                    chosen_line = random.choice(lyrics_lines)
                song_lyrics[song_title] = chosen_line
            else:
                song_lyrics[song_title] = "Lyrics not found"
        return render_template('results.html', artist=artist, song_lyrics=song_lyrics, sorted_songs=sorted_songs)  # Ensure song_lyrics is passed to the template
    else:
        return 'Sorted songs not found'

    

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


if __name__ == '__main__':
    app.run(debug=True)
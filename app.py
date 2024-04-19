from flask import Flask, request, render_template
from lyricsgenius import Genius

app = Flask(__name__)
genius = Genius('WgL88zDw74vN0BHApKBu4Mfoz_EObXEFHKgxUlfdIhUcgZFvp5Vi7RcL0hs8J3rL')

@app.route('/')
def index():
    return render_template('index.html')
#

@app.route('/search', methods=['GET'])
def search():
    artist_name = request.args.get('artist')
    if artist_name:
        sorted_songs = get_artist_songs_by_pop(artist_name)
        if sorted_songs:
            song_titles = [song['title'] for song in sorted_songs]
            return render_template('results.html', artist=artist_name, songs=song_titles)
    return 'No Songs Found for artist'

def get_artist_songs_by_pop(artist_name, max_songs = None):
    artist = genius.search_artist(artist_name, max_songs=max_songs)
    if artist:
        songs = []
        page = 1
        while page:
            request = genius.artist_songs(artist.id, sort ='populatrty', per_page=50, page=page)
            songs.extend(request['songs'])
            page = request['next_page']

        #sort the songs
        sorted_songs = sorted(songs,key=lambda x: x['stats']['pageviews'], reverse=True)
        return sorted_songs
    
#def printSortedSongs(artist_name, max_songs=None):
#    sorted_songs = getArtistSongsByPop(artist_name,max_songs)
#    if sorted_songs:
#        for song in sorted_songs:
#            print(song['title'])

#printSortedSongs('​kevin abstract')

if __name__ ==  '__main__':
    app.run(debug=True)
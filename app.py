import lyricsgenius
genius = lyricsgenius.Genius(WgL88zDw74vN0BHApKBu4Mfoz_EObXEFHKgxUlfdIhUcgZFvp5Vi7RcL0hs8J3rL)

genius = Genius(WgL88zDw74vN0BHApKBu4Mfoz_EObXEFHKgxUlfdIhUcgZFvp5Vi7RcL0hs8J3rL)
# lyric genius is installed on laptop instal on home pc pip install git+https://github.com/johnwmillr/LyricsGenius.git

def getArtistSongsByPop(artist_name, max_songs = None):
    artist = genius.search_artist(artist_name, max_songs=max_songs)
    if artist:
        songs = []
        page = 1
        while page:
            request = genius.artist_songs(artist._id, sort ='populatrty', per_page=50, page=page)
            songs.extend(request['songs'])
            page = request['next_page']

        #sort the songs
        sorted_songs = sorted(songs,key=lambda x: x['stats']['pageviews'], reverse=True)
        return sorted_songs


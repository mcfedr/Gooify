import sys
import os
import time

import spotipy
import spotipy.util as util
from num2words import num2words

class SpotifyClient:
    def __init__(self):
        """
        This connects to Spotify's servers.
        """
        # This determines what the app has access to do
        scope = 'user-library-read user-library-modify playlist-modify-private playlist-read-private playlist-modify-public'
        
        # username = input('Type your Spotify username below.\n--> ')
        username = os.getenv('SPOTIFY_USERNAME')

        # If used an old scope, we might have to delete the cache
        dir_path = os.path.dirname(os.path.realpath(__file__)) + '/.cache-spotify' + username
        cache = 0
        if(not os.path.isfile(dir_path)):
            cache = open(dir_path, 'w')
            cache.write("v1.0")
            if(os.path.isfile(f".cache-{username}")):
                os.remove(f".cache-{username}") # Only needed if already ran the app in different mode
        else:
            cache = open(dir_path, 'r')
            if(cache.read() != "v1.0"):
                cache.close()
                if(os.path.isfile(f".cache-{username}")):
                    os.remove(f".cache-{username}") # Only needed if already ran the app in different mode
                cache = open(dir_path, 'w')
                cache.write("v1.0")
        cache.close()

        token = util.prompt_for_user_token(username=username, scope=scope, client_id=os.getenv("SPOTIFY_CLIENT_ID"), client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"), redirect_uri=os.getenv('SPOTIFY_REDIRECT_URL'))

        if(token):
            self.api = spotipy.Spotify(auth=token)
            print('Connected to Spotify')
        else:
            print('Can\'t get the token for', username)

    def add_playlist(self, playlist_name):
        """
        Adds a playlist to the library, if not already present.
        """
        usr = self.api.current_user()['id']
        id = self.get_playlist(playlist_name)
        if(id == None):
            self.api.user_playlist_create(user=usr, name=playlist_name, public=False)
            return self.get_playlist(playlist_name)
        else:
            return id

    def get_playlist(self, playlist_name):
        """
        Gets a playlist with a given name and returns its id.
        """
        usr = self.api.current_user()['id']
        p_lists = self.api.user_playlists(user=usr)['items']
        for lst in p_lists:
            if(lst['name'] == playlist_name):
                return lst['id']
        return None

    def add_song_to_playlist_uris(self, playlist_id, uris, repeat=True):
        """
        Adds a song to a playlist, specified by its Spotify id.
        """
        usr = self.api.current_user()['id']
        try:
            self.api.user_playlist_add_tracks(user=usr, playlist_id=playlist_id, tracks=uris)
        except spotipy.SpotifyException as e:
            if e.http_status == 429 and repeat:
                print('Spotify rate limit', e.headers['Retry-After'])
                time.sleep(e.headers['Retry-After'] if 'Retry-After' in e.headers and e.headers['Retry-After'] < 120 else 30)
                return self.add_song_to_playlist_uris(playlist_id, uris, False)
            raise e

    def replace_songs_to_playlist_uris(self, id, uris):
        usr = self.api.current_user()['id']

        self.api.user_playlist_replace_tracks(usr, id, uris)

    def get_song_uri(self, track):
        """
        Gets the Spotify URI for the tracks
            return: the Spotify URI
        """
        # Get the song info from Google
        trackname = track['title'].replace("'", "")
        artistname = track['artist'].replace("'", "")
        albumname = track['album'].replace("'", "")

        # Find the song on spotify
        song = self.find_song(trackname, artistname, albumname)

        # If no result, say so.
        if(song == None):
            return None
        else:
            return song['uri']

    def find_song(self, trackname, artistname, albumname):
        """
        Finds a song from Spotify based on the track name and
        artist name. It will shorten the names in order to find
        the closest match, since many will not fit exactly.
            return: Spotify song object
        """
        # Fix the artist name
        artistname = artistname.replace('and', ' ')

        # Fix the title
        translation_table = dict.fromkeys(map(ord, ';/"()&'), ' ')
        artistname = artistname.translate(translation_table)
        trackname = trackname.translate(translation_table)
        albumname = albumname.translate(translation_table)

        string = "track:" + trackname
        string += " artist:" + artistname
        string += " album:" + albumname
        results = self.api.search(q=string, type='track', limit=1)
        items = results['tracks']['items']

        if (len(items) == 0):
            return None
        else:
            return items[0]

    def add_album_uris(self, uris):
        """
        Adds a track to the Spotify account. Returns if it was
        successfully found on Spotify.
        """
        self.api.current_user_saved_albums_add(uris)

    def get_album_uri(self, track):
        """
        Gets the Spotify URI for the tracks
            return: the Spotify URI
        """
        # Get the song info from Google
        artistname = track['artist'].replace("'", "")
        albumname = track['album'].replace("'", "")

        # Find the song on spotify
        song = self.find_album(artistname, albumname)

        # If no result, say so.
        if(song == None):
            return None
        else:
            return song['uri']

    def find_album(self, artistname, albumname):
        """
        Finds a song from Spotify based on the track name and
        artist name. It will shorten the names in order to find
        the closest match, since many will not fit exactly.
            return: Spotify song object
        """
        # Fix the artist name
        artistname = artistname.replace('and', ' ')

        # Fix the title
        translation_table = dict.fromkeys(map(ord, ';/"()&'), ' ')
        artistname = artistname.translate(translation_table)
        albumname = albumname.translate(translation_table)

        string = "artist:" + artistname
        string += " album:" + albumname
        results = self.api.search(q=string, type='album', limit=1)
        items = results['albums']['items']

        if(len(items) == 0):
            return None
        else:
            return items[0]

    def add_artist_uris(self, uris):
        """
        Adds a track to the Spotify account. Returns if it was
        successfully found on Spotify.
        """
        self.api.user_follow_artists(uris)

    def get_artist_uri(self, track):
        """
        Gets the Spotify URI for the tracks
            return: the Spotify URI
        """
        # Get the song info from Google
        artistname = track['artist'].replace("'", "")

        # Find the song on spotify
        song = self.find_arist(artistname)

        # If no result, say so.
        if(song == None):
            return None
        else:
            return song['uri']

    def find_arist(self, artistname):
        """
        Finds a song from Spotify based on the track name and
        artist name. It will shorten the names in order to find
        the closest match, since many will not fit exactly.
            return: Spotify song object
        """
        # Fix the artist name
        artistname = artistname.replace('and', ' ')

        # Fix the title
        translation_table = dict.fromkeys(map(ord, ';/"()&'), ' ')
        artistname = artistname.translate(translation_table)

        string = "artist:" + artistname
        results = self.api.search(q=string, type='artist', limit=1)
        items = results['artists']['items']

        if(len(items) == 0):
            return None
        else:
            return items[0]


import os
from gmusicapi import Mobileclient
import pickle

class GMusicClient:
    def __init__(self):
        """
        This connects to the google music server by requesting credentials.
        """
        self.api = Mobileclient()

        # username = input('Type your Google Play Music email below.\n--> ')
        self.username = os.getenv('GOOGLE_USERNAME')
        dir_path = os.path.dirname(os.path.realpath(__file__)) + '/.cache-gmusic-' + ''.join(filter(str.isalpha, self.username))
        # Check if already authenticated
        if(not os.path.isfile(dir_path)):
            self.api.perform_oauth(open_browser=True, storage_filepath=dir_path)

        # Attempt to log in; if fail, get new token.
        try:
            self.api.oauth_login(Mobileclient.FROM_MAC_ADDRESS, oauth_credentials=dir_path)
        except:
            self.api.perform_oauth(open_browser=True, storage_filepath=dir_path)
            self.api.oauth_login(Mobileclient.FROM_MAC_ADDRESS, oauth_credentials=dir_path)

        print('Connected to GMusic')

    def get_playlists(self):
        """
        Gets all the playlists in Google Play Music. Some may not actually
        have any music, but they will be processed anyways.
        """
        playlists_cache_path = os.path.dirname(os.path.realpath(__file__)) + '/.cache-playlists_cache-' + ''.join(filter(str.isalpha, self.username))
        if (os.path.isfile(playlists_cache_path)):
            with open(playlists_cache_path, 'rb') as playlists_cache_file:
                playlists = pickle.load(playlists_cache_file)
        else:
            print('Requesting Google playlists')
            playlistsG = self.api.get_all_user_playlist_contents()
            print('Received Google playlists, we have', len(playlistsG), 'playlists')
            playlists = Playlists(playlistsG)
            with open(playlists_cache_path, 'wb') as playlists_cache_file:
                pickle.dump(playlists, playlists_cache_file)

        return playlists

    def get_all_songs(self):
        """
        Gets the entire Google library for adding to the
        """
        lib_cache_path = os.path.dirname(os.path.realpath(__file__)) + '/.cache-lib_cache-' + ''.join(filter(str.isalpha, self.username))
        if (os.path.isfile(lib_cache_path)):
            with open(lib_cache_path, 'rb') as lib_cache_file:
                library = pickle.load(lib_cache_file)
        else:
            print('Requesting Google library')
            librarySongs = self.api.get_all_songs()
            print('Received Google library, we have', len(librarySongs), 'songs')
            library = MusicLibrary(librarySongs)
            with open(lib_cache_path, 'wb') as lib_cache_file:
                pickle.dump(library, lib_cache_file)

        return library

class Playlists:
    """
    Playlists is an iterable object which simply contains
    all the playlists, excluding the playlists with no songs.
    """
    def __init__(self, lists):
        """
        Creates a new playlist object
        """
        self.playlists = []
        for l in lists:
            plist = Playlist(l)
            # Only add it if it has songs
            if(plist.has_songs()):
                self.playlists.append(plist)
        self.p_index = 0

    def start_from(self, i):
        """
        Sets the index to start reading the library from.
        """
        self.index = i

    def __iter__(self):
        """
        Allows iterating over all the playlists.
        """
        return self

    def __next__(self):
        """
        Gets the next playlist
        """
        self.p_index += 1
        if(self.p_index <= len(self.playlists)):
            return self.playlists[self.p_index - 1]
        else:
            raise StopIteration

class Playlist:
    """
    A Playlist is an iterable object that goes through all
    the songs in the playlist. It also has an associated name.
    """
    def __init__(self, plist):
        """
        Creates a new playlist from an incomplete list from Google's
        servers, which is a disorganized pile of junk.
        """
        self.tracks = []
        self.name = plist['name']
        for t in plist['tracks']:
            # Ensures that the track has info attached
            if('track' in t):
                self.tracks.append(t['track'])
        self.index = 0

    def get_name(self):
        """
        Gets the name of the playlist.
        """
        return self.name

    def has_songs(self):
        """
        Checks if the playlist is empty.
        """
        if(len(self.tracks) > 0):
            return True
        else:
            return False

    def __iter__(self):
        """
        Allows the playlist to iterate over its tracks.
        """
        return self

    def __next__(self):
        """
        Gets the next song.
        """
        self.index = self.index + 1
        if(self.index > len(self.tracks)):
            raise StopIteration
        else:
            return self.tracks[self.index - 1]

class MusicLibrary:
    def __init__(self, lib):
        """
        Creates a new music library.
        """
        self.library = lib
        self.index = 0 # We start at the 0-index location when adding songs

    def start_from(self, i):
        """
        Sets the index to start reading the library from.
        """
        self.index = i

    def __iter__(self):
        """
        Allows iterating over the entire library, starting
        from the starting index.
        """
        return self

    def __next__(self):
        """
        Gets the next track in the library, if available.
        """
        self.index = self.index + 1
        if(self.index > len(self.library)):
            raise StopIteration
        else:
            return self.library[self.index - 1]

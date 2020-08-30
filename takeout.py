import os
import csv

class GoogleMusicTakeoutClient:
    def __init__(self):
        self.dir = os.getenv('GOOGLE_TAKEOUT_DIR')

    def get_playlists(self):
        """
        Gets all the playlists in Google Play Music. Some may not actually
        have any music, but they will be processed anyways.
        """

        lists = []
        for playlistDir in os.listdir(self.dir + '/Playlists'):
            if playlistDir.startswith('.'):
                continue
            if playlistDir.lower() == 'thumbs up':
                continue
            playlistName = self.name_from_metadata(self.dir + '/Playlists/' + playlistDir + '/Metadata.csv')
            if playlistName is None:
                continue
            tracks = []
            for trackFile in os.listdir(self.dir + '/Playlists/' + playlistDir + '/Tracks'):
                if trackFile.startswith('.'):
                    continue
                track = self.track_from_file(self.dir + '/Playlists/' + playlistDir + '/Tracks/' + trackFile)
                if track is None:
                    continue
                tracks.append(track)
            lists.append(Playlist(playlistName, tracks))

        return Playlists(lists)

    def name_from_metadata(self, path):
        with open(path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                return row['Title']
        return None

    def track_from_file(self, path):
        with open(path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Removed'] == 'Yes':
                    return None
                if row['Title'] == '' or row['Album'] == '' or row['Artist'] == '':
                    return None
                return { "title" : row['Title'], "album" : row['Album'], "artist" : row['Artist'], "deleted" : False, 'playCount' : row['Play Count'] }
        return None

    def get_all_songs(self):
        """
        Gets the entire Google library for adding to the
        """
        tracks = []
        for trackFile in os.listdir(self.dir + '/Tracks'):
            if trackFile.startswith('.'):
                continue
            track = self.track_from_file(self.dir + '/Tracks/' + trackFile)
            if track is None:
                continue
            tracks.append(track)

        return MusicLibrary(tracks)

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
        for plist in lists:
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
    def __init__(self, name, tracks):
        """
        Creates a new playlist from an incomplete list from Google's
        servers, which is a disorganized pile of junk.
        """
        self.name = name
        self.tracks = tracks
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

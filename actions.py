from gmus import *
from spotify import *
from takeout import *
from actions import *
import datetime

def setup(name):
    if os.getenv('GOOGLE_TAKEOUT_DIR'):
        gmus = GoogleMusicTakeoutClient()
    elif os.getenv('GOOGLE_USERNAME'):
        gmus = GMusicClient()
    else:
        raise Exception('No google env vars set')

    if os.getenv('SPOTIFY_CLIENT_ID') and os.getenv('SPOTIFY_CLIENT_SECRET') and os.getenv('SPOTIFY_REDIRECT_URL') and os.getenv('SPOTIFY_USERNAME'):
        spot = SpotifyClient()
    else:
        raise Exception('Missing spotify env vars')

    log = open('actions.log', 'a+')

    log.write('----------------------------------------------------------------------------------------\n')
    log.write('Starting\t' + name + '\t' + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y") + '\n')

    return (gmus, spot, log)

def albums(add):
    gmus, spot, log = setup('albums')

    prev = []
    uris = []
    for song in gmus.get_all_songs():
        key = song['artist'] + ':' + song['album']
        if key in prev:
            continue
        prev.append(key)
        if song['deleted']:
            continue
        if song['playCount'] == 0:
            continue
        uri = spot.get_album_uri(song)
        if uri is not None:
            log.write('Found\t' + song['artist'] + '\t' + song['album'] + '\t' + uri + '\n')
            uris.append(uri)
        else:
            log.write('Skipped\t' + song['artist'] + '\t' + song['album'] + '\n')
        if len(uris) > 50:
            if add:
                spot.add_album_uris(uris)
            uris = []
    if len(uris) > 0 and add:
        spot.add_album_uris(uris)

def artists(add):
    gmus, spot, log = setup('artists')

    prev = []
    uris = []
    for song in gmus.get_all_songs():
        key = song['artist']
        if key in prev:
            continue
        prev.append(key)
        if song['deleted']:
            continue
        if song['playCount'] == 0:
            continue
        uri = spot.get_artist_uri(song)
        if uri is not None:
            log.write('Found\t' + song['artist'] + '\t' + uri + '\n')
            uris.append(uri)
        else:
            log.write('Skipped\t' + song['artist'] + '\n')
        if len(uris) > 50:
            if add:
                spot.add_artist_uris(uris)
            uris = []
    if len(uris) > 0 and add:
        spot.add_artist_uris(uris)

def playlists(add):
    gmus, spot, log = setup('playlists')

    for playlist in gmus.get_playlists():
        name = playlist.get_name()
        id = spot.get_playlist(name)
        if id is not None:
            log.write('Playlist Found\t' + name + '\t' + id + '\n')
        else:
            log.write('Creating Playlist\t' + name + '\n')
            if add:
                id = spot.add_playlist(name)

        first = True
        uris = []
        for song in playlist:
            if song['deleted']:
                continue
            if song['playCount'] == 0:
                continue
            uri = spot.get_song_uri(song)
            if uri is not None:
                log.write('Adding\t' + song['artist'] + '\t' + song['album'] + '\t' + song['title'] + '\t' + uri + '\n')
                uris.append(uri)
            else:
                log.write('Skipped\t' + song['artist'] + '\t' + song['album'] + '\t' + song['title'] + '\n')

            if len(uris) == 100:
                if add:
                    if first:
                        spot.replace_songs_to_playlist_uris(id, uris)
                        first = False
                    else:
                        spot.add_song_to_playlist_uris(id, uris)
                uris = []
        if len(uris) > 0 and add:
            if first:
                spot.replace_songs_to_playlist_uris(id, uris)
            else:
                spot.add_song_to_playlist_uris(id, uris)

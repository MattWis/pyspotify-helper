import threading
import spotify
from random import shuffle
import credentials

def play_track(name):
    play(search_for_track(name))

def play_album(name):
    play_track_list(get_album_tracks(name))

def shuffle_album(name):
    track_seq = get_album_tracks(name)
    shuffle_seq(track_seq)

def play_artist(name):
    play_track_list(get_artist_tracks(name))

def shuffle_artist(name):
    track_seq = get_artist_tracks(name)
    shuffle_seq(track_seq)

def play(track):
    session.player.load(track)
    session.player.play()

#Returns best track result, ignores all others
def search_for_track(term):
    return session.search("title:" + term).load().tracks[0].load()

#Returns best album result, ignores all others
def search_for_album(term):
    return session.search("album:" + term).load().albums[0].load()

#Returns best artist result, ignores all others
def search_for_artist(term):
    return session.search("artist:" + term).load().artists[0].load()

def get_album_tracks(name):
    album = search_for_album(name)
    return album.browse().load().tracks

def get_artist_tracks(name):
    artist = search_for_artist(name)
    return artist.browse().load().tracks

def play_track_list(tracks):
    for track in tracks:
        print track.name, track.availability
        if track.availability is spotify.TrackAvailability.AVAILABLE:
            play(track)
            while not end_of_track.wait(0.1):
                pass
            end_of_track.clear()

def shuffle_seq(track_seq):
    tracks = []
    for track in track_seq:
        tracks.append(track)
    shuffle(tracks)
    play_track_list(tracks)

def init_spotify():
    # Assuming a spotify_appkey.key in the current dir
    session = spotify.Session()
    loop = spotify.EventLoop(session)
    loop.start()
    
    # Connect an audio sink
    audio = spotify.PortAudioSink(session)
    
    def on_login(session):
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            logged_in.set()
    def on_end_of_track(self):
        end_of_track.set()
    
    # Register event listeners
    logged_in = threading.Event()
    end_of_track = threading.Event()
    session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, on_login)
    session.on(spotify.SessionEvent.END_OF_TRACK, on_end_of_track)
    
    session.login(credentials.username, credentials.password)
    logged_in.wait()

    return session, end_of_track

session, end_of_track = init_spotify()
play_album("Stadium Arcadium")

raw_input()

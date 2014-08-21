import time
from thread import start_new_thread
import threading
import spotify
from random import shuffle
import credentials

class Spotify:
    
    def play_track(self, name):
        start_new_thread(self._play, (self._search(name, "tracks"), ))
    
    def play_album(self, name):
        self._play_track_list_noblock(self._get_tracks(name, "albums"))
    
    def shuffle_album(self, name):
        self._shuffle_seq(self._get_tracks(name, "albums"))
    
    def play_artist(self, name):
        self._play_track_list_noblock(self._get_tracks(name, "artists"))
    
    def shuffle_artist(self, name):
        self._shuffle_seq(self._get_tracks(name, "artists"))
    
    def _play(self, track):
        self.session.player.load(track)
        self.session.player.play()
    
    #Returns best search result
    #category is "tracks", "artists", or "albums"
    def _search(self, term, category):
        return getattr(self.session.search(term).load(), category)[0].load()
    
    def _get_tracks(self, name, category):
        grouping = self._search(name, category)
        return grouping.browse().load().tracks

    def _play_track_list_noblock(self, tracks):
        start_new_thread(self._play_track_list, (tracks, ))
    
    def _play_track_list(self, tracks):
        for track in tracks:
            if track.availability is spotify.TrackAvailability.AVAILABLE:
                self._play(track)
                while not self.end_of_track.wait(0.1):
                    pass
                self.end_of_track.clear()

    def _shuffle_seq(self, track_seq):
        tracks = []
        for track in track_seq:
            tracks.append(track)
        shuffle(tracks)
        self._play_track_list_noblock(tracks)
    
    def __init__(self):
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

        self.session = session
        self.end_of_track = end_of_track

if __name__ == "__main__":
    s = Spotify()
    s.play_album("Stadium Arcadium")
    time.sleep(3)
    s.play_album("Red")

    print "I can print while the song plays"
    raw_input()

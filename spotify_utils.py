import threading
import spotify
from random import shuffle
import credentials

class Spotify:
    
    def play_track(self, name):
        self._play(self._search_for_track(name))
    
    def play_album(self, name):
        self._play_track_list(self._get_album_tracks(name))
    
    def shuffle_album(self, name):
        self._shuffle_seq(self._get_album_tracks(name))
    
    def play_artist(self, name):
        self._play_track_list(self._get_artist_tracks(name))
    
    def shuffle_artist(self, name):
        self._shuffle_seq(self._get_artist_tracks(name))
    
    def _play(self, track):
        self.session.player.load(track)
        self.session.player.play()
    
    #Returns best track result, ignores all others
    def _search_for_track(self, term):
        return self.session.search("title:" + term).load().tracks[0].load()
    
    #Returns best album result, ignores all others
    def _search_for_album(self, term):
        return self.session.search("album:" + term).load().albums[0].load()
    
    #Returns best artist result, ignores all others
    def _search_for_artist(self, term):
        return self.session.search("artist:" + term).load().artists[0].load()
    
    def _get_album_tracks(self, name):
        album = self._search_for_album(name)
        return album.browse().load().tracks
    
    def _get_artist_tracks(self, name):
        artist = self._search_for_artist(name)
        return artist.browse().load().tracks
    
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
        self._play_track_list(tracks)
    
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
    Spotify().play_album("Stadium Arcadium")

import time
from thread import start_new_thread
import threading
import spotify
from random import shuffle
import credentials

if credentials.username == '' or credentials.password == '':
    raise "Put your Spotify Pro account credentials in credentials.py"

# Make Spotify a singleton object
_spotify = None
def Spotify():
  global _spotify
  if _spotify is None:
    _spotify = _Spotify()
  return _spotify

class _Spotify:
  
  def play_track(self, name):
    runner = lambda x: self._play(self._search(x, "tracks"))
    start_new_thread(runner, (name, ))
  
  def play_album(self, name):
    runner = lambda x: self._play_tracks(self._get_tracks(x, "albums"))
    start_new_thread(runner, (name, ))
  
  def shuffle_album(self, name):
    runner = lambda x: self._shuffle_seq(self._get_tracks(x, "albums"))
    start_new_thread(runner, (name, ))
  
  def play_artist(self, name):
    runner = lambda x: self._play_tracks(self._get_tracks(x, "artists"))
    start_new_thread(runner, (name, ))
  
  def shuffle_artist(self, name):
    runner = lambda x: self._shuffle_seq(self._get_tracks(x, "artists"))
    start_new_thread(runner, (name, ))
  
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

  def _play_tracks(self, tracks):
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
    self._play_tracks(tracks)
  
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
  s.shuffle_artist("Taylor Swift")

  print "I can print while the song plays"
  raw_input()

import time
from thread import start_new_thread
import threading
import spotify
from random import shuffle

# Make Spotify a singleton object
_spotify = None
def Spotify(profile = None):
  global _spotify
  if _spotify is None:
    _spotify = _Spotify(profile)
  return _spotify

class _Spotify:

  def play_track(self, name):
    runner = lambda x: self._play(self._search(x, "tracks"))
    start_new_thread(runner, (name, ))
    self.playing = True

  def play_album(self, name):
    runner = lambda x: self._play_tracks(self._get_tracks(x, "albums"))
    start_new_thread(runner, (name, ))
    self.playing = True

  def shuffle_album(self, name):
    runner = lambda x: self._shuffle_seq(self._get_tracks(x, "albums"))
    start_new_thread(runner, (name, ))
    self.playing = True

  def play_artist(self, name):
    runner = lambda x: self._play_tracks(self._get_tracks(x, "artists"))
    start_new_thread(runner, (name, ))
    self.playing = True

  def shuffle_artist(self, name):
    runner = lambda x: self._shuffle_seq(self._get_tracks(x, "artists"))
    start_new_thread(runner, (name, ))
    self.playing = True

  def next_track(self):
    # Seek to the end of the song, 10,000,000 milliseconds > 2.5 hours
    self.session.player.seek(10000000)
    self.playing = True

  def pause_toggle(self):
    if self.playing is None:
      self.playing = True
    self.playing = not self.playing
    self.session.player.play(self.playing)

  def pause(self):
    self.playing = False
    self.session.player.pause()

  def resume(self):
    self.playing = True
    self.session.player.play()

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

  def __init__(self, profile):
    if not profile.has_key("spotify_name") or \
       not profile.has_key("spotify_password") or \
       profile["spotify_name"] is "" or \
       profile["spotify_password"] is "":
      raise("Pass in a profile with spotify_name and spotify_password")

    # Assuming a spotify_appkey.key in the current dir
    session = spotify.Session()
    loop = spotify.EventLoop(session)
    loop.start()

    # Connect an audio sink
    audio = spotify.AlsaSink(session)

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

    session.login(profile["spotify_name"], profile["spotify_password"])
    logged_in.wait()

    self.session = session
    self.end_of_track = end_of_track
    self.playing = None

if __name__ == "__main__":
  #To use this example, fill in the empty 'profile.yml'
  import yaml
  profile = yaml.load(open("profile.yml", 'rb').read())

  Spotify(profile).play_album("Stadium Arcadium")
  print("I can print while the song plays")
  time.sleep(2)
  Spotify().pause_toggle()
  time.sleep(2)
  Spotify().next_track()
  time.sleep(2)
  Spotify().shuffle_artist("Taylor Swift")


  raw_input()

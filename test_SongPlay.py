from h2core import Logger, Object, Filesystem, Preferences, Hydrogen, Drumkit, Song
import time

# log_levels = Logger.log_levels
logger = Logger.bootstrap(0xFFF)
Object.bootstrap(logger, True)
Filesystem.bootstrap(logger, "/usr/local/share/hydrogen/data/")
prefs = Preferences.create_instance()
hydrogen = Hydrogen.get_instance(False, True)
dk = Drumkit.load_file(
     "/home/rebelcat/.hydrogen/data/drumkits/RoRBateria/drumkit.xml", False
)
song = Song.load("/home/rebelcat/envelope_test.h2song")
hydrogen.setSong(song)
hydrogen.sequencer_play()
time.sleep(3)
hydrogen.sequencer_stop()
# hydrogen.setSong(None)
print(song)
del song
del hydrogen
del prefs
del logger
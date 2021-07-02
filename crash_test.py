from h2core import Logger, Object, Filesystem, Preferences, Hydrogen, Drumkit, Song
import time

# log_levels = Logger.log_levels
logger = Logger.bootstrap(0xFF
)
Object.bootstrap(logger, True)
Filesystem.bootstrap(logger, "/usr/local/share/hydrogen/data/")
prefs = Preferences.create_instance()
hydrogen = Hydrogen.get_instance(False, True)
dk = Drumkit.load_file(
    "/home/rebelcat/.hydrogen/data/drumkits/RoRBateria/drumkit.xml", False
)
#song = Song.load("/home/rebelcat/envelope_test.h2song")
#hydrogen.setSong(song)
# hydrogen.sequencer_play()
# hydrogen.sequencer_stop()
#print(song)
# dc,=dk.get_components() too hard
print(dk)
ins=dk.get_instruments()
print(ins)
i=ins.get(0)
print(i)
# del i
# print("i deleted")
del ins
print("ins deleted")
del dk
print("dk deleted")
del hydrogen
print("h deleted")
del prefs
print("prefs deleted")
del logger
print("logger deleted")
del i
print("i deleted")

#ic=i.get_component(0)
#print(ic)

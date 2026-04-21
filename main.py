"""
set_recorder info:
Generates the following important variables:

Chosen from csv file 'Radio_Stns.csv' - please update if missing stations

stn: Radio Station - string
urlink: URL to radio station - string
start_time: tells you when to start recording - datetime
end_time: tells you when to end recording - datetime
filename: file name for recording - string
f_ext: extension for filename - string
streamtyp: tells you which recorder to use (Icecast/Shoutcast or HLS) - string


recorders:

records either m3u8 or cast (continuous byte stream):

m3u8:
get_m3u8_play: generates playlist for each url the url generates
record_m3u8: records and stitches all playlists generated during the timeframe

cast:
cast_recorder: records byte stream for the duration of timeframe

"""
#step 1 - Import
from set_recorder import *
from recorders import *

#step 2 - wait to record
from timer import countdown_timer
countdown_timer(start_time)

#step 3 - start recording
if streamtyp == 'Icecast/Shoutcast':
    data = cast_recorder(start_time,end_time, urlink)
elif streamtyp == 'HLS':
    data = record_m3u8(start_time,end_time,urlink)

file_path = os.path.join(home,downloads,filename)
with open(file_path, "wb") as outfile:
    outfile.write(data)
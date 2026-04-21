"""
records either m3u8 or cast (continuous byte stream):

m3u8:
get_m3u8_play: generates playlist for each url the url generates
record_m3u8: records and stitches all playlists generated during the timeframe

cast:
cast_recorder: records byte stream for the duration of timeframe
"""

#importing packages

#stuff everyone should have:

import time
import os
from datetime import datetime as dt
# stuff you may not have:

#add an installer:
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import requests
except:
    print('one-time installation: requests')
    install('requests')
    import requests
try:
    import m3u8
except:
    print('one-time installation: m3u8')
    install('m3u8')
    import m3u8
    
with open('buffer.txt','r') as f:
    buffer = int(f.read())

def get_m3u8_play(url):
    """ Fetch the media playlist and return segment URLs """
    playlist = m3u8.load(url)

    if playlist.is_variant:  # It's a master playlist, not segments
        #print("Master playlist detected. Fetching media playlist...")
        for playlist_variant in playlist.playlists:
            media_url = playlist_variant.uri  # Get the first available media playlist
            #print(f"Switching to: {media_url}")
            return get_m3u8_play(media_url)  # Recursively get segments
    
    # Return the actual media segments
    return [segment.uri for segment in playlist.segments]


def record_m3u8(start_time,end_time,urlink):
    """using given start/end datetimes and url this will record for the alotted time"""
    downloaded_segments = set()  # To keep track of segments already downloaded.
    # Wait until start_time if needed.
    while dt.now() < start_time:
        if dt.now() > end_time:
            break
        time.sleep(buffer)
    itr = 0
    print('Recording as of',dt.now().strftime('%Y-%m-%d'))
    print('from',dt.now().strftime('%H:%M'),'to',end_time.strftime('%H:%M'))
    
    all_data_chunks = []
    while dt.now() < end_time:
        segments = get_m3u8_play(urlink)
        data_chunks = []
        itr += 1
        for seg_url in segments:
            try:
                response = requests.get(seg_url)
                response.raise_for_status()
                data_chunk = requests.get(seg_url).content
            except requests.RequestException as e:
                print(f"Error downloading {seg_url}: {e}")
            if data_chunk not in all_data_chunks and data_chunk not in data_chunks:
                data_chunks.append(data_chunk)
    
        # Wait for a short interval before checking for new segments.
        all_data_chunks += data_chunks
        time.sleep(buffer)
    return b''.join(all_data_chunks)
    
def cast_recorder(start_time,end_time, stream_url):
    data = b''
    # Create an initial response object
    response = requests.get(stream_url, stream=True)
    # Check the status code of the initial request
    if response.status_code != 200:
        logging.info(f"Failed to retrieve the audio stream. Status code: {response.status_code}")
        error_ind = True
        return None
    run_time = dt.now()
    while dt.now() < end_time: #initial wait
        if dt.now() >= start_time:
            print('Recording as of',dt.now().strftime('%Y-%m-%d'))
            print('from',dt.now().strftime('%H:%M'),'to',end_time.strftime('%H:%M'))
        while dt.now() >= start_time and dt.now() < end_time:
            # write into chunk
            data += response.raw.read(1024)
    return data




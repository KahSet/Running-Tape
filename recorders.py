"""
records either m3u8 or cast (continuous byte stream):

m3u8:
get_media_playlist_url: resolves master playlist → media playlist (ONCE)
record_m3u8: follows live stream forward near live edge

cast:
cast_recorder: records byte stream for the duration of timeframe
"""

import time
from datetime import datetime as dt
import subprocess
import sys
from urllib.parse import urljoin


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
    
import requests, uuid

def get_session_url(base_url):
    params = {
        "downloadSessionID": "0",
        "args": "web_01",
        "player_type": "footer",
        "uid": str(uuid.uuid4()),
        "aw_0_req.gdpr": "false",
        "gdpr": "false",
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://z1035.com/player/",
        "Origin": "https://z1035.com",
    }

    r = requests.get(
        base_url,
        params=params,
        headers=headers,
        allow_redirects=True,
        timeout=15,
    )

    return r.url

with open('buffer.txt', 'r') as f:
    buffer = int(f.read())

def get_session_url(url):
    """returns the session url"""
    sess_url = url # do something
    return sess_url

def get_media_playlist_url(url):
    playlist = m3u8.load(url)

    if playlist.is_variant:
        variant = playlist.playlists[0]
        media_url = urljoin(url, variant.uri)
        return get_media_playlist_url(media_url)

    return url


def record_m3u8(start_time, end_time, urlink, startup_segments=1):
    """
    startup_segments:
        0 = start only with future segments after first poll
        1 = include only last visible segment on first poll
        2 = include last 2 visible segments on first poll
    """
    
    urlink = get_session_url(urlink)
    
    while dt.now() < start_time:
        if dt.now() > end_time:
            return b''
        time.sleep(buffer)

    print('Recording as of', dt.now().strftime('%Y-%m-%d'))
    print('from', dt.now().strftime('%H:%M'), 'to', end_time.strftime('%H:%M'))

    media_url = get_media_playlist_url(urlink)
    print("Locked media playlist:", media_url)

    last_sequence = None
    all_data = []

    while dt.now() < end_time:
        try:
            playlist = m3u8.load(media_url)
        except Exception as e:
            print("Playlist error:", e)
            time.sleep(buffer)
            continue

        if not playlist.segments:
            time.sleep(buffer)
            continue

        seq = playlist.media_sequence or 0
        segment_count = len(playlist.segments)

        if last_sequence is None:
            # First pass: start near the live edge, not from the whole visible buffer
            if startup_segments <= 0:
                start_index = segment_count
            else:
                start_index = max(0, segment_count - startup_segments)
        else:
            # Later passes: only fetch segments after the last seen one
            start_index = last_sequence - seq + 1
            if start_index < 0:
                start_index = 0

        downloaded_any = False

        for i in range(start_index, segment_count):
            segment = playlist.segments[i]
            seg_url = urljoin(media_url, segment.uri)

            try:
                response = requests.get(seg_url, timeout=15)
                response.raise_for_status()
                all_data.append(response.content)
                downloaded_any = True
            except requests.RequestException as e:
                print(f"Segment error: {e}")

        # Move last_sequence forward to the end of the visible playlist
        last_sequence = seq + segment_count - 1

        time.sleep(buffer)

    return b''.join(all_data)


def cast_recorder(start_time, end_time, stream_url):
    data = b''

    while dt.now() < start_time:
        if dt.now() > end_time:
            return b''
        time.sleep(buffer)

    print('Recording as of', dt.now().strftime('%Y-%m-%d'))
    print('from', dt.now().strftime('%H:%M'), 'to', end_time.strftime('%H:%M'))

    try:
        response = requests.get(stream_url, stream=True, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to retrieve stream: {e}")
        return None

    while dt.now() < end_time:
        try:
            chunk = response.raw.read(1024)
            if not chunk:
                break
            data += chunk
        except Exception as e:
            print(f"Stream read error: {e}")
            break

    return data
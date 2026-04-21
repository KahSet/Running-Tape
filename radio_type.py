import requests

def detect_radio_stream(url):
    """
    Detects the type of radio stream and suggests an appropriate file extension.
    
    Returns:
        (stream_type, file_extension)
        - "Icecast/Shoutcast" -> ".mp3" / ".aac"
        - "HLS" -> ".ts" (segments) or ".aac" (if merged)
        - "DASH" -> ".mpd" (but should be converted to .aac or .m4a)
        - "RTMP" -> ".flv" or ".aac"
        - "RTSP" -> ".aac" / ".mp3"
        - "MMS" -> ".wma"
        - "UNKNOWN" -> ".bin" (raw data)
    """
    try:
        # Handle RTMP/RTSP streams (No HTTP request possible)
        if url.startswith("rtmp://"):
            return ("RTMP", ".flv")  # RTMP streams are usually Flash Video (.flv)
        if url.startswith("rtsp://"):
            return ("RTSP", ".aac")  # RTSP can stream AAC/MP3

        # Make a request to get headers
        response = requests.get(url, stream=True, timeout=5)
        content_type = response.headers.get("Content-Type", "").lower()

        # Identify HLS (M3U8)
        if "mpegurl" in content_type or url.endswith(".m3u8"):
            return ("HLS", ".aac")  # HLS streams are often AAC-based

        # Identify DASH (MPD)
        if "dash+xml" in content_type or url.endswith(".mpd"):
            return ("DASH", ".m4a")  # DASH streams usually contain M4A/AAC

        # Identify Icecast/Shoutcast (MP3, AAC)
        if "audio/mpeg" in content_type or url.endswith(".mp3"):
            return ("Icecast/Shoutcast", ".mp3")
        elif "audio/aac" in content_type or "audio/aacp" in content_type or url.endswith(".aac"):
            return ("Icecast/Shoutcast", ".aac")

        # Identify MMS (Microsoft Media Server)
        if "x-mms" in content_type or url.startswith("mms://") or url.endswith(".asx") or url.endswith(".wma"):
            return ("MMS", ".wma")

        return ("UNKNOWN", ".bin")  # If we can't detect it, save raw binary

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return ("UNKNOWN", ".bin")

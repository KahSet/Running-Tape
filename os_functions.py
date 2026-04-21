import os
import platform
from pathlib import Path

def get_downloads_folder():
    system = platform.system()
    
    if system == "Windows":
        return Path(os.path.join(os.environ['USERPROFILE'], 'Downloads'))
    elif system == "Darwin":  # macOS
        return Path.home() / "Downloads"
    elif system == "Linux":
        return Path.home() / "Downloads"
    else:
        raise NotImplementedError(f"Unsupported OS: {system}")

downloads_path = get_downloads_folder()
print(f"Downloads folder: {downloads_path}")
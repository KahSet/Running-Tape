"""
Generates the following important variables:

Chosen from csv file 'Radio_Stns.csv' - please update if missing stations

stn: Radio Station - string
urlink: URL to radio station - string
start_time: tells you when to start recording - datetime
end_time: tells you when to end recording - datetime
filename: file name for recording - string
f_ext: extension for filename - string



"""
#importing packages

#stuff everyone should have:
import radio_type as rt
import tkinter as tk
import time
import os
from datetime import datetime as dt, timedelta
from pathlib import Path

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
    import pandas as pd
except:
    print('one-time installation: pandas')
    install('pandas')
    import pandas as pd


def get_download_flder():
    dwnld_pth = Path.home() / 'Downloads'
    if dwnld_pth.exists() and dwnld_pth.is_dir():
        return dwnld_pth
    else:
        cwd = os.getcwd()
        fallback_path = os.path.join(cwd,'downloads')
        #fallback_path.mkdir(exist_ok=True)
        return fallback_path
    

home = os.getcwd()
downloads = get_download_flder()
urls = os.path.join(home,'Radio_Stns.csv')

stns = pd.read_csv(urls,index_col='Radio_Stn')

urlink = ''
stn = ''

def on_select(event):
    # Check if there is any selection in the listbox
    if listbox.curselection():
        submitButton.config(state=tk.NORMAL)
    else:
        submitButton.config(state=tk.DISABLED)

def singlesubmit():
    global urlink
    global stn
    stn = listbox.get(listbox.curselection())
    urlink = stns['URL'][stn]
    
    # Enable the close button if urlink is not an empty string
    if urlink:
        closeButton.config(state=tk.NORMAL)
        station_win.destroy()



station_win = tk.Tk()

listbox = tk.Listbox(station_win,
                  bg="#f7ffde",
                  font=("consolas",20),
                  width=12,
                  selectmode=tk.SINGLE)

for i,x in enumerate(stns.index):
    listbox.insert(i,x)

listbox.config(height=listbox.size())
listbox.bind('<<ListboxSelect>>', on_select)
listbox.pack()
submitButton = tk.Button(station_win, text="submit",command=singlesubmit,state=tk.DISABLED)
submitButton.pack(side=tk.LEFT)
closeButton = tk.Button(station_win, text="close",command=station_win.destroy,state=tk.DISABLED)
closeButton.pack(side=tk.RIGHT)
station_win.mainloop()

import requests

streamtyp, f_ext = rt.detect_radio_stream(urlink)

print('stream type:',streamtyp)
print('file extension:',f_ext)

# import tkinter as tk
from tkinter import messagebox

def has_time(event):
    # Check if there is any selection in the listbox
    if start_hour_entry.get() and start_minute_entry.get() and end_hour_entry.get() and end_minute_entry.get():
        settime.config(state=tk.NORMAL)
    else:
        settime.config(state=tk.DISABLED)

def validate_hour(char):
    """Allow only numeric characters and limit to 2 digits."""
    return char.isdigit() and len(char) <= 2 and int(char)<=23 or char==''

def validate_minute(char):
    """Allow only numeric characters and limit to 2 digits."""
    return char.isdigit() and len(char) <= 2 and int(char)<=59 or char==''

def set_times():
    global start_time, end_time
    """
    Retrieve input from the Tkinter GUI, validate it, and set the start and end times.
    """
    try:
        # Get input values and format them correctly
        start_hour = start_hour_entry.get().zfill(2)
        start_minute = start_minute_entry.get().zfill(2)
        end_hour = end_hour_entry.get().zfill(2)
        end_minute = end_minute_entry.get().zfill(2)

        # Ensure inputs are valid (non-empty)
        if not all([start_hour, start_minute, end_hour, end_minute]):
            raise ValueError("All fields must be filled.")

        # Format as HH:MM and parse
        start_time_str = f"{start_hour}:{start_minute}"
        end_time_str = f"{end_hour}:{end_minute}"

        # Convert user input into datetime objects
        now = dt.now()
        current_date = dt.now().date()
        start_time = dt.strptime(start_time_str, "%H:%M").time()
        end_time = dt.strptime(end_time_str, "%H:%M").time()
        
        start_time = dt.combine(current_date, start_time)
        end_time = dt.combine(current_date, end_time)
        
        # If current time already passed the start time, move both forward one day
        if now > start_time:
            start_time += timedelta(days=1)
            end_time += timedelta(days=1)

        # Ensure inputs are valid (non-empty)
        if end_time < start_time:
            raise ValueError("Start time must come before end time.")

        # Generate filename based on start time
        global filename
        filename = stn +'_'+ start_time.strftime("%Y%m%d_%H%M%S") + "_rcrd" + f_ext
        
        # Display confirmation message
        print(f"Recording times set!\nStart: {start_time}\nEnd: {end_time}\nFile: {filename}")
        
        # Close the Tkinter window after setting times
        root.destroy()
    
    except ValueError as e:
        messagebox.showerror("Error", str(e))

# Create the Tkinter window
root = tk.Tk()
root.title("Set Recording Time")
root.geometry("300x200")

# Validation command (only allows numbers & max 2 chars)
validate_hrcommand = root.register(validate_hour)
validate_mincommand = root.register(validate_minute)

# Labels and Inputs for Start Time
tk.Label(root, text="Start Time (HH:MM):").pack()
start_frame = tk.Frame(root)
start_frame.pack()

start_hour_entry = tk.Entry(start_frame, width=3, validate="key", validatecommand=(validate_hrcommand, "%P"))

start_minute_entry = tk.Entry(start_frame, width=3, validate="key", validatecommand=(validate_mincommand, "%P"))

start_hour_entry.pack(side="left")
tk.Label(start_frame, text=":").pack(side="left")
start_minute_entry.pack(side="left")

# Labels and Inputs for End Time
tk.Label(root, text="End Time (HH:MM):").pack()
end_frame = tk.Frame(root)
end_frame.pack()

end_hour_entry = tk.Entry(end_frame, width=3, validate="key", validatecommand=(validate_hrcommand, "%P"))
end_minute_entry = tk.Entry(end_frame, width=3, validate="key", validatecommand=(validate_mincommand, "%P"))

end_hour_entry.pack(side="left")
tk.Label(end_frame, text=":").pack(side="left")
end_minute_entry.pack(side="left")

# Button to set times
settime = tk.Button(root, text="Set Times", command=set_times,state=tk.DISABLED)
settime.pack()

# Bind the "has_time" function to all entry fields so the button updates dynamically
for entry in [start_hour_entry, start_minute_entry, end_hour_entry, end_minute_entry]:
    entry.bind("<KeyRelease>", has_time)  # Runs when the user types or deletes

# Run the Tkinter event loop
root.mainloop()

# Now filename contains the filename with the correct timestamp
#print("Final filename:", filename)

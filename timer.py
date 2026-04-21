import time
import datetime
import tkinter as tk
import threading

def countdown_timer(start_time):
    start_time -= datetime.timedelta(seconds=1)
    """
    Displays a countdown timer, closes when start_time begins
    """
    root = tk.Tk()
    root.title(" ")
    root.configure(bg="black")  # Set background color

    # Fonts (Use DS-Digital if installed, fallback to Courier New)
    try:
        digital_font = ("DS-Digital", 36, "bold")  # Install DS-Digital for best look
    except:
        digital_font = ("Courier New", 36, "bold")  # Monospaced alternative

    # "Starting in" Label (Above the Timer)
    start_label = tk.Label(root, text="Starting in", font=("Arial", 16, "bold"), fg="red", bg="black")
    start_label.pack(pady=(10, 5))  # Add spacing above

    # Timer Label (Larger and Styled)
    time_label = tk.Label(root, text="", font=digital_font, fg="red", bg="black")
    time_label.pack(padx=10)

    def update_timer():
        while True:
            now = datetime.datetime.now()
            remaining = start_time - now

            if remaining.total_seconds() <= 0:
                time_label.config(text="00:00:00", fg="green")
                start_label.config(text="Recording Started!", fg="green")
                root.destroy()  # closes
                break

            time_str = str(remaining).split(".")[0]  # Format as HH:MM:SS
            time_label.config(text=time_str)
            root.update()
            time.sleep(1)


    # Start the countdown in a separate thread
    threading.Thread(target=update_timer, daemon=True).start()
    
    root.mainloop()

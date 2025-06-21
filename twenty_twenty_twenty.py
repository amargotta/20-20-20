# twenty_twenty_twenty.py
# Alexander Margotta — v1.1 with configuration
# GitHub: amargotta
# June 21, 2025

# --- CONFIGURATION — edit these to customize behavior ---
BREAK_INTERVAL_MINUTES   = 20                                               # Interval between breaks in minutes (default is 20 minutes, the whole point of the program)
NOTIFICATION_TITLE       = "20-20-20 Reminder"                              # Title of the notification 
NOTIFICATION_MESSAGE     = "Look at something 20 feet away for 20 seconds." # Message of the notification
SOUND_FILE               = "/System/Library/Sounds/Glass.aiff"              # Path to sound file to play when the break time is reached
# Popular built-in sounds: "Glass.aiff", "Ping.aiff", "Funk.aiff", "Submarine.aiff"

ICON_SIZE                = (64, 64)
ICON_BG_COLOR            = (255, 255, 255)
ICON_FG_COLOR            = (0, 0, 0)
# ------------------------------------------

# --- IMPORTS ---
import threading                            # For running background tasks (e.g., timer, countdown) without freezing the main app
import time                                 # For handling time delays (sleep)
from datetime import datetime, timedelta    # For calculating future break times
from pystray import Icon, Menu, MenuItem    # Used to create the system tray icon and its menu
from PIL import Image, ImageDraw            # Used to create a custom icon image    
import subprocess                           # Used to send macOS notifications and play sounds
import os                                   # Used to check if the sound file exists 

# --- MAIN APP CLASS ---
class TwentyTwentyTwenty:
    def __init__(self):
        self.running = False                # Whether the timer is currently active
        self.next_break_time = None         # The datetime of the next scheduled break
        self.timer_thread = None            # Reference to the timer thread
        self.countdown_thread = None        # Reference to the countdown update thread
        self.icon = Icon(
            "20-20-20",
            self.create_image(size=ICON_SIZE, bg=ICON_BG_COLOR, fg=ICON_FG_COLOR),
            menu=self.create_menu()
        )                                   # Initializes the tray icon with a label, a generated icon image, and a menu                          

    def create_image(self, size, bg, fg):
        image = Image.new('RGB', size, color=bg)    # Create a new image with the specified background color
        draw  = ImageDraw.Draw(image)               # Create a drawing context for the image
        margin = 0.25 * size[0]                     # Calculate margin as 25% of width
        draw.ellipse(
            (margin, margin, size[0] - margin, size[1] - margin),
            fill=fg
        )                                   # Draw a filled circle in the center of the image with the specified foreground color
        return image                        # Returns the created image to use as the tray icon

    def create_menu(self):                  # Creates the menu for the tray icon
        self.dynamic_status = MenuItem(
            lambda item: self.get_status_label(),
            lambda: None,
            enabled=False
        )                                   # Menu item that dynamically updates to show the next break time or status
        return Menu(
            self.dynamic_status,
            MenuItem("Go",        self.start,      default=True),
            MenuItem("Stop",      self.stop),
            MenuItem("Test Alert",self.test_alert),
            MenuItem("Quit",      self.quit)
        )                                   # Creates the menu with options to start, stop, test alert, and quit the app

    def get_status_label(self):
        if self.running and self.next_break_time:
            delta = self.next_break_time - datetime.now()       # Calculate time remaining until next break
            if delta.total_seconds() > 0:                       # If the break time is still in the future  
                m, s = divmod(int(delta.total_seconds()), 60)   # Convert seconds to minutes and seconds
                return f"Next: {m:02d}:{s:02d}"                 # Format as MM:SS   
            return "Break due!"                                 # If the break time has passed, indicate that a break is due
        return "Not running"                                    # Default status when the timer is not running

    def notify(self):
        # Sends a native macOS notification using AppleScript
        subprocess.run([
            "osascript", "-e",
            f'display notification "{NOTIFICATION_MESSAGE}" with title "{NOTIFICATION_TITLE}"'
        ])
        # Play sound if sound file available
        if os.path.exists(SOUND_FILE):
            subprocess.Popen(["afplay", SOUND_FILE])            # Use Popen so it plays asynchronously

    def run_timer(self):
        while self.running:
            self.next_break_time = datetime.now() + timedelta(minutes=BREAK_INTERVAL_MINUTES)   # Set next break time based on configured interval
            for _ in range(BREAK_INTERVAL_MINUTES * 60):                                        # Wait for the specified number of seconds (20 minutes) 
                if not self.running:
                    return                                                                      # Exit early if the timer is stopped
                time.sleep(1)                                                                   # Sleep for 1 second before checking again
            if self.running:
                self.notify()                                                                   # Send alert when the break time is reached     
    
    def run_countdown(self):
        while True:
            if self.running:
                self.icon.update_menu()                                                         # Refresh the menu every second to update the countdown label   
            time.sleep(1)                                                                       # Sleep for 1 second before next update

    def start(self, icon, item):
        if not self.running:                                                                        # Check if the timer is not already running
            self.running = True                                                                     # Mark as running
            self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)                # Start the timer in a background thread    
            self.timer_thread.start()                                                               # Start the countdown updater if it’s not already running 
            if not self.countdown_thread or not self.countdown_thread.is_alive():                   # Check if countdown thread is not running
                self.countdown_thread = threading.Thread(target=self.run_countdown, daemon=True)    # Create a new countdown thread
                self.countdown_thread.start()                                                       # Start the countdown updater thread

    def stop(self, icon, item):
        self.running = False                # Halt timer logic
        self.next_break_time = None         # Clear the next scheduled break
        self.icon.update_menu()             # Refresh menu to reflect stopped state

    def test_alert(self, icon, item):
        self.notify()                       # Manually trigger alert (notification + sound)

    def quit(self, icon, item):
        self.stop(icon, item)               # Stop timers
        self.icon.stop()                    # Close the tray icon and exit the app

    def run(self):
        self.icon.run()                     # Start the system tray icon loop (blocks forever)

# --- SCRIPT ENTRY POINT ---
if __name__ == "__main__":
    TwentyTwentyTwenty().run()              # Create an instance of the app and run it


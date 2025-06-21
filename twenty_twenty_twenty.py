# Alexander Margotta
# GitHub: amargotta
# June 21, 2025

# --- IMPORTS ---
import threading  # For running background tasks (e.g., timer, countdown) without freezing the main app
import time  # For handling time delays (sleep)
from datetime import datetime, timedelta  # For calculating future break times

# from plyer import notification  # Originally used for cross-platform notifications, now disabled on macOS

from pystray import Icon, Menu, MenuItem  # Used to create the system tray icon and its menu
from PIL import Image, ImageDraw  # Used to create a custom icon image
import subprocess  # Used to send macOS notifications and play sounds
import os  # Used to check if the sound file exists


# --- MAIN APP CLASS ---
class TwentyTwentyTwenty:
    def __init__(self):
        self.running = False  # Whether the timer is currently active
        self.next_break_time = None  # The datetime of the next scheduled break
        self.timer_thread = None  # Reference to the timer thread
        self.countdown_thread = None  # Reference to the countdown update thread
        self.icon = Icon("20-20-20", self.create_image(), menu=self.create_menu())
        # Initializes the tray icon with a label, a generated icon image, and a menu

    def create_image(self):
        image = Image.new('RGB', (64, 64), color=(255, 255, 255))  # Creates a blank white 64x64 image
        draw = ImageDraw.Draw(image)  # Allows drawing on the image
        draw.ellipse((16, 16, 48, 48), fill=(0, 0, 0))  # Draws a black circle centered in the image
        return image  # Returns the created image to use as the tray icon

    def create_menu(self):
        # Menu item with dynamic text (e.g., "Next: 17:32")
        self.dynamic_status = MenuItem(lambda item: self.get_status_label(), lambda: None, enabled=False)
        return Menu(
            self.dynamic_status,  # Top row showing countdown or status
            MenuItem("Go", self.start, default=True),  # Starts the timer
            MenuItem("Stop", self.stop),  # Stops the timer
            MenuItem("Test Alert", self.test_alert),  # Triggers a manual alert
            MenuItem("Quit", self.quit)  # Exits the app
        )

    def get_status_label(self):
        if self.running and self.next_break_time:
            delta = self.next_break_time - datetime.now()  # Time remaining until next break
            if delta.total_seconds() > 0:
                minutes, seconds = divmod(int(delta.total_seconds()), 60)  # Convert seconds to MM:SS
                return f"Next: {minutes:02d}:{seconds:02d}"  # Display countdown in menu
            else:
                return "Break due!"  # If time has passed
        return "Not running"  # Default status when stopped

    def notify(self):
        # Sends a native macOS notification using AppleScript
        subprocess.run([
            "osascript", "-e",
            'display notification "Look at something 20 feet away for 20 seconds." with title "20-20-20 Reminder"'
        ])

        # Plays a soft system chime, if the file exists
        sound_path = "/System/Library/Sounds/Glass.aiff"
        if os.path.exists(sound_path):
            subprocess.Popen(["afplay", sound_path])  # Use Popen so it plays asynchronously

    def run_timer(self):
        while self.running:
            self.next_break_time = datetime.now() + timedelta(minutes=20)  # Set next break 20 minutes from now
            for _ in range(20 * 60):  # Wait for 1200 seconds (20 minutes), second by second
                if not self.running:
                    return  # Exit early if timer is stopped
                time.sleep(1)  # Wait 1 second before next loop iteration
            if self.running:
                self.notify()  # Send alert when 20 minutes have passed

    def run_countdown(self):
        while True:
            if self.running:
                self.icon.update_menu()  # Refresh menu every second to update countdown label
            time.sleep(1)

    def start(self, icon, item):
        if not self.running:
            self.running = True  # Mark as running
            # Start timer in background
            self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
            self.timer_thread.start()
            # Start countdown updater if it’s not already running
            if not self.countdown_thread or not self.countdown_thread.is_alive():
                self.countdown_thread = threading.Thread(target=self.run_countdown, daemon=True)
                self.countdown_thread.start()

    def stop(self, icon, item):
        self.running = False  # Halt timer logic
        self.next_break_time = None  # Clear the next scheduled break
        self.icon.update_menu()  # Refresh menu to reflect stopped state

    def test_alert(self, icon, item):
        self.notify()  # Manually trigger alert (notification + sound)

    def quit(self, icon, item):
        self.stop(icon, item)  # Stop timers
        self.icon.stop()  # Close the tray icon and exit the app

    def run(self):
        self.icon.run()  # Start the system tray icon loop (blocks forever)

# --- SCRIPT ENTRY POINT ---
if __name__ == "__main__":
    TwentyTwentyTwenty().run()  # Create an instance of the app and run it

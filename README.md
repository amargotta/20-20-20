## 20-20-20 Timer (macOS Tray App) v1
This is a lightweight, macOS-native tray utility that reminds you to follow the **20-20-20 rule**:  
> Every 20 minutes, look at something 20 feet away for 20 seconds.

I got sick of not remembering to do this myself, and manually making and remaking a timer on the phone is a hastle. This is meant to be an easy app to simply hit "Go" when you're at your computer.

Protect your eyes!

## Features
v1 is basic functionality:
- Sits in your macOS system tray --> Look for a white square with a black circle in your tray/toolbar
- "Go" starts a 20-minute countdown cycle --> Press "Go" when you are at your computer and doing work
- "Stop" stops the timer and resets --> Press "Stop" when you are not at your computer
- "Test Alert" triggers a notification and chime immediately to test it out
- Countdown timer shown in dropdown menu when icon is clicked
- Gentle macOS system notification + soft chime (Glass.aiff default)

Every time the timer finishes its countdown it sends a soft ping and notification reminding you to look 20 feet away for 20 seconds, then it automatically starts a new timer.

Future quality of life improvements to come.

## Requirements
Requires pystray and pillow
"pip install pystray pillow" in Terminal

## Run
"python twenty_twenty_twenty.py" in Terminal inside the folder where the .py script lives
or "python3" if you have Python 3

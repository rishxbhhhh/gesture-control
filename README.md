# Gesture Control App

A gesture-controlled media player using MediaPipe and pyautogui.

## Features
- Play/Pause media with a hand gesture
- Volume control (up/down) with hand gestures
- Next/Previous track navigation with hand gestures
- Headless operation (runs in the background)

## Gesture Controls
- **Play/Pause**: Raise 1 finger (Index)
- **Volume Up**: Raise 2 fingers (Index + Middle)
- **Volume Down**: Raise 3 fingers (Index + Middle + Ring)
- **Next Track**: Raise 4 fingers (Index + Middle + Ring + Pinky)
- **Previous Track**: Raise 5 fingers (All fingers)

## Requirements
- Python 3.11
- OpenCV
- MediaPipe
- pyautogui

## Installation
1. Clone this repository
2. Install dependencies:
   ```bash
   pip install opencv-python mediapipe pyautogui
   ```
3. Download the `hand_landmarker.task` model file from:
   ```bash
   https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
   ```
   and place it in the project directory.

## Usage
Run the script:
```bash
python gesture_controller.py
```

Place your hand in front of the camera and perform the gestures to control media playback.

## How It Works
- Uses MediaPipe for hand landmark detection
- Uses pyautogui to simulate media key presses
- Runs headlessly without displaying the camera feed
- Includes a 3-second delay after play/pause actions
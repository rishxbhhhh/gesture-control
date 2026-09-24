import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import time
import pyautogui
import sys
import threading
import win32gui
import win32con
import win32api

# ===== Configuration =====
GESTURE_COOLDOWN = 0.5  # seconds between gesture actions
CONFIDENCE_THRESHOLD = 0.9
MIN_NUM_HANDS = 1
MAX_NUM_HANDS = 1

# Hand landmark indices for gesture detection
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20
INDEX_PIP = 6
MIDDLE_PIP = 10
RING_PIP = 14
PINKY_PIP = 18
WRIST = 0

# ===== Media Key Constants (Windows) =====
VK_MEDIA_NEXT_TRACK = 0x00B0
VK_MEDIA_PREV_TRACK = 0x00B1
VK_MEDIA_PLAY_PAUSE = 0x00B0  # Actually 0xCD but we'll use win32con
VK_MEDIA_VOLUME_UP = 0x00AE
VK_MEDIA_VOLUME_DOWN = 0x00AF

# Actually the proper win32con values
VOLUME_DOWN = 0xAE
VOLUME_UP = 0xAF
MEDIA_NEXT = 0xB0
MEDIA_PREV = 0xB1
MEDIA_PLAY_PAUSE = 0xCD

# ===== Initialize MediaPipe HandLandmarker =====
BaseOptions = mp.tasks.BaseOptions
VisionRunningMode = mp.tasks.vision.RunningMode

import os

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, 'hand_landmarker.task')

options = vision.HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=MAX_NUM_HANDS,
    min_hand_detection_confidence=CONFIDENCE_THRESHOLD,
    min_hand_presence_confidence=CONFIDENCE_THRESHOLD
)

landmarker = vision.HandLandmarker.create_from_options(options)

# ===== Gesture State =====
last_gesture_time = 0


def get_active_window_title():
    """Get the title of the currently active window."""
    try:
        foreground = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(foreground)
        return title
    except:
        return ""


def send_media_key(key_code):
    """Send a Windows media key press."""
    try:
        win32api.keybd_event(key_code, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    except Exception as e:
        print(f"Error sending media key: {e}")




def increase_volume():
    """Increase system volume by 20%."""
    try:
        for _ in range(5):
            pyautogui.press('volumeup')
            time.sleep(0.05)  # Small delay between presses
        time.sleep(1)  # Slight delay after volume change
        print("Volume increased")
    except Exception as e:
        print(f"Error increasing volume: {e}")


def decrease_volume():
    """Decrease system volume by 20%."""
    try:
        for _ in range(5):
            pyautogui.press('volumedown')
            time.sleep(0.05)  # Small delay between presses
        time.sleep(1)
        print("Volume decreased")
    except Exception as e:
        print(f"Error decreasing volume: {e}")


def next_track():
    """Skip to next track."""
    try:
        pyautogui.press('nexttrack')
    except Exception as e:
        print(f"Error skipping to next track: {e}")


def previous_track():
    """Go to previous track."""
    try:
        pyautogui.press('prevtrack')
    except Exception as e:
        print(f"Error going to previous track: {e}")


def play_pause():
    """Toggle play/pause with a 3-second delay after pressing."""
    try:
        pyautogui.press('playpause')
        time.sleep(3)  # Add 3-second delay after play/pause
    except Exception as e:
        print(f"Error toggling play/pause: {e}")
        try:
            pyautogui.press('space')
            time.sleep(3)  # Add 3-second delay after spacebar press
        except Exception as e:
            print(f"Error simulating spacebar: {e}")


def is_media_playing():
    """Check if any media is playing by simulating a media key press."""
    # This is a heuristic check that works for many media players
    try:
        # Try to send a media key press and see if it triggers a response
        # This is a simple way to check if media is active
        pyautogui.press('playpause')
        time.sleep(0.1)  # Small delay to allow potential response
        return True
    except Exception as e:
        print(f"Error checking media playing status: {e}")
        return False


def detect_gesture(hand_landmarks):
    """
    Detect hand gestures from MediaPipe hand landmarks.
    Returns one of: 'play_pause', 'volume_up', 'volume_down', 'next', 'previous', or None
    """
    global last_gesture_time

    landmarks = hand_landmarks

    # Get finger tip and pip positions
    fingers = []

    # Thumb: compare tip (4) with ip (3)
    thumb_tip = landmarks[THUMB_TIP]
    thumb_ip = landmarks[3]
    # Thumb is open if tip x is greater than ip x (for right hand)
    thumb_open = thumb_tip.x > thumb_ip.x

    # Index finger: compare tip (8) with pip (6)
    index_tip = landmarks[INDEX_TIP]
    index_pip = landmarks[INDEX_PIP]
    index_open = index_tip.y < index_pip.y  # Tip above pip = extended

    # Middle finger: compare tip (12) with pip (10)
    middle_tip = landmarks[MIDDLE_TIP]
    middle_pip = landmarks[MIDDLE_PIP]
    middle_open = middle_tip.y < middle_pip.y

    # Ring finger: compare tip (16) with pip (14)
    ring_tip = landmarks[RING_TIP]
    ring_pip = landmarks[RING_PIP]
    ring_open = ring_tip.y < ring_pip.y

    # Pinky: compare tip (20) with pip (18)
    pinky_tip = landmarks[PINKY_TIP]
    pinky_pip = landmarks[PINKY_PIP]
    pinky_open = pinky_tip.y < pinky_pip.y

    fingers = [thumb_open, index_open, middle_open, ring_open, pinky_open]

    # Count raised fingers
    raised_count = sum(fingers)

    # Get hand position/yaw info
    wrist = landmarks[WRIST]
    index_tip_pos = landmarks[INDEX_TIP]

    current_time = time.time()

    # ===== Improved Finger Count Gestures =====

    # 1. One finger raised (Index) -> Play / Pause
    if raised_count == 1 and index_open and not thumb_open and not middle_open and not ring_open and not pinky_open \
            and current_time - last_gesture_time > GESTURE_COOLDOWN:
        last_gesture_time = current_time
        return 'play_pause'

    # 2. Two fingers raised (Index + Middle) -> Volume Up
    if raised_count == 2 and index_open and middle_open \
            and current_time - last_gesture_time > GESTURE_COOLDOWN:
        last_gesture_time = current_time
        return 'volume_up'

    # 3. Three fingers raised (Index + Middle + Ring) -> Volume Down
    if raised_count == 3 and index_open and middle_open and ring_open \
            and current_time - last_gesture_time > GESTURE_COOLDOWN:
        last_gesture_time = current_time
        return 'volume_down'

    # 4. Four fingers raised (Index + Middle + Ring + Pinky) -> Next Track
    if raised_count == 4 and index_open and middle_open and ring_open and pinky_open and not thumb_open \
            and current_time - last_gesture_time > GESTURE_COOLDOWN:
        last_gesture_time = current_time
        return 'next'

    # 5. Five fingers raised (All fingers open) -> Previous Track
    if raised_count == 5 and index_open and middle_open and ring_open and pinky_open and thumb_open \
            and current_time - last_gesture_time > GESTURE_COOLDOWN:
        last_gesture_time = current_time
        return 'previous'

    # Gesture 6: Stop/No gesture - All fingers down (fist)
    if (not index_open and not middle_open and not ring_open and not pinky_open
            and not thumb_open
            and current_time - last_gesture_time > GESTURE_COOLDOWN):
        # This is just a reset, don't return an action
        pass

    return None


def draw_gesture_info(image, gesture):
    """Draw gesture information on the image."""
    cv2.putText(image, f"Gesture: {gesture or 'None'}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


def main():
    """Main loop for gesture-controlled media."""
    global last_gesture_time
    last_gesture_time = 0
    print("Starting Gesture Controller...")
    print("Press 'q' to quit")
    print("Wave hands in front of camera to control media")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video device")
        sys.exit(1)

    # Get screen size for reference
    screen_width, screen_height = pyautogui.size()

    print(f"Screen resolution: {screen_width}x{screen_height}")

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame")
            continue

        # Flip the image horizontally for a mirror view
        image = cv2.flip(image, 1)

        # Convert the BGR image to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert OpenCV image to MediaPipe Image format
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        # Process the image and detect hands using HandLandmarker
        detection_result = landmarker.detect(mp_image)

        # Detect gesture
        if detection_result.hand_landmarks:
            for hand_landmarks_list in detection_result.hand_landmarks:
                current_time = time.time()
                if current_time - last_gesture_time > GESTURE_COOLDOWN:
                    gesture = detect_gesture(hand_landmarks_list)
                    if gesture:
                        last_gesture_time = current_time
                        print(f"Detected: {gesture}")

                        # Execute the corresponding action
                        if gesture == 'play_pause':
                            play_pause()
                            print(" -> Play/Pause toggled")
                        elif gesture == 'volume_up':
                            increase_volume()
                            print(" -> Volume Up")
                        elif gesture == 'volume_down':
                            decrease_volume()
                            print(" -> Volume Down")
                        elif gesture == 'next':
                            next_track()
                            print(" -> Next Track")
                        elif gesture == 'previous':
                            previous_track()
                            print(" -> Previous Track")

        # Exit on 'q' key press if window is shown, but here it's headless processing loop
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break


    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

    print("Gesture Controller stopped.")


if __name__ == "__main__":
    main()
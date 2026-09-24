#!python
import urllib.request

url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
destination = "C:\\Users\\rishabh\\Desktop\\gesture-control\\hand_landmarker.task"

try:
    print(f"Downloading model from {url}...")
    urllib.request.urlretrieve(url, destination)
    print(f"Model downloaded to {destination}")
except Exception as e:
    print(f"Error downloading model: {e}")
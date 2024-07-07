import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import os

# Initialize Mediapipe and PyAutoGUI
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

screen_width, screen_height = pyautogui.size()
print(f"Screen size: {screen_width}x{screen_height}")

last_click_time = 0
double_click_threshold = 0.3  # seconds
zooming = False

def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save("screenshot.png")
    print("Screenshot taken")

def mute_unmute_audio():
    pyautogui.press('volumeup')
    time.sleep(0.1)
    pyautogui.press('volumedown')
    print("Audio muted/unmuted")

def volume_control(up=True):
    if up:
        pyautogui.press('volumeup')
        print("Volume up")
    else:
        pyautogui.press('volumedown')
        print("Volume down")

def brightness_control(up=True):
    if os.name == 'nt':
        if up:
            pyautogui.hotkey('fn', 'f3')  # Adjust to your system's brightness control key
            print("Brightness up")
        else:
            pyautogui.hotkey('fn', 'f2')  # Adjust to your system's brightness control key
            print("Brightness down")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame from webcam.")
        break

    # Flip the frame horizontally for a later selfie-view display
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the position of the index finger tip
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
            pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

            x = int(index_finger_tip.x * frame.shape[1])
            y = int(index_finger_tip.y * frame.shape[0])
            print(f"Index finger tip position: {x}, {y}")

            # Move the mouse
            screen_x = int(screen_width * index_finger_tip.x)
            screen_y = int(screen_height * index_finger_tip.y)
            pyautogui.moveTo(screen_x, screen_y)
            print(f"Moved mouse to: {screen_x}, {screen_y}")

            # Detect click gesture (e.g., if thumb tip is close to index finger tip)
            if abs(index_finger_tip.x - thumb_tip.x) < 0.05 and abs(index_finger_tip.y - thumb_tip.y) < 0.05:
                current_time = time.time()
                if current_time - last_click_time < double_click_threshold:
                    pyautogui.doubleClick()
                    print("Mouse double click detected")
                else:
                    pyautogui.click()
                    print("Mouse left click detected")
                last_click_time = current_time
                
            # Right click
            if abs(middle_finger_tip.x - thumb_tip.x) < 0.05 and abs(middle_finger_tip.y - thumb_tip.y) < 0.05:
                pyautogui.click(button='right')
                print("Mouse right click detected")

            # Scroll up
            if abs(index_finger_tip.x - middle_finger_tip.x) < 0.05 and index_finger_tip.y < middle_finger_tip.y:
                pyautogui.scroll(20)
                print("Scroll up detected")

            # Scroll down
            if abs(index_finger_tip.x - middle_finger_tip.x) < 0.05 and index_finger_tip.y > middle_finger_tip.y:
                pyautogui.scroll(-20)
                print("Scroll down detected")

            # Drag (index finger and thumb close, index finger and middle finger far apart)
            if abs(index_finger_tip.x - thumb_tip.x) < 0.05 and abs(index_finger_tip.x - middle_finger_tip.x) > 0.1:
                pyautogui.mouseDown()
                print("Mouse drag start detected")
            else:
                pyautogui.mouseUp()
                print("Mouse drag end detected")

            # Zoom in/out
            if abs(index_finger_tip.x - middle_finger_tip.x) < 0.05 and abs(index_finger_tip.x - ring_finger_tip.x) < 0.05:
                if not zooming:
                    pyautogui.hotkey('ctrl', '+')
                    print("Zoom in detected")
                    zooming = True
            elif abs(index_finger_tip.x - middle_finger_tip.x) < 0.05 and abs(index_finger_tip.x - pinky_tip.x) < 0.05:
                if not zooming:
                    pyautogui.hotkey('ctrl', '-')
                    print("Zoom out detected")
                    zooming = True
            else:
                zooming = False

            # Switch applications (four fingers close to the thumb)
            if abs(index_finger_tip.x - thumb_tip.x) < 0.05 and abs(middle_finger_tip.x - thumb_tip.x) < 0.05 and abs(ring_finger_tip.x - thumb_tip.x) < 0.05 and abs(pinky_tip.x - thumb_tip.x) < 0.05:
                pyautogui.hotkey('alt', 'tab')
                print("Switch application detected")

            # Take a screenshot (index finger and thumb form a circle)
            if abs(index_finger_tip.x - thumb_tip.x) < 0.05 and abs(index_finger_tip.y - thumb_tip.y) < 0.05 and abs(middle_finger_tip.x - thumb_tip.x) < 0.05 and abs(middle_finger_tip.y - thumb_tip.y) < 0.05:
                take_screenshot()
            
            # Mute/Unmute audio (all fingers extended and spread)
            if (abs(index_finger_tip.x - pinky_tip.x) > 0.1 and abs(index_finger_tip.y - pinky_tip.y) < 0.1 and
                abs(middle_finger_tip.x - ring_finger_tip.x) > 0.1 and abs(middle_finger_tip.y - ring_finger_tip.y) < 0.1):
                mute_unmute_audio()

            # Volume control (index finger up/down for volume up/down)
            if abs(index_finger_tip.x - thumb_tip.x) < 0.05 and index_finger_tip.y < thumb_tip.y:
                volume_control(up=True)
            elif abs(index_finger_tip.x - thumb_tip.x) < 0.05 and index_finger_tip.y > thumb_tip.y:
                volume_control(up=False)
                
            # Brightness control (middle finger up/down for brightness up/down)
            if abs(middle_finger_tip.x - thumb_tip.x) < 0.05 and middle_finger_tip.y < thumb_tip.y:
                brightness_control(up=True)
            elif abs(middle_finger_tip.x - thumb_tip.x) < 0.05 and middle_finger_tip.y > thumb_tip.y:
                brightness_control(up=False)

    cv2.imshow('Hand Gesture Mouse Control', frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

import pygetwindow as gw
import numpy as np
import requests
from PIL import ImageGrab, Image
import time

# Функция для отправки кадра на дисплей
def send_frame_to_badge(frame, url='http://badge.phd2/api/v1/led/picture'):
    payload = {
        "values": frame
    }
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to send data: {e}")
        response = None
    return response

# Функция для захвата окна
def capture_window(window_title):
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        print(f"No window with title '{window_title}' found.")
        return None
    
    window = windows[0]
    bbox = (window.left, window.top, window.right, window.bottom)
    screenshot = ImageGrab.grab(bbox)
    return screenshot

# Размер дисплея (10x10)
size = 10

window_title = input("Enter the window title to capture: ")

while True:
    screenshot = capture_window(window_title)
    if screenshot is None:
        continue
    
    # Изменение размера изображения
    resized_frame = screenshot.resize((size, size), Image.ANTIALIAS)
    
    # Преобразование кадра в массив для отправки на бейдж
    flattened_frame = np.array(resized_frame).flatten().tolist()

    # Отправка кадра на бейдж
    response = send_frame_to_badge(flattened_frame)
    if response and response.status_code == 200:
        print("Frame sent successfully")
    else:
        if response:
            print(f"Failed to send frame: {response.status_code}")

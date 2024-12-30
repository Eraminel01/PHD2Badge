import cv2
import numpy as np
import requests
import time
from moviepy.editor import VideoFileClip
import pygame
import tempfile

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

pygame.init()
pygame.mixer.init()
video_path = 'bad_apple.mp4'
clip = VideoFileClip(video_path)

# Извлечение и сохранение аудио во временный файл
with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio_file:
    clip.audio.write_audiofile(temp_audio_file.name)
    audio_path = temp_audio_file.name

cap = cv2.VideoCapture(video_path)
size = 10  # размер дисплея 10x10
fps = cap.get(cv2.CAP_PROP_FPS)

# Создаем два окна: для оригинального видео и для пиксельной версии
cv2.namedWindow('Original Video', cv2.WINDOW_NORMAL)
cv2.namedWindow('Pixelated Video', cv2.WINDOW_NORMAL)

# Устанавливаем размеры окон
cv2.resizeWindow('Original Video', 400, 400)
cv2.resizeWindow('Pixelated Video', 400, 400)

# Воспроизведение аудио из видео
pygame.mixer.music.load(audio_path)
pygame.mixer.music.play()

start_time = time.time()
while cap.isOpened():
    elapsed_time = time.time() - start_time
    frame_idx = int(elapsed_time * fps)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ret, frame = cap.read()
    if not ret:
        break
    
    # Изменение размера кадра для дисплея бейджа
    resized_frame = cv2.resize(frame, (size, size))
    
    # Увеличиваем пиксельную версию обратно для лучшей видимости
    display_pixelated = cv2.resize(resized_frame, (400, 400), interpolation=cv2.INTER_NEAREST)
    
    # Масштабируем оригинальное видео до того же размера для согласованности
    display_original = cv2.resize(frame, (400, 400))
    
    # Преобразование кадра в массив значений для отправки
    flattened_frame = resized_frame.flatten().tolist()
    
    # Отправка кадра на дисплей
    response = send_frame_to_badge(flattened_frame)
    if response and response.status_code == 200:
        print("Frame sent successfully")
    else:
        if response:
            print(f"Failed to send frame: {response.status_code}")
    
    # Отображение обоих кадров в соответствующих окнах
    cv2.imshow('Original Video', display_original)
    cv2.imshow('Pixelated Video', display_pixelated)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()

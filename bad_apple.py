import cv2
import numpy as np
import requests
import time
from moviepy.editor import VideoFileClip
import pygame
import tempfile
import os

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

def render_frames(video_path, size):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    output_file = f"{os.path.splitext(os.path.basename(video_path))[0]}.txt"
    with open(output_file, "w") as f:
        for i in range(frame_count):
            ret, frame = cap.read()
            if not ret:
                break
            resized_frame = cv2.resize(frame, (size, size))
            flattened_frame = resized_frame.flatten().tolist()
            f.write(f"{flattened_frame}\n")
    cap.release()
    print(f"Frames rendered and saved in {output_file}")
    return output_file

def play_video_with_audio(video_path, audio_path, size):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Video', 400, 400)
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
        resized_frame = cv2.resize(frame, (size, size))
        flattened_frame = resized_frame.flatten().tolist()
        response = send_frame_to_badge(flattened_frame)
        if response and response.status_code == 200:
            print("Frame sent successfully")
        else:
            if response:
                print(f"Failed to send frame: {response.status_code}")
        cv2.imshow('Video', resized_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

def play_rendered_frames(rendered_file, audio_path, size, fps):
    with open(rendered_file, "r") as f:
        frames = [line.strip() for line in f]
    
    cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Video', 400, 400)
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
    for frame_data in frames:
        frame_list = eval(frame_data)
        frame_array = np.array(frame_list, dtype=np.uint8).reshape((size, size, 3))
        response = send_frame_to_badge(frame_list)
        if response and response.status_code == 200:
            print("Frame sent successfully")
        else:
            if response:
                print(f"Failed to send frame: {response.status_code}")
        cv2.imshow('Video', frame_array)
        if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()
    pygame.quit()

def main():
    video_path = input("Enter the path to the video file: ")
    size = 10
    mode = input("Choose mode: render (r) or live (l): ").strip().lower()
    
    pygame.init()
    pygame.mixer.init()

    clip = VideoFileClip(video_path)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio_file:
        clip.audio.write_audiofile(temp_audio_file.name)
        audio_path = temp_audio_file.name

    if mode == 'r':
        rendered_file = render_frames(video_path, size)
        play_rendered_frames(rendered_file, audio_path, size, clip.fps)
    elif mode == 'l':
        play_video_with_audio(video_path, audio_path, size)
    else:
        print("Invalid mode selected. Please choose 'r' for render or 'l' for live.")

if __name__ == "__main__":
    main()

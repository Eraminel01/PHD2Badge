import requests
import time
import numpy as np

def generate_gradient_frame(step, size=10, steps=200):
    gradient = []
    for i in range(size * size):
        angle = 2 * np.pi * (i % steps + step) / steps
        r = int((np.sin(angle) + 1) * 127.5)
        g = int((np.sin(angle + 2 * np.pi / 3) + 1) * 127.5)
        b = int((np.sin(angle + 4 * np.pi / 3) + 1) * 127.5)
        gradient.extend([r, g, b])
    return gradient

def send_gradient_to_badge(gradient, url='http://badge.phd2/api/v1/led/picture'):
    payload = {
        "values": gradient
    }
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to send data: {e}")
        response = None
    return response

# Получение входных данных от пользователя с возможностью пропуска
def get_input(prompt, default):
    user_input = input(prompt)
    if user_input == '':
        return default
    return type(default)(user_input)

# Ввод параметров пользователем
size = 10
steps = get_input("Enter the number of steps in the gradient (default 200): ", 200)
delay = get_input("Enter the delay between frames in seconds (default 0.01): ", 0.01)

# Генерация градиента и отправка его на бейдж циклически
while True:
    for step in range(steps):
        gradient = generate_gradient_frame(step, size, steps)
        response = send_gradient_to_badge(gradient)
        if response and response.status_code == 200:
            print(f"Frame {step} sent successfully")
        else:
            if response:
                print(f"Failed to send frame {step}: {response.status_code}")
        time.sleep(float(delay))  # задержка между отправками

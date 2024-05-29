import pygame
import requests
import numpy as np

# Функция для отправки кадра на бейдж
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

looser_values = [0,0,0,0,0,0,0,0,0,255,0,0,255,0,0,255,0,0,142,17,17,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,101,101,255,0,0,255,0,0,255,0,0,238,16,5,255,0,0,0,0,0,0,0,0,0,0,0,255,0,0,255,0,0,0,0,0,255,0,0,255,0,0,0,0,0,249,19,8,255,0,0,0,0,0,142,17,17,255,0,0,255,0,0,0,0,0,255,0,0,255,0,0,0,0,0,249,19,8,255,0,0,255,101,101,142,17,17,255,0,0,255,0,0,255,0,0,255,0,0,255,0,0,255,0,0,249,19,8,249,19,8,255,101,101,142,17,17,255,0,0,255,0,0,255,0,0,0,0,0,0,0,0,255,0,0,255,0,0,249,19,8,255,101,101,142,17,17,255,0,0,255,0,0,0,0,0,255,0,0,255,0,0,0,0,0,255,0,0,249,19,8,255,101,101,0,0,0,142,17,17,0,0,0,255,0,0,255,0,0,255,0,0,255,0,0,0,0,0,255,101,101,0,0,0,0,0,0,0,0,0,148,18,16,255,32,3,255,0,0,255,34,0,255,0,0,255,101,101,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,142,17,17,255,0,0,255,34,0,255,101,101,0,0,0,0,0,0,0,0,0]

pygame.init()

# Размер дисплея
size = 10
cell_size = 20

# Настройка окна Pygame
screen = pygame.display.set_mode((size * cell_size, size * cell_size))
pygame.display.set_caption("Snake to Badge")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Настройки игры
clock = pygame.time.Clock()
snake_pos = [5, 5]
snake_body = [[5, 5]]
snake_direction = 'UP'
change_to = snake_direction
speed = 10

# Позиция еды
food_pos = [np.random.randint(0, size), np.random.randint(0, size)]
food_spawn = True

# Основной игровой цикл
running = True
game_over = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake_direction != 'DOWN':
                change_to = 'UP'
            elif event.key == pygame.K_DOWN and snake_direction != 'UP':
                change_to = 'DOWN'
            elif event.key == pygame.K_LEFT and snake_direction != 'RIGHT':
                change_to = 'LEFT'
            elif event.key == pygame.K_RIGHT and snake_direction != 'LEFT':
                change_to = 'RIGHT'

    if not game_over:
        # Изменение направления змейки
        snake_direction = change_to

        # Обновление позиции змейки
        if snake_direction == 'UP':
            snake_pos[1] -= 1
        elif snake_direction == 'DOWN':
            snake_pos[1] += 1
        elif snake_direction == 'LEFT':
            snake_pos[0] -= 1
        elif snake_direction == 'RIGHT':
            snake_pos[0] += 1

        # Условия окончания игры
        if (snake_pos[0] < 0 or snake_pos[0] >= size or
                snake_pos[1] < 0 or snake_pos[1] >= size):
            game_over = True
        for block in snake_body[1:]:
            if snake_pos == block:
                game_over = True

        # Рост змейки
        snake_body.insert(0, list(snake_pos))
        if snake_pos == food_pos:
            food_spawn = False
        else:
            snake_body.pop()

        if not food_spawn:
            food_pos = [np.random.randint(0, size), np.random.randint(0, size)]
        food_spawn = True

        # Рендеринг игры
        screen.fill(BLACK)
        for pos in snake_body:
            pygame.draw.rect(screen, GREEN, pygame.Rect(
                pos[0] * cell_size, pos[1] * cell_size, cell_size, cell_size))
        pygame.draw.rect(screen, RED, pygame.Rect(
            food_pos[0] * cell_size, food_pos[1] * cell_size, cell_size, cell_size))

        pygame.display.flip()

        # Подготовка кадра для дисплея
        frame = np.zeros((size, size, 3), dtype=np.uint8)
        for pos in snake_body:
            if 0 <= pos[0] < size and 0 <= pos[1] < size:
                frame[pos[1], pos[0]] = [0, 255, 0]  # Зеленый цвет змейки
        if 0 <= food_pos[0] < size and 0 <= food_pos[1] < size:
            frame[food_pos[1], food_pos[0]] = [255, 0, 0]  # Красный цвет еды
        flattened_frame = frame.flatten().tolist()

        # Отправка картинки на бейдж
        response = send_frame_to_badge(flattened_frame)
        if response and response.status_code == 200:
            print("Frame sent successfully")
        else:
            if response:
                print(f"Failed to send frame: {response.status_code}")

    else:
        # Отображение надписи при проигрыше
        send_frame_to_badge(looser_values)
        running = False

    clock.tick(speed)

pygame.quit()

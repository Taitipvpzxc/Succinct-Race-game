import pygame
import random
import math

pygame.init()

WIDTH = 800
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Succinct Race")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

font = pygame.font.SysFont(None, 36)
large_font = pygame.font.SysFont(None, 48)

# Загрузка изображения машины
car_image = pygame.image.load("car_image.png").convert_alpha()
car_image = pygame.transform.scale(car_image, (40, 60))

# Загрузка изображения препятствия (машинки)
mascot_image = pygame.image.load("5.png").convert_alpha()
mascot_image = pygame.transform.scale(mascot_image, (40, 60))

player_car = pygame.Rect(WIDTH // 2 - 20, HEIGHT * 3 // 4 - 30, 40, 60)  # Фиксированная позиция
player_speed_x = 0
player_speed_y = 0
max_speed_x = 5
max_speed_y = 3
drifting = False
drift_angle = 0

track_width = 300  # Увеличиваем ширину дороги
track_speed = 2  # Начальная скорость меньше
road_offset = 0  # Смещение дороги для прокрутки

# Множитель скорости
speed_multiplier = 1.0

mascots = []
mascot_speed = 5
mascot_spawn_timer = 0
mascot_spawn_interval = 60

# Розовые крабы вместо деревьев
crabs = []
for i in range(10):
    crabs.append(pygame.Rect(50, random.randint(-HEIGHT, 0), 20, 30))  # Левый край
    crabs.append(pygame.Rect(WIDTH - 70, random.randint(-HEIGHT, 0), 20, 30))  # Правый край

game_over = False
score = 0
game_started = False

# Тряска экрана
shake_timer = 0
shake_offset_x = 0
shake_offset_y = 0

# Тахометр
tachometer_value = 0

funny_comments = [
    "My crypto's faster than my car… but still stuck in traffic",
    "Leading the race, but my wallet’s still in the pit stop.",
    "Outrunning the crash… but not the meme coins!",
    "I race, crypto crashes, I coast!"
]
comment = ""
comment_timer = 0

def draw_start_screen():
    window.fill(BLACK)
    title = large_font.render("Succinct race!", True, WHITE)
    window.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
    controls = [
        "Controls:",
        "W / Up Arrow - Speed up",
        "S / Down Arrow - Speed down",
        "A / Left Arrow - Move Left",
        "D / Right Arrow - Move Right",
        "R - Restart after crash",
    ]
    for i, line in enumerate(controls):
        text = font.render(line, True, WHITE)
        window.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 40))
    start_button = pygame.Rect(WIDTH // 2 - 100, 450, 200, 50)
    pygame.draw.rect(window, GREEN, start_button)
    start_text = font.render("Start Game", True, BLACK)
    window.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 465))
    return start_button

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                player_car.x = WIDTH // 2 - 20
                player_car.y = HEIGHT * 3 // 4 - 30
                player_speed_x = 0
                player_speed_y = 0
                mascots = []
                game_over = False
                score = 0
                comment = ""
                road_offset = 0
                speed_multiplier = 1.0
                track_speed = 2  # Сбрасываем скорость при рестарте
                shake_timer = 0
                tachometer_value = 0
            elif event.key == pygame.K_SPACE and game_started and not game_over:
                drifting = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                drifting = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_started:
            if start_button.collidepoint(event.pos):
                game_started = True

    if not game_started:
        start_button = draw_start_screen()
        pygame.display.flip()
        continue

    keys = pygame.key.get_pressed()
    if not game_over:
        # Более отзывчивое управление
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_speed_x = -max_speed_x
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_speed_x = max_speed_x
        else:
            player_speed_x *= 0.9

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_speed_y = -max_speed_y
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_speed_y = max_speed_y
        else:
            player_speed_y *= 0.9

        # Управление скоростью
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            track_speed += 0.02  # Уменьшаем ускорение
            if track_speed > 10:
                track_speed = 10
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            track_speed -= 0.02  # Уменьшаем замедление
            if track_speed < 2:
                track_speed = 2
        else:
            track_speed -= 0.01  # Уменьшаем снижение скорости
            if track_speed < 2:
                track_speed = 2

        # Обновляем множитель скорости на основе текущей скорости
        speed_multiplier = track_speed / 5

        # Управление тахометром
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            tachometer_value += 0.5
            if tachometer_value > 13:
                tachometer_value = 13
        else:
            tachometer_value -= 0.3
            if tachometer_value < 0:
                tachometer_value = 0

        # Дрифт
        if drifting:
            drift_angle = player_speed_x * 5
            player_speed_x *= 0.95
        else:
            drift_angle *= 0.9

        # Двигаем дорогу и препятствия вместо машинки
        road_offset += track_speed

        # Ограничиваем машинку в пределах дороги
        track_center_x = WIDTH // 2
        track_left = track_center_x - track_width // 2
        track_right = track_center_x + track_width // 2 - player_car.width
        player_car.x += player_speed_x
        if player_car.x < track_left:
            player_car.x = track_left
            player_speed_x = 0
        if player_car.x > track_right:
            player_car.x = track_right
            player_speed_x = 0

        # Двигаем крабов
        for crab in crabs:
            crab.y += track_speed
            if crab.y > HEIGHT:
                crab.y = -crab.height
                crab.x = 50 if crab.x < WIDTH // 2 else WIDTH - 70

        # Спавн препятствий
        mascot_spawn_timer += 1
        if mascot_spawn_timer >= mascot_spawn_interval:
            mascot_x = random.randint(int(track_center_x - track_width // 2), int(track_center_x + track_width // 2 - 40))
            mascots.append(pygame.Rect(mascot_x, -60, 40, 60))
            mascot_spawn_timer = 0

        # Двигаем препятствия
        for mascot in mascots[:]:
            mascot.y += (mascot_speed + track_speed) * speed_multiplier
            if mascot.y > HEIGHT:
                mascots.remove(mascot)

        # Проверка столкновений
        for mascot in mascots:
            if player_car.colliderect(mascot):
                game_over = True
                comment = "Crashed into a car! Press R to restart."
                shake_timer = 30
        # Случайный комментарий
        if random.random() < 0.01 and not comment:
            comment = random.choice(funny_comments)
            comment_timer = 120

        score += int(1 * speed_multiplier)  # Увеличиваем очки с учетом множителя скорости

    # Тряска экрана
    if shake_timer > 0:
        shake_offset_x = random.randint(-5, 5)
        shake_offset_y = random.randint(-5, 5)
        shake_timer -= 1
    else:
        shake_offset_x = 0
        shake_offset_y = 0

    # Рисуем фон
    window.fill((255, 182, 193))  # Светло-розовый фон
    for _ in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        pygame.draw.circle(window, WHITE, (x, y), 2)

    # Рисуем дорогу
    track_left = WIDTH // 2 - track_width // 2
    track_right = WIDTH // 2 + track_width // 2
    pygame.draw.rect(window, GRAY, (track_left + shake_offset_x, 0 + shake_offset_y, track_width, HEIGHT))  # Дорога

    # Рисуем центральную линию
    for y in range(-50, HEIGHT, 50):
        y_pos = (y + road_offset) % (HEIGHT + 50) - 50
        pygame.draw.line(window, WHITE, (WIDTH // 2 + shake_offset_x, y_pos + shake_offset_y), (WIDTH // 2 + shake_offset_x, y_pos + 30 + shake_offset_y), 5)

    # Рисуем бортики
    barrier_width = 20
    for y in range(-50, HEIGHT, 50):
        y_pos = (y + road_offset) % (HEIGHT + 50) - 50
        color = RED if (y // 50) % 2 == 0 else WHITE
        pygame.draw.rect(window, color, (track_left - barrier_width + shake_offset_x, y_pos + shake_offset_y, barrier_width, 50))  # Левый бортик
        pygame.draw.rect(window, color, (track_right + shake_offset_x, y_pos + shake_offset_y, barrier_width, 50))  # Правый бортик

    # Рисуем розовых крабов
    for crab in crabs:
        # Тело краба (овал)
        pygame.draw.ellipse(window, (255, 105, 180), (crab.x + shake_offset_x, crab.y + shake_offset_y, crab.width, crab.height))
        
        # Клешни (более выразительные)
        pygame.draw.polygon(window, (255, 105, 180), [
            (crab.x + shake_offset_x, crab.y + 5 + shake_offset_y),
            (crab.x - 15 + shake_offset_x, crab.y - 5 + shake_offset_y),
            (crab.x - 10 + shake_offset_x, crab.y + 5 + shake_offset_y),
            (crab.x - 15 + shake_offset_x, crab.y + 15 + shake_offset_y)
        ])
        pygame.draw.polygon(window, (255, 105, 180), [
            (crab.x + crab.width + shake_offset_x, crab.y + 5 + shake_offset_y),
            (crab.x + crab.width + 15 + shake_offset_x, crab.y - 5 + shake_offset_y),
            (crab.x + crab.width + 10 + shake_offset_x, crab.y + 5 + shake_offset_y),
            (crab.x + crab.width + 15 + shake_offset_x, crab.y + 15 + shake_offset_y)
        ])
        
        # Глаза (два маленьких круга)
        pygame.draw.circle(window, BLACK, (crab.x + 5 + shake_offset_x, crab.y + 5 + shake_offset_y), 3)
        pygame.draw.circle(window, BLACK, (crab.x + crab.width - 5 + shake_offset_x, crab.y + 5 + shake_offset_y), 3)
        
        # Ноги (4 линии с каждой стороны)
        for i in range(4):
            leg_x = crab.x + (i * 5)
            pygame.draw.line(window, (255, 105, 180), (leg_x + shake_offset_x, crab.y + crab.height + shake_offset_y), (leg_x - 5 + shake_offset_x, crab.y + crab.height + 10 + shake_offset_y), 2)
            pygame.draw.line(window, (255, 105, 180), (leg_x + crab.width - (i * 5) + shake_offset_x, crab.y + crab.height + shake_offset_y), (leg_x + crab.width - (i * 5) + 5 + shake_offset_x, crab.y + crab.height + 10 + shake_offset_y), 2)

    # Рисуем препятствия
    for mascot in mascots:
        mascot_rect = mascot_image.get_rect(center=(mascot.centerx + shake_offset_x, mascot.centery + shake_offset_y))
        window.blit(mascot_image, mascot_rect)

    # Рисуем машинку
    car_surface = pygame.transform.rotate(car_image, drift_angle)
    car_rect = car_surface.get_rect(center=(player_car.centerx + shake_offset_x, player_car.centery + shake_offset_y))
    window.blit(car_surface, car_rect)

    # Рисуем HUD
    score_text = font.render(f"Score: {score}", True, WHITE)
    window.blit(score_text, (10 + shake_offset_x, 50 + shake_offset_y))

    # Рисуем тахометр
    tachometer_center = (WIDTH - 100 + shake_offset_x, 100 + shake_offset_y)
    pygame.draw.circle(window, BLACK, tachometer_center, 50, 2)

    # Зоны тахометра
    pygame.draw.arc(window, GREEN, (tachometer_center[0] - 50, tachometer_center[1] - 50, 100, 100), math.radians(135), math.radians(180), 10)  # Зеленая зона
    pygame.draw.arc(window, YELLOW, (tachometer_center[0] - 50, tachometer_center[1] - 50, 100, 100), math.radians(180), math.radians(225), 10)  # Желтая зона
    pygame.draw.arc(window, RED, (tachometer_center[0] - 50, tachometer_center[1] - 50, 100, 100), math.radians(225), math.radians(270), 10)  # Красная зона

    # Стрелка тахометра
    angle = math.radians(135 + (tachometer_value / 13) * 135)
    arrow_length = 40
    arrow_end_x = tachometer_center[0] + math.cos(angle) * arrow_length
    arrow_end_y = tachometer_center[1] - math.sin(angle) * arrow_length
    pygame.draw.line(window, BLACK, tachometer_center, (arrow_end_x, arrow_end_y), 3)

    if comment:
        comment_text = font.render(comment, True, WHITE)
        window.blit(comment_text, (10 + shake_offset_x, HEIGHT - 40 + shake_offset_y))
        comment_timer -= 1
        if comment_timer <= 0:
            comment = ""

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

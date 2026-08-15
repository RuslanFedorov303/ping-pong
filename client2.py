from pygame import *
import socket
import json
from threading import Thread

# ---ПУГАМЕ НАЛАШТУВАННЯ ---
WIDTH, HEIGHT = 800, 600
init()
mixer.init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")

# ---СЕРВЕР ---
def connect_to_server():
    while True:
        try: #'4.tcp.eu.ngrok.io', 25536
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080)) # ---- Підключення до сервера
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass


def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            game_state["winner"] = -1
            break

# --- ШРИФТИ ---
font_win = font.Font(None, 72)
font_main = font.Font(None, 36)
# --- ЗОБРАЖЕННЯ ----
fon_game = transform.scale(image.load('images/ChatGPT Image 1 серп. 2026 р., 16_40_15.png'), (WIDTH, HEIGHT))
fon_win  = transform.scale(image.load('images/images.jfif'), (WIDTH, HEIGHT))
fon_lose = transform.scale(image.load('images/images (1).jfif'), (WIDTH, HEIGHT))
fon_load = transform.scale(image.load('images/ChatGPT Image 1 серп. 2026 р., 16_40_25.png'), (WIDTH, HEIGHT))
bullet_image = transform.scale(image.load('images/ТРАМП_КРУГ.png'), (20, 20))

# --- ЗВУКИ ---
mixer.music.load('music/hurryup.wav')
mixer.music.play(-1)

ball_touch = mixer.Sound('music/FX01.wav')
win = mixer.Sound('music/Coin01.wav')

# --- ГРА ---
game_over = False
winner = None
you_winner = None
my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive, daemon=True).start()
while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

    if "countdown" in game_state and game_state["countdown"] > 0:
        screen.fill((0, 0, 0))
        countdown_text = font.Font(None, 72).render(str(game_state["countdown"]), True, (255, 255, 255))
        screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
        display.update()
        continue  # Не малюємо гру до завершення відліку

    if "winner" in game_state and game_state["winner"] is not None:
        screen.fill((20, 20, 20))

        if you_winner is None:  # Встановлюємо тільки один раз
            if game_state["winner"] == my_id:
                you_winner = True

            else:
                you_winner = False


        if you_winner:
            screen.blit(fon_win, (0, 0))
            text = ""
        else:
            screen.blit(fon_lose, (0, 0))
            text = ""

        win_text = font_win.render(text, True, (255, 215, 0))
        text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_text, text_rect)

        text = font_win.render('К - рестарт', True, (255, 215, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        screen.blit(text, text_rect)

        win.play()

        display.update()
        continue  # Блокує гру після перемоги

    if game_state:
        # screen.fill((30, 30, 30))
        screen.blit(fon_game, (0, 0))
        draw.rect(screen, (0, 255, 0), (20, game_state['paddles']['0'], 20, 100))
        draw.rect(screen, (255, 0, 255), (WIDTH - 40, game_state['paddles']['1'], 20, 100))
        draw.circle(screen, (255, 255, 255), (game_state['ball']['x'], game_state['ball']['y']), 10)
        screen.blit(bullet_image, (game_state['ball']['x'], game_state['ball']['y']))
        score_text = font_main.render(f"{game_state['scores'][0]} : {game_state['scores'][1]}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH // 2 -25, 20))

        if game_state['sound_event']:
            if game_state['sound_event'] == 'platform_hit':
                ball_touch.play()

    else:
        wating_text = font_main.render(f"Очікування гравців...", True, (255, 255, 255))
        screen.blit(fon_load, (0, 0))
        screen.blit(wating_text, (WIDTH // 2 - 25, 20))

    display.update()
    clock.tick(60)

    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")

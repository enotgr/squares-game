import pygame
import socket
from pygame.locals import *
import threading

pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

class Player():
  def __init__(self, x, y, color):
    self.x = x
    self.y = y
    self.color = pygame.Color(color)
    self.rect = pygame.Rect(x, y, 50, 50)

  def move(self, dx, dy):
    self.rect.x += dx
    self.rect.y += dy

  def draw(self, surface):
    pygame.draw.rect(surface, self.color, self.rect)

def handle_server_messages(s, other_player):
  buffer = ""
  while True:
    try:
      data = s.recv(2048).decode("utf-8")
      if data:
        buffer += data
        while '\n' in buffer:
          message, buffer = buffer.split('\n', 1)
          dx, dy = map(int, message.split(","))
          print('dx:', dx, 'dy:', dy)
          other_player.move(dx, dy)
    except socket.error as e:
      print(e)
      break

def main():
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(("YOUR SERVER IP ADDRESS", 5555))

  color = s.recv(2048).decode("utf-8")
  player = Player(width // 2, height // 2, color)
  other_color = "red" if color == "blue" else "blue"
  other_player = Player(width // 2, height // 2, other_color)

  # Создаем и запускаем поток для получения сообщений от сервера
  t = threading.Thread(target=handle_server_messages, args=(s, other_player))
  t.daemon = True
  t.start()

  running = True

  while running:
    clock.tick(60)
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
      if event.type == QUIT:
        running = False
        pygame.quit()
        break

    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[K_UP]:
      dy = -5
    if keys[K_DOWN]:
      dy = 5
    if keys[K_LEFT]:
      dx = -5
    if keys[K_RIGHT]:
      dx = 5

    if dx != 0 or dy != 0:
      try:
        s.sendall(f"{dx},{dy}\n".encode("utf-8"))
        player.move(dx, dy)
        pygame.time.delay(20)
      except socket.error as e:
        print(e)
        running = False
        break

    player.draw(screen)
    other_player.draw(screen)
    pygame.display.flip()

if __name__ == "__main__":
  main()

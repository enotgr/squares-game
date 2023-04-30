import socket
from _thread import start_new_thread

server = '0.0.0.0'
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
  s.bind((server, port))
except socket.error as e:
  print(e)

s.listen(2)
print('Waiting for connections...')

colors = ['red', 'blue']
players = []

def threaded_client(conn, player):
  conn.send(str.encode(colors[player]))
  buffer = '' # Буфер для хранения частичных сообщений
  while True:
    try:
      data = conn.recv(2048).decode('utf-8')
      if not data:
        break

      # Обрабатываем сообщения с учетом разделителя
      buffer += data
      while '\n' in buffer:
        message, buffer = buffer.split('\n', 1)

        # Проверяем формат данных перед отправкой
        try:
          dx, dy = map(int, message.split(','))
          print('dx:', dx, 'dy:', dy)
        except ValueError as e:
          print('Invalid data format:', message)
          continue

        data_to_send = f'{dx},{dy}\n'.encode('utf-8')
        if player == 0:
          if players[1] is not None:
            players[1].sendall(data_to_send)
        else:
          if players[0] is not None:
            players[0].sendall(data_to_send)

    except socket.error as e:
      print(e)
      break

  players[player] = None
  conn.close()

current_player = 0
while True:
  conn, addr = s.accept()
  print('Connected to:', addr)
  players.append(conn)
  start_new_thread(threaded_client, (conn, current_player))
  current_player = 1 - current_player

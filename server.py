import sys
import socket
import selectors
import json


players = {}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sel = selectors.DefaultSelector()

host = "localhost"
messages_size = 1024
port = int(sys.argv[1])

def receiveMessage(client):
   message_received = json.loads(client.recv(messages_size)
                                       .decode("UTF-8"))
   return message_received

def sendMessage(client, message_to_send):
   message_to_send = json.dumps(message_to_send)\
                         .encode("UTF-8")
   client.send(message_to_send)

def accept(sock, mask):
   client, client_address = sock.accept()
   client.setblocking(False)
   sel.register(client, selectors.EVENT_READ, initialize)

def initialize(client, mask):
   message_received = receiveMessage(client)
   player_name = message_received["name"]
   action = message_received["action"]
   position = message_received["position"]

   all_registered_players_names = list(players.keys())

   if action == "register":

      invert_movement_ball = False
      if len(all_registered_players_names):
         invert_movement_ball = True

      if player_name not in all_registered_players_names:
         players[player_name] = {"id": client,
                                 "position": position}
         sendMessage(client, [True, invert_movement_ball])
      else:
         sendMessage(client, [False, invert_movement_ball])
   elif action == "update_position":
      if len(all_registered_players_names) > 1:
         players[player_name]["position"] = position
   elif action == "receive_position":
      if len(all_registered_players_names) > 1:
         player_index = all_registered_players_names.index(player_name)
         opponent_name = all_registered_players_names[(player_index + 1) % 2]
         sendMessage(players[opponent_name]["id"], players[player_name]["position"])




sock.bind((host, port))
sock.listen(2)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

while True:
   events = sel.select()
   for key, mask in events:
      callback = key.data
      callback(key.fileobj, mask)

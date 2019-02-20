# Pong
Simple implementation of legendary game Pong

## Description
 - Game created using sockets, selectors and pygame.
 - To play it, you must run, at first, the code in 
 _server.py_ . Then, you have to run the code in _player.py_ 
 two times, to start the game for two players.
 - My idea is to use a raspberry to run the server code connected 
 to my private home network, but for that this solution must work correctly
  
## Run the server and the players (linux)
 - Server: _$ python3 server.py 2000_ 
 - Players: _$ python3 player.py 2000_ 
 (where 2000 is the port of localhost, you can put other if you want to)
 
## Problems to be resolved
 - The game is very slow when the user position is changed
 - Problems with the clock 
 - No errors handling
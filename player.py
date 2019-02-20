import sys
import socket
import json
import pygame

# Constants
WIDTH = 900
HEIGHT = 500
CLOCK_TIME = 60

BACKGROUND_COLOR = (0, 0, 0)

BALL_RAD = 10
BALL_COLOR = (255, 255, 255)
BALL_INITIAL_VEL = 300

GOAL_DIMENSIONS = (10, 100)
GOAL_COLOR = (255, 255, 255)
GOAL_INITIAL_Y_POSITION = HEIGHT//2 - GOAL_DIMENSIONS[1]//2
GOAL_MOV = 300


# initialize socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "localhost"
messages_size = 1024
port = int(sys.argv[1])


# classes
class Ball(pygame.sprite.Sprite):
   def __init__(self):
      pygame.sprite.Sprite.__init__(self)

      # create image
      self.image = pygame.Surface([BALL_RAD*2,
                                   BALL_RAD*2])

      position = (BALL_RAD,
                  BALL_RAD)
      pygame.draw.circle(self.image, BALL_COLOR, position, BALL_RAD, BALL_RAD)

      self.rect = self.image.get_rect()

      # physics
      self.rect.centerx, self.rect.centery = WIDTH//2 + BALL_RAD, HEIGHT//2 + BALL_RAD
      self.acceleration = [0]*2
      self.velocity = [BALL_INITIAL_VEL]*2

   def checkCollision(self, g):
      col = pygame.sprite.collide_rect(self, g)
      if col:
         self.velocity[0] = -self.velocity[0]
         self.velocity[1] = -self.velocity[1]

   def touchBorders(self):
      if self.rect.centerx <= BALL_RAD or (self.rect.centerx + BALL_RAD) >= WIDTH:
         self.velocity[0] = -self.velocity[0]
      if self.rect.centery <= BALL_RAD or (self.rect.centery + BALL_RAD) >= HEIGHT:
         self.velocity[1] = -self.velocity[1]

   def updatePosition(self):
      applied_vel = [x/CLOCK_TIME for x in self.velocity]
      self.rect.centerx += applied_vel[0]
      self.rect.centery += applied_vel[1]

   def draw(self, surface):
      self.touchBorders()
      self.updatePosition()

      surface.blit(self.image, (self.rect.x, self.rect.y))


class Goal(pygame.sprite.Sprite):
   def __init__(self, x_position, this_player, my_name):
      pygame.sprite.Sprite.__init__(self)
      self.x_position = x_position
      self.this_player = this_player
      self.my_name = my_name

      # create image
      self.image = pygame.Surface(list(GOAL_DIMENSIONS))

      pygame.draw.rect(self.image, GOAL_COLOR, (0, 0, GOAL_DIMENSIONS[0], GOAL_DIMENSIONS[1]))

      self.rect = self.image.get_rect()

      # physics
      self.rect.y = GOAL_INITIAL_Y_POSITION
      self.rect.x = self.x_position
      self.velocity = 0


   def touchBorders(self):
      if self.rect.y < 0:
         self.rect.y = 0
      if (self.rect.y + GOAL_DIMENSIONS[1]) > HEIGHT:
         self.rect.y = HEIGHT - GOAL_DIMENSIONS[1]

   def move(self):
      if self.this_player:
         key = pygame.key.get_pressed()
         send_message = False
         if key[pygame.K_DOWN]:
            self.rect.y += GOAL_MOV/CLOCK_TIME
            send_message = True
         elif key[pygame.K_UP]:
            self.rect.y -= GOAL_MOV/CLOCK_TIME
            send_message = True

         # send position
         if send_message:
            sendMessage(sock, self.my_name, "update_position", self.rect.y)
      else:
         sendMessage(sock, self.my_name, "receive_position", 0)
         self.rect.y = receiveMessage(sock)

   def draw(self, surface):
      surface.blit(self.image, (self.x_position, self.rect.y))



def receiveMessage(sock):
   message_received = json.loads(sock.recv(messages_size).decode("UTF-8"))
   return message_received

def sendMessage(sock, name, action, position):
   message_to_send = {"name": name,
                      "action": action,
                      "position": position}
   message_to_send = json.dumps(message_to_send).encode("UTF-8")
   sock.send(message_to_send)


# Initialize game with name request
def register():
   sock.connect((host, port))

   request_name = True
   while request_name:
      name = input("\n\n\nName?\n"
                   "> ")
      sendMessage(sock, name, "register", GOAL_INITIAL_Y_POSITION)

      message_received = receiveMessage(sock)
      request_name = not message_received[0]
      invert_mov_ball = message_received[1]

      if invert_mov_ball:
         global BALL_INITIAL_VEL
         BALL_INITIAL_VEL = -BALL_INITIAL_VEL

   return name




# register this client
my_name = register()

# Initialize pygame
pygame.init()
font = pygame.font.SysFont("couriernew", 72)
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Initialize objects
ball = Ball()
goal1 = Goal(100, True, my_name)
goal2 = Goal(WIDTH - 100, False, my_name)

# Initialize draw loop
running = True
while running:
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         pygame.quit()
         running = False

   screen.fill(BACKGROUND_COLOR)

   goal1.touchBorders()
   goal1.draw(screen)
   goal1.move()

   goal2.touchBorders()
   goal2.draw(screen)
   goal2.move()

   ball.draw(screen)
   ball.checkCollision(goal1)
   ball.checkCollision(goal2)



   pygame.display.update()
   clock.tick(CLOCK_TIME)

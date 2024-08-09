import pygame, sys,random
from pygame.locals import *

#####################
# Variables 101
####################
bg = "bg.jpg"
pl = "player.gif"
bl = "shot.gif"
bm = "bomb.gif"
em = "enemy.gif"
ex = "explosion1.gif"
VIEWPORT = Rect(0,0,1024,768)
CLOCK = pygame.time.Clock()
MAX_BULLETS = 5
SPAWNLOAD = 100   #frames between new enemies
LIVES = 2
SCORE = 0

###################
#Helper Functions
###################

'This function loads a single images'
def LoadImage(file):
    try:
        surface = pygame.image.load(file).convert_alpha()
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file,pygame.get_error()))
    return surface

'Powerful way to load multiple images with on call'
def LoadImages(*files):
    img = []
    for file in files:
        img.append(LoadImage(file))
    return img

'Load Sound'
class dummysound:
    def play(self):pass

def Load_Sound(file):
    if not pygame.mixer:
        return dummysound()
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print('Warning, no sound %s'%file)
    return dummysound()

###########################################
#Builds the screen or window
#param 1: window width and height
#param 2: a flag set 0
#param 3: the bits
#############################################
screen = pygame.display.set_mode((1024,1768),0,32)

##########################
#Load Images
#########################
background = LoadImage(bg)
mouse_c = LoadImage(bl)



##################################
#
#GAME OBJECTS
##################################

#Player
class Player(pygame.sprite.Sprite):
    speed = 10
    bounce = 24
    gun_offset = -11
    images = []
    life = 2
    def __init__(self):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image = self.image
        self.rect = self.image.get_rect(midbottom = VIEWPORT.midbottom)
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1

    def move(self,direction):
        if direction:
            self.facing = direction

        #Move the rectangle in place(where to move,no offset)
        self.rect.move_ip(direction*self.speed,0)
        self.rect = self.rect.clamp(VIEWPORT)       

        self.rect.top = self.origtop - (self.rect.left//self.bounce%2)

    def gunpos(self):
        pos = self.facing * self.gun_offset + self.rect.centerx
        return pos, self.rect.top

'The Enemy Plane'
class Enemy(pygame.sprite.Sprite):
    speed = 13

    def __init__(self):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image = self.image
        self.rect = self.image.get_rect()
        self.facing = 1

    def update(self):
        self.rect.move_ip(self.facing,0)
        if not VIEWPORT.contains(self.rect):
            self.facing = -self.facing
            self.rect.top = self.rect.bottom +1
            self.rect = self.rect.clamp(VIEWPORT)
            
'bullet'
class Bullet(pygame.sprite.Sprite):
    speed = -11

    def __init__(self,pos):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image = self.image
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self):
        self.rect.move_ip(0,self.speed)
        if self.rect.top < 0:
            self.kill()

'enemy bullets'
class Bomb(pygame.sprite.Sprite):
    speed = 9
    def __init__(self,enemy):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image = self.image
        self.rect = self.image.get_rect(midbottom = enemy.rect.move(0,5).midbottom)

    def update(self):
        self.rect.move_ip(0,self.speed)
        if self.rect.bottom  >= 768:
            self.kill()

'kaboom'
class Explosion(pygame.sprite.Sprite):
    elife = 12
    animcycle = 3
    images = []
    def __init__(self,actor):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.elife

    def update(self):
        self.life = self.life - 1
        #(//) Floor Division 
        self.image = self.images[self.life//self.animcycle%2]
        if self.life <= 0:
            self.kill()


    


###########################
#Main Loop & INIT
###########################
pygame.init()

#Set Image to objects
Player.image = LoadImage(pl)
Enemy.image = LoadImage(em)
Bullet.image = LoadImage(bl)
Bomb.image = LoadImage(bm)
temp = LoadImage(ex)
Explosion.images = [temp,pygame.transform.flip(temp,1,1)]
#Initialize Object / game groups
ememies = pygame.sprite.Group()
bullet = pygame.sprite.Group()
bombs = pygame.sprite.Group()
all = pygame.sprite.RenderUpdates()
#The GroupSingle container only holds a single Sprite. When a new Sprite is added, the old one is removed. 
lastspawn = pygame.sprite.GroupSingle()

#assign default groups to each sprite class
Player.containers = all
Enemy.containers = ememies, all, lastspawn
Bullet.containers = bullet,all
Bomb.containers = bombs,all
Explosion.containers = all

#Initialize our starting sprites
player = Player()
Enemy()

#######################
#Create Background
bgd = LoadImage(bg)
screen.blit(bgd,(0,0))
# update the full display Surface to the screen(flip)
pygame.display.flip()

##########################
# Load sound
boom_sound = Load_Sound('boom.wav')
shoot_sound = Load_Sound('car_door.wav')

if pygame.mixer:
    pygame.mixer.music.load('house_lo.wav')
    pygame.mixer.music.play(-1)




while True:

    #shut down event
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()

    #Update key press events
    keystate = pygame.key.get_pressed()

    ###################
    #spawn enemies
    ###################
    if SPAWNLOAD:
        SPAWNLOAD = SPAWNLOAD - 1
    elif not int(random.random() * 22):
        Enemy()
        SPAWNLOAD = 100

    #enemy attack, chance onit attacking
    if lastspawn and not int(random.random()* 60):
        Bomb(lastspawn.sprite)


    

    ############################
    # UPDATE & Clear
    #############################
    all.clear(screen,bgd)

    all.update()



#gives us a x and y var to position the mouse
    #x,y = pygame.mouse.get_pos()
   # x -= mouse_c.get_width()/2
   # y -= mouse_c.get_height()/2

#Player Movement    
    direction = keystate[K_RIGHT] - keystate[K_LEFT]
    firing = keystate[K_SPACE]
   
    if not player.reloading and firing and len(bullet) < MAX_BULLETS:
        shoot_sound.play()
        Bullet(player.gunpos())
    player.reloading = firing

    
        

    #screen.blit(mouse_c,(x,y))
    player.move(direction)




    ###############
    #Collsion Update
    ################

    'bullet & enemy'
    for enemy in pygame.sprite.groupcollide(bullet,ememies,1,1).keys():
          Explosion(enemy)
          boom_sound.play()
          SCORE = SCORE +1

    'bomb with player'
    for bomb in pygame.sprite.spritecollide(player,bombs,1):
        Explosion(bomb)
        boom_sound.play()
        player.life -= 1

    if player.life == 0:
        player.kill()

 
    

    ########################
    #RENDER ALL
    ########################
    dirty = all.draw(screen)
    pygame.display.update(dirty)

    #Cap the framerate
    CLOCK.tick(60)

#! /usr/bin/env python


#Import
import os, sys, pygame, random, numpy 
from pygame.locals import *
os.environ['SDL_VIDEO_CENTERED'] = "1"
pygame.init()
pygame.display.set_caption("Space Ranger")
icon = pygame.image.load("Space Ranger.png")
icon = pygame.display.set_icon(icon)
screen = pygame.display.set_mode((800, 600))
pygame.mouse.set_visible(0)
FPS = 120

#Background
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0,0,0))
    
#Music
music = pygame.mixer.music.load ("data/sounds/music.mp3") 
pygame.mixer.music.play(-1)


#Load Images
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error.message:
        print ('Cannot load image:'), fullname
        raise SystemExit
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

#Load Sounds
def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print ('Cannot load sound:'), fullname
        raise SystemExit
    return sound

#Sprites

#This class controls the arena background
class Arena(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("menu/bg1.png", -1)
        self.reset()
        self.dy = 1
    def update(self):
        self.rect.bottom += self.dy
        if self.rect.bottom >= 600:
            self.reset() 
    
    def reset(self):
        self.rect.top = -600
        

#Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/player.png", -1)
        self.rect.center = (400,500)
        self.dx = 0
        self.dy = 0
        self.reset()
        self.lasertimer = 1
        self.lasermax = 4
        self.bombamount = 2
        self.bombtimer = 0
        self.bombmax = 10
        
    def update(self):
        self.rect.move_ip((self.dx, self.dy))
        
        #Fire the laser
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            self.lasertimer = self.lasertimer + 1
            if self.lasertimer == self.lasermax:
                laserSprites.add(Laser(self.rect.midtop))
                fire.play()
                self.lasertimer = 0
                 
        #Fire the bomb          
        if key[pygame.K_LCTRL]:
            self.bombtimer = self.bombtimer + 1
            if  self.bombtimer == self.bombmax:
                self.bombtimer = 0
                if self.bombamount > 0:
                    self.bombamount = self.bombamount -1
                    score.bomb += -1
                    bombSprites.add(Bomb(self.rect.midtop))
                    blaster.play()
                    
                                
        #Player Boundaries    
        if self.rect.left < 0:
          self.rect.left = 0
        elif self.rect.right > 800:
          self.rect.right = 800
         
        if self.rect.top <= 160:
          self.rect.top = 160
        elif self.rect.bottom >= 600:
          self.rect.bottom = 600
         
          
        
    def reset(self):
        self.rect.bottom = 600  




#Laser class
class Laser(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/laser.png", -1)
        self.rect.center = pos

    
    def update(self):
        if self.rect.top < 0:
            self.kill()
        else:    
            self.rect.move_ip(0, -15)  
                

#Bomb class
class Bomb(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/bomb.png", -1)
        self.rect.center = pos
    
    def update(self):
        if self.rect.top < 0:
            self.kill()
        else:    
            self.rect.move_ip(0, -5)
        if pygame.sprite.groupcollide(enemySprites, bombSprites, 1, 1):
               bombExplosionSprites.add(BombExplosion(self.rect.center))
               explode.play()

#Laser class
class EnemyLaser(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/elaser.png", -1)
        self.rect.center = pos

    
    def update(self):
        if self.rect.bottom < 0:
            self.kill()
        else:    
            self.rect.move_ip(0, 15) 
   
class bossLaser(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/blaser.png", -1)
        self.rect.center = pos

    
    def update(self):
        if self.rect.bottom < 0:
            self.kill()
        else:    
            self.rect.move_ip(0, 15)
    
        
#Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, centerx):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/enemy.png", -1)
        self.rect = self.image.get_rect()
        self.dy = 8
        self.reset()
        
    def update(self):
        self.rect.centerx += self.dx
        self.rect.centery += self.dy
        if self.rect.top > screen.get_height():
            self.reset() 
           
        #random 1 - 60 determines if firing
        efire = random.randint(1,30)
        if efire == 1:
            enemyLaserSprites.add(EnemyLaser(self.rect.midbottom))
            efire = load_sound("sounds/elaser.ogg")
            efire.play()
            
        #Laser Collisions    
        if pygame.sprite.groupcollide(enemySprites, laserSprites, 1, 1):
           explosionSprites.add(EnemyExplosion(self.rect.center))
           explode.play()
           score.score += 10
            
        #Bomb Collisions    
        if pygame.sprite.groupcollide(enemySprites, bombSprites, 1, 1):
           bombExplosionSprites.add(BombExplosion(self.rect.center))
           explode.play()
           score.score += 10
            
        #Bomb Explosion Collisions    
        if pygame.sprite.groupcollide(enemySprites, bombExplosionSprites, 1, 0):
           explosionSprites.add(EnemyExplosion(self.rect.center))
           explode.play()
           score.score += 10

    
    def reset(self):
        self.rect.bottom = 0
        self.rect.centerx = random.randrange(0, screen.get_width())
        self.dy = random.randrange(5, 10)
        self.dx = random.randrange(-2, 2)

class boss(pygame.sprite.Sprite):
     def __init__(self, centerx):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/boss.png", 0)
        #self.rect = self.image.get_rect()
        self.dx = random.randint(-1,9)
     def update(self):
        self.rect.centerx += self.dx
        if self.rect.left < 0:
          self.rect.centerx = random.randint(100,700)
        elif self.rect.right > 800:
          self.rect.centerx = random.randint(100,700)
           
        #random 1 - 60 determines if firing
        efire = random.randint(1,90)
        if efire == 1:
            bossLaserSprites.add(bossLaser(self.rect.midbottom))
            efire = load_sound("sounds/elaser.ogg")
            efire.play()
            
        #Laser Collisions    
        if pygame.sprite.groupcollide(bossSprite, laserSprites, 1, 1):
            explosionSprites.add(bossExplosion(self.rect.center))
            explode.play()
            score.boss -= 10
            if score.boss <= 0:
                score.score += 100
                self.kill()
            
        #Bomb Collisions    
        if pygame.sprite.groupcollide(enemySprites, bombSprites, 1, 1):
           bombExplosionSprites.add(BombExplosion(self.rect.center))
           explode.play()
           score.boss -= 10
           if score.boss <= 0:
                score.score += 100
                self.kill()
            
        #Bomb Explosion Collisions    
        if pygame.sprite.groupcollide(bossSprite, bombExplosionSprites, 1, 0):
           explosionSprites.add(bossExplosion(self.rect.center))
           explode.play()
           score.boss -= 10
           if score.boss <= 0:
                score.score += 100
                self.kill()
    
class Shield(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/shield.png", -1)
        self.rect.center = pos
        self.counter = 0
        self.maxcount = 5
    def update(self):
        self.counter = self.counter + 1
        if self.counter == self.maxcount:
            self.kill()
            
class EnemyExplosion(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/enemyexplosion.png", -1)
        self.rect.center = pos        
        self.counter = 0
        self.maxcount = 10
    def update(self):
        self.counter = self.counter + 1
        if self.counter == self.maxcount:
            self.kill()

class bossExplosion(pygame.sprite.Sprite):
    def __init__(self,pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/bossexplosion.png",-1)
        self.rect.center = pos
        self.counter = 0
        self.maxcount = 10
    def update(self):
        self.counter = self.counter + 1
        if self.counter == self.maxcount:
            self.kill()
            
class BombExplosion(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/bombexplosion.png", -1)
        self.rect.center = pos        
        self.counter = 0
        self.maxcount = 5
    def update(self):
        self.counter = self.counter + 1
        if self.counter == self.maxcount:
            self.kill()
            
#Bomb Powerup
class BombPowerup(pygame.sprite.Sprite):
    def __init__(self, centerx):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/blasterpowerup.png", -1)
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randrange(0, screen.get_width())
     
        
    def update(self):
        if self.rect.top > screen.get_height():
            self.kill
        else:    
            self.rect.move_ip(0, 6) 

#Shield Powerup
class ShieldPowerup(pygame.sprite.Sprite):
    def __init__(self, centerx):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/shieldpowerup.png", -1)
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randrange(0, screen.get_width())
     
        
    def update(self):
        if self.rect.top > screen.get_height():
            self.kill
        else:    
            self.rect.move_ip(0, 6)         
        
class Score(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.shield = 100
        self.score = 0
        self.bomb = 2
        self.boss = 200
        self.font = pygame.font.Font("data/fonts/kongo.otf", 28)
        
    def update(self):
        self.text = "Shield: %d                    Score: %d                        Blaster: %d" % (self.shield, self.score, self.bomb)
        self.image = self.font.render(self.text, 1, (0, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = (400,20)
         
class Gameover(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font("data/fonts/Neon_Vampire.ttf", 54)
        
    def update(self):
        self.text = "GAME OVER, Score: %d" % (score.score)
        self.image = self.font.render(self.text, 1, (0, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = (400,300)
        
        
class Gameoveresc(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font("data/fonts/kongo.otf", 38)
        
    def update(self):
        self.text = "PRESS ESC TO RETURN"
        self.image = self.font.render(self.text, 1, (0, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = (400,400)
class Gamewon(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font("data/fonts/Neon_Vampire.ttf", 38)
        
    def update(self):
        self.text = "You Beat THE BOSS WITH A SCORE OF %d" % (score.score)
        self.image = self.font.render(self.text, 1, (0, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = (400,300)
        
        
class Gamewonesc(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font("data/fonts/kongo.otf", 28)
        
    def update(self):
        self.text = "PRESS ESC TO RETURN"
        self.image = self.font.render(self.text, 1, (0, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = (400,400)
#Game Module    
def game():
 
    #Game Objects
    global player
    player = Player()
    global score
    score = Score()
    global boss_counter
    boss_counter = 0
    global fire
    fire = load_sound("sounds/bullet.ogg")
    global explode
    explode = load_sound("sounds/explode.ogg")
    global blaster
    blaster = load_sound("sounds/blaster.ogg")
    global powerup
    powerup = load_sound("sounds/powerup.ogg")
    global gameover
    gameover = load_sound("music/blassic.ogg")
    music = False 
    
    #Game Groups
    
    #Player/Enemy
    playerSprite = pygame.sprite.RenderPlain((player))

    global bossSprite
    bossSprite = pygame.sprite.RenderPlain(())

    global enemySprites
    enemySprites = pygame.sprite.RenderPlain(())
    enemySprites.add(Enemy(200))
    enemySprites.add(Enemy(300))
    enemySprites.add(Enemy(400))
    
    #Projectiles
    global laserSprites
    laserSprites = pygame.sprite.RenderPlain(())
    global bossLaserSprites
    bossLaserSprites = pygame.sprite.RenderPlain(())
    global bossExplosionSprites
    bossExplosionSprites = pygame.sprite.RenderPlain(())
    
    global bombSprites
    bombSprites = pygame.sprite.RenderPlain(())
    global enemyLaserSprites
    enemyLaserSprites = pygame.sprite.RenderPlain(())
    
    #Powerups
    global bombPowerups
    bombPowerups = pygame.sprite.RenderPlain(())
    global shieldPowerups
    shieldPowerups = pygame.sprite.RenderPlain(())
    
    #Special FX
    shieldSprites = pygame.sprite.RenderPlain(())
    
    global explosionSprites
    explosionSprites = pygame.sprite.RenderPlain(())
    
    global bombExplosionSprites
    bombExplosionSprites = pygame.sprite.RenderPlain(())
    
    #Score/and game over
    scoreSprite = pygame.sprite.Group(score)
    gameOverSprite = pygame.sprite.RenderPlain(())
    GamewonSprite = pygame.sprite.RenderPlain(())
    #Arena
    arena = Arena()
    arena = pygame.sprite.RenderPlain((arena))
    
    
    #Set Clock
    clock = pygame.time.Clock()
    keepGoing = True
    counter = 0
  
    #Main Loop
    while keepGoing:
       clock.tick(30)
       #input
       for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    keepGoing = False
                elif event.key == pygame.K_LEFT:
                    player.dx = -15
                elif event.key == K_RIGHT:
                    player.dx = 15
                elif event.key == K_UP:
                    player.dy = -15
                elif event.key == K_DOWN:
                    player.dy = 15
            elif event.type == KEYUP:
                if event.key == K_LEFT:
                    player.dx = 0
                elif event.key == K_RIGHT:
                    player.dx = 0
                elif event.key == K_UP:
                    player.dy = 0
                elif event.key == K_DOWN:
                  player.dy = 0
                
             
             
       #Update and draw on the screen
       
       #Update     
       screen.blit(background, (0,0))     
       playerSprite.update()
       enemySprites.update()
       laserSprites.update()
       bombSprites.update()
       enemyLaserSprites.update()
       bossLaserSprites.update()
       bossExplosionSprites.update()
       bombPowerups.update()
       shieldPowerups.update()
       shieldSprites.update()
       explosionSprites.update()
       bombExplosionSprites.update()
       bossSprite.update()
       arena.update()
       scoreSprite.update()
       gameOverSprite.update()
       GamewonSprite.update()
       #Draw
       arena.draw(screen)
       playerSprite.draw(screen)
       enemySprites.draw(screen)
       laserSprites.draw(screen)
       bombSprites.draw(screen)
       enemyLaserSprites.draw(screen)
       bombPowerups.draw(screen)
       shieldPowerups.draw(screen)
       shieldSprites.draw(screen)
       explosionSprites.draw(screen)
       bombExplosionSprites.draw(screen)
       bossLaserSprites.draw(screen)
       bossExplosionSprites.draw(screen)
       bossSprite.draw(screen)
       scoreSprite.draw(screen)
       gameOverSprite.draw(screen)
       GamewonSprite.draw(screen)
       pygame.display.flip()
     
       #Spawn new enemies
       counter += 1
       if counter >= 20:
          enemySprites.add(Enemy(300))
          counter = 0
       
       #Spawn Shield Power up
       #shieldPowerupcounter += 1
       spawnShieldpowerup = random.randint(1,500)
       if spawnShieldpowerup == 1:
          shieldPowerups.add(ShieldPowerup(300))
          
        
       #Spawn Bomb Power up
       spawnBombpowerup = random.randint(1,500)
       if spawnBombpowerup == 1:
          bombPowerups.add(BombPowerup(300))
          bombPowerupcounter = 0
      
       #check if score is above 1000
       if score.score == 1000:
            boss_counter == 10
            bossSprite.add(boss(300))
            enemySprites.remove(enemySprites)
            score.shield = 150
       if score.boss == -500 or score.score >= 5000:
            bossSprite.remove(bossSprite)
            GamewonSprite.add(Gamewon())
            GamewonSprite.add(Gamewonesc())
            playerSprite.remove(player)
            

            
                
       #Check if enemy lasers hit player's ship   
       for hit in pygame.sprite.groupcollide(enemyLaserSprites, playerSprite, 1, 0):
           explode.play()
           explosionSprites.add(Shield(player.rect.center))
           score.shield -= 10
           if score.shield <= 0:
              gameOverSprite.add(Gameover())
              gameOverSprite.add(Gameoveresc())
              playerSprite.remove(player)

       for hit in pygame.sprite.groupcollide(bossLaserSprites, playerSprite, 1, 0):
            explode.play()
            explosionSprites.add(Shield(player.rect.center))
            score.shield -= 5
            if score.shield <= 0:
                gameOverSprite.add(Gameover())
                gameOverSprite.add(Gameoveresc())
                playerSprite.remove(player)       
                
       #Check if enemy collides with player 
       for hit in pygame.sprite.groupcollide(enemySprites, playerSprite, 1, 0):
           explode.play()
           explosionSprites.add(Shield(player.rect.center))
           score.shield -= 10
           if score.shield <= 0:
              gameOverSprite.add(Gameover())
              gameOverSprite.add(Gameoveresc())
              playerSprite.remove(player)

       for hit in pygame.sprite.groupcollide(bossSprite, playerSprite, 1, 0):
           explode.play()
           explosionSprites.add(Shield(player.rect.center))
           score.shield -= 20
           score.boss -= 5
           if score.shield <= 0:
              gameOverSprite.add(Gameover())
              gameOverSprite.add(Gameoveresc())
              playerSprite.remove(player)
            
       #Check if player collides with shield powerup       
       for hit in pygame.sprite.groupcollide(shieldPowerups, playerSprite, 1, 0):
            if score.shield < 100:
               powerup.play()
               score.shield += 10
             
       #Check if player collides with bomb powerup
       for hit in pygame.sprite.groupcollide(bombPowerups, playerSprite, 1, 0):
           powerup.play()
           player.bombamount += 3
           score.bomb += 3

#Class Module
class SpaceMenu:

#Define the initalize self options
    def __init__(self, *options):

        self.options = options
        self.x = 0
        self.y = 0
        self.font = pygame.font.Font(None, 32)
        self.option = 0
        self.width = 1
        self.color = [0, 0, 0]
        self.hcolor = [0, 0, 0]
        self.height = len(self.options)*self.font.get_height()
        for o in self.options:
            text = o[0]
            ren = self.font.render(text, 1, (0, 0, 0))
            if ren.get_width() > self.width:
                self.width = ren.get_width()

#Draw the menu
    def draw(self, surface):
        i=0
        for o in self.options:
            if i==self.option:
                clr = self.hcolor
            else:
                clr = self.color
            text = o[0]
            ren = self.font.render(text, 1, clr)
            if ren.get_width() > self.width:
                self.width = ren.get_width()
            surface.blit(ren, (self.x, self.y + i*self.font.get_height()))
            i+=1

#Menu Input            
    def update(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    self.option += 1
                if e.key == pygame.K_UP:
                    self.option -= 1
                if e.key == pygame.K_RETURN:
                    self.options[self.option][1]()
        if self.option > len(self.options)-1:
            self.option = 0
        if self.option < 0:
            self.option = len(self.options)-1

#Position Menu
    def set_pos(self, x, y):
        self.x = x
        self.y = y

#Font Style        
    def set_font(self, font):
        self.font = font

#Highlight Color        
    def set_highlight_color(self, color):
        self.hcolor = color

#Font Color        
    def set_normal_color(self, color):
        self.color = color

#Font position        
    def center_at(self, x, y):
        self.x = x-(self.width/2)
        self.y = y-(self.height/2)

def missionMenu():
    
    #Arena
    arena = Arena()
    arena = pygame.sprite.RenderPlain((arena))
    

    #Title for Option Menu
    menuTitle = SpaceMenu(
        ["Space Ranger"])

    #Option Menu Text
    instructions = SpaceMenu(
        [""], 
        ["Dragons from another universe are invading...Your chance for glory has come!"],
        [""],
        ["Score the highest and you will be rewarded with fame and the highest of honors!"],
        [""],
        ["Use arrow keys to move your spaceship in space"],
        [""],
        ["the space bar is for firing laser."],
        [""],
        ["Left control for special bombs (limited btw)"],
        [""],
        ["THE MORE YOU KILL MORE THE GLORY YOU ACHIEVE!"],
        [""],
        [""],
        ["                   PRESS ESC TO RETURN                    "])

    #Title 
    menuTitle.center_at(250, 150)
    menuTitle.set_font(pygame.font.Font("data/fonts/Neon_Vampire.ttf", 48))
    menuTitle.set_highlight_color((0, 255, 255))
        

    #Title Center
    instructions.center_at(500, 350)

    #Menu Font
    instructions.set_font(pygame.font.Font("data/fonts/kongo.otf", 22))

    #Highlight Color
    instructions.set_normal_color((0, 255, 255))


    #Set Clock
    clock = pygame.time.Clock()
    keepGoing = True

    while keepGoing:
           clock.tick(30)
           #input
           for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    keepGoing = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        keepGoing = False
           #Draw
           screen.blit(background, (0,0))    
           arena.update()
           arena.draw(screen)
           menuTitle.draw(screen)
           instructions.draw(screen)
           pygame.display.flip()




def aboutMenu():
 
    #Arena
    arena = Arena()
    arena = pygame.sprite.RenderPlain((arena))
    
    #About Menu Text
    #Title for Option Menu
    menuTitle = SpaceMenu(
        ["Space Ranger"])

    info = SpaceMenu(
        [""], 
        ["Space Ranger Beta"],
        [""],
        ["Devloped in Python using Pygame."],
        [""],
        ["      PRESS ESC TO RETURN            "])
        

    #About Title Font color, alignment, and font type
    menuTitle.center_at(150, 150)
    menuTitle.set_font(pygame.font.Font("data/fonts/Neon_Vampire.ttf", 48))
    menuTitle.set_highlight_color((0, 255, 255))

    #About Menu Text Alignment
    info.center_at(400, 310)

    #About Menu Font
    info.set_font(pygame.font.Font("data/fonts/kongo.otf", 28))

    #About Menu Font Color
    info.set_normal_color((0, 255, 255))


    #Set Clock
    clock = pygame.time.Clock()
    keepGoing = True

    while keepGoing:
           clock.tick(30)
           #input
           for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    keepGoing = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        keepGoing = False
           #Draw
           screen.blit(background, (0,0))    
           arena.update()
           arena.draw(screen)
           menuTitle.draw(screen)
           info.draw(screen)
           pygame.display.flip()

#Functions

def option1():
    game()
def option2():
    missionMenu()
def option3():
    aboutMenu()
def option4():
    pygame.quit()
    sys.exit()
    
        

#Main
def main():

    
    #Arena
    arena = Arena()
    arena = pygame.sprite.RenderPlain((arena))

   
    #Defines menu, option functions, and option display. 
    menuTitle = SpaceMenu(
        ["Space Ranger"])
        
    menu = SpaceMenu(
        ["Start", option1],
        ["Mission", option2],
         ["About", option3],
        ["Quit", option4])
        
        

    #Title
    menuTitle.center_at(190, 150)
    menuTitle.set_font(pygame.font.Font("data/fonts/Neon_Vampire.ttf", 78))
    menuTitle.set_highlight_color((0, 255, 255))
    
    #Menu settings
    menu.center_at(400, 320)
    menu.set_font(pygame.font.Font("data/fonts/KONGO.otf", 42))
    menu.set_highlight_color((0, 255, 255))
    menu.set_normal_color((0, 85, 85))
    
    clock = pygame.time.Clock()
    keepGoing = True


    while 1:
        clock.tick(30)

        #Events
        events = pygame.event.get()

        #Update Menu
        menu.update(events)

        #Quit Event
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit()
                return

        #Draw
        screen.blit(background, (0,0))
        arena.update()
        arena.draw(screen)
        menu.draw(screen)
        menuTitle.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
   main()


##########################################################################
# Right2Live Checklist                                                   #
# Computing programing project made in python using pygame               #
# (checklist can be seen bellow).                                        #             #
#                                                                        #
# List of prototype progression:                                         #
#   * Player movement and rotation.                                      #
#   * Basic player collision with tile.                                  #
#   * Change code to work using multiple classes.                        #
#   - Different tile collison based on material and if wall or floor.    #
#   - Maps with settable tiles made using 3d array.                      #
#   - Basic ai with pathfinding.                                         #
#   - Menu system allowing for loading of different maps via menu.       #
#                                                                        #
#   Tasks Complete(2/7)                                                  #
##########################################################################

#Useful pygame tutorials#
#https://www.youtube.com/playlist?list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i#

#Imports all needed libraries#
import pygame as pg
import random, math, time

#Local librarie imports#
import entity, tile

#Main game class#
class Game():

    def __init__(self):
        #Initialises pygame#
        pg.init()

        #Initialisation of global constants#
        self.screenWidth = 720
        self.screenHeight = 720
        self.gameFPS = 60
        self.delta = 1.0

        self.gameboard = [["*","*","*","*","*","*","*","*","*","*","*","*","*","*","*","*","*","*","*","*"],
                          ["*"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," "," "," ","*"," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," "," "," ","*"," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," "," "," ","*"," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," "," "," ","*"," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," "," "," ","*"," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," ","*","*","*"," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," ","*"," "," "," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," ","*","*","*"," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","*"],
                          ["*"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","*"],
                          ["*","*","*","*","*","*","*","*","*","*","*","*","*","*","*","*","*","*","*","*"]]

        #Sets up game window and game clock#
        self.screen = pg.display.set_mode((self.screenWidth, self.screenHeight))
        pg.display.set_caption("Movement Prototype")
        self.clock = pg.time.Clock()

        #Creates group to store all sprites in#
        self.all_sprites = pg.sprite.Group()
        self.player = entity.player(self, 500, 500)

        #Initialises all game tiles#
        self.all_tiles = pg.sprite.Group()

        for x in range(0, 20):
            for y in range(0, 20):
                if self.gameboard[y][x] == "*":
                    tile.Tile(self, x*36, y*36)

    
    def drawGame(self):
        #Draws all content in the window including sprites#
        self.screen.fill((0,0,0))
        self.all_sprites.draw(self.screen)
        pass
        
    def gameHandler(self):
        #Updates angle of rotation of player based on mouse positioning#
        moveVector = (self.mousex - self.player.rect.x, -(self.mousey - self.player.rect.y))

        angleBackup = self.angle
        
        try:
            self.angle = math.degrees(math.acos(moveVector[0] / (math.sqrt(moveVector[0]**2 + moveVector[1]**2))))

        except:
            self.angle = angleBackup
            print("k")
        
        if moveVector[1] < 0:
            self.angle = 360 - self.angle

        #Rotates the image then sets it back it the original to keep image quality (required to prevent image going blurry)#
        self.oldimage = self.player.PLAYER_SPRITE
        self.player.image = pg.transform.rotate(self.oldimage, self.angle)
        self.player.rect = self.player.image.get_rect(center=self.player.rect.center)
        self.player.image.blit(self.player.image, self.player.rect)
        pass
    
    def gameLoop(self):
        #Initialises key values before main game loop.#
        self.gameRunning = True
        self.mousex = 0
        self.mousey = 0
        self.angle = 0

        #Main game loop#
        while self.gameRunning:

            #Runs throught all pygame events#
            for event in pg.event.get():

                #Ends main game loop once quit event is fired#
                if event.type == pg.QUIT:
                    self.gameRunning = False

                #Updates current mouse poistion once pygame detects mouse movement#
                if event.type == pg.MOUSEMOTION:
                    self.mousex, self.mousey = event.pos
                    
            #Sets delta to current game tick rate (in this case based on frame rate)#
            self.delta = self.clock.tick(self.gameFPS)
            
            #Runs update code for player rotation, sprites, game graphics and game window in general#
            self.gameHandler()
            self.all_sprites.update(self.delta)
            self.drawGame()
            pg.display.flip()
        
    
#Main game initialisation, loop and game end when window is closed#
myGame = Game()
myGame.gameLoop()
pg.quit()

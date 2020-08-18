###############################################################################
# Right2Live Checklist                                                        #
# Computing programing project made in python using pygame                    #
# (checklist can be seen bellow).                                             #             
#                                                                             #
# List of game progression:                                                   #
#   * Player movement and rotation.                                           #
#   * Basic player collision with tile.                                       #
#   * Change code to work using multiple classes.                             #
#   * Maps with settable tiles made using 3d array.                           #
#   * Different tile collison based on material and if wall or floor.         #
#   * Make map code dynamic so new maps can be added without changing code.   #
#   - Add map scrolling so bigger maps can be made but not all shown at once. #
#   - Menu system allowing for loading of different maps via menu.            #
#   - Basic ai with pathfinding.                                              #
#   - Improved player collision and movement to work better with rotation.    #
#                                                                             #
#   Tasks Complete(6/10)                                                      #
###############################################################################

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
        self.screenWidth = 720 #Change to 1280 to make 720p game
        self.screenHeight = 720
        self.gameFPS = 60
        self.delta = 1.0

        #Sets up game window and game clock#
        self.screen = pg.display.set_mode((self.screenWidth, self.screenHeight))
        pg.display.set_caption("Movement Prototype")
        self.clock = pg.time.Clock()

        #Initialises all sprite groups#
        self.all_sprites = pg.sprite.Group()
        self.all_tiles = pg.sprite.Group()

        #Loads gameboard from textfile#
        self.gameboard = []
        tempboard = open("Maps\TestMap.txt", "r")

        for i in tempboard:
            self.gameboard.append(i)

        #Draws gameboard by placing tiles in set locations#
        for x in range(0, len(self.gameboard)):
            for y in range(0, len(self.gameboard[0]) - 1):

                #Sets the game tiles with different textures based on coordinate in the tile set#
                if self.gameboard[x][y] == "#":
                    tile.Tile(self, y*36, x*36, 1, 0, True)

                if self.gameboard[x][y] == "*":
                    tile.Tile(self, y*36, x*36, 2, 0, False)

        #Closes textfile#
        tempboard.close()

        #Creates player entity#
        self.player = entity.player(self, 500, 500)

    
    def drawGame(self):
        #Draws all content in the window including sprites#
        self.screen.fill((255,255,255))
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

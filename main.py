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
#   * Add map scrolling so bigger maps can be made but not all shown at once. #
#   - Menu system allowing for loading of different maps via menu.            #
#   - Basic ai with pathfinding.                                              #
#   - Improved player collision and movement to work better with rotation.    #
#   - Draw tiles more efficently to reduce both RAM and GPU usage.            #
#                                                                             #
#   Tasks Complete(7/10)                                                      #
###############################################################################

#Imports all needed libraries#
import pygame as pg
import random, math, time

#Local librarie imports#
import entity, tile, gameMap

#Main game class#
class Game():

    def __init__(self):
        #Initialises pygame#
        pg.init()

        #Initialisation of global constants#
        self.screenWidth = 856
        self.screenHeight = 480
        self.tileSize = 36
        self.gameFPS = 60
        self.delta = 1.0

        #Sets up game window and game clock#
        self.screen = pg.display.set_mode((self.screenWidth, self.screenHeight))
        pg.display.set_caption("Movement Prototype")
        self.clock = pg.time.Clock()

        #Initialises all sprite groups#
        self.all_sprites = pg.sprite.Group()
        self.all_tiles = pg.sprite.Group()

        #Loads gameboard from textfile via map class#
        self.map = gameMap.Map(self,"Maps\TestMap.txt")

        #Draws gameboard by placing tiles in set locations#
        for x in range(0, self.map.tilesX):
            for y in range(0, self.map.tilesY):
                #Sets the game tiles with different textures based on coordinate in the tile set#
                if self.map.gameboard[x][y] == "#":
                    tile.Tile(self, x, y, 1, 0, True)

                if self.map.gameboard[x][y] == "*":
                    tile.Tile(self, x, y, 2, 0, False)

        #Creates player entity#
        self.player = entity.player(self, 500, 500)

        #Creates map view#
        self.view = gameMap.MapView(self.map.pixelX, self.map.pixelY)

    
    def drawGame(self):
        #Draws all content in the window including sprites in the designated map view#
        self.screen.fill((255,255,255))
        self.all_sprites.draw(self.screen)

        for sprites in self.all_sprites:
            self.screen.blit(sprites.image, self.view.createView(sprites))
        pass
        
    def gameHandler(self):
        #Updates angle of rotation of player based on mouse positioning and current view of screen#
        moveVector = ( (self.mousex - self.view.viewRect.x) - self.player.rect.x, -( (self.mousey - self.view.viewRect.y) - self.player.rect.y))
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
            
            #Runs update code for player rotation, sprites, game graphics and the game window view in general#
            self.gameHandler()
            self.all_sprites.update(self.delta)
            self.view.update(self, self.player)
            self.drawGame()
            pg.display.flip()
        
    
#Main game initialisation, loop and game end when window is closed#
myGame = Game()
myGame.gameLoop()
pg.quit()

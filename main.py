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
#   * Menu system allowing for loading of different maps via menu.            #
#   - Fully functioning options menu.                                         #
#   - Basic ai with pathfinding.                                              #
#   - Improved player collision and movement to work better with rotation.    #
#   - Draw tiles more efficently to reduce both RAM and GPU usage (use rect). #
#   - Working weapons with fireable bullets.                                  #
#                                                                             #
#   Tasks Complete(8/13)                                                      #
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
        pg.font.init()

        #Initialisation of global constants#
        self.screenWidth = 856
        self.screenHeight = 480
        self.tileSize = 36
        self.gameFPS = 60
        self.delta = 1.0
        self.antialiasing = True

        #Sets up game window and game clock#
        self.screen = pg.display.set_mode((self.screenWidth, self.screenHeight))
        pg.display.set_caption("Right2Live Dev Build")
        self.clock = pg.time.Clock()

        #Initialises all sprite groups#
        self.all_sprites = pg.sprite.Group()
        self.all_tiles = pg.sprite.Group()

    def setupGame(self, mapFile):
        #Loads gameboard from textfile via map class#
        self.map = gameMap.Map(self, mapFile)

        #Creats transparent overlays for background#
        self.transOverlayLight = pg.Surface(self.screen.get_size()).convert_alpha()
        self.transOverlayLight.fill(( 0, 0, 0, 120))

        self.transOverlayDark = pg.Surface((self.screenWidth /  4, self.screenHeight)).convert_alpha()
        self.transOverlayDark.fill(( 0, 0, 0, 60))

        #Draws gameboard by placing tiles in set locations#
        for x in range(0, self.map.tilesX):
            for y in range(0, self.map.tilesY):
                #Sets the game tiles with different textures based on coordinate in the tile set#
                if self.map.gameboard[x][y] == "#":
                    tile.Tile(self, y, x, 1, 0, True)

                if self.map.gameboard[x][y] == "*":
                    tile.Tile(self, y, x, 2, 0, False)

        #Creates player entity#
        self.player = entity.player(self, 500, 500)

        #Creates map view#
        self.view = gameMap.MapView(self.map.pixelX, self.map.pixelY)

    def createText(self, font, size, text, colour, position):
        #Funtion used to create text easily ingame#
        myfont = pg.font.SysFont(font, size)
        textsurface = myfont.render(text, self.antialiasing, colour)
        self.screen.blit(textsurface, position)
    
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

    def mainMenu(self):
        #Sets up some constants#
        self.quit = False
        self.leftClick = False
        
        while not self.quit:
            #Updates current mouse poistion#
            self.mousex, self.mousey = pg.mouse.get_pos()
            
            #Clears screen of all old screen elements#
            self.screen.fill((0,0,0))

            #Draws the menu button#
            spButton = pg.Rect(int((50/856) * self.screenWidth), int((120/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            optionsButton = pg.Rect(int((50/856) * self.screenWidth), int((180/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            quitButton = pg.Rect(int((50/856) * self.screenWidth), int((240/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))

            #Opens a menu to allow player to choose the level they want to play#
            if spButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), spButton)
                if self.leftClick:
                    self.mapSelection()
            else:
                pg.draw.rect(self.screen, (255, 0, 0), spButton)

            #Allows the player to change different game options#
            if optionsButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), optionsButton)
                if self.leftClick:
                    pass
            else:
                pg.draw.rect(self.screen, (255, 0, 0), optionsButton)

            #When pressed closes the game#
            if quitButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), quitButton)
                if self.leftClick:
                    self.quit = True
            else:
                pg.draw.rect(self.screen, (255, 0, 0), quitButton)

            #Draws all text for the menu#
            self.createText('baskervilleoldface', int((50/480) * self.screenHeight), 'Right2Live', (255,0,0), (int((25/856) * self.screenWidth), int((40/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Single Player', (0,0,0), (int((60/856) * self.screenWidth), int((130/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Options', (0,0,0), (int((60/856) * self.screenWidth), int((190/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Quit Game', (0,0,0), (int((60/856) * self.screenWidth), int((250/480) * self.screenHeight)))
            

            #Resets the leftclick read to detect when another click occours#
            self.leftClick = False
            
            for event in pg.event.get():
                #Ends main game loop once quit event is fired#
                if event.type == pg.QUIT:
                    self.quit = True

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.quit = True

                #Checks for a mouse click and if so sets leftClick to true#
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.leftClick = True
            
            pg.display.flip()



    def mapSelection(self):
        #Sets up some constants#
        self.selectingMap = True
        self.leftClick = False
        
        self.maps = [['Dev Test',"Maps\TestMap.txt"],['Level 1',"Maps\L1.txt"],['level 2',"Maps\L2.txt"]]
        self.level = 0
        
        while self.selectingMap:
            
            #Updates current mouse poistion#
            self.mousex, self.mousey = pg.mouse.get_pos()
            
            #Clears screen of all old screen elements#
            self.screen.fill((0,0,0))

            #Draws the menu button#
            homeButton = pg.Rect(int((200/856) * self.screenWidth), int((350/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            playButton = pg.Rect(int((456/856) * self.screenWidth), int((350/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))

            leftButton = pg.Rect(int((290/856) * self.screenWidth), int((200/480) * self.screenHeight), int((20/856) * self.screenWidth), int((70/480) * self.screenHeight))
            rightButton = pg.Rect(int((546/856) * self.screenWidth), int((200/480) * self.screenHeight), int((20/856) * self.screenWidth), int((70/480) * self.screenHeight))

            #Starts the game for the player (ADD MENU TO CHOOSE LEVEL)#
            if homeButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), homeButton)
                if self.leftClick:
                    self.selectingMap = False
            else:
                pg.draw.rect(self.screen, (255, 0, 0), homeButton)

            #When pressed closes the game#
            if playButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), playButton)
                if self.leftClick:
                    self.setupGame(self.maps[self.level][1])
                    self.gameLoop()
            else:
                pg.draw.rect(self.screen, (255, 0, 0), playButton)


            #Buttons for changing current map from list#

            if leftButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), leftButton)
                if self.leftClick:
                    if self.level != 0:
                        self.level += -1
            else:
                pg.draw.rect(self.screen, (255, 0, 0), leftButton)

            if rightButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), rightButton)
                if self.leftClick:
                    if self.level != (len(self.maps)-1):
                        self.level += 1
            else:
                pg.draw.rect(self.screen, (255, 0, 0), rightButton)

            #Draws all text for the map selection screen#
            self.createText('baskervilleoldface', int((50/480) * self.screenHeight), 'Map Selection', (255,0,0), (int((25/856) * self.screenWidth), int((40/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Back', (0,0,0), (int((210/856) * self.screenWidth), int((360/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Play', (0,0,0), (int((466/856) * self.screenWidth), int((360/480) * self.screenHeight)))

            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), '<', (0,0,0), (int((295/856) * self.screenWidth), int((227/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), '>', (0,0,0), (int((552/856) * self.screenWidth), int((227/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((30/480) * self.screenHeight), self.maps[self.level][0], (255,0,0), (int((373/856) * self.screenWidth), int((235/480) * self.screenHeight)))  

            #Resets the leftclick read to detect when another click occours#
            self.leftClick = False
            
            for event in pg.event.get():
                #Ends main game loop once quit event is fired#
                if event.type == pg.QUIT:
                    self.selectingMap = False
                    self.quit = True

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.selectingMap = False

                #Checks for a mouse click and if so sets leftClick to true#
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.leftClick = True
            
            pg.display.flip()



    #Options menu (ADD LATER)#
    def options(self):
        pass
    
    
    def gameLoop(self):
        #Initialises key values before main game loop.#
        self.gameRunning = True
        self.mousex = 0
        self.mousey = 0
        self.angle = 0
        self.paused = False

        #Main game loop#
        while self.gameRunning:

            #Records information about basic mouse actions#
            self.leftClick = False
            
            #Runs throught all pygame events#
            for event in pg.event.get():

                #Ends main game loop once quit event is fired#
                if event.type == pg.QUIT:
                    self.gameRunning = False
                    self.selectingMap = False
                    self.quit = True

                #Updates current mouse poistion once pygame detects mouse movement#
                if event.type == pg.MOUSEMOTION:
                    self.mousex, self.mousey = event.pos

                if event.type == pg.KEYDOWN:
                    #Checks to see if the player wants to acccess the pause menu#
                    if event.key == pg.K_ESCAPE:
                        self.paused = not self.paused

                if event.type == pg.MOUSEBUTTONDOWN:
                    #Checks to see if player left clicks#
                    if event.button == 1:
                        self.leftClick = True
                    
            #Sets delta to current game tick rate (in this case based on frame rate)#
            self.delta = self.clock.tick(self.gameFPS)

            if self.paused == False:
                #Runs update code for player rotation, sprites, game graphics and the game window view in general#
                self.gameHandler()
                self.all_sprites.update(self.delta)
                self.view.update(self, self.player)
                self.drawGame()

            else:
                #Runs the games pause menu stoping all game updates#
                self.pauseMenu()
            
            pg.display.flip()


    def pauseMenu(self):
        #Draws the game screen in place every frame#
        self.drawGame()

        #Draws all ui elements for the pause screen#
        self.screen.blit(self.transOverlayLight, (0,0))
        self.screen.blit(self.transOverlayDark, (0,0))

        #Adds all buttons to the game#
        returnButton = pg.Rect(int((50/856) * self.screenWidth), int((120/480) * self.screenHeight), int((150/856) * self.screenWidth), int((50/480) * self.screenHeight))
        optionsButton = pg.Rect(int((50/856) * self.screenWidth), int((180/480) * self.screenHeight), int((150/856) * self.screenWidth), int((50/480) * self.screenHeight))
        menuButton = pg.Rect(int((50/856) * self.screenWidth), int((240/480) * self.screenHeight), int((150/856) * self.screenWidth), int((50/480) * self.screenHeight))

        #Returns the player back to the game#
        if returnButton.collidepoint((self.mousex, self.mousey)):
            pg.draw.rect(self.screen, (255, 54, 54), returnButton)
            if self.leftClick:
                self.paused = False
        else:
            pg.draw.rect(self.screen, (255, 0, 0), returnButton)

        #Allows the player to change different game options#     
        if optionsButton.collidepoint((self.mousex, self.mousey)):
            pg.draw.rect(self.screen, (255, 54, 54), optionsButton)
            if self.leftClick:
                print("add later")

        else:
            pg.draw.rect(self.screen, (255, 0, 0), optionsButton)

        #Returns the player to the main menu and clears all sprites#    
        if menuButton.collidepoint((self.mousex, self.mousey)):
            pg.draw.rect(self.screen, (255, 54, 54), menuButton)
            if self.leftClick:
                self.paused = False
                self.selectingMap = False
                self.gameRunning = False
                self.leftClick = False
                
                self.all_sprites.empty()
                self.all_tiles.empty()
        else:
            pg.draw.rect(self.screen, (255, 0, 0), menuButton)

        #Draws all text for pause menu#
        self.createText('baskervilleoldface', int((30/480) * self.screenHeight), 'Paused', (255,0,0), (int((25/856) * self.screenWidth), int((40/480) * self.screenHeight)))
        self.createText('baskervilleoldface', int((15/480) * self.screenHeight), 'Resume', (0,0,0), (int((60/856) * self.screenWidth), int((130/480) * self.screenHeight)))
        self.createText('baskervilleoldface', int((15/480) * self.screenHeight), 'Options', (0,0,0), (int((60/856) * self.screenWidth), int((190/480) * self.screenHeight)))
        self.createText('baskervilleoldface', int((15/480) * self.screenHeight), 'Quit To Menu', (0,0,0), (int((60/856) * self.screenWidth), int((250/480) * self.screenHeight)))
                
    
#Main game initialisation, loop and game end when window is closed#
myGame = Game()
myGame.mainMenu()
pg.quit()

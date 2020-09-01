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
#   * Fully functioning options menu (ADD CONTROLS AND VIDEO SETTINGS).       #
#   * Draw tiles more efficently to reduce both RAM and GPU usage (use rect). #
#   * Working weapons with fireable bullets.                                  #
#   - Basic ai with pathfinding.                                              #
#   - Improved player collision and movement to work better with rotation.    #
#   - Make full screen and resoultions scale corretly to the pc's screen.     #
#                                                                             #
#   Tasks Complete(10/13)                                                     #
###############################################################################

#Imports all needed libraries#
import pygame as pg
import random, math, time, json

#Local librarie imports#
import entity, tile, gameMap

#Main game class#
class Game():

    def __init__(self):
        #Initialises pygame#
        pg.init()
        pg.font.init()

        #Initialisation of values for keys from Json file (if file doesn't exist then one is created from base Json)#
        self.keys = '{"North": ["w",119],"South": ["s",115],"East": ["d",100],"West": ["a",97],"Shoot": ["space",32],"Reload": ["r",114],"Switch Weapon": ["1",49],"Interact": ["2",50]}'        
        try:
            with open('controls.json') as f:
                self.keys = json.load(f)
                print(self.keys)
                
        except:
            with open('controls.json', 'w') as f:
                json.dump(self.keys, f)

        self.keyList = json.loads(self.keys)

        #Initialisation of values for graphics and audio control (if file doesn't exist then one is created from base Json)#
        self.graphicsSettings = '{"AntiAliasing": [true], "Resolution": [856,480], "Fullscreen": [false], "Music": [1.0], "Sound": [1.0]}'

        try:
            with open('graphics.json') as f:
                self.graphicsSettings = json.load(f)
                print(self.graphicsSettings)
                
        except:
            with open('graphics.json', 'w') as f:
                json.dump(self.graphicsSettings, f)

        self.graphicsList = json.loads(self.graphicsSettings)

        #Initialisation of global constants#
        self.screenWidth, self.screenHeight  = self.graphicsList["Resolution"]
        self.tileSize = 36
        self.gameFPS = 60
        self.delta = 1.0
        
        #Sets up game window and game clock#
        
        if self.graphicsList["Fullscreen"][0]:
            self.screen = pg.display.set_mode((self.screenWidth, self.screenHeight), pg.FULLSCREEN)
        else:
            self.screen = pg.display.set_mode((self.screenWidth, self.screenHeight))
            
        pg.display.set_caption("Right2Live Dev Build")
        self.clock = pg.time.Clock()

        #Initialises all sprite groups#
        self.all_sprites = pg.sprite.Group()
        self.all_tiles = pg.sprite.Group()
        self.all_projectiles = pg.sprite.Group()

        print(pg.display.list_modes()[0])

    def setupGame(self, mapFile):
        #Loads gameboard from textfile via map class and #
        #Tile texture initialisation#
        self.TILE_SET = pg.image.load("Textures\World\TileSet.png").convert_alpha()
        self.map = gameMap.Map(self, mapFile)

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
        textsurface = myfont.render(text, self.graphicsList["AntiAliasing"][0], colour)
        self.screen.blit(textsurface, position)
    
    def drawGame(self):
        #Draws all content in the window including sprites in the designated map view#
        self.screen.fill((255,255,255))
        self.all_sprites.draw(self.screen)

        for sprites in self.all_sprites:
            self.screen.blit(sprites.image, self.view.createView(sprites))
        pass

    def drawPlayerInfo(self):
        
        #Initalises some varibles for the screen#
        textColour = (255,255,255)
        self.transOverlay = pg.Surface(( int((210/856) * self.screenWidth),  int((90/480) * self.screenHeight))).convert_alpha()
        self.transOverlay.fill(( 0, 0, 0, 80))

        #Draws all ui elements for the weapon screen#
        self.screen.blit(self.transOverlay, (0,0))
        self.createText('baskervilleoldface', int((30/480) * self.screenHeight), str(self.player.returnCurrentWeaponValue(0)), textColour, (int((10/856) * self.screenWidth), int((20/480) * self.screenHeight)))

        #Changes colour of ammo text if reloading or has infinte ammo#
        if (int(self.player.returnCurrentWeaponValue(1)) == -1):
            textColour = (76,165,224)
        elif (self.player.reloading) or ((int(self.player.returnCurrentWeaponValue(2)) == 0) and (int(self.player.returnCurrentWeaponValue(1)) == 0)):
            textColour = (214,26,26)

        #Draws special text if gun has infinite ammo#
        if int(self.player.returnCurrentWeaponValue(1)) == -1:
            self.createText('baskervilleoldface', int((30/480) * self.screenHeight), "Infinite Ammo", textColour, (int((10/856) * self.screenWidth), int((55/480) * self.screenHeight)))

        else:
            self.createText('baskervilleoldface', int((30/480) * self.screenHeight), "Ammo: " + (str(self.player.returnCurrentWeaponValue(1)) + "/" + str(self.player.returnCurrentWeaponValue(2))), textColour, (int((10/856) * self.screenWidth), int((55/480) * self.screenHeight)))
        
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
        #Sets up some base values and constants#
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
                    self.options()
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

                #Resizes surface when window size changes#
                #if event.type == pg.VIDEORESIZE:
                #    surface = pg.display.set_mode((event.w, event.h),pg.RESIZABLE)
                #    self.screenWidth = event.w
                #    self.screenHeight = event.h
            
            pg.display.flip()



    def mapSelection(self):
        #Sets up some base values and constants#
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

                #Resizes surface when window size changes#
                #if event.type == pg.VIDEORESIZE:
                #    surface = pg.display.set_mode((event.w, event.h),pg.RESIZABLE)
                #    self.screenWidth = event.w
                #    self.screenHeight = event.h
            
            pg.display.flip()

    def options(self):
        #Sets up some base values and constants#
        self.changingOptions = True
        self.leftClick = False

        while self.changingOptions:
            #Updates current mouse poistion#
            self.mousex, self.mousey = pg.mouse.get_pos()
            
            #Clears screen of all old screen elements#
            self.screen.fill((0,0,0))

            #Draws the menu button#
            controlsButton = pg.Rect(int((328/856) * self.screenWidth), int((140/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            videoButton = pg.Rect(int((328/856) * self.screenWidth), int((200/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            returnButton = pg.Rect(int((328/856) * self.screenWidth), int((260/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))

            #Opens a menu to allow player to change keybinds#
            if controlsButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), controlsButton)
                if self.leftClick:
                    self.controls()
            else:
                pg.draw.rect(self.screen, (255, 0, 0), controlsButton)

            #Opens a menu to allow player to change video settings (ADD LATER)#
            if videoButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), videoButton)
                if self.leftClick:
                    self.graphicsOptions()
            else:
                pg.draw.rect(self.screen, (255, 0, 0), videoButton)

            #When pressed returns player to previous menu#
            if returnButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), returnButton)
                if self.leftClick:
                    self.changingOptions = False

            else:
                pg.draw.rect(self.screen, (255, 0, 0), returnButton)

            #Draws all text for the options screen#
            self.createText('baskervilleoldface', int((50/480) * self.screenHeight), 'Options', (255,0,0), (int((338/856) * self.screenWidth), int((40/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Controls', (0,0,0), (int((338/856) * self.screenWidth), int((150/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Graphics And Audio', (0,0,0), (int((338/856) * self.screenWidth), int((210/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Done', (0,0,0), (int((338/856) * self.screenWidth), int((270/480) * self.screenHeight)))

            #Resets the leftclick read to detect when another click occours#
            self.leftClick = False
            
            for event in pg.event.get():
                #Ends main game loop once quit event is fired#
                if event.type == pg.QUIT:
                    self.changingOptions = False
                    self.selectingMap = False
                    self.gameRunning = False
                    self.quit = True

                if event.type == pg.KEYDOWN:

                    #When pressed returns player to previous menu#
                    if event.key == pg.K_ESCAPE:
                        self.changingOptions = False


                #Checks for a mouse click and if so sets leftClick to true#
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.leftClick = True

                #Resizes surface when window size changes#
                #if event.type == pg.VIDEORESIZE:
                #    surface = pg.display.set_mode((event.w, event.h),pg.RESIZABLE)
                #    self.screenWidth = event.w
                #    self.screenHeight = event.h
            
            pg.display.flip()

    
    def controls(self):
        #Sets up some base values and constants#
        self.changingControls = True
        self.leftClick = False
        key = ""

        while self.changingControls:
            #Updates current mouse poistion#
            self.mousex, self.mousey = pg.mouse.get_pos()
            
            #Clears screen of all old screen elements#
            self.screen.fill((0,0,0))

            #Draws the menu button#
            northButton = pg.Rect(int((200/856) * self.screenWidth), int((140/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            southButton = pg.Rect(int((200/856) * self.screenWidth), int((200/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            eastButton = pg.Rect(int((200/856) * self.screenWidth), int((260/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            westButton = pg.Rect(int((200/856) * self.screenWidth), int((320/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))

            shootButton = pg.Rect(int((456/856) * self.screenWidth), int((140/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            reloadButton = pg.Rect(int((456/856) * self.screenWidth), int((200/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            switchButton = pg.Rect(int((456/856) * self.screenWidth), int((260/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            interactButton = pg.Rect(int((456/856) * self.screenWidth), int((320/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            
            returnButton = pg.Rect(int((328/856) * self.screenWidth), int((400/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))

            #Used to change north button#
            if northButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), northButton)
                if self.leftClick:
                    key = "North"
            else:
                pg.draw.rect(self.screen, (255, 0, 0), northButton)

            #Used to change south button#
            if southButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), southButton)
                if self.leftClick:
                    key = "South"
            else:
                pg.draw.rect(self.screen, (255, 0, 0), southButton)

            #Used to change east button#
            if eastButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), eastButton)
                if self.leftClick:
                    key = "East"
            else:
                pg.draw.rect(self.screen, (255, 0, 0), eastButton)

            #Used to change west button#
            if westButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), westButton)
                if self.leftClick:
                    key = "West"
            else:
                pg.draw.rect(self.screen, (255, 0, 0), westButton)

            #Used to change shoot button#
            if shootButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), shootButton)
                if self.leftClick:
                    key = "Shoot"
            else:
                pg.draw.rect(self.screen, (255, 0, 0), shootButton)

            #Used to change reload button#
            if reloadButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), reloadButton)
                if self.leftClick:
                    key = "Reload"
            else:
                pg.draw.rect(self.screen, (255, 0, 0), reloadButton)

            #Used to change switch button#
            if switchButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), switchButton)
                if self.leftClick:
                    key = "Switch Weapon"
            else:
                pg.draw.rect(self.screen, (255, 0, 0), switchButton)

            #Used to change interact button#
            if interactButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), interactButton)
                if self.leftClick:
                    key = "Interact"
            else:
                pg.draw.rect(self.screen, (255, 0, 0), interactButton)

            #When pressed returns player to previous menu#
            if returnButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), returnButton)
                if self.leftClick:
                    self.changingControls = False

            else:
                pg.draw.rect(self.screen, (255, 0, 0), returnButton)

            #Draws all text for the controls screen#
            self.createText('baskervilleoldface', int((50/480) * self.screenHeight), 'Controls', (255,0,0), (int((338/856) * self.screenWidth), int((40/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'North: ' + self.keyList["North"][0], (0,0,0), (int((210/856) * self.screenWidth), int((150/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'South: ' + self.keyList["South"][0], (0,0,0), (int((210/856) * self.screenWidth), int((210/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'East: ' + self.keyList["East"][0], (0,0,0), (int((210/856) * self.screenWidth), int((270/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'West: ' + self.keyList["West"][0], (0,0,0), (int((210/856) * self.screenWidth), int((330/480) * self.screenHeight)))

            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Shoot: ' + self.keyList["Shoot"][0], (0,0,0), (int((466/856) * self.screenWidth), int((150/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Reload: ' + self.keyList["Reload"][0], (0,0,0), (int((466/856) * self.screenWidth), int((210/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Switch Weapon: ' + self.keyList["Switch Weapon"][0], (0,0,0), (int((466/856) * self.screenWidth), int((270/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Interact: ' + self.keyList["Interact"][0], (0,0,0), (int((466/856) * self.screenWidth), int((330/480) * self.screenHeight)))

            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Done', (0,0,0), (int((338/856) * self.screenWidth), int((410/480) * self.screenHeight)))


            #Resets the leftclick read to detect when another click occours#
            self.leftClick = False
            
            for event in pg.event.get():
                #Ends main game loop once quit event is fired#
                if event.type == pg.QUIT:
                    self.changingControls = False
                    self.changingOptions = False
                    self.selectingMap = False
                    self.gameRunning = False
                    self.quit = True

                if event.type == pg.KEYDOWN:

                    #When pressed returns player to previous menu#
                    if event.key == pg.K_ESCAPE:
                        self.changingControls = False

                    #Switches the key to the one that is pressed#
                    else:
                        if key != "":    
                            self.keyList[key] = [pg.key.name(event.key) ,event.key]
                            self.keys = json.dumps(self.keyList)
                            with open('controls.json', 'w') as f:
                                json.dump(self.keys, f)
                                
                            key = ""

                #Checks for a mouse click and if so sets leftClick to true#
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.leftClick = True

                #Resizes surface when window size changes#
                #if event.type == pg.VIDEORESIZE:
                #    surface = pg.display.set_mode((event.w, event.h),pg.RESIZABLE)
                #    self.screenWidth = event.w
                #    self.screenHeight = event.h
            
            pg.display.flip()


    def graphicsOptions(self):
        #Sets up some base values and constants#
        self.changingGraphics = True
        self.leftClick = False

        resolutions = [[856,480],[960,540],[1280,720],[1600,900],[1920,1080]]
        audioOptions = [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]

        while self.changingGraphics:
            #Updates current mouse poistion#
            self.mousex, self.mousey = pg.mouse.get_pos()
            
            #Clears screen of all old screen elements#
            self.screen.fill((0,0,0))

            #Draws the menu button#
            aaButton = pg.Rect(int((328/856) * self.screenWidth), int((100/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            resolutionButton = pg.Rect(int((328/856) * self.screenWidth), int((160/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            fullscreenButton = pg.Rect(int((328/856) * self.screenWidth), int((220/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            musicVolumeButton = pg.Rect(int((328/856) * self.screenWidth), int((280/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            gameVolumeButton = pg.Rect(int((328/856) * self.screenWidth), int((340/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            
            returnButton = pg.Rect(int((328/856) * self.screenWidth), int((420/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))

            #Used to change if Anti-Aliasing is enabled or not button#
            if aaButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), aaButton)
                if self.leftClick:
                    self.graphicsList["AntiAliasing"] = [not(self.graphicsList["AntiAliasing"][0])]
                    self.graphicsSettings = json.dumps(self.graphicsList)
                    with open('graphics.json', 'w') as f:
                        json.dump(self.graphicsSettings, f)
            else:
                pg.draw.rect(self.screen, (255, 0, 0), aaButton)

            #Used to change the Resolution and size (if not in full screen) of the game window#
            if resolutionButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), resolutionButton)
                if self.leftClick:

                    #Check to see if the resolution is custom or the final in list, if so sets resolution to the intial one in the list#
                    if (self.graphicsList["Resolution"] not in resolutions) or (self.graphicsList["Resolution"] == resolutions[-1]):
                        self.graphicsList["Resolution"] = resolutions[0]
                        
                    else:
                        #Sets resolution to that of the next value in the list#
                        complete = False
                        for res in range(len(resolutions)):
                            if (self.graphicsList["Resolution"] == resolutions[res]) and (not complete):
                                self.graphicsList["Resolution"] = resolutions[res + 1]
                                complete = True

                    #Writes the change to the graphics option in the settings#
                    self.graphicsSettings = json.dumps(self.graphicsList)
                    with open('graphics.json', 'w') as f:
                        json.dump(self.graphicsSettings, f)

                    #Resizes window apropriatly and accounts for fullscreen#
                    self.screenWidth, self.screenHeight  = self.graphicsList["Resolution"]

                    if self.graphicsList["Fullscreen"][0]:
                        self.screen = pg.display.set_mode((self.screenWidth, self.screenHeight), pg.FULLSCREEN)
                    else:
                        self.screen = pg.display.set_mode((self.screenWidth, self.screenHeight))
                    
            else:
                pg.draw.rect(self.screen, (255, 0, 0), resolutionButton)

            #Used for player to enable fullscreen mode#
            if fullscreenButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), fullscreenButton)
                if self.leftClick:
                    self.graphicsList["Fullscreen"] = [not(self.graphicsList["Fullscreen"][0])]
                    self.graphicsSettings = json.dumps(self.graphicsList)
                    with open('graphics.json', 'w') as f:
                        json.dump(self.graphicsSettings, f)

                    #Switches the game between windowed and fullscreen mode#
                    if self.graphicsList["Fullscreen"][0]:
                        self.screen = pg.display.set_mode((self.screenWidth, self.screenHeight), pg.FULLSCREEN)
                    else:
                        self.screen = pg.display.set_mode((self.screenWidth, self.screenHeight))
                        
            else:
                pg.draw.rect(self.screen, (255, 0, 0), fullscreenButton)

            #Used to change the volume of the game music#
            if musicVolumeButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), musicVolumeButton)
                if self.leftClick:
                    if (self.graphicsList["Music"][0] not in audioOptions) or (self.graphicsList["Music"][0] == audioOptions[-1]):
                        self.graphicsList["Music"] = [audioOptions[0]]
                        
                    else:
                        #Sets music sound to that of the next value in the list#
                        complete = False
                        for aud in range(len(audioOptions)):
                            if (self.graphicsList["Music"][0] == audioOptions[aud]) and (not complete):
                                self.graphicsList["Music"] = [audioOptions[aud + 1]]
                                complete = True

                    #Writes the change to the graphics option in the settings#
                    self.graphicsSettings = json.dumps(self.graphicsList)
                    with open('graphics.json', 'w') as f:
                        json.dump(self.graphicsSettings, f)
            else:
                pg.draw.rect(self.screen, (255, 0, 0), musicVolumeButton)

            #Used to change the volume of the game sounds#
            if gameVolumeButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), gameVolumeButton)
                if self.leftClick:
                    if (self.graphicsList["Sound"][0] not in audioOptions) or (self.graphicsList["Sound"][0] == audioOptions[-1]):
                        self.graphicsList["Sound"] = [audioOptions[0]]
                        
                    else:
                        #Sets game sound to that of the next value in the list#
                        complete = False
                        for aud in range(len(audioOptions)):
                            if (self.graphicsList["Sound"][0] == audioOptions[aud]) and (not complete):
                                self.graphicsList["Sound"] = [audioOptions[aud + 1]]
                                complete = True

                    #Writes the change to the graphics option in the settings#
                    self.graphicsSettings = json.dumps(self.graphicsList)
                    with open('graphics.json', 'w') as f:
                        json.dump(self.graphicsSettings, f)
            else:
                pg.draw.rect(self.screen, (255, 0, 0), gameVolumeButton)

            #When pressed returns player to previous menu#
            if returnButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), returnButton)
                if self.leftClick:
                    self.changingGraphics = False

            else:
                pg.draw.rect(self.screen, (255, 0, 0), returnButton)

            #Draws all text for the controls screen#
            self.createText('baskervilleoldface', int((50/480) * self.screenHeight), 'Graphics and Audio', (255,0,0), (int((238/856) * self.screenWidth), int((40/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Anti Aliasing: ' + str(self.graphicsList["AntiAliasing"][0]), (0,0,0), (int((338/856) * self.screenWidth), int((110/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Resolution: ' + str(self.graphicsList["Resolution"][0]) + "x" + str(self.graphicsList["Resolution"][1]), (0,0,0), (int((338/856) * self.screenWidth), int((170/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Fullscreen: ' + str(self.graphicsList["Fullscreen"][0]), (0,0,0), (int((338/856) * self.screenWidth), int((230/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Music Volume: ' + str(int(self.graphicsList["Music"][0] * 100)) + '%', (0,0,0), (int((338/856) * self.screenWidth), int((290/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Sound Volume: ' + str(int(self.graphicsList["Sound"][0] * 100)) + '%', (0,0,0), (int((338/856) * self.screenWidth), int((350/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Done', (0,0,0), (int((338/856) * self.screenWidth), int((430/480) * self.screenHeight)))


            #Resets the leftclick read to detect when another click occours#
            self.leftClick = False
            
            for event in pg.event.get():
                #Ends main game loop once quit event is fired#
                if event.type == pg.QUIT:
                    self.changingGraphics = False
                    self.changingOptions = False
                    self.selectingMap = False
                    self.gameRunning = False
                    self.quit = True

                if event.type == pg.KEYDOWN:

                    #When pressed returns player to previous menu#
                    if event.key == pg.K_ESCAPE:
                        self.changingGraphics = False

                #Checks for a mouse click and if so sets leftClick to true#
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.leftClick = True

                #Resizes surface when window size changes#
                #if event.type == pg.VIDEORESIZE:
                #    surface = pg.display.set_mode((event.w, event.h),pg.RESIZABLE)
                #    self.screenWidth = event.w
                #    self.screenHeight = event.h
            
            pg.display.flip()

    
    
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

                #Resizes surface when window size changes#
                #if event.type == pg.VIDEORESIZE:
                #    surface = pg.display.set_mode((event.w, event.h),pg.RESIZABLE)
                #    self.screenWidth = event.w
                #    self.screenHeight = event.h
                    
            #Sets delta to current game tick rate (in this case based on frame rate)#
            self.delta = self.clock.tick(self.gameFPS)

            if self.paused == False:
                #Runs update code for player rotation, sprites, game graphics and the game window view in general#
                self.gameHandler()
                self.all_sprites.update(self.delta)
                self.view.update(self, self.player)
                self.drawGame()
                self.drawPlayerInfo()

            else:
                #Runs the games pause menu stoping all game updates#
                self.pauseMenu()
            
            pg.display.flip()


    def pauseMenu(self):
        #Draws the game screen in place every frame#
        self.drawGame()

        #Creats transparent overlays for background#
        self.transOverlayLight = pg.Surface(self.screen.get_size()).convert_alpha()
        self.transOverlayLight.fill(( 0, 0, 0, 120))

        self.transOverlayDark = pg.Surface((self.screenWidth /  4, self.screenHeight)).convert_alpha()
        self.transOverlayDark.fill(( 0, 0, 0, 60))

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
                self.options()

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

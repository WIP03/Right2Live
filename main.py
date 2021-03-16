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
###############################################################################
#   * Work on Upgrades.                                                       #
#   * Add upgrade shops (Weapon Mod limit of 3).                              #
#   * Add customisation (including new menu for it).                          #
#   * Level system (each round 1xp which increase by 1 after every 5 rounds). #
#   * Add skill tree where points are given to spend after each level.        #
#   * Allow player new customisation after each level (up to 10).             #
#   * Fix bug which skips animations and kills entities when game is paused.  #
###############################################################################
#   * Basic ai with pathfinding.                                              #
#   - Improved player collision and movement to work better with rotation.    #
#   - Make full screen and resoultions scale corretly to the pc's screen.     #
#                                                                             #
#   Tasks Complete(19/21)                                                     #
###############################################################################

#Imports all needed libraries and hide pygame prompt#
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
import random, math, time, json, copy

#Local librarie imports#
import entity, tile, gameMap, tree, listManipulation

#Main game class#
class Game():

    def __init__(self):
        #Initialises pygame#
        pg.init()
        pg.font.init()

        #Initialisation of values for keys from Json file (if file doesn't exist then one is created from base Json)#
        self.keys = '{"North": ["w",119],"South": ["s",115],"East": ["d",100],"West": ["a",97],"Shoot": ["space",32],"Reload": ["r",114],"Switch Weapon": ["1",49],"Interact": ["2",50]}'        
        try:
            with open(os.path.join("controls.json")) as f:
                self.keys = json.load(f)
                
        except:
            with open(os.path.join("controls.json"), 'w') as f:
                json.dump(self.keys, f)

        self.keyList = json.loads(self.keys)

        #Initialisation of values for graphics and audio control (if file doesn't exist then one is created from base Json)#
        self.graphicsSettings = '{"AntiAliasing": [true], "Resolution": [856,480], "Fullscreen": [false], "Music": [1.0], "Sound": [1.0]}'

        try:
            with open(os.path.join("graphics.json")) as f:
                self.graphicsSettings = json.load(f)
                
        except:
            with open(os.path.join("graphics.json"), 'w') as f:
                json.dump(self.graphicsSettings, f)

        self.graphicsList = json.loads(self.graphicsSettings)
        
        #Changes game resoloution to not exceed monitor size#
        self.screenWidth, self.screenHeight  = self.graphicsList["Resolution"]
        
        if (self.screenWidth > pg.display.list_modes()[0][0]) or (self.screenHeight > pg.display.list_modes()[0][1]):

            self.graphicsList["Resolution"] = (856,480)
            self.graphicsSettings = json.dumps(self.graphicsList)
            with open(os.path.join("graphics.json"), 'w') as f:
                json.dump(self.graphicsSettings, f)

            self.screenWidth, self.screenHeight  = self.graphicsList["Resolution"]
        
        
        
        #Setup for player profile #
        self.updatePlayerProfile(True)
        self.skillTree = tree.skillTree()
        
        if self.profileList["TreeUnlocks"] == []:

            #Adds all the nodes to the tree (Node Name, parent node number, description of node function)#
            self.skillTree.addNodes("Extra Points", '0', ["Gives player +100", "starting points each game."])#

            self.skillTree.addNodes("Health Boost One",'1', ["Gives the player +5 health","at the start of game."])#
            self.skillTree.addNodes("Healing Speed Boost",'2', ["Decreases the time before a","player can heal by 0.5 seconds."])#
            self.skillTree.addNodes("Health Powerup Increase",'3', ["Health powerup give the","player an extra 50 health."])#
            self.skillTree.addNodes("Health Boost Two",'3', ["Gives the player +5 health","at the start of game."])#

            self.skillTree.addNodes("Speed Boost One",'1', ["Gives the player a base speed","increase of 5% each game."])#
            self.skillTree.addNodes("Kill Point Boost",'6', ["Increase point gain","for a kill by +5."])#
            self.skillTree.addNodes("Points Powerup Increase",'7', ["Increase length of the","points powerup by 2 seconds."])#
            self.skillTree.addNodes("Speed Boost Two",'7', ["Gives the player a base speed","increase of 5% each game."])#

            self.skillTree.addNodes("Reload Boost One",'1', ["Decrease the time to","reload a weapon by 5%."])#
            self.skillTree.addNodes("Damage Boost",'10', ["Increase the damage","a player deals by +2."])#
            self.skillTree.addNodes("Damage Powerup Increase",'11', ["Increase length of damage","powerup by 2 seconds."])#
            self.skillTree.addNodes("Reload Boost Two",'11', ["Decrease the time to","reload a weapon by 5%."])#

            self.profileList["TreeUnlocks"] = self.skillTree.nodes
            self.profileValues = json.dumps(self.profileList)
            with open(os.path.join("profile.json"), 'w') as f:
                json.dump(self.profileValues, f)
                
        else:
            self.skillTree.nodes = self.profileList["TreeUnlocks"]
        
        #Initialisation of global constants#
        self.tileSize = 36
        self.gameFPS = 60
        self.delta = 1.0
        self.pausedTime = 0
        
        #Colour customisation constants (Skin, Hair, Clothes, Backpack)#
        self.colour = [[(236,188,180),(209,163,164),(197,140,133),(161,102,94),(80,51,53)],
                      [(206,206,206),(250,240,190),(165,58,0),(124,10,2),(90,56,37)],
                      [(237,2,10),(80,168,62),(80,168,227),(255,202,43),(241, 80, 150)],
                      [(244,101,40),(53,156,9),(173,222,250),(245,208,98),(255,169,206)]]
        
        #Sets up game window and game clock#
        
        if self.graphicsList["Fullscreen"][0]:
            self.screen = pg.display.set_mode((self.screenWidth, self.screenHeight), pg.FULLSCREEN)
        else:
            self.screen = pg.display.set_mode((self.screenWidth, self.screenHeight))
            
        pg.display.set_caption("Right2Live Dev Build")
        self.clock = pg.time.Clock()
        
        #Sets window icon placeholder#
        gameIcon = pg.image.load(os.path.join("Textures","icon.png"))
        pg.display.set_icon(gameIcon)
        
        #Sets the image for menu backgrounds#
        self.backGround = pg.image.load(os.path.join("Textures","Menus","Background","mainMenu.png"))
        self.optionBackGround = pg.image.load(os.path.join("Textures","Menus","Background","optionMenu.png"))
        self.deathBackGround = pg.image.load(os.path.join("Textures","Menus","Background","deathMenu.png"))

        #Sets the images for the menu overlays#
        self.RED_CROSS = pg.image.load(os.path.join("Textures","Menus","Overlays","redCross.png")).convert_alpha()#
        self.TREE_LINES = pg.image.load(os.path.join("Textures","Menus","Overlays","skillTreeLines.png")).convert_alpha()

        self.CUSTOMISATION_LAYER1 = pg.image.load(os.path.join("Textures","Menus","Overlays","Player","Layer1.png")).convert_alpha()
        self.CUSTOMISATION_LAYER2 = pg.image.load(os.path.join("Textures","Menus","Overlays","Player","Layer2.png")).convert_alpha()
        self.CUSTOMISATION_LAYER3 = pg.image.load(os.path.join("Textures","Menus","Overlays","Player","Layer3.png")).convert_alpha()
        self.CUSTOMISATION_LAYER4 = pg.image.load(os.path.join("Textures","Menus","Overlays","Player","Layer4.png")).convert_alpha()
        self.CUSTOMISATION_LAYER5 = pg.image.load(os.path.join("Textures","Menus","Overlays","Player","Layer5.png")).convert_alpha()

        #Initialises all sprite groups#
        self.all_sprites = pg.sprite.Group()
        self.all_tiles = pg.sprite.Group()
        self.all_bullets = pg.sprite.Group()
        self.all_magic = pg.sprite.Group()
        self.all_mobs = pg.sprite.Group()
        self.all_players = pg.sprite.Group()
        self.all_powerups = pg.sprite.Group()
        self.all_bodies = pg.sprite.Group()

        self.all_floor = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()
        self.all_shops = pg.sprite.Group()
        self.all_doors = pg.sprite.Group()
        self.all_upgrades = pg.sprite.Group()
        self.all_spawners = pg.sprite.Group()
        self.all_perks = pg.sprite.Group()

    def setupGame(self, mapFile):
        #Creates round varibles#
        self.round = 1
        self.previousRound = 1
        self.enemyList = ["EMPTY"]
        self.lastSpawnTime = pg.time.get_ticks()
        self.roundEndTime = pg.time.get_ticks()
        self.roundPause = [False,0,0]
        
        self.currentGameXp = 0
        self.currentEnemyKills = 0
        playerSpawn = (0,0)
        
        #Tile texture initialisation#
        self.TILE_SET = pg.image.load(os.path.join("Textures","World","TileSet.png")).convert_alpha()
        
        self.POWERUP_SET = pg.image.load(os.path.join("Textures","Entities","Upgrades","powerUpsFloor.png")).convert_alpha()
        self.POWERUPINV_SET = pg.image.load(os.path.join("Textures","Entities","Upgrades","powerUpsIcons.png")).convert_alpha()
        self.WEAPONUPGRADE_SET = pg.image.load(os.path.join("Textures","Entities","Upgrades","upgradeIcons.png")).convert_alpha()
        self.PERK_SET = pg.image.load(os.path.join("Textures","Entities","Upgrades","perkIcons.png")).convert_alpha()

        self.ENEMY_BODIES = pg.image.load(os.path.join("Textures","Entities","Enemies","EnemyBodies.png")).convert_alpha()
        
        self.map = gameMap.Map(self, mapFile)
        self.enemies = []
        self.magicProjectiles = []
        self.aiMap = []

        #Draws gameboard by placing tiles in set locations#
        for x in range(0, self.map.tilesX):
            mapLine = ""
            for y in range(0, self.map.tilesY):
                #Sets the tile to a given texture and sets whether is a wall or not#
                if self.map.gameboard[x][y][0] == "TILE":
                    tile.Tile(self, y, x, self.map.gameboard[x][y][1][1][0], self.map.gameboard[x][y][1][1][1], self.map.gameboard[x][y][1][0])

                    #Adds tiles to ai map (different if is a wall or not)#
                    if self.map.gameboard[x][y][1][0]:
                        mapLine += "#"
                    else:
                        mapLine += "*"
                
                #Sets up a shop on the map for the given weapon#
                if self.map.gameboard[x][y][0] == "SHOP":
                    tile.Tile(self, y, x, self.map.gameboard[x][y][1][1][0], self.map.gameboard[x][y][1][1][1], False)
                    tile.Shop(self, y, x, self.map.gameboard[x][y][1][0])
                    mapLine += "*"

                #Sets up a door on the map with different texture given is verticle or horizontal#
                if self.map.gameboard[x][y][0] == "DOOR":
                    tile.Tile(self, y, x, self.map.gameboard[x][y][1][1][0], self.map.gameboard[x][y][1][1][1], False)
                    if self.map.gameboard[x][y][1][0]:
                        tile.Door(self, y, x, "Vet", self.map.gameboard[x][y][1][2])
                    else:
                        tile.Door(self, y, x, "Hoz", self.map.gameboard[x][y][1][2])
                    mapLine += "D"

                #Sets up a upgrade shop on the map for the given upgrade#   
                if self.map.gameboard[x][y][0] == "UPGRADE":
                    tile.Tile(self, y, x, self.map.gameboard[x][y][1][1][0], self.map.gameboard[x][y][1][1][1], False)
                    tile.Upgrade(self, y, x, self.map.gameboard[x][y][1][0])
                    mapLine += "*"

                if self.map.gameboard[x][y][0] == "PERK":
                    tile.Tile(self, y, x, self.map.gameboard[x][y][1][1][0], self.map.gameboard[x][y][1][1][1], False)
                    tile.Perks(self, y, x, self.map.gameboard[x][y][1][0])
                    mapLine += "*"

                #Sets up an enemy spwaner and gives it is door locations for doors is connected to#
                if self.map.gameboard[x][y][0] == "SPAWNER":
                    tile.Tile(self, y, x, self.map.gameboard[x][y][1][0], self.map.gameboard[x][y][1][1], False)
                    tile.Spawner(self, y, x, self.map.gameboard[x][y][2])
                    mapLine += "*"

                #Sets the players spawn point which is then used when the map is all loaded to spawn the player#
                if self.map.gameboard[x][y][0] == "PLAYER":
                    tile.Tile(self, y, x, self.map.gameboard[x][y][1][0], self.map.gameboard[x][y][1][1], False)
                    playerSpawn = (y*36,x*36)

            #Adds the map line to the ai map#
            self.aiMap.append(mapLine)

        #Removes base map when nolonger needed to save on memory#
        self.map.gameboard = []
        
        #Sets up the game classes in a list (for upgrades: 1 Reload Speed, 2 Shoot Speed, 3 Weapon Damage, 4 Clip Size, 5 Burst(2 shot))#
        classes = [[["Pistol",[1]], ["",[]], 1, 1],
                   [["Pistol",[2]], ["",[]], 1.25, 0.75],
                   [["Pistol",[3]], ["",[]], 0.8, 1.25]]
        
        #Creates player entity#
        self.player = entity.player(self, playerSpawn, classes[self.classNum])

        #Creates map view#
        self.view = gameMap.MapView(self.map.pixelX, self.map.pixelY)

    def createText(self, font, size, text, colour, position):
        #Funtion used to create text easily ingame#
        myfont = pg.font.SysFont(font, size)
        textsurface = myfont.render(text, self.graphicsList["AntiAliasing"][0], colour)
        self.screen.blit(textsurface, position)

    def createTextCentered(self, font, size, text, colour, position):
        #Funtion used to create text easily ingame#
        myfont = pg.font.SysFont(font, size)
        textsurface = myfont.render(text, self.graphicsList["AntiAliasing"][0], colour)
        text_rect = textsurface.get_rect(center=position)
        self.screen.blit(textsurface, text_rect)
    
    def drawGame(self):
        #Draws all content in the window including sprites in the designated map view#

        self.screen.fill((255,255,255))
        #self.all_sprites.draw(self.screen)
        #self.all_floor.draw(self.screen)
        #self.all_tiles.draw(self.screen)
        #self.all_walls.draw(self.screen)
        #self.all_shops.draw(self.screen)
        #self.all_upgrades.draw(self.screen)
        #self.all_perks.draw(self.screen)
        #self.all_spawners.draw(self.screen)
        #self.all_bodies.draw(self.screen)
        #self.all_powerups.draw(self.screen)
        #self.all_mobs.draw(self.screen)
        #self.all_players.draw(self.screen)
        #self.all_doors.draw(self.screen)
        #self.all_bullets.draw(self.screen)
        #self.all_magic.draw(self.screen)

        spriteGroups = [self.all_sprites, self.all_floor, self.all_tiles, self.all_walls, self.all_shops, self.all_upgrades, self.all_perks, self.all_spawners, self.all_bodies, self.all_powerups, self.all_mobs, self.all_players, self.all_doors, self.all_bullets, self.all_magic]

        for i in spriteGroups:
            for sprites in i:
                self.screen.blit(sprites.image, self.view.createView(sprites))
        pass

    def drawPlayerInfo(self):
        
        #Initalises some varibles for the screen#
        textColour = (255,255,255)
        self.transOverlay = pg.Surface(( int((210/856) * self.screenWidth),  int((115/480) * self.screenHeight))).convert_alpha()
        self.transOverlay.fill(( 0, 0, 0, 80))
        
        self.transOverlayShop = pg.Surface(( int((190/856) * self.screenWidth),  int((80/480) * self.screenHeight))).convert_alpha()
        self.transOverlayShop.fill(( 0, 0, 0, 80))

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
        
        #Health and points info#
        self.screen.blit(self.transOverlay, (int((650/856) * self.screenWidth), int((0/480) * self.screenHeight)))
        self.createText('baskervilleoldface', int((30/480) * self.screenHeight), "Health: " + str(self.player.health[1]), (255,255,255), (int((656/856) * self.screenWidth), int((20/480) * self.screenHeight)))
        self.createText('baskervilleoldface', int((30/480) * self.screenHeight), "Points: " + str(self.player.points), (255,255,255), (int((656/856) * self.screenWidth), int((55/480) * self.screenHeight)))
        
        #Shows current round#
        self.screen.blit(self.transOverlayShop, (int((790/856) * self.screenWidth), int((420/480) * self.screenHeight)))
        roundColour = (255,255,255)
        if (pg.time.get_ticks() - self.roundEndTime > 10000):
            roundColour = (214,26,26)
        self.createTextCentered('baskervilleoldface', int((50/480) * self.screenHeight), str(self.round), roundColour, (int((823/856) * self.screenWidth), int((455/480) * self.screenHeight)))
        
        #Shop Info#
        self.purchaseGui(self.player.shopInfo, (str(self.player.shopInfo[1])), True)
        self.purchaseGui(self.player.doorInfo, "Open Door", True)
        self.purchaseGui(self.player.upgradeInfo, str(self.player.upgradeInfo[1]), True)
        self.purchaseGui(self.player.perkInfo, str(self.player.perkInfo[1]), True)

        #Draws weapon upgrade images#
        for i in range(3):
            if (len(self.player.currentWeapons[1][self.player.currentWeapons[0]][3])) >= (i + 1):
                self.screen.blit(self.WEAPONUPGRADE_SET, (int(((15+(30*i))/856) * self.screenWidth),int((90/480) * self.screenHeight)), ((20*self.player.currentWeapons[1][self.player.currentWeapons[0]][3][i]),0,20,20))
            else:
                self.screen.blit(self.WEAPONUPGRADE_SET, (int(((15+(30*i))/856) * self.screenWidth),int((90/480) * self.screenHeight)), (0,0,20,20))

        #Draws weapon upgrade images#
        for i in range(3):
            if (len(self.player.perkDrawOrder) >= (i + 1)):
                self.screen.blit(self.PERK_SET, (int(((665+(30*i))/856) * self.screenWidth),int((90/480) * self.screenHeight)), ((20*(self.player.perkDrawOrder[i]+1)),0,20,20))
            else:
                self.screen.blit(self.PERK_SET, (int(((665+(30*i))/856) * self.screenWidth),int((90/480) * self.screenHeight)), (0,0,20,20))
        
        #Draws the powerup in order of length of use left#
        self.screen.blit(self.transOverlayShop, (int((-50/856) * self.screenWidth), int((420/480) * self.screenHeight)))
        sortTimes = listManipulation.bubbleSortPowerUps([[0,self.player.powerups[0][1]],[1,self.player.powerups[1][1]],[2,self.player.powerups[2][1]]])
        donePowerUps = 0
        for i in range(3):
            iconPosition = 0
            self.screen.blit(self.POWERUPINV_SET, (int(((15+(40*(i)))/856) * self.screenWidth),int((435/480) * self.screenHeight)), (150,0,30,30))

            if sortTimes[i][0] == 1:
                if self.player.powerups[1][2] == 2:
                    iconPosition = 1
                elif self.player.powerups[1][2] == 3:
                    iconPosition = 2
                else:
                    iconPosition = 3
            elif sortTimes[i][0] == 2:
                iconPosition = 4

            if ((pg.time.get_ticks() - sortTimes[i][1]) < 20000) and (sortTimes[i][1] != 0):
                if (pg.time.get_ticks() - sortTimes[i][1]) >= 15000:
                    self.screen.blit(self.POWERUPINV_SET, (int(((15+(40*(i-donePowerUps)))/856) * self.screenWidth),int((435/480) * self.screenHeight)), ((30*iconPosition),30,30,30))
                else:
                    self.screen.blit(self.POWERUPINV_SET, (int(((15+(40*(i-donePowerUps)))/856) * self.screenWidth),int((435/480) * self.screenHeight)), ((30*iconPosition),0,30,30))

            else:
                donePowerUps += 1
                
            
    def purchaseGui(self, info, text, showCost):
        #Code is used to show the player the shop values and if they can afford then item#
        if info[0]:
            self.screen.blit(self.transOverlayShop, (int((333/856) * self.screenWidth), int((390/480) * self.screenHeight)))
            
            if (showCost):
                self.createTextCentered('baskervilleoldface', int((30/480) * self.screenHeight), text, (255,255,255), (int((428/856) * self.screenWidth), int((415/480) * self.screenHeight)))

                if (self.player.upgradeInfo[3] in self.player.currentWeapons[1][self.player.currentWeapons[0]][3]) and self.player.upgradeInfo[0]:
                    self.createTextCentered('baskervilleoldface', int((30/480) * self.screenHeight), "Equipped", (214,26,26), (int((428/856) * self.screenWidth), int((450/480) * self.screenHeight)))  

                elif (self.player.perks[self.player.perkInfo[3]] == True) and (self.player.perkInfo[0]):
                    self.createTextCentered('baskervilleoldface', int((30/480) * self.screenHeight), "Perk In Use", (214,26,26), (int((428/856) * self.screenWidth), int((450/480) * self.screenHeight)))  

                elif (sum(self.player.perks) >= 3) and (self.player.perkInfo[0]):
                    self.createTextCentered('baskervilleoldface', int((30/480) * self.screenHeight), "Max Perks", (214,26,26), (int((428/856) * self.screenWidth), int((450/480) * self.screenHeight)))  
                
                elif (info[2] <= self.player.points):
                    self.createTextCentered('baskervilleoldface', int((30/480) * self.screenHeight), "Cost: " + (str(info[2])), (255,255,255), (int((428/856) * self.screenWidth), int((450/480) * self.screenHeight)))       
                
                else:
                    self.createTextCentered('baskervilleoldface', int((30/480) * self.screenHeight), "Cost: " + (str(info[2])), (214,26,26), (int((428/856) * self.screenWidth), int((450/480) * self.screenHeight)))  
            
            else:
                self.createTextCentered('baskervilleoldface', int((30/480) * self.screenHeight), text, (255,255,255), (int((428/856) * self.screenWidth), int((430/480) * self.screenHeight)))
                
    def gameHandler(self):

        #Updates angle of rotation of player based on mouse positioning and current view of screen#
        self.playerAngleCalculation()

        #Rotates the image then sets it back it the original to keep image quality (required to prevent image going blurry)#
        self.oldimage = self.player.PLAYER_SPRITE
        self.player.image = pg.transform.rotate(self.oldimage, self.angle)
        self.player.rect = self.player.image.get_rect(center=self.player.rect.center)
        self.player.image.blit(self.player.image, self.player.rect)

        #Run the round code for the game (spawns new mobs, changes round value, etc)#
        self.gameRounds()

        #Updates player xp when player enters new round#
        if self.previousRound != self.round:
            self.previousRound = (self.round)
            if self.round >= 31:
                self.currentGameXp += 7
            else:
                self.currentGameXp += ((self.round-1)//5)+1
        
        #Draws shops, doors, upgrades and spawners every round#
        for shop in self.all_shops:
            shop.image = shop.SHOP
            shop.image.blit(shop.SHOP, shop.rect)
            
        for door in self.all_doors:
            door.image = door.DOOR
            door.image.blit(door.DOOR, door.rect)
            
        for upgrade in self.all_upgrades:
            upgrade.image = upgrade.UPGRADE
            upgrade.image.blit(upgrade.UPGRADE, upgrade.rect)

        for perks in self.all_perks:
            perks.image = perks.PERKS
            perks.image.blit(perks.PERKS, perks.rect)

        for spawner in self.all_spawners:
            spawner.image = spawner.SPAWNER
            spawner.image.blit(spawner.SPAWNER, spawner.rect)

        for power in self.all_powerups:
            power.image = pg.Surface((20,20), pg.SRCALPHA, 32).convert_alpha()
            power.image.blit(self.POWERUP_SET,(0, 0), (20*power.textureStage, 20*power.type, 20, 20))

        for bodies in self.all_bodies:
            bodies.image = pg.Surface((30,30), pg.SRCALPHA, 32).convert_alpha()
            bodies.image.blit(self.ENEMY_BODIES,(0, 0), ((30*bodies.textureIndex[1]), (30*bodies.textureIndex[0]), 30, 30))
            bodies.image = pg.transform.rotate(bodies.image, bodies.angle)
            
        #Updates all mob images to current rotation maintaining transparency#
        for enemy in self.all_mobs:
            oldimagez = enemy.ENEMY_SPRITE
            enemy.image = pg.transform.rotate(oldimagez, enemy.angle)
            enemy.rect = enemy.image.get_rect(center=enemy.rect.center)
            enemy.image.blit(enemy.image, enemy.rect)

        #Updates all magic projectile images to current rotation maintaining transparency#
        for magic in self.magicProjectiles:
            oldimagez = magic.MAGIC_SPRITE
            magic.image = pg.transform.rotate(oldimagez, magic.angle)
            magic.rect = magic.image.get_rect(center=magic.rect.center)
            magic.image.blit(magic.image, magic.rect)
        
        #Checks for magic collision with player, if there is then damage is delt and is destroyed#
        hits = pg.sprite.groupcollide(self.all_players, self.all_magic, False, pg.sprite.collide_mask)
        for play in hits:
            for pro in hits[play]:
                if pro.type == "magic":
                    play.health[1] -= pro.damage
                    play.healing[2] = pg.time.get_ticks()
                    pro.kill()

        #Checks for powerup collision with player, if there is then a tempary upgrade is given and the sprite is destroyed#
        collide = pg.sprite.groupcollide(self.all_players, self.all_powerups, False, pg.sprite.collide_mask)
        for play in collide:
            for power in collide[play]:
                play.powerups[power.type][0] = True
                play.powerups[power.type][1] = pg.time.get_ticks()
                if power.type == 0:
                    play.powerups[0][2] = 2
                elif power.type == 1:
                    play.powerups[1][2] = random.choices([2,3,-1],[70,25,5])[0]
                elif power.type == 2:
                    play.powerups[2][2] = 1

                #print(str(power.type),str(play.powerups[power.type][2]))
                power.kill()

        #Checks for bullet collision with mobs, if there is then damage is delt and is destroyed (has 1 in 20 chance of double damage as a head shot)#
        hits = pg.sprite.groupcollide(self.all_mobs, self.all_bullets, False, pg.sprite.collide_mask)
        for zom in hits:
            for pro in hits[zom]:
                if pro.type == "bullet":
                    self.player.points += 10 * self.player.powerups[0][2]

                    #Extra 6 points for damage if using pick pocket#
                    if self.player.perks[2]:
                        self.player.points += 5
                    
                    if self.player.powerups[1][2] == -1:
                        zom.health = -1
                    else:
                        zom.health -= pro.damage * random.choices([1,2],[19,1])[0] * self.player.powerups[1][2]

                    pro.kill()

    def playerAngleCalculation(self):

        #Calculates the vector difference in coordinates between the player and the mouse (uses view coordinate aswell to take camera position into calculation)#
        moveVector = ( (self.mousex - self.view.viewRect.x) - self.player.rect.x, -( (self.mousey - self.view.viewRect.y) - self.player.rect.y))
        #Backup of angle created to keep same angle position if cant calculate angle#
        angleBackup = self.angle

        try:
            #Calculates angle using cos from soh cah toa#
            self.angle = math.degrees(math.acos(moveVector[0] / (math.sqrt(moveVector[0]**2 + moveVector[1]**2))))

            #Edits angle value if the vector value on the y-axis is above the player#
            if moveVector[1] < 0:
                self.angle = 360 - self.angle
            
        except:
            #Used in case the angle generated doesn't work (bottom value given is 0)#
            self.angle = angleBackup

    
    def drawMenuBackground(self, image):
        #Function is used to draw a backround of a menu using a given image#
        self.screen.fill((0,0,0))    
        self.backSurface = pg.Surface((856,480)).convert_alpha()
        self.backSurface.blit(image, (0,0))
        self.backSurface = pg.transform.scale(self.backSurface, (self.screenWidth, self.screenHeight))   
        self.screen.blit(self.backSurface, self.backSurface.get_rect())

    def gameRounds(self):
        #Sets the base values for the game round each update#
        enemyTypes = ["Zombie","Ghoul","Mage","Hound"]
        activeSpawners = []
        healthMultiplier = 0

        #Changes time values to be correct after a game pause#
        if self.roundPause[0]:
            self.roundPause[0] = False
            self.lastSpawnTime = self.roundPause[1]
            self.roundEndTime = self.roundPause[2]

        #Generates a list of all spawners which are active to use#    
        for spawns in self.all_spawners:
            if spawns.canSpawn:
                activeSpawners.append((spawns.rect.x + 2 , spawns.rect.y + 2))

        #Sets up inital round enemy composition#   
        if (self.enemyList == ["EMPTY"]) and (self.round == 1):
            self.enemyList = []
            for i in range(12):
                self.enemyList.append("Zombie")

        #Spawns enemies from the enemyList if is not empty, less then 8 enemies are present and if the times are correct to allow spawning#
        if (self.enemyList != []) and (len(self.all_mobs) < 8) and (activeSpawners != []) and (pg.time.get_ticks() - self.lastSpawnTime > 2000) and (pg.time.get_ticks() - self.roundEndTime > 10000):

            #Makes healthmultiplier for each round not increase after round 30#
            if self.round > 30:
                healthMultiplier = 30
            else:
                healthMultiplier = self.round - 1
                
            #Used to spawn enemies from the generated list #
            if self.enemyList[0] == ("Zombie"):
                entity.enemy(self, random.choice(activeSpawners), (100+(5*(healthMultiplier))), 1, 20, "Zombie.png", "Zombie")

            elif self.enemyList[0] == ("Ghoul"):
                entity.enemy(self, random.choice(activeSpawners), (50+(3*(healthMultiplier))), 1.2, 15, "Ghoul.png", "Ghoul")

            elif self.enemyList[0] == ("Mage"):
                entity.enemy(self, random.choice(activeSpawners), (160+(6*(healthMultiplier))), 0.8, 20, "Mage.png", "Mage")

            elif self.enemyList[0] == ("Hound"):
                entity.enemy(self, random.choice(activeSpawners), (20+(2*(healthMultiplier))), 1.4, 10, "HellHound.png", "Hound")

            #Removes spwaned enemy from list and sets lastSpawnTime to current time#   
            del self.enemyList[0]
            self.lastSpawnTime = pg.time.get_ticks()

        #Used to setup enemy compostions for all rounds after 1#
        elif (self.enemyList == []) and (len(self.all_mobs) == 0):
            self.round += 1

            #Used to limit enemy total per round to 40#
            if self.round < 29:
                enemiesToSpawn = 11 + self.round
            else:
                enemiesToSpawn = 40

            #Makes to so every 5 rounds is a hound round#
            if ((self.round % 5) == 0):
                for i in range(enemiesToSpawn):
                    self.enemyList.append("Hound")

            #Else makes a unique enemy list with mages (max 4), ghouls (max 6) and the rest are zombies#
            else:
                for i in range(min(4,self.round//5)):
                    self.enemyList.append("Mage")
                    enemiesToSpawn -= 1

                for i in range(min(6,self.round//4)):
                    self.enemyList.append("Ghoul")
                    enemiesToSpawn -= 1

                for i in range(enemiesToSpawn):
                    self.enemyList.append("Zombie")

                #Shuffles the list so the enemies spawn in a random order#
                random.shuffle(self.enemyList) #MAYBE ADD OWN SHUFFLE CODE?#

            #Sets a new value for the round end time#
            self.roundEndTime = pg.time.get_ticks() 
            
    
    def mainMenu(self):
        #Sets up some base values and constants#
        self.quit = False
        self.leftClick = False
        
        while not self.quit:
            #Updates current mouse poistion#
            self.mousex, self.mousey = pg.mouse.get_pos()
            
            #Clears screen of all old screen elements (NEW CODE)#
            self.drawMenuBackground(self.backGround)

            #Creats transparent overlays for background#
            self.transOverlayLight = pg.Surface(self.screen.get_size()).convert_alpha()
            self.transOverlayLight.fill(( 0, 0, 0, 120))

            self.transOverlayDark = pg.Surface((int(260/856*self.screenWidth), self.screenHeight)).convert_alpha()
            self.transOverlayDark.fill(( 0, 0, 0, 60))

            #Draws all ui elements for the main menu#
            self.screen.blit(self.transOverlayLight, (0,0))
            self.screen.blit(self.transOverlayDark, (0,0))

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
        
        self.maps = [['Dead Storage',"L1-DeadStorage.txt"],['Data Hive',"L2-DataHive.txt"],['Under Buncker',"L3-UnderBuncker.txt"]]
        self.classList = ['Base','Speed','Brute']
        self.level = 0
        self.classNum = 0
        
        while self.selectingMap:
            
            #Updates current mouse poistion#
            self.mousex, self.mousey = pg.mouse.get_pos()
            
            #Clears screen of all old screen elements (NEW CODE)#
            self.drawMenuBackground(self.optionBackGround)

            #Creats transparent overlays for background#
            self.transOverlayLight = pg.Surface(self.screen.get_size()).convert_alpha()
            self.transOverlayLight.fill(( 0, 0, 0, 120))

            self.transOverlayDark = pg.Surface((int(320/856*self.screenWidth), self.screenHeight)).convert_alpha()
            self.transOverlayDark.fill(( 0, 0, 0, 60))

            self.transOverlayCycleButtons = pg.Surface(((int(445/856*self.screenWidth)), (int(60/480*self.screenHeight)))).convert_alpha()
            self.transOverlayCycleButtons.fill(( 0, 0, 0, 60))
            
            self.transOverlayMapArt = pg.Surface(((int(445/856*self.screenWidth)), (int(220/480*self.screenHeight)))).convert_alpha()
            self.transOverlayMapArt.fill(( 0, 0, 0, 60))

            #Draws all ui elements for the map selection menu#
            self.screen.blit(self.transOverlayLight, (0,0))
            self.screen.blit(self.transOverlayDark, (0,0))
            self.screen.blit(self.transOverlayCycleButtons, ((int(375/856*self.screenWidth)), (int(345/480*self.screenHeight))))
            self.screen.blit(self.transOverlayMapArt, ((int(375/856*self.screenWidth)), (int(90/480*self.screenHeight))))
            
            #Draws a picture of the map the player has choosen (if an image for it exists#
            try:
                self.MAP_ART = pg.image.load(os.path.join("Textures","Menus","Overlays","Maps",(self.maps[self.level][0]+".png"))).convert_alpha()
            except:
                self.MAP_ART = pg.image.load(os.path.join("Textures","Menus","Overlays","Maps","Placeholder.png")).convert_alpha()
            
            newImage = pg.transform.scale(self.MAP_ART, (int((435/856) * self.screenWidth), int((210/480) * self.screenHeight)))
            self.screen.blit(newImage, (int((380/856) * self.screenWidth),int((95/480) * self.screenHeight)), (0,0,int((435/856) * self.screenWidth), int((210/480) * self.screenHeight)))
                           

            #Draws the menu button#
            homeButton = pg.Rect(int((35/856) * self.screenWidth), int((350/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            playButton = pg.Rect(int((35/856) * self.screenWidth), int((120/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))

            mapButton = pg.Rect(int((380/856) * self.screenWidth), int((350/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            
            classButton = pg.Rect(int((611/856) * self.screenWidth), int((350/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            customiseButton = pg.Rect(int((35/856) * self.screenWidth), int((190/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            treeButton = pg.Rect(int((35/856) * self.screenWidth), int((260/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))

            
            #When pressed closes the game#
            if homeButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), homeButton)
                if self.leftClick:
                    self.selectingMap = False
            else:
                pg.draw.rect(self.screen, (255, 0, 0), homeButton)

            #Starts the game for the player#
            if playButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), playButton)
                if self.leftClick:
                    self.setupGame(self.maps[self.level][1])
                    self.gameLoop()
            else:
                pg.draw.rect(self.screen, (255, 0, 0), playButton)
                
            #Opens the customisation menu#
            if customiseButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), customiseButton)
                if self.leftClick:
                    self.playerCustomisation()
            else:
                pg.draw.rect(self.screen, (255, 0, 0), customiseButton)
                
            #Opens the tree customisation menu#
            if treeButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), treeButton)
                if self.leftClick:
                    self.treeCustomisation()
            else:
                pg.draw.rect(self.screen, (255, 0, 0), treeButton)


            #Button for cycling through the maps#
            if mapButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), mapButton)
                if self.leftClick:
                    if self.level != (len(self.maps) - 1):
                        self.level += 1
                    else:
                        self.level = 0
            else:
                pg.draw.rect(self.screen, (255, 0, 0), mapButton)
                
            #Button for cycling through the classes#
            if classButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), classButton)
                if self.leftClick:
                    self.classNum += 1
                    if self.classNum == (len(self.classList)):
                        self.classNum = 0

            else:
                pg.draw.rect(self.screen, (255, 0, 0), classButton)

            #Draws all text for the map selection screen#
            self.createText('baskervilleoldface', int((50/480) * self.screenHeight), 'Map Selection', (255,0,0), (int((25/856) * self.screenWidth), int((40/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Play', (0,0,0), (int((45/856) * self.screenWidth), int((130/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Customisation', (0,0,0), (int((45/856) * self.screenWidth), int((200/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Skilltree', (0,0,0), (int((45/856) * self.screenWidth), int((270/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Back', (0,0,0), (int((45/856) * self.screenWidth), int((360/480) * self.screenHeight)))

            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Current Map:', (0,0,0), (int((480/856) * self.screenWidth), int((365/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), self.maps[self.level][0], (0,0,0), (int((480/856) * self.screenWidth), int((390/480) * self.screenHeight)))

            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Current Class:', (0,0,0), (int((711/856) * self.screenWidth), int((365/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), self.classList[self.classNum], (0,0,0), (int((711/856) * self.screenWidth), int((390/480) * self.screenHeight)))
            
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
    
    
    
    
    def playerCustomisation(self):
        #Sets up some base values and constants#
        self.playerCustomising = True
        self.leftClick = False
        customisation = 0
        unlockLevel = "N/A"

        self.updatePlayerCustomisationTexture()
        
        while self.playerCustomising:
            
            #Updates current mouse poistion#
            self.mousex, self.mousey = pg.mouse.get_pos()
            
            #Clears screen of all old screen elements#
            self.drawMenuBackground(self.optionBackGround)

            #Creats transparent overlays for background#
            self.transOverlayLight = pg.Surface(self.screen.get_size()).convert_alpha()
            self.transOverlayLight.fill(( 0, 0, 0, 120))

            self.transOverlayDark = pg.Surface((int(320/856*self.screenWidth), self.screenHeight)).convert_alpha()
            self.transOverlayDark.fill(( 0, 0, 0, 60))

            self.transOverlayColours = pg.Surface(((int(60/856*self.screenWidth)), (int(285/480*self.screenHeight)))).convert_alpha()
            self.transOverlayColours.fill(( 0, 0, 0, 60))

            #Draws all ui elements for the customisation menu#
            self.screen.blit(self.transOverlayLight, (0,0))
            self.screen.blit(self.transOverlayDark, (0,0))

            #Draws the menu button#
            homeButton = pg.Rect(int((35/856) * self.screenWidth), int((350/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
                         
            skinButton = pg.Rect(int((35/856) * self.screenWidth), int((100/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            hairButton = pg.Rect(int((35/856) * self.screenWidth), int((160/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            shirtButton = pg.Rect(int((35/856) * self.screenWidth), int((220/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            backpackButton = pg.Rect(int((35/856) * self.screenWidth), int((280/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))

            #Takes player back to game option menu.#
            if homeButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), homeButton)
                if self.leftClick:
                    self.playerCustomising = False
            else:
                pg.draw.rect(self.screen, (255, 0, 0), homeButton)

             
            #Click to give player option to choose skin tone.#
            if skinButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), skinButton)
                if self.leftClick:
                    if customisation != 1:
                        customisation = 1
                    else:
                        customisation = 0

            elif customisation == 1:
                pg.draw.rect(self.screen, (235, 40, 40), skinButton)
                
            else:
                pg.draw.rect(self.screen, (255, 0, 0), skinButton)
                
            #Click to give player option to choose hair colour.#
            if hairButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), hairButton)
                if self.leftClick:
                    if customisation != 2:
                        customisation = 2
                    else:
                        customisation = 0

            elif customisation == 2:
                pg.draw.rect(self.screen, (235, 40, 40), hairButton)

            else:
                pg.draw.rect(self.screen, (255, 0, 0), hairButton)
                
            #Click to give player option to choose cloth colour.#
            if shirtButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), shirtButton)
                if self.leftClick:
                    if customisation != 3:
                        customisation = 3
                    else:
                        customisation = 0

            elif customisation == 3:
                pg.draw.rect(self.screen, (235, 40, 40), shirtButton)

            else:
                pg.draw.rect(self.screen, (255, 0, 0), shirtButton)
                
            #Click to give player option to choose backpack colour.#
            if backpackButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), backpackButton)
                if self.leftClick:
                    if customisation != 4:
                        customisation = 4
                    else:
                        customisation = 0

            elif customisation == 4:
                pg.draw.rect(self.screen, (235, 40, 40), backpackButton)
            
            else:
                pg.draw.rect(self.screen, (255, 0, 0), backpackButton)

            #Draws the choosable colours on screen and if the players level is high enough allows the player to choose that colour#
            if customisation != 0:
                #Draws the transparent overlay for the colour choices#
                self.screen.blit(self.transOverlayColours, (int((735/856) * self.screenWidth),int((95/480) * self.screenHeight)))
                
                for i in range (5):
                    unlocked = True
                    
                    cusButton = pg.Rect(int((740/856) * self.screenWidth), int(((100 + (i * 55))/480) * self.screenHeight), int((50/856) * self.screenWidth), int((50/480) * self.screenHeight))
                    pg.draw.rect(self.screen, self.colour[customisation-1][i], cusButton)

                    if (((customisation == 3) and ((self.profileList["Xp"][0] // 50) < (2*i + 2))) or ((customisation == 4) and ((self.profileList["Xp"][0] // 50) < (2*i + 1)))) and (i != 0):
                            unlocked = False
                            newImage = pg.transform.scale(self.RED_CROSS, (int((52/856) * self.screenWidth), int((52/480) * self.screenHeight)))
                            self.screen.blit(newImage, (int((739/856) * self.screenWidth),int(((99 + (i * 55))/480) * self.screenHeight)), (0,0,int((52/856) * self.screenWidth), int((52/480) * self.screenHeight)))
                           
                    if cusButton.collidepoint((self.mousex, self.mousey)):
                        if self.leftClick:

                            unlockLevel = "N/A"
                            if(i != 0):
                                if(customisation == 3):
                                    unlockLevel = str(2*i + 2)
                                elif(customisation == 4):
                                    unlockLevel = str(2*i + 1)
                            
                            if unlocked:
                                self.profileList["CurrentOutfit"][customisation-1] = i
                                self.profileValues = json.dumps(self.profileList)
                                with open(os.path.join("profile.json"), 'w') as f:
                                    json.dump(self.profileValues, f)

                                self.updatePlayerCustomisationTexture()

            #Draw a player texture which uses the currently selected colours to give the player an idea about how there charater will look#
            newCustomisationImage = pg.transform.scale(self.PLAYER_CUSTOMISATION_SPRITE, (int((228/856) * self.screenWidth), int((288/480) * self.screenHeight)))
            self.screen.blit(newCustomisationImage, (int((400/856) * self.screenWidth),int((95/480) * self.screenHeight)), (0,0,int((228/856) * self.screenWidth), int((288/480) * self.screenHeight)))                    

            #Draws all text for the map selection screen#
            self.createText('baskervilleoldface', int((50/480) * self.screenHeight), 'Customisation', (255,0,0), (int((25/856) * self.screenWidth), int((40/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Skin Tone', (0,0,0), (int((45/856) * self.screenWidth), int((110/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Hair Colour', (0,0,0), (int((45/856) * self.screenWidth), int((170/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Shirt Colour', (0,0,0), (int((45/856) * self.screenWidth), int((230/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Backpack Colour', (0,0,0), (int((45/856) * self.screenWidth), int((290/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Back', (0,0,0), (int((45/856) * self.screenWidth), int((360/480) * self.screenHeight)))

            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), ('Required Level: '+str(unlockLevel)), (173, 9, 9), (int((765/856) * self.screenWidth), int((430/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), ('Current Level: '+str(self.profileList["Xp"][0] // 50)), (173, 9, 9), (int((765/856) * self.screenWidth), int((460/480) * self.screenHeight)))
            
            #Resets the leftclick read to detect when another click occours#
            self.leftClick = False
            
            for event in pg.event.get():
                #Ends main game loop once quit event is fired#
                if event.type == pg.QUIT:
                    self.playerCustomising = False
                    self.selectingMap = False
                    self.quit = True

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.playerCustomising = False

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


    def updatePlayerCustomisationTexture(self):
        
        #Sets the player customisation texture based on there current choosen colours by the player#
        self.temp1 = pg.Surface((228,288), pg.SRCALPHA, 32).convert_alpha()
        self.temp1.blit(self.CUSTOMISATION_LAYER1,(0, 0))
        self.temp1.fill((self.colour[0][self.profileList["CurrentOutfit"][0]][0], self.colour[0][self.profileList["CurrentOutfit"][0]][1], self.colour[0][self.profileList["CurrentOutfit"][0]][2], 128), special_flags=pg.BLEND_MULT)
        
        self.temp2 = pg.Surface((228,288), pg.SRCALPHA, 32).convert_alpha()
        self.temp2.blit(self.CUSTOMISATION_LAYER2,(0, 0))
        self.temp2.fill((self.colour[2][self.profileList["CurrentOutfit"][2]][0], self.colour[2][self.profileList["CurrentOutfit"][2]][1], self.colour[2][self.profileList["CurrentOutfit"][2]][2], 128), special_flags=pg.BLEND_MULT)
        
        self.temp3 = pg.Surface((228,288), pg.SRCALPHA, 32).convert_alpha()
        self.temp3.blit(self.CUSTOMISATION_LAYER3,(0, 0))
        self.temp3.fill((self.colour[1][self.profileList["CurrentOutfit"][1]][0], self.colour[1][self.profileList["CurrentOutfit"][1]][1], self.colour[1][self.profileList["CurrentOutfit"][1]][2], 128), special_flags=pg.BLEND_MULT)
        
        self.temp4 = pg.Surface((228,288), pg.SRCALPHA, 32).convert_alpha()
        self.temp4.blit(self.CUSTOMISATION_LAYER4,(0, 0))
        self.temp4.fill((self.colour[3][self.profileList["CurrentOutfit"][3]][0], self.colour[3][self.profileList["CurrentOutfit"][3]][1], self.colour[3][self.profileList["CurrentOutfit"][3]][2], 128), special_flags=pg.BLEND_MULT)
        
        self.temp5 = pg.Surface((228,288), pg.SRCALPHA, 32).convert_alpha()
        self.temp5.blit(self.CUSTOMISATION_LAYER5,(0, 0))
        
        self.PLAYER_CUSTOMISATION_SPRITE = pg.Surface((228,288), pg.SRCALPHA, 32).convert_alpha()
        
        self.PLAYER_CUSTOMISATION_SPRITE.blit(self.temp1, self.temp1.get_rect())
        self.PLAYER_CUSTOMISATION_SPRITE.blit(self.temp2, self.temp2.get_rect())
        self.PLAYER_CUSTOMISATION_SPRITE.blit(self.temp3, self.temp3.get_rect())
        self.PLAYER_CUSTOMISATION_SPRITE.blit(self.temp4, self.temp4.get_rect())
        self.PLAYER_CUSTOMISATION_SPRITE.blit(self.temp5, self.temp5.get_rect())


    
    
    def treeCustomisation(self):
        #Sets up some base values and constants#
        self.treeCustomising = True
        self.leftClick = False
        customisation = 0
        selectedNode = 0

        #Makes all the screen positions for the nodes and creates the tree#
        nodePositions = [(583,100),(483,180),(483,260),(458,340),(508,340),(583,180),(583,260),(558,340),(608,340),(683,180),(683,260),(658,340),(708,340)]
        
        while self.treeCustomising:
            
            #Updates current mouse poistion#
            self.mousex, self.mousey = pg.mouse.get_pos()
            
            #Clears screen of all old screen elements#
            self.drawMenuBackground(self.optionBackGround)
            
            #Creats transparent overlays for background#
            self.transOverlayLight = pg.Surface(self.screen.get_size()).convert_alpha()
            self.transOverlayLight.fill(( 0, 0, 0, 120))

            self.transOverlayDark = pg.Surface((int(320/856*self.screenWidth), self.screenHeight)).convert_alpha()
            self.transOverlayDark.fill(( 0, 0, 0, 60))

            self.transOverlayTree = pg.Surface((int(288/856*self.screenWidth), int(315/480*self.screenHeight))).convert_alpha()
            self.transOverlayTree.fill(( 0, 0, 0, 60))

            #Draws all ui elements for the map selection menu#
            self.screen.blit(self.transOverlayLight, (0,0))
            self.screen.blit(self.transOverlayDark, (0,0))
            self.screen.blit(self.transOverlayTree, (int((450/856) * self.screenWidth),int((90/480) * self.screenHeight)))

            #Draws the menu button#
            unlockButton = pg.Rect(int((35/856) * self.screenWidth), int((290/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            homeButton = pg.Rect(int((35/856) * self.screenWidth), int((350/480) * self.screenHeight), int((200/856) * self.screenWidth), int((50/480) * self.screenHeight))
            
            #Unlocks a skill for the player if they have enough points, the skill isn't already unlocked and is parent is unlocked.#
            if unlockButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), unlockButton)
                if self.leftClick and (self.profileList["PointsToSpend"][0] > 0) and (not (self.skillTree.nodes[str(selectedNode)][1])) and (self.skillTree.nodes[self.skillTree.nodes[str(selectedNode)][2]][1]):
                    self.skillTree.unlockSkill(str(selectedNode))
                    self.profileList["TreeUnlocks"] = self.skillTree.nodes
                    self.profileList["PointsToSpend"][0] -= 1

                    self.profileValues = json.dumps(self.profileList)
                    with open(os.path.join("profile.json"), 'w') as f:
                        json.dump(self.profileValues, f)
            else:
                pg.draw.rect(self.screen, (255, 0, 0), unlockButton) 
            
            #Takes player back to game option menu.#
            if homeButton.collidepoint((self.mousex, self.mousey)):
                pg.draw.rect(self.screen, (255, 54, 54), homeButton)
                if self.leftClick:
                    self.treeCustomising = False
            else:
                pg.draw.rect(self.screen, (255, 0, 0), homeButton) 

            #Draws the lines which are used in the skill tree#
            newTreeImage = pg.transform.scale(self.TREE_LINES, (int((268/856) * self.screenWidth), int((249/480) * self.screenHeight)))
            self.screen.blit(newTreeImage, (int((462/856) * self.screenWidth),int((110/480) * self.screenHeight)), (0,0,int((268/856) * self.screenWidth), int((249/480) * self.screenHeight)))
            
            #Draws all the tree nodes and switches selected node so that only the player can view information on that node and if possible unlock it#
            for i in range (1, len(self.skillTree.nodes)):
                cusButton = pg.Rect(int((nodePositions[i-1][0]/856) * self.screenWidth), int((nodePositions[i-1][1]/480) * self.screenHeight), int((20/856) * self.screenWidth), int((20/480) * self.screenHeight))
                
                if self.skillTree.nodes[str(i)][1] == True:
                    pg.draw.rect(self.screen, (0,255,0), cusButton)
                else:
                    pg.draw.rect(self.screen, (255,255,255), cusButton)
                
                if cusButton.collidepoint((self.mousex, self.mousey)):
                        if (self.leftClick):
                            selectedNode = i

            #Draws all text for the map selection screen#
            self.createText('baskervilleoldface', int((50/480) * self.screenHeight), 'Skill Tree', (255,0,0), (int((25/856) * self.screenWidth), int((40/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Points Available: '+str(self.profileList["PointsToSpend"][0]), (173, 12, 12), (int((593/856) * self.screenWidth), int((390/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Back', (0,0,0), (int((45/856) * self.screenWidth), int((360/480) * self.screenHeight)))

            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), self.skillTree.nodes[str(selectedNode)][0], (240, 12, 12), (int((45/856) * self.screenWidth), int((140/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), self.skillTree.nodes[str(selectedNode)][3][0], (240, 12, 12), (int((45/856) * self.screenWidth), int((210/480) * self.screenHeight)))
            self.createText('baskervilleoldface', int((20/480) * self.screenHeight), self.skillTree.nodes[str(selectedNode)][3][1], (240, 12, 12), (int((45/856) * self.screenWidth), int((240/480) * self.screenHeight)))

            #Draws skill name and description text when a node is selected#
            if selectedNode != 0:
                self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Skill Name:', (200, 9, 9), (int((45/856) * self.screenWidth), int((110/480) * self.screenHeight)))
                self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Description:', (200, 9, 9), (int((45/856) * self.screenWidth), int((180/480) * self.screenHeight)))

            #Draws the corrent text for the skill unlock button#
            if (selectedNode == 0):
                self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'No Skill Selected', (0,0,0), (int((45/856) * self.screenWidth), int((300/480) * self.screenHeight)))
            elif not(self.skillTree.nodes[self.skillTree.nodes[str(selectedNode)][2]][1]):
                self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Prerequisites Not Met', (0,0,0), (int((45/856) * self.screenWidth), int((300/480) * self.screenHeight)))
            elif (self.skillTree.nodes[str(selectedNode)][1]):
                self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Already Unlocked', (0,0,0), (int((45/856) * self.screenWidth), int((300/480) * self.screenHeight)))
            elif (self.profileList["PointsToSpend"][0] < 1):
                self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Not Enough Points', (0,0,0), (int((45/856) * self.screenWidth), int((300/480) * self.screenHeight)))
            else:
                self.createText('baskervilleoldface', int((20/480) * self.screenHeight), 'Unlock Skill?', (0,0,0), (int((45/856) * self.screenWidth), int((300/480) * self.screenHeight)))
    
            #Resets the leftclick read to detect when another click occours#
            self.leftClick = False
            
            for event in pg.event.get():
                #Ends main game loop once quit event is fired#
                if event.type == pg.QUIT:
                    self.treeCustomising = False
                    self.selectingMap = False
                    self.quit = True

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.treeCustomising = False

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
            
            #Clears screen of all old screen elements (NEW CODE)#
            self.drawMenuBackground(self.optionBackGround)

            #Creats transparent overlays for background#
            self.transOverlayLight = pg.Surface(self.screen.get_size()).convert_alpha()
            self.transOverlayLight.fill(( 0, 0, 0, 120))

            self.transOverlayDark = pg.Surface((int(286/856*self.screenWidth), int(300/480*self.screenHeight))).convert_alpha()
            self.transOverlayDark.fill(( 0, 0, 0, 60))

            #Draws all ui elements for the options menu#
            self.screen.blit(self.transOverlayLight, (0,0))
            self.screen.blit(self.transOverlayDark, (int(285/856*self.screenWidth), int(30/480*self.screenHeight)))

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
            self.createTextCentered('baskervilleoldface', int((50/480) * self.screenHeight), 'Options', (255,0,0), (int((428/856) * self.screenWidth), int((65/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Controls', (0,0,0), (int((428/856) * self.screenWidth), int((160/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Graphics And Audio', (0,0,0), (int((428/856) * self.screenWidth), int((220/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Done', (0,0,0), (int((428/856) * self.screenWidth), int((280/480) * self.screenHeight)))

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
            
            #Clears screen of all old screen elements (NEW CODE)#
            self.drawMenuBackground(self.optionBackGround)

            #Clears screen of all old screen elements (NEW CODE)#
            self.drawMenuBackground(self.optionBackGround)

            #Creats transparent overlays for background#
            self.transOverlayLight = pg.Surface(self.screen.get_size()).convert_alpha()
            self.transOverlayLight.fill(( 0, 0, 0, 120))

            self.transOverlayDark = pg.Surface((int(570/856*self.screenWidth), int(430/480*self.screenHeight))).convert_alpha()
            self.transOverlayDark.fill(( 0, 0, 0, 60))

            #Draws all ui elements for the controls menu#
            self.screen.blit(self.transOverlayLight, (0,0))
            self.screen.blit(self.transOverlayDark, (int(143/856*self.screenWidth), int(30/480*self.screenHeight)))

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
            self.createTextCentered('baskervilleoldface', int((50/480) * self.screenHeight), 'Controls', (255,0,0), (int((428/856) * self.screenWidth), int((65/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'North: ' + self.keyList["North"][0], (0,0,0), (int((300/856) * self.screenWidth), int((165/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'South: ' + self.keyList["South"][0], (0,0,0), (int((300/856) * self.screenWidth), int((225/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'East: ' + self.keyList["East"][0], (0,0,0), (int((300/856) * self.screenWidth), int((285/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'West: ' + self.keyList["West"][0], (0,0,0), (int((300/856) * self.screenWidth), int((345/480) * self.screenHeight)))

            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Shoot: ' + self.keyList["Shoot"][0], (0,0,0), (int((556/856) * self.screenWidth), int((165/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Reload: ' + self.keyList["Reload"][0], (0,0,0), (int((556/856) * self.screenWidth), int((225/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Switch Weapon: ' + self.keyList["Switch Weapon"][0], (0,0,0), (int((556/856) * self.screenWidth), int((285/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Interact: ' + self.keyList["Interact"][0], (0,0,0), (int((556/856) * self.screenWidth), int((345/480) * self.screenHeight)))

            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Done', (0,0,0), (int((428/856) * self.screenWidth), int((425/480) * self.screenHeight)))


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
                            with open(os.path.join("controls.json"), 'w') as f:
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
            
            #Clears screen of all old screen elements (NEW CODE)#
            self.drawMenuBackground(self.optionBackGround)

            #Creats transparent overlays for background#
            self.transOverlayLight = pg.Surface(self.screen.get_size()).convert_alpha()
            self.transOverlayLight.fill(( 0, 0, 0, 120))

            self.transOverlayDark = pg.Surface((int(430/856*self.screenWidth), int(445/480*self.screenHeight))).convert_alpha()
            self.transOverlayDark.fill(( 0, 0, 0, 60))

            #Draws all ui elements for the graphics menu#
            self.screen.blit(self.transOverlayLight, (0,0))
            self.screen.blit(self.transOverlayDark, (int(213/856*self.screenWidth), int(30/480*self.screenHeight)))

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
                    with open(os.path.join("graphics.json"), 'w') as f:
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
                                
                                #NEW CODE#
                                if (resolutions[res + 1][0] > pg.display.list_modes()[0][0]) or (resolutions[res + 1][1] > pg.display.list_modes()[0][1]):
                                    self.graphicsList["Resolution"] = resolutions[0]
                                    
                                else:
                                    self.graphicsList["Resolution"] = resolutions[res + 1]
                                
                                complete = True

                    #Writes the change to the graphics option in the settings#
                    self.graphicsSettings = json.dumps(self.graphicsList)
                    with open(os.path.join("graphics.json"), 'w') as f:
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
                    with open(os.path.join("graphics.json"), 'w') as f:
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
                    with open(os.path.join("graphics.json"), 'w') as f:
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
                    with open(os.path.join("graphics.json"), 'w') as f:
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
            self.createTextCentered('baskervilleoldface', int((50/480) * self.screenHeight), 'Graphics and Audio', (255,0,0), (int((428/856) * self.screenWidth), int((65/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Anti Aliasing: ' + str(self.graphicsList["AntiAliasing"][0]), (0,0,0), (int((428/856) * self.screenWidth), int((120/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Resolution: ' + str(self.graphicsList["Resolution"][0]) + "x" + str(self.graphicsList["Resolution"][1]), (0,0,0), (int((428/856) * self.screenWidth), int((180/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Fullscreen: ' + str(self.graphicsList["Fullscreen"][0]), (0,0,0), (int((428/856) * self.screenWidth), int((240/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Music Volume: ' + str(int(self.graphicsList["Music"][0] * 100)) + '%', (0,0,0), (int((428/856) * self.screenWidth), int((300/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Sound Volume: ' + str(int(self.graphicsList["Sound"][0] * 100)) + '%', (0,0,0), (int((428/856) * self.screenWidth), int((360/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((20/480) * self.screenHeight), 'Done', (0,0,0), (int((428/856) * self.screenWidth), int((440/480) * self.screenHeight)))


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
                self.pausedTime = 0

            else:
                #Runs the games pause menu stoping all game updates (NEW CODE)#
                if self.pausedTime == 0:
                    self.pausedTime = pg.time.get_ticks()
                
                self.all_sprites.update(self.delta)
                self.pauseMenu()

                #Updates round time values when the game is paused#
                self.roundPause[0] = True
                self.roundPause[1] = (pg.time.get_ticks() + self.lastSpawnTime) - self.pausedTime
                self.roundPause[2] = (pg.time.get_ticks() + self.roundEndTime) - self.pausedTime

            #If the player dies the death menu is shown and all other functions stop#
            if self.player.health[1] <= 0:
                self.deathMenu()
            
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
                #self.paused = False
                #self.selectingMap = False
                #self.gameRunning = False
                #self.leftClick = False

                #self.updatePlayerProfile(False)
                
                #self.all_sprites.empty()
                #self.all_tiles.empty()
                #self.all_bullets.empty()
                #self.all_magic.empty()
                #self.all_mobs.empty()
                #self.all_players.empty()
                #self.all_walls.empty()
                #self.all_shops.empty()
                #self.all_doors.empty()
                #self.all_upgrades.empty()
                #self.all_spawners.empty()

                self.deathMenu()
                
        else:
            pg.draw.rect(self.screen, (255, 0, 0), menuButton)

        #Draws all text for pause menu#
        self.createText('baskervilleoldface', int((30/480) * self.screenHeight), 'Paused', (255,0,0), (int((25/856) * self.screenWidth), int((40/480) * self.screenHeight)))
        self.createText('baskervilleoldface', int((15/480) * self.screenHeight), 'Resume', (0,0,0), (int((60/856) * self.screenWidth), int((130/480) * self.screenHeight)))
        self.createText('baskervilleoldface', int((15/480) * self.screenHeight), 'Options', (0,0,0), (int((60/856) * self.screenWidth), int((190/480) * self.screenHeight)))
        self.createText('baskervilleoldface', int((15/480) * self.screenHeight), 'Quit To Menu', (0,0,0), (int((60/856) * self.screenWidth), int((250/480) * self.screenHeight)))



    def deathMenu(self):
        #Sets up some base values and constants#
        self.isDead = True
        self.leftClick = False

        #Gets the player there death text#
        lines = open(os.path.join("deathText.txt")).read().splitlines()
        deathText = random.choice(lines)

        while self.isDead:
            #Updates current mouse poistion#
            self.mousex, self.mousey = pg.mouse.get_pos()
            
            #Clears screen of all old screen elements#
            self.drawMenuBackground(self.deathBackGround)#self.optionBackGround)

            #Creats transparent overlays for background#
            self.transOverlayLight = pg.Surface(self.screen.get_size()).convert_alpha()
            self.transOverlayLight.fill(( 0, 0, 0, 120))

            #Draws all ui elements for the death screen#
            self.screen.blit(self.transOverlayLight, (0,0))

            
            #Draws all text for the death screen#
            self.createTextCentered('baskervilleoldface', int((45/480) * self.screenHeight), deathText, (255,0,0), (int((428/856) * self.screenWidth), int((60/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((40/480) * self.screenHeight), 'Survived to round: ' + str(self.round), (255,0,0), (int((428/856) * self.screenWidth), int((200/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((40/480) * self.screenHeight), 'Experience points earned: ' + str(self.currentGameXp), (255,0,0), (int((428/856) * self.screenWidth), int((260/480) * self.screenHeight)))
            self.createTextCentered('baskervilleoldface', int((50/480) * self.screenHeight), 'Press "' + self.keyList["Interact"][0] + '" to return to menu.', (255,0,0), (int((428/856) * self.screenWidth), int((400/480) * self.screenHeight)))
            
            for event in pg.event.get():
                #Ends main game loop once quit event is fired#
                if event.type == pg.QUIT:
                    self.isDead = False
                    self.gameRunning = False
                    self.selectingMap = False
                    self.quit = True

                if event.type == pg.KEYDOWN:

                    #When the shoot key is pressed it returns the player to start menu#
                    if event.key == self.keyList["Interact"][1]:
                        self.isDead = False
                        self.gameRunning = False
                        self.selectingMap = False

                        self.updatePlayerProfile(False)

                        self.all_sprites.empty()
                        self.all_tiles.empty()
                        self.all_floor.empty()
                        self.all_bullets.empty()
                        self.all_magic.empty()
                        self.all_mobs.empty()
                        self.all_players.empty()
                        self.all_walls.empty()
                        self.all_shops.empty()
                        self.all_doors.empty()
                        self.all_upgrades.empty()
                        self.all_spawners.empty()
                        self.all_powerups.empty()
                        self.all_bodies.empty()
                        self.all_perks.empty()


                #Resizes surface when window size changes#
                #if event.type == pg.VIDEORESIZE:
                #    surface = pg.display.set_mode((event.w, event.h),pg.RESIZABLE)
                #    self.screenWidth = event.w
                #    self.screenHeight = event.h
            
            pg.display.flip()

    def updatePlayerProfile(self, inital):

        #Setup for player profile#
        self.profileValues = '{"Name": ["user"],"Xp": [0],"PointsToSpend": [0],"PointsGained": [0],"TreeUnlocks": [],"CurrentOutfit": [0,0,0,0]}'        
        try:
            with open(os.path.join("profile.json")) as f:
                self.profileValues = json.load(f)
                
        except:
            with open(os.path.join("profile.json"), 'w') as f:
                json.dump(self.profileValues, f)

        self.profileList = json.loads(self.profileValues)

        #Adds current game xp to the profiles xp if is called during a round and not at the start of a game#
        if (inital == False):
            self.profileList["Xp"][0] += self.currentGameXp
        
        #Used to give player points which they are owed for reaching certain level or takes away unearned ones (NEW CODE)#
        if ((self.profileList["Xp"][0] // 50) > (self.profileList["PointsGained"][0])) or ((self.profileList["Xp"][0] // 50) < (self.profileList["PointsGained"][0])):
            
            if (self.profileList["Xp"][0] // 50) > (self.profileList["PointsGained"][0]):
                self.profileList["PointsToSpend"][0] += (self.profileList["Xp"][0] // 50) - self.profileList["PointsGained"][0]
                                
            elif (self.profileList["Xp"][0] // 50) < (self.profileList["PointsGained"][0]):
                self.profileList["PointsToSpend"][0] -= self.profileList["PointsGained"][0] - (self.profileList["Xp"][0] // 50)
                            
            self.profileList["PointsGained"][0] = (self.profileList["Xp"][0] // 50)
            #print(self.profileList["PointsGained"][0])
                            
        self.profileValues = json.dumps(self.profileList)
        with open(os.path.join("profile.json"), 'w') as f:
            json.dump(self.profileValues, f)
        
    
#Main game initialisation, loop and game end when window is closed#
if __name__ == '__main__':
    myGame = Game()
    myGame.mainMenu()
    pg.quit()

import pygame as pg
import random, math, time, json, os, threading
import pathfinding


#Values To Store In Profile#
#                          #
#name str                  #
#xp int                    #
#pointsToSpend int         #
#treeUnlocks Array         #
#currentOutfit Array       #


class player(pg.sprite.Sprite):
    def __init__(self, game, coord, pClass):

        #Allows other parts of class to grab values from main class#
        self.game = game
        
        #Sprite texture initialisation#
        self.image_names = ["Pistol", "PistolShooting", "Shotgun", "ShotgunShooting", "Super Shotgun", "Super ShotgunShooting", "SMG", "SMGShooting", "Rifle", "RifleShooting"]
        self.PLAYER_SPRITE_DICT = dict(((img_name, pg.image.load(os.path.join("Textures","Entities","Player","Weapons",(img_name + ".png"))).convert_alpha()) for img_name in self.image_names))

        #os.path.join("Textures","Entities","Player","Weapons",(img_name + ".png"))
        
        self.layer1 = pg.image.load(os.path.join("Textures","Entities","Player","Player","Layer1.png")).convert_alpha()
        self.layer2 = pg.image.load(os.path.join("Textures","Entities","Player","Player","Layer2.png")).convert_alpha()
        self.layer3 = pg.image.load(os.path.join("Textures","Entities","Player","Player","Layer3.png")).convert_alpha()
        self.layer4 = pg.image.load(os.path.join("Textures","Entities","Player","Player","Layer4.png")).convert_alpha()
        
        #Setup weapons for player("Name": [Ammo, Magsize, Reload time, Bullets per shot, Bullet damage, Fire rate, Spread angle, Velocity, Time before despawn, cost])#
        self.weapons = '{"Pistol": [-1, 0, 0, 1, 34, 600, 1, 0.5, 1500, 0], "Shotgun": [5, 25, 2200, 4, 27, 900, 5, 1.5, 250, 1500], "Super Shotgun": [2, 30, 2000, 7, 25, 1200, 10, 1.5, 125, 3250], "SMG": [32, 128, 2500, 1, 11, 110, 4, 1.1, 455, 1200], "Rifle": [8, 64, 3200, 1, 70, 800, 1, 1.5, 600, 2500]}'
        
        try:
            with open(os.path.join("weapons.json")) as f:
                self.weapons = json.load(f)
                
        except:
            with open(os.path.join("weapons.json"), 'w') as f:
                json.dump(self.weapons, f)

        self.weaponList = json.loads(self.weapons)
        
        #Grabs the selected player class and stores locally[weapon1, weapon2, speed multiplier, health multiplier]#
        self.playerClass = pClass
        #self.playerClass = [["Pistol",0], ["",0], 1, 1]
        
        #List of weapons in inventory (Name, Ammo, Magsize, Weapon Mods)#
        if self.playerClass[1][0] == "":
            self.currentWeapons = [0,[[ self.playerClass[0][0],self.weaponList[self.playerClass[0][0]][0],self.weaponList[self.playerClass[0][0]][1],self.playerClass[0][1]],["",0,0,[]]]]
        else:
            self.currentWeapons = [0,[[ self.playerClass[0][0],self.weaponList[self.playerClass[0][0]][0],self.weaponList[self.playerClass[0][0]][1],self.playerClass[0][1]],[ self.playerClass[1][0],self.weaponList[self.playerClass[1][0]][0],self.weaponList[self.playerClass[1][0]][1],self.playerClass[1][1]]]]


        self.updatePlayerTexture(self.returnCurrentWeaponValue(0))

        #Sets the player size and sprite#
        self.groups = game.all_sprites, game.all_players
        pg.sprite.Sprite.__init__(self, self.groups)
        
        self.image = pg.Surface((30,30)).convert_alpha()
        self.image.blit(self.PLAYER_SPRITE,(0, 0))

        #Sets player rectangle to selected image and sets player start location#
        self.rect = self.image.get_rect()

        self.coord = pg.math.Vector2(coord)
        self.rect.center = self.coord
        self.movement = pg.math.Vector2(0,0)

        #Values used for player weapons#
        self.previous_shot = 0
        self.previous_weapon_change = 0
        self.reload_time = 0
        self.shooting = False
        self.reloading = False
        
        #Other player varibles needed like time values and points are set#
        self.shop_time = 0
        self.points = 500 + (100 * sum([self.game.profileList["TreeUnlocks"]["1"][1]]))
        self.health = [int(100 * self.playerClass[3]) + (5 * sum([self.game.profileList["TreeUnlocks"]["2"][1],self.game.profileList["TreeUnlocks"]["5"][1]])),int(100 * self.playerClass[3])]
        self.healing = [50,1,0,0] #Time every heal, health gain, last hit, last health gain#
        self.speed = 300 * (self.playerClass[2] + (0.05 * sum([self.game.profileList["TreeUnlocks"]["6"][1],self.game.profileList["TreeUnlocks"]["9"][1]])))
        self.powerups = [[False,0,1],[False,0,1],[False,0,1]]
        self.perks = [False, False, False, False]
        self.perkDrawOrder = []
        #print(str(int(100 * self.playerClass[3]) + (5 * sum([self.game.profileList["TreeUnlocks"]["2"][1],self.game.profileList["TreeUnlocks"]["5"][1]]))))
        #print(str(self.game.profileList["TreeUnlocks"]["2"][1]))

        self.shopInfo = [False, "", 0]
        self.doorInfo = [False, "", 0, 0, 0]
        self.upgradeInfo = [False, "" , 0, 0]
        self.perkInfo = [False, "" , 0, 0]
        
        
        self.pausedValues = [False,0,0,0,0,0,0,0,0,0]
        
    def update(self, delta):
        #Main player update loop, called every frame#
        
        #keeps varibles while pausing to reduce bugs#
        if (self.game.paused):
            if (self.game.pausedTime != 0):
                self.pausedValues[0] = True
                values = [self.previous_shot, self.previous_weapon_change, self.reload_time, self.shop_time, self.healing[2], self.healing[3],self.powerups[0][1],self.powerups[1][1],self.powerups[2][1]]
                for i in range(1,10):
                    self.pausedValues[i] = (pg.time.get_ticks() + values[i-1]) - self.game.pausedTime
                
        else:
            
            #Resets values after game pause saving all time values#
            if self.pausedValues[0]:
                self.previous_shot,self.previous_weapon_change,self.reload_time,self.shop_time,self.healing[2],self.healing[3],self.powerups[0][1],self.powerups[1][1],self.powerups[2][1] = self.pausedValues[1:10]
                self.pausedValues[0] = False
            
            #Updates the movement of the player#
            self.playerKeypress(delta)

            #Calls code to change postion of player and update shop#
            self.updateShop()
            collision(self, self.game.all_tiles, True)
            self.enemyCollision()

            #Function which heals the player if health is not full and the time is fine for healing#
            self.healPlayer()

            
            self.powerUpsFunction()
            
            #Resets the movement vector for the player#
            self.movement = pg.math.Vector2(0,0)

        #Creates collsion mask for player#
        self.mask = pg.mask.from_surface(self.image)

    def playerKeypress(self, delta):
        #Grabing Pygame Info#
        keys = pg.key.get_pressed()
        currentTime = pg.time.get_ticks()

        #Updates the players movement per frame being greater the smaller the frame rate#
        currentSpeed = self.speed * (delta / 1000) * 0.9
        directionMovement = [0,0]
        
        #X coordinate control#

        #Move player east#
        if keys[self.game.keyList["East"][1]]:
            directionMovement[0] += 1

        #Move player west#
        if keys[self.game.keyList["West"][1]]:
            directionMovement[0] -= 1
        
        #Y coordinate control#

        #Move player north#
        if keys[self.game.keyList["North"][1]]:
            directionMovement[1] -= 1

        #Move player south#
        if keys[self.game.keyList["South"][1]]:
            directionMovement[1] += 1

        #Changes player speed if moving on both x and y#
        if (directionMovement[0] != 0) and (directionMovement[1] != 0):
            currentSpeed = math.ceil(currentSpeed * math.cos(math.radians(45)))

        #Sets the movement vector based on player input#
        self.movement[0] = currentSpeed * directionMovement[0]
        self.movement[1] = currentSpeed * directionMovement[1]

            
        
        #Weapon usage#
        if not self.reloading:
            
            #Interaction code used when interacting with non static tiles#
            if keys[self.game.keyList["Interact"][1]]:

                #Allows player to purchase a weapons of a shop if is been long enough and if they have enough points#
                if self.shopInfo[0] and (self.shopInfo[2] <= self.points) and ((currentTime - self.shop_time) >= 300):
                    self.points -= self.shopInfo[2]
                    self.shop_time = currentTime
                    
                    if (self.currentWeapons[1][0][0] == self.shopInfo[1]):
                        if (self.currentWeapons[1][0][2] != self.weaponList[self.shopInfo[1]][1]):
                            self.currentWeapons[1][0][2] =  self.weaponList[self.shopInfo[1]][1]
                        else:
                            self.points += self.shopInfo[2]
                    
                    elif self.currentWeapons[1][1][0] == self.shopInfo[1]:
                        if (self.currentWeapons[1][1][2] != self.weaponList[self.shopInfo[1]][1]):
                            self.currentWeapons[1][1][2] = self.weaponList[self.shopInfo[1]][1]
                        else:
                            self.points += self.shopInfo[2]
                    
                    elif self.currentWeapons[1][0][0] == "":
                        self.currentWeapons[1][0] = [self.shopInfo[1],self.weaponList[self.shopInfo[1]][0],self.weaponList[self.shopInfo[1]][1],[]]
                        self.currentWeapons[0] = 0
                    
                    elif self.currentWeapons[1][1][0] == "":
                        self.currentWeapons[1][1] = [self.shopInfo[1],self.weaponList[self.shopInfo[1]][0],self.weaponList[self.shopInfo[1]][1],[]]
                        self.currentWeapons[0] = 1
                    
                    else:
                        self.currentWeapons[1][self.currentWeapons[0]] = [self.shopInfo[1],self.weaponList[self.shopInfo[1]][0],self.weaponList[self.shopInfo[1]][1],[]]
                    
                    self.updatePlayerTexture(self.returnCurrentWeaponValue(0))

                #If a player has enough points allows then to open a door#
                if self.doorInfo[0] and (self.doorInfo[2] <= self.points) and ((currentTime - self.shop_time) >= 300):
                    self.points -= self.doorInfo[2]
                    self.shop_time = currentTime
                    self.doorInfo[1].kill()
                    
                    #Allows Ai to go through a door when a player opens it#
                    line = list(self.game.aiMap[self.doorInfo[4]//36])
                    line[self.doorInfo[3]//36] = "*"
                    self.game.aiMap[self.doorInfo[4]//36] = "".join(line)
                    
                    self.game.currentGameXp += 1

                #If a player has enough points it allows the to upgrade there weapon (replacing 1st upgrade if 3 are present)#  
                if self.upgradeInfo[0] and (self.upgradeInfo[2] <= self.points) and (self.upgradeInfo[3] not in self.currentWeapons[1][self.currentWeapons[0]][3]) and ((currentTime - self.shop_time) >= 300):
                    self.points -= self.upgradeInfo[2]
                    self.shop_time = currentTime
                    if (len(self.currentWeapons[1][self.currentWeapons[0]][3]) > 2):
                        del self.currentWeapons[1][self.currentWeapons[0]][3][0]
                    self.currentWeapons[1][self.currentWeapons[0]][3].append(self.upgradeInfo[3])


                #If a player has enough points it allows the player to unlock a perk (if they have less then 3 active perks)#
                if self.perkInfo[0] and (self.perkInfo[2] <= self.points) and (self.perks[self.perkInfo[3]] == False) and (sum(self.perks) < 3) and ((currentTime - self.shop_time) >= 300):
                    self.points -= self.perkInfo[2]
                    self.shop_time = currentTime
                    self.perks[self.perkInfo[3]] = True
                    self.perkDrawOrder.append(self.perkInfo[3])

                    #If the perk is long life it adds 100 to the base health#
                    if self.perkInfo[3] == 0:
                        self.health[0] += 100

            #Reloading code for if a player wants to reload when the mag is not full#
            if keys[self.game.keyList["Reload"][1]]:
                if ((4 in self.currentWeapons[1][self.currentWeapons[0]][3] and (int(self.returnCurrentWeaponValue(1)) < int(self.weaponValue(0) * 2)) or (int(self.returnCurrentWeaponValue(1)) < int(self.weaponValue(0))))) and (int(self.returnCurrentWeaponValue(2)) > 0):
                    self.reloading = True
                    self.reload_time = currentTime
                    
                    #Weapon mod which reduces reload time by 20% (id:1)#
                    if 1 in self.currentWeapons[1][self.currentWeapons[0]][3]:
                        self.reload_time -= self.weaponValue(2) * 0.2

            #Used to switch player weapon to the other one in there inventory#
            elif keys[self.game.keyList["Switch Weapon"][1]] and (currentTime - self.previous_weapon_change > 500):
                if not((self.currentWeapons[0] == 0 and self.currentWeapons[1][1][0] == "") or (self.currentWeapons[0] == 1 and self.currentWeapons[1][0][0] == "")):
                    if (self.currentWeapons[0] == 0):
                        self.currentWeapons[0] = 1

                    elif (self.currentWeapons[0] == 1):
                        self.currentWeapons[0] = 0

                    if self.shooting:
                        self.shooting = False

                    self.previous_weapon_change = currentTime
                    self.updatePlayerTexture(self.returnCurrentWeaponValue(0))
                    

            elif keys[self.game.keyList["Shoot"][1]]:

                #Reloads weapon if ammo is empty#
                if (int(self.returnCurrentWeaponValue(1)) == 0) and (int(self.returnCurrentWeaponValue(2)) > 0):
                    self.reloading = True
                    self.reload_time = currentTime
                    
                    #Weapon mod which reduces reload time by 20% (id:1)#
                    if 1 in self.currentWeapons[1][self.currentWeapons[0]][3]:
                        self.reload_time -= self.weaponValue(2) * 0.2

                elif currentTime - self.previous_shot > self.weaponValue(5) and ((int(self.returnCurrentWeaponValue(1)) != 0)):
                    #Used to find starting coord of the player#
                    bullCord = pg.math.Vector2(self.rect.center) + pg.math.Vector2(15,0).rotate(-self.game.angle)

                    #Sets values to see if the player if shooting and changes player texture#
                    self.shooting = True
                    self.updatePlayerTexture(self.returnCurrentWeaponValue(0) + "Shooting")
                    
                    #Weapon mod which burst fires the weapon(id:5)#
                    if (5 in self.currentWeapons[1][self.currentWeapons[0]][3]) and (int(self.returnCurrentWeaponValue(1)) != 1):
                        numberOfBullets = self.weaponValue(3) * 2
                    else:
                        numberOfBullets = self.weaponValue(3)
                    
                    #Spawns a new bullet#
                    for i in range(numberOfBullets):
                        #Weapon mod which increase damage by 25% (id:3)#
                        if 3 in self.currentWeapons[1][self.currentWeapons[0]][3]:
                            bullet(self.game, self.weaponValue(6), self.weaponValue(7), bullCord, self.weaponValue(8), math.ceil(self.weaponValue(4) * 1.25))
                        else:
                            bullet(self.game, self.weaponValue(6), self.weaponValue(7), bullCord, self.weaponValue(8), self.weaponValue(4))
                    
                    if self.weaponValue(0) != -1:
                        self.currentWeapons[1][self.currentWeapons[0]][1] -= int(numberOfBullets / self.weaponValue(3))

                    self.previous_shot = currentTime
                    
                    #Weapon mod which reduces time between shoots by 30% (id:2)#
                    if 2 in self.currentWeapons[1][self.currentWeapons[0]][3]:
                        self.previous_shot -= self.weaponValue(5) * 0.3

        #Used to revert player model to remove fire from shot#
        if currentTime - self.previous_shot > 200 and self.shooting:
            
            self.shooting = False
            self.updatePlayerTexture(self.returnCurrentWeaponValue(0))

        #Reloads current weapon in use#
        if (self.reloading) and (currentTime - self.reload_time > (self.weaponValue(2) * (1 - (0.05 * sum([self.game.profileList["TreeUnlocks"]["10"][1],self.game.profileList["TreeUnlocks"]["13"][1]]))))):
            self.reloading = False
            self.reloadCurrentWeapon()

    #Returns a asked for constant value for the current weapon#
    def weaponValue(self, indent):
        weapon = self.returnCurrentWeaponValue(0)
        value = self.weaponList[weapon][indent]
        return value

    #Returns a asked for changeable value for the current weapon (or name)#
    def returnCurrentWeaponValue(self, valueLookingFor):
        value = str(self.currentWeapons[1][self.currentWeapons[0]][valueLookingFor])
        return value

    #Used to reload the current weapon the player is using#
    def reloadCurrentWeapon(self):
        extraAmmo = int(0)

        #Sets any left over ammo as extra ammo to be added back to the magazine#
        if int(self.returnCurrentWeaponValue(1)) > 0:
            extraAmmo = int(self.returnCurrentWeaponValue(1))
        
        #Weapon mod which doubles ammo capacity (id:4)#
        magValue = int(self.weaponValue(0))
        if 4 in self.currentWeapons[1][self.currentWeapons[0]][3]:
            magValue += magValue
            
        #Puts all leftover ammo into ammo object if less ammo then the max at one is avalible#
        if (int(self.returnCurrentWeaponValue(2)) + extraAmmo) < magValue:
            self.currentWeapons[1][self.currentWeapons[0]][1] = (int(self.returnCurrentWeaponValue(2)) + extraAmmo)

        #Fill current ammo object to that of is maxiumum value#
        else:
            self.currentWeapons[1][self.currentWeapons[0]][1] = magValue

        #Updates the ammo value for the external magazine#
        self.currentWeapons[1][self.currentWeapons[0]][2] += extraAmmo - int(self.returnCurrentWeaponValue(1))

    def updatePlayerTexture(self, weapon):
        
        #Sets the player texture based on there current weapon and the choosen colours by the player#
        self.temp1 = pg.Surface((30,30), pg.SRCALPHA, 32).convert_alpha()
        self.temp1.blit(self.layer1,(0, 0))
        self.temp1.fill((self.game.colour[0][self.game.profileList["CurrentOutfit"][0]][0], self.game.colour[0][self.game.profileList["CurrentOutfit"][0]][1], self.game.colour[0][self.game.profileList["CurrentOutfit"][0]][2], 128), special_flags=pg.BLEND_MULT)
        
        self.temp2 = pg.Surface((30,30), pg.SRCALPHA, 32).convert_alpha()
        self.temp2.blit(self.layer2,(0, 0))
        self.temp2.fill((self.game.colour[2][self.game.profileList["CurrentOutfit"][2]][0], self.game.colour[2][self.game.profileList["CurrentOutfit"][2]][1], self.game.colour[2][self.game.profileList["CurrentOutfit"][2]][2], 128), special_flags=pg.BLEND_MULT)
        
        self.temp3 = pg.Surface((30,30), pg.SRCALPHA, 32).convert_alpha()
        self.temp3.blit(self.layer3,(0, 0))
        self.temp3.fill((self.game.colour[1][self.game.profileList["CurrentOutfit"][1]][0], self.game.colour[1][self.game.profileList["CurrentOutfit"][1]][1], self.game.colour[1][self.game.profileList["CurrentOutfit"][1]][2], 128), special_flags=pg.BLEND_MULT)
        
        self.temp4 = pg.Surface((30,30), pg.SRCALPHA, 32).convert_alpha()
        self.temp4.blit(self.layer4,(0, 0))
        self.temp4.fill((self.game.colour[3][self.game.profileList["CurrentOutfit"][3]][0], self.game.colour[3][self.game.profileList["CurrentOutfit"][3]][1], self.game.colour[3][self.game.profileList["CurrentOutfit"][3]][2], 128), special_flags=pg.BLEND_MULT)
        
        self.temp5 = pg.Surface((30,30), pg.SRCALPHA, 32).convert_alpha()
        self.temp5.blit(self.PLAYER_SPRITE_DICT[weapon],(0, 0))
        
        self.PLAYER_SPRITE = pg.Surface((30,30), pg.SRCALPHA, 32).convert_alpha()
        
        self.PLAYER_SPRITE.blit(self.temp1, self.temp1.get_rect())
        self.PLAYER_SPRITE.blit(self.temp2, self.temp2.get_rect())
        self.PLAYER_SPRITE.blit(self.temp3, self.temp3.get_rect())
        self.PLAYER_SPRITE.blit(self.temp4, self.temp4.get_rect())
        self.PLAYER_SPRITE.blit(self.temp5, self.temp5.get_rect())

    #Used to move play position when colliding with an enemy ai#
    def enemyCollision(self):

        #Creates a list of enemies that are colliding with the player at the current time#
        hits = pg.sprite.spritecollide(self, self.game.all_mobs, False)
        for hit in hits:

            #Does damage to the player if is been 1 second since last attack by that enemy#
            if (pg.time.get_ticks() - hit.attackedTime) >= 1000:

                self.health[1] -= hit.damage
                self.healing[2] = pg.time.get_ticks()
                hit.attacked = True
                hit.attackedTime = pg.time.get_ticks()

        if hits:
            #Moves the player if they have been attacked by an enemy#
            self.coord += pg.math.Vector2(1, 0).rotate(-hits[0].angle)
            self.rect.x, self.rect.y = self.coord

            #Checks if a tile is in the area of the player boxed hitbox#
            if pg.sprite.spritecollide(self, self.game.all_tiles, False):
            #Checks for Pixel Perfect collision detection using masks and alpha#
                if pg.sprite.spritecollide(self, self.game.all_tiles, False, pg.sprite.collide_mask):
                    self.coord -= pg.math.Vector2(1, 0).rotate(-hits[0].angle)
                    self.rect.x, self.rect.y = self.coord

    def healPlayer(self):
        #Does checks to see if the player hasn't be touched in 5 second (4 seconds if using self care), if the player hasn't healed since the last set number and if the health is not full#

        if self.perks[1]:
            healTime = 4000 - (500 * sum([self.game.profileList["TreeUnlocks"]["3"][1]]))
        else:
            healTime = 5000 - (500 * sum([self.game.profileList["TreeUnlocks"]["3"][1]]))
        
        if ((pg.time.get_ticks() - self.healing[2]) >= healTime) and ((pg.time.get_ticks() - self.healing[3]) >= self.healing[0]) and (self.health[1] < self.health[0]):

            #Changes last time of healing to current time#
            self.healing[3] = pg.time.get_ticks()

            #Add's health gain value to health if there is more then that gain till health is full else it sets it to full#
            if (self.health[0] - self.health[1]) >= (self.healing[1] * self.powerups[2][2]):
                self.health[1] += self.healing[1] * self.powerups[2][2]

            elif self.powerups[2][0] and (self.health[1] > self.health[0]):
                pass
            
            else:
                self.health[1] = self.health[0]

    def powerUpsFunction(self):

        if self.powerups[0][0]:
            if (pg.time.get_ticks() - self.powerups[0][1] >= (20000 + (2000 * sum([self.game.profileList["TreeUnlocks"]["3"][1]])))):
                self.powerups[0][0] = False
                self.powerups[0][1] = 0
                self.powerups[0][2] = 1

        if self.powerups[1][0]:
            if (pg.time.get_ticks() - self.powerups[1][1] >= (20000 + (2000 * sum([self.game.profileList["TreeUnlocks"]["12"][1]])))):
                self.powerups[1][0] = False
                self.powerups[1][1] = 0
                self.powerups[1][2] = 1

        if self.powerups[2][0]:
            if self.powerups[2][2] == 1:
                self.health[1] = self.health[0] + 100 + (50 * sum([self.game.profileList["TreeUnlocks"]["4"][1]]))
                self.powerups[2][2] = 2

            if (pg.time.get_ticks() - self.powerups[2][1] >= 20000):
                self.powerups[2][0] = False
                self.powerups[2][1] = 0
                self.powerups[2][2] = 1
        
    
    def updateShop(self):
        
        #MAKE UPDATE CODE ACTUALLY WORK (NEW CODE)#
        
        #Changes player movement based on calculated speed vector#
        

        #Checks if a tile is in the area of the player boxed hitbox#
#         if pg.sprite.spritecollide(self, self.game.all_tiles, False):
#             
#             #Checks for Pixel Perfect collision detection using masks and alpha#
#             collideTile = pg.sprite.spritecollide(self, self.game.all_tiles, False, pg.sprite.collide_mask)
#             for tile in collideTile:
#                 if self.currentSpeed[0] > 0:
#                     self.rect.x = tile.rect.left - (self.rect.width / 2)
#                     self.currentSpeed[0] = 0
#                     print("R")
#                     
#                 elif self.currentSpeed[0] < 0:
#                     self.rect.x = tile.rect.right + (self.rect.width / 2)
#                     self.currentSpeed[0] = 0
#                     print("L")
#                     
#                 if self.currentSpeed[1] > 0:
#                     self.rect.y = tile.rect.top - (self.rect.height / 2)
#                     self.currentSpeed[1] = 0
#                     print("B")
#                     
#                 elif self.currentSpeed[1] < 0:
#                     self.rect.y = tile.rect.bottom + (self.rect.height / 2)
#                     self.currentSpeed[1] = 0
#                     print("T")
                    
        #self.currentPosX += self.currentSpeed[0]
        #self.currentPosY += self.currentSpeed[1]
        #self.rect.x = self.currentPosX
        #self.rect.y = self.currentPosY
        
        #if pg.sprite.spritecollide(self, self.game.all_tiles, False, pg.sprite.collide_mask):    
            #self.currentPosX -= self.currentSpeed[0]
            #self.currentPosY -= self.currentSpeed[1]
            #self.rect.x = self.currentPosX
            #self.rect.y = self.currentPosY
        
        
        
        
        #Shop collision code#
        collideShop = pg.sprite.spritecollide(self, self.game.all_shops, False)
        for shop in collideShop:
            self.shopInfo = [True, shop.type, self.weaponList[shop.type][9]]
            
        if collideShop == []:
            self.shopInfo = [False, "", 0]
            
        #Door collision code#
        collideDoor = pg.sprite.spritecollide(self, self.game.all_doors, False)
        for door in collideDoor:
            self.doorInfo = [True, door, door.cost, door.rect.x, door.rect.y]
            
        if collideDoor == []:
            self.doorInfo = [False,"", 0, 0, 0]
            
        #Upgrade collision code#
        collideUpgrade = pg.sprite.spritecollide(self, self.game.all_upgrades, False)
        for upgrade in collideUpgrade:
            self.upgradeInfo = [True, upgrade.type, upgrade.cost, upgrade.num]
            
        if collideUpgrade == []:
            self.upgradeInfo = [False, "" , 0, 0]

        #Perk collision code#
        collidePerk = pg.sprite.spritecollide(self, self.game.all_perks, False)
        for perk in collidePerk:
            self.perkInfo = [True, perk.type, 5000, perk.num]
            
        if collidePerk == []:
            self.perkInfo = [False, "" , 0, 0]


class bullet(pg.sprite.Sprite):
    def __init__(self, game, spread, velocity, coord, bullRange, damage):

        #Allows other parts of class to grab values from main class#
        self.game = game
        
        #Sprite texture initialisation#
        self.BULLET_SPRITE = pg.image.load(os.path.join("Textures","Entities","Projectiles","Bullet.png")).convert_alpha()

        #Sets the bullet size and sprite#
        self.groups = game.all_sprites, game.all_bullets
        pg.sprite.Sprite.__init__(self, self.groups)

        self.image = pg.Surface((4,4)).convert()
        self.image.blit(self.BULLET_SPRITE,(0, 0))

        #Sets bullet rectangle to selected image#
        self.rect = self.image.get_rect()
        self.coord = pg.math.Vector2(coord)
        self.rect.center = self.coord
        self.bloom = random.uniform(-spread, spread)
        self.movement = pg.math.Vector2(1, 0).rotate(-game.angle).rotate(self.bloom) * velocity

        self.bullRange = bullRange
        self.spawn_time = pg.time.get_ticks()
        self.pausedValues = [False, 0]
        self.damage = damage + (2 * sum([self.game.profileList["TreeUnlocks"]["11"][1]]))
        self.type = "bullet"

    def update(self, delta):
        #Changes spawn time so the same amount of time is remaining after pause(NEW CODE)#
        if (self.game.paused):
            if (self.game.pausedTime != 0):
                self.pausedValues[0] = True
                self.pausedValues[1] = (pg.time.get_ticks() + self.spawn_time) - self.game.pausedTime
                #print(self.pausedValues[1], pg.time.get_ticks(), self.game.pausedTime - self.spawn_time, pg.time.get_ticks() - self.pausedValues[1])
        
        else:
            #Resets values after game pause saving all time values (NEW CODE)#
            if self.pausedValues[0]:
                self.spawn_time = self.pausedValues[1]
                self.pausedValues[0] = False
            
            #Works out bullet speed based on fps#
            self.coord += self.movement * delta
            self.rect.center = self.coord

            #Checks if a tile is in the area of the player boxed hitbox#
            if (pg.sprite.spritecollide(self, self.game.all_tiles, False)):
                self.kill()

            #Kills the bullet if is travled is maximum distance#
            if pg.time.get_ticks() - self.spawn_time > self.bullRange:
                self.kill()
            
        #Creates collsion mask for bullet#
        self.mask = pg.mask.from_surface(self.image)

class enemy(pg.sprite.Sprite):
    def __init__(self, game, coord, health, speed, damage, texture, enemyType):
        
        self.game = game

        #Sprite texture initialisation#
        self.ENEMY_SPRITE = pg.image.load(os.path.join("Textures","Entities","Enemies",texture)).convert_alpha()

        #Sets the enemy size, sprite groups and positioning#

        self.groups = game.all_sprites, game.all_mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        
        self.image = pg.Surface((30,30)).convert_alpha()
        self.image.blit(self.ENEMY_SPRITE,(0, 0))

        self.rect = self.image.get_rect()
        self.coord = pg.math.Vector2(coord)
        self.rect.center = self.coord

        #Sets zombie varibles#
        self.health = health
        self.speed = speed
        self.damage = damage
        self.enemyType = enemyType
        self.angle = 0
        self.movement = pg.math.Vector2(0,0)
        self.prePathTime = -550
        self.pathDone = True
        self.attacked = False
        self.attackedTime = -1000
        self.magicTime = 0

        self.nodeList = [(0,0)]
        self.currentMoveNode = 0
        self.currentMovement = 0
        self.movementTime = 0
        self.pausedValues = [False, 0, 0, 0, 0]

    def update(self, delta):

        #Changes spawn time so the same amount of time is remaining after pause(NEW CODE)#
        if (self.game.paused):
            if (self.game.pausedTime != 0):
                self.pausedValues[0] = True
                self.pausedValues[1] = (pg.time.get_ticks() + self.prePathTime) - self.game.pausedTime
                self.pausedValues[2] = (pg.time.get_ticks() + self.movementTime) - self.game.pausedTime
                self.pausedValues[3] = (pg.time.get_ticks() + self.magicTime) - self.game.pausedTime
                self.pausedValues[4] = (pg.time.get_ticks() + self.attackedTime) - self.game.pausedTime
                #print(self.pausedValues[1], pg.time.get_ticks(), self.game.pausedTime - self.spawn_time, pg.time.get_ticks() - self.pausedValues[1])
        
        else:
            #Resets values after game pause saving all time values (NEW CODE)#
            if self.pausedValues[0]:
                self.prePathTime = self.pausedValues[1]
                self.movementTime = self.pausedValues[2]
                self.magicTime = self.pausedValues[3]
                self.attackedTime = self.pausedValues[4]
                self.pausedValues[0] = False

            #Resets non pathed movement to zero#
            self.movement = pg.math.Vector2(0, 0)

            #Gets the current position of the enemy on the tile map#
            self.coord = pg.math.Vector2((self.rect.center[0] // 36),(self.rect.center[1] // 36))

            #Kills enemy if the health is less then or equal to zero#
            if self.health <= 0:
                self.kill()
                enemyBodies(self.game, (self.rect.x,self.rect.y), self.enemyType, self.angle)

                #Gives player 1 in 30 chance of getting a powerup when killing an enemy#
                if random.choices([False,True],[29,1])[0]:
                    powerup(self.game, (self.rect.x,self.rect.y))

                #Gives bettween 0 and 5 bullets for a kill if using Salvager (and external mag isnt full)#
                if self.game.player.perks[3]:
                    bulletSalvage = random.choices([0,1,2,3,4,5],[8,16,28,24,18,6])[0]
                    if (bulletSalvage + self.game.player.currentWeapons[1][self.game.player.currentWeapons[0]][2]) >= self.game.player.weaponValue(1):
                        self.game.player.currentWeapons[1][self.game.player.currentWeapons[0]][2] = self.game.player.weaponValue(1)
                    else:
                        self.game.player.currentWeapons[1][self.game.player.currentWeapons[0]][2] += bulletSalvage

                #Extra 20 points for a kill if using pick pocket and an extra 5 points when using a set unlock in the skill tree#
                self.game.player.points += (100 * self.game.player.powerups[0][2]) + (5 * sum([self.game.profileList["TreeUnlocks"]["7"][1]])) + (20 * sum([self.game.player.perks[2]]))
                self.game.currentEnemyKills += 1
                    
                if self.game.currentEnemyKills >= 30:
                    self.game.currentEnemyKills = 0
                    self.game.currentGameXp += 1

            #Pauses enemy after attack#
            if self.attacked:
                if self.currentMovement == 0 and self.pathDone == True:
                    self.nodeList = []
                    self.currentMoveNode = 0
                    self.attacked = False

            #Calculates that difference in coordinate bettween the enemy and player#
            moveVector = ( (self.game.player.rect.x) - self.rect.x, -( (self.game.player.rect.y) - self.rect.y))
            angleBackup = self.angle

            #Calls the function to find the enemies path after every 0.5 seconds#
            if ((pg.time.get_ticks() - self.prePathTime) >= 500) and (self.pathDone == True) and (self.currentMovement == 0) and (self.enemyType != "Ghoul"):

                #Resets movement varibles#
                self.nodeList = []
                self.currentMoveNode = 0
                self.currentMovement = 0

                #Creats a thread for the pathfinding function#
                self.pathDone = False
                aPathfindingThread = threading.Thread(target=pathfindingThread, args=(self,))
                aPathfindingThread.start()

            #Calculates the enemies angle of rotation#
            try:
                self.angle = math.degrees(math.acos(moveVector[0] / (math.sqrt(moveVector[0]**2 + moveVector[1]**2))))
            except:
                self.angle = angleBackup
            
            if moveVector[1] < 0:
                self.angle = 360 - self.angle

            #Adds manual movement for enemy types which can go through walls#
            if (self.enemyType == "Ghoul"):
                self.movement = pg.math.Vector2(1, 0).rotate(-self.angle) * (300 * (delta / 1000)) * self.speed * 0.8

            #Runs a function to make enemies avoid eachother so the dont overlap that much#
            self.avoidEnemy()

            #Used to move the enemy based on is path and external movement code#
            if (((len(self.nodeList) - 1) >= self.currentMoveNode) or (self.enemyType == "Ghoul")) and ((pg.time.get_ticks() - self.movementTime) >= (10 / self.speed))  and (self.pathDone == True):
                #Changes the x and y of the enemy#
                if (self.enemyType != "Ghoul"):
                    self.rect.x += (self.nodeList[self.currentMoveNode][0] * 3)
                    self.rect.y += (self.nodeList[self.currentMoveNode][1] * 3)

                self.rect.x += self.movement[0]
                self.rect.y += self.movement[1]

                #Sets up local varible#
                touchingWall = False

                #Checks if a tile is in the area of the enemies boxed hitbox
                if (self.enemyType != "Ghoul"):
                    if (pg.sprite.spritecollide(self, self.game.all_tiles, False) and (self.enemyType != "Hound")) or (pg.sprite.spritecollide(self, self.game.all_walls, False) and (self.enemyType == "Hound")):
                    #Checks for Pixel Perfect collision detection using masks and alpha#
                        if (pg.sprite.spritecollide(self, self.game.all_tiles, False, pg.sprite.collide_mask) and (self.enemyType != "Hound")) or (pg.sprite.spritecollide(self, self.game.all_walls, False, pg.sprite.collide_mask) and (self.enemyType == "Hound")):
                            #Changes enemy position to middle of is proper tile if it collides with a wall#
                            self.currentMovement = 0
                            self.prePathTime -= 500
                            touchingWall = True
                            self.rect.centerx = (36 * self.coord[0]) + 18
                            self.rect.centery = (36 * self.coord[1]) + 18

                #If the enemy doesn't touch a wall it changes the positon of which node to move to in the list#
                if not touchingWall:
                
                    self.currentMovement += 1
                    self.movementTime = pg.time.get_ticks()

                    #Resets the movement and put the enemy on a new node if a node is fully complete#
                    if self.currentMovement > 11:
                        self.currentMoveNode += 1
                        self.currentMovement = 0


            #If the enemy is magic then a projectile is released which tracks the play like an enemy that can through walls#
            if (self.enemyType == "Mage") and ((pg.time.get_ticks() - self.magicTime) >= 3000) and (math.sqrt(moveVector[0]**2 + moveVector[1]**2) > 180):
                projCord = pg.math.Vector2(self.rect.center) + pg.math.Vector2(15,10).rotate(-self.angle)
                self.game.magicProjectiles.append(magic(self.game, projCord, 3000))
                self.magicTime = pg.time.get_ticks()

        #Sets up the enemies image and collision mask each update#
        self.image.blit(self.ENEMY_SPRITE, self.rect)
        self.mask = pg.mask.from_surface(self.image)

    #Used to make enemies seperate from eachother#
    def avoidEnemy(self):
        for mob in self.game.all_mobs:
            if (mob != self):
                dist = pg.math.Vector2((self.rect.x - mob.rect.x),(self.rect.y - mob.rect.y))
                if 0 < (math.sqrt(dist[0]**2 + dist[1]**2)) < 20:
                    #Used to prevent crashes if the angle cant be calculated#
                    try:
                        self.movement += pg.math.Vector2(5, 0).rotate(math.degrees(math.acos(dist[0] / (math.sqrt(dist[0]**2 + dist[1]**2)))))
                    except:
                        pass

class magic(pg.sprite.Sprite):
    def __init__(self, game, coord, bullRange):

        #Allows other parts of class to grab values from main class#
        self.game = game
        
        #Sprite texture initialisation#
        self.MAGIC_SPRITE = pg.image.load(os.path.join("Textures","Entities","Projectiles","Magic.png")).convert_alpha()

        #Sets the magic size and sprite#
        self.groups = game.all_sprites, game.all_magic
        pg.sprite.Sprite.__init__(self, self.groups)

        self.image = pg.Surface((6,6)).convert_alpha()
        self.image.blit(self.MAGIC_SPRITE,(0, 0))

        #Sets magic rectangle to selected image#
        self.rect = self.image.get_rect()
        self.coord = pg.math.Vector2(coord)
        self.rect.center = self.coord

        #Sets up base varibles#
        self.angle = 0
        self.bullRange = bullRange
        self.spawn_time = pg.time.get_ticks()
        self.type = "magic"
        self.damage = 10
        self.pausedValues = [False, 0]

    def update(self, delta):

        #Changes spawn time so the same amount of time is remaining after pause#
        if (self.game.paused):
            if (self.game.pausedTime != 0):
                self.pausedValues[0] = True
                self.pausedValues[1] = (pg.time.get_ticks() + self.spawn_time) - self.game.pausedTime
                #print(self.pausedValues[1], pg.time.get_ticks(), self.game.pausedTime - self.spawn_time, pg.time.get_ticks() - self.pausedValues[1])
        
        else:
            #Resets values after game pause saving all time values#
            if self.pausedValues[0]:
                self.spawn_time = self.pausedValues[1]
                self.pausedValues[0] = False
        
            #Works out the projectile movement based on player location#
            moveVector = ( (self.game.player.rect.x) - self.rect.x, -( (self.game.player.rect.y) - self.rect.y))
            angleBackup = self.angle

            #If possible calculates the angle between the magic and player#
            try:
                self.angle = math.degrees(math.acos(moveVector[0] / (math.sqrt(moveVector[0]**2 + moveVector[1]**2))))
            except:
                self.angle = angleBackup
            
            if moveVector[1] < 0:
                self.angle = 360 - self.angle

            #Sets the magic movement value based on the speed of the game and angle#
            self.movement = pg.math.Vector2(1, 0).rotate(-self.angle) * (18 * (delta / 1000))

            #Works out projectile speed based on fps#
            self.coord += self.movement * delta
            self.rect.center = self.coord

            #Checks if a tile is in the area of the player boxed hitbox#
            if (pg.sprite.spritecollide(self, self.game.all_tiles, False)):
                self.kill()

            if (pg.time.get_ticks() - self.spawn_time > self.bullRange):
                self.kill()

        #Sets up magic collsion mask each update#
        self.mask = pg.mask.from_surface(self.image)


class powerup(pg.sprite.Sprite):
    def __init__(self, game, coord):
        #POWERTYPE 0 is points, 1 is damage, 2 is health#

        #Allows other parts of class to grab values from main class#
        self.game = game
        self.spawn_time = pg.time.get_ticks()
        self.lastTextureChange = pg.time.get_ticks()
        self.type = random.randint(0,2)
        self.textureStage = 0
        self.pausedValues = [False, 0, 0]

        #Sets the powerup size and sprite#
        self.groups = game.all_sprites, game.all_powerups
        pg.sprite.Sprite.__init__(self, self.groups)

        self.image = pg.Surface((20,20), pg.SRCALPHA, 32).convert_alpha()
        self.image.blit(self.game.POWERUP_SET,(0, 0), (20*self.textureStage, 20*self.type, 20, 20))

        #Sets powerup rectangle to selected image#
        self.rect = self.image.get_rect()
        self.coord = pg.math.Vector2(coord)
        self.rect.center = self.coord

    def update(self, delta):

        #Changes spawn time so the same amount of time is remaining after pause#
        if self.game.paused:
            if (self.game.pausedTime != 0):
                self.pausedValues[0] = True
                self.pausedValues[1] = (pg.time.get_ticks() + self.spawn_time) - self.game.pausedTime
                self.pausedValues[2] = (pg.time.get_ticks() + self.lastTextureChange) - self.game.pausedTime
                
            
        else:
            #Resets values after game pause saving all time values#
            if self.pausedValues[0]:
                self.spawn_time = self.pausedValues[1]
                self.lastTextureChange = self.pausedValues[2]
                self.pausedValues[0] = False
            
            if (pg.time.get_ticks() - self.lastTextureChange > 500):
                if self.textureStage == 0:
                    self.textureStage = 1
                else:
                    for i in range(1,5):
                        if self.textureStage == i:
                            if (pg.time.get_ticks() - self.spawn_time < (5000*i)):
                                self.textureStage = i-1
                            else:
                                self.textureStage = i+1

                            break

                    if self.textureStage >= 5:
                        self.kill()

                self.lastTextureChange = pg.time.get_ticks()

            #Sets up powerup collsion mask each update#
            self.mask = pg.mask.from_surface(self.image)



class enemyBodies(pg.sprite.Sprite):
    def __init__(self, game, coord, enemyType, angle):
        #BODIES 0 is ZOMBIE, 1 is GHOUL, 2 is MAGE, 3 is HOUND#

        #Allows other parts of class to grab values from main class#
        self.game = game
        self.spawn_time = pg.time.get_ticks()
        self.angle = angle
        self.pausedValues = [False, 0]
        self.textureIndex = [0,0]

        #Sets the body size and sprite#
        self.groups = game.all_sprites, game.all_bodies
        pg.sprite.Sprite.__init__(self, self.groups)

        types = ["Zombie","Ghoul","Mage","Hound"]
        for i in range(len(types)):
            if enemyType == types[i]:
                self.textureIndex[0] = i

        self.image = pg.Surface((30,30), pg.SRCALPHA, 32).convert_alpha()
        self.image.blit(self.game.ENEMY_BODIES,(0, 0), (0, (30*self.textureIndex[0]), 20, 20))

        #Sets body rectangle to selected image#
        self.rect = self.image.get_rect()
        self.coord = pg.math.Vector2(coord)
        self.rect.center = self.coord

    def update(self, delta):

        #Changes spawn time so the same amount of time is remaining after pause#
        if self.game.paused:
            if (self.game.pausedTime != 0):
                self.pausedValues[0] = True
                self.pausedValues[1] = (pg.time.get_ticks() + self.spawn_time) - self.game.pausedTime
                
            
        else:
            #Resets values after game pause saving all time values#
            if self.pausedValues[0]:
                self.spawn_time = self.pausedValues[1]
                self.pausedValues[0] = False
            
            if (pg.time.get_ticks() - self.spawn_time > 5000):
                self.kill()

            else:
                for i in range(3,-1,-1):
                    if (pg.time.get_ticks() - self.spawn_time > (1250*i)):
                        self.textureIndex[1] = i
                        break
                    
            
            #Sets up powerup collsion mask each update#
            self.mask = pg.mask.from_surface(self.image)






def pathfindingThread(self):
    #Run the A-Star algorithm in the pathfinding class and calculates the route that should be taken to get there#
    self.nodeList = pathfinding.aStar(self.game.aiMap, pathfinding.Node(((self.rect.center[0] // 36),(self.rect.center[1] // 36)), None), pathfinding.Node(((self.game.player.rect.center[0] // 36),(self.game.player.rect.center[1] // 36)), None), self)    
    self.prePathTime = pg.time.get_ticks()
    self.pathDone = True


def collision(sprite, group, doesCollied):
    #Updates entitys current position#
    sprite.coord += sprite.movement
    sprite.rect.x, sprite.rect.y = sprite.coord

    if doesCollied:
        #Checks if a tile is in the area of the player boxed hitbox#
        if pg.sprite.spritecollide(sprite, group, False):
            #Checks for Pixel Perfect collision detection using masks and alpha#
            if pg.sprite.spritecollide(sprite, group, False, pg.sprite.collide_mask):
                sprite.coord -= sprite.movement
                sprite.rect.x, sprite.rect.y = sprite.coord
        


        

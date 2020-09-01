import pygame as pg
import random, math, time, json

class player(pg.sprite.Sprite):
    def __init__(self, game, x , y):

        #Allows other parts of class to grab values from main class#
        self.game = game
        
        #Sprite texture initialisation#
        self.image_names = ["Pistol", "PistolShooting", "Shotgun", "ShotgunShooting", "Super Shotgun", "Super ShotgunShooting", "SMG", "SMGShooting", "Rifle", "RifleShooting"]
        self.PLAYER_SPRITE_DICT = dict(((img_name, pg.image.load("Textures\Entities\Player\\" + img_name + ".png").convert_alpha()) for img_name in self.image_names))

        #Setup weapons for player("Name": [Ammo, Magsize, Reload time, Bullets per shot, Bullet damage, Fire rate, Spread angle, Velocity, Time before despawn])#
        self.weapons = '{"Pistol": [-1, 0, 0, 1, 34, 600, 0, 0.5, 1500], "Shotgun": [5, 25, 2200, 4, 27, 900, 5, 1.5, 250], "Super Shotgun": [2, 30, 2000, 7, 25, 1200, 10, 1.5, 125], "SMG": [32, 128, 2500, 1, 11, 110, 4, 1.1, 455], "Rifle": [8, 64, 3200, 1, 70, 800, 1, 3.5, 220]}'
        
        try:
            with open('weapons.json') as f:
                self.weapons = json.load(f)
                print(self.keys)
                
        except:
            with open('weapons.json', 'w') as f:
                json.dump(self.weapons, f)

        self.weaponList = json.loads(self.weapons)

        #List of weapons in inventory (Name, Ammo, Magsize)#
        #self.currentWeapons = [0,[["Pistol",self.weaponList["Pistol"][0],self.weaponList["Pistol"][1]],["Super Shotgun",self.weaponList["Super Shotgun"][0],self.weaponList["Super Shotgun"][1]]]]
        self.currentWeapons = [0,[["Shotgun",self.weaponList["Shotgun"][0],self.weaponList["Shotgun"][1]],["Super Shotgun",self.weaponList["Super Shotgun"][0],self.weaponList["Super Shotgun"][1]]]]
        #self.currentWeapons = [0,[["SMG",self.weaponList["SMG"][0],self.weaponList["SMG"][1]],["Rifle",self.weaponList["Rifle"][0],self.weaponList["Rifle"][1]]]]

        self.PLAYER_SPRITE = self.PLAYER_SPRITE_DICT[self.returnCurrentWeaponValue(0)]

        #Sets the player size and sprite#
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        
        self.image = pg.Surface((30,30)).convert_alpha()
        self.image.blit(self.PLAYER_SPRITE,(0, 0))

        #Sets player rectangle to selected image and sets player start location#
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.currentSpeed = [0,0]
        self.currentPosX = self.rect.x
        self.currentPosY = self.rect.y

        #Values used for player weapons#
        self.previous_shot = 0
        self.previous_weapon_change = 0
        self.reload_time = 0
        self.shooting = False
        self.reloading = False
        
    def update(self, delta):
        #Main player update loop, called every frame#

        #Updates the movement of the player#
        self.playerKeypress(delta)

        #Calls code to change postion of player#
        self.updatePosition()
        
        #Resets the movement vector for the player#
        self.currentSpeed = [0,0]

        #Creates collsion mask for player#
        self.mask = pg.mask.from_surface(self.image)

    def playerKeypress(self, delta):
        #Grabing Pygame Info#
        keys = pg.key.get_pressed()
        currentTime = pg.time.get_ticks()

        #Updates the players movement per frame being greater the smaller the frame rate#
        currentSpeed = 300 * (delta / 1000)
        
        #X coordinate control#
        if keys[self.game.keyList["East"][1]] and keys[self.game.keyList["West"][1]]:
            #Stops movement if both are pressed#
            self.currentSpeed[0] = 0
        
        elif keys[self.game.keyList["East"][1]]:
            #Move player east#
            self.currentSpeed[0] = currentSpeed
            
        elif keys[self.game.keyList["West"][1]]:
            #Move player west#
            self.currentSpeed[0] = -currentSpeed
        
        #Y coordinate control#
        if keys[self.game.keyList["North"][1]] and keys[self.game.keyList["South"][1]]:
            #Stops movement if both are pressed#
            self.currentSpeed[1] = 0

        elif keys[self.game.keyList["North"][1]]:
            #Move player north#
            self.currentSpeed[1] = -currentSpeed
        
        elif keys[self.game.keyList["South"][1]]:
            #Move player south#
            self.currentSpeed[1] = currentSpeed

        #Weapon usage#
        if not self.reloading:

            #Reloading code for if a player wonts to reload when the mag is not full#
            if keys[self.game.keyList["Reload"][1]] and (int(self.returnCurrentWeaponValue(1)) < int(self.weaponValue(0))) and (int(self.returnCurrentWeaponValue(2)) > 0):
                self.reloading = True
                self.reload_time = currentTime

            #Used to switch player weapon to the other one in there inventory#
            elif keys[self.game.keyList["Switch Weapon"][1]] and (currentTime - self.previous_weapon_change > 500):
                if (self.currentWeapons[0] == 0):
                    self.currentWeapons[0] = 1

                elif (self.currentWeapons[0] == 1):
                    self.currentWeapons[0] = 0

                if self.shooting:
                    self.shooting = False

                self.previous_weapon_change = currentTime
                self.PLAYER_SPRITE = self.PLAYER_SPRITE_DICT[self.returnCurrentWeaponValue(0)]   
                    

            elif keys[self.game.keyList["Shoot"][1]]:

                #Reloads weapon if ammo is empty#
                if (int(self.returnCurrentWeaponValue(1)) == 0) and (int(self.returnCurrentWeaponValue(2)) > 0):
                    self.reloading = True
                    self.reload_time = currentTime

                elif currentTime - self.previous_shot > self.weaponValue(5) and ((int(self.returnCurrentWeaponValue(1)) != 0)):
                    #Used to find starting coord of the player#
                    bullCord = pg.math.Vector2(self.rect.center) + pg.math.Vector2(15,0).rotate(-self.game.angle)

                    #Sets values to see if the player if shooting and changes player texture#
                    self.shooting = True
                    self.PLAYER_SPRITE = self.PLAYER_SPRITE_DICT[self.returnCurrentWeaponValue(0) + "Shooting"]

                    #Spawns a new bullet#
                    for i in range(self.weaponValue(3)):
                        bullet(self.game, self.weaponValue(6), self.weaponValue(7), bullCord, self.weaponValue(8))

                    if self.weaponValue(0) != -1:
                        self.currentWeapons[1][self.currentWeapons[0]][1] -= 1

                    self.previous_shot = currentTime


        #Used to revert player model to remove fire from shot#
        if currentTime - self.previous_shot > 200 and self.shooting:
            
            self.shooting = False
            self.PLAYER_SPRITE = self.PLAYER_SPRITE_DICT[self.returnCurrentWeaponValue(0)]

        #Reloads current weapon in use#
        if (self.reloading) and (currentTime - self.reload_time > self.weaponValue(2)):
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

        #Puts all leftover ammo into ammo object if less ammo then the max at one is avalible#
        if (int(self.returnCurrentWeaponValue(2)) + extraAmmo) < int(self.weaponValue(0)):
            self.currentWeapons[1][self.currentWeapons[0]][1] = (int(self.returnCurrentWeaponValue(2)) + extraAmmo)

        #Fill current ammo object to that of is maxiumum value#
        else:
            self.currentWeapons[1][self.currentWeapons[0]][1] = int(self.weaponValue(0))

        #Updates the ammo value for the external magazine#
        self.currentWeapons[1][self.currentWeapons[0]][2] += extraAmmo - int(self.returnCurrentWeaponValue(1))

    
    def updatePosition(self):
        #Changes player movement based on calculated speed vector#
        self.currentPosX += self.currentSpeed[0]
        self.currentPosY += self.currentSpeed[1]
        self.rect.x = self.currentPosX
        self.rect.y = self.currentPosY

        #Checks if a tile is in the area of the player boxed hitbox#
        if pg.sprite.spritecollide(self, self.game.all_tiles, False):
            #Checks for Pixel Perfect collision detection using masks and alpha#
            if pg.sprite.spritecollide(self, self.game.all_tiles, False, pg.sprite.collide_mask):
                self.currentPosX -= self.currentSpeed[0]
                self.currentPosY -= self.currentSpeed[1]
                self.rect.x = self.currentPosX
                self.rect.y = self.currentPosY




class bullet(pg.sprite.Sprite):
    def __init__(self, game, spread, velocity, coord, bullRange):

        #Allows other parts of class to grab values from main class#
        self.game = game
        
        #Sprite texture initialisation#
        self.BULLET_SPRITE = pg.image.load("Textures\Entities\Projectiles\Bullet.png").convert_alpha()

        #Sets the bullet size and sprite#
        self.groups = game.all_sprites, game.all_projectiles
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

    def update(self, delta):
        #Works out bullet speed based on fps#
        self.coord += self.movement * delta
        self.rect.center = self.coord

        #Checks if a tile is in the area of the player boxed hitbox#
        if (pg.sprite.spritecollide(self, self.game.all_tiles, False)):
            self.kill()

        if pg.time.get_ticks() - self.spawn_time > self.bullRange:
            self.kill()

        

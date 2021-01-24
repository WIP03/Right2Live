import pygame as pg
import random, math, time, json, threading, os
import pathfinding

class player(pg.sprite.Sprite):
    def __init__(self, game, coord):

        #Allows other parts of class to grab values from main class#
        self.game = game
        
        #Sprite texture initialisation#
        self.image_names = ["Pistol", "PistolShooting", "Shotgun", "ShotgunShooting", "Super Shotgun", "Super ShotgunShooting", "SMG", "SMGShooting", "Rifle", "RifleShooting"]
        self.PLAYER_SPRITE_DICT = dict(((img_name, pg.image.load(os.path.join("Textures","Entities","Player", (img_name + ".png"))).convert_alpha()) for img_name in self.image_names))

        #Setup weapons for player("Name": [Ammo, Magsize, Reload time, Bullets per shot, Bullet damage, Fire rate, Spread angle, Velocity, Time before despawn])#
        self.weapons = '{"Pistol": [-1, 0, 0, 1, 32, 600, 0, 0.5, 1500], "Shotgun": [5, 25, 2200, 4, 27, 900, 5, 1.5, 250], "Super Shotgun": [2, 30, 2000, 7, 23, 1200, 12, 1.5, 125], "SMG": [32, 128, 2500, 1, 12, 110, 4, 1.1, 455], "Rifle": [8, 64, 3200, 1, 70, 800, 1, 2.5, 308]}'
        
        try:
            with open(os.path.join("weapons.json")) as f:
                self.weapons = json.load(f)
                print(self.keys)
                
        except:
            with open(os.path.join("weapons.json"), 'w') as f:
                json.dump(self.weapons, f)

        self.weaponList = json.loads(self.weapons)

        #List of weapons in inventory (Name, Ammo, Magsize)#
        self.currentWeapons = [0,[["Pistol",self.weaponList["Pistol"][0],self.weaponList["Pistol"][1]],["Super Shotgun",self.weaponList["Super Shotgun"][0],self.weaponList["Super Shotgun"][1]]]]
        #self.currentWeapons = [0,[["Shotgun",self.weaponList["Shotgun"][0],self.weaponList["Shotgun"][1]],["Super Shotgun",self.weaponList["Super Shotgun"][0],self.weaponList["Super Shotgun"][1]]]]
        #self.currentWeapons = [0,[["SMG",self.weaponList["SMG"][0],self.weaponList["SMG"][1]],["Rifle",self.weaponList["Rifle"][0],self.weaponList["Rifle"][1]]]]

        self.PLAYER_SPRITE = self.PLAYER_SPRITE_DICT[self.returnCurrentWeaponValue(0)]

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

        self.health = 100
        
    def update(self, delta):
        #Main player update loop, called every frame#

        #Updates the movement of the player#
        self.playerKeypress(delta)

        #Calls code to change postion of player#
        collision(self, self.game.all_tiles, True)
        self.enemyCollision()
        
        #Resets the movement vector for the player#
        self.movement = pg.math.Vector2(0,0)

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
             self.movement[0] = 0
        
        elif keys[self.game.keyList["East"][1]]:
            #Move player east#
            self.movement[0] = currentSpeed
            
        elif keys[self.game.keyList["West"][1]]:
            #Move player west#
            self.movement[0] = -currentSpeed
        
        #Y coordinate control#
        if keys[self.game.keyList["North"][1]] and keys[self.game.keyList["South"][1]]:
            #Stops movement if both are pressed#
            self.movement[1] = 0

        elif keys[self.game.keyList["North"][1]]:
            #Move player north#
            self.movement[1] = -currentSpeed
        
        elif keys[self.game.keyList["South"][1]]:
            #Move player south#
            self.movement[1] = currentSpeed

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
                        bullet(self.game, self.weaponValue(6), self.weaponValue(7), bullCord, self.weaponValue(8), self.weaponValue(4))

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

    #Used to move play position when colliding with an enemy ai#
    def enemyCollision(self):

        #Creates a list of enemies that are colliding with the player at the current time#
        hits = pg.sprite.spritecollide(self, self.game.all_mobs, False)
        for hit in hits:

            #Does damage to the player if is been 1 second since last attack by that enemy#
            if (pg.time.get_ticks() - hit.attackedTime) >= 1000:

                self.health -= hit.damage
                hit.attacked = True
                hit.attackedTime = pg.time.get_ticks()

            #if self.player.health <= 0:
            #    self.playing = False

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
        self.damage = damage
        self.type = "bullet"

    def update(self, delta):
        #Works out bullet speed based on fps#
        self.coord += self.movement * delta
        self.rect.center = self.coord

        #Checks if a tile is in the area of the player boxed hitbox#
        if (pg.sprite.spritecollide(self, self.game.all_tiles, False)):
            self.kill()

        #Kills the bullet if is travled is maximum distance#
        if pg.time.get_ticks() - self.spawn_time > self.bullRange:
            self.kill()

class enemy(pg.sprite.Sprite):
    def __init__(self, game, coord, health, speed, damage, collision, texture, magic):
        
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
        self.collision = collision
        self.isMagic = magic
        self.angle = 0
        self.movement = pg.math.Vector2(0,0)
        self.prePathTime = -500
        self.pathDone = True
        self.attacked = False
        self.attackedTime = -1000
        self.magicTime = 0

        self.nodeList = []
        self.currentMoveNode = 0
        self.currentMovement = 0
        self.movementTime = 0

    def update(self, delta):

        #Resets non pathed movement to zero#
        self.movement = pg.math.Vector2(0, 0)

        #Gets the current position of the enemy on the tile map#
        self.coord = pg.math.Vector2((self.rect.center[0] // 36),(self.rect.center[1] // 36))

        #Kills enemy if the health is less then or equal to zero#
        if self.health <= 0:
            self.kill()

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
        if ((pg.time.get_ticks() - self.prePathTime) >= 500) and (self.pathDone == True) and (self.currentMovement == 0) and (self.collision == True):

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
        if (self.collision == False):
            self.movement = pg.math.Vector2(1, 0).rotate(-self.angle) * (300 * (delta / 1000)) * self.speed * 0.8

        #Runs a function to make enemies avoid eachother so the dont overlap that much#
        self.avoidEnemy()

        #Used to move the enemy based on is path and external movement code#
        if ((len(self.nodeList) - 1) >= self.currentMoveNode) and ((pg.time.get_ticks() - self.movementTime) >= (10 / self.speed)) and (self.collision == True):
            #Changes the x and y of the enemy#
            self.rect.x += (self.nodeList[self.currentMoveNode][0] * 3) + self.movement[0]
            self.rect.y += (self.nodeList[self.currentMoveNode][1] * 3) + self.movement[1]

            #Sets up local varible#
            touchingWall = False

            #Checks if a tile is in the area of the enemies boxed hitbox#
            if pg.sprite.spritecollide(self, self.game.all_tiles, False):
            #Checks for Pixel Perfect collision detection using masks and alpha#
                if pg.sprite.spritecollide(self, self.game.all_tiles, False, pg.sprite.collide_mask):
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
        if self.isMagic and ((pg.time.get_ticks() - self.magicTime) >= 3000) and (math.sqrt(moveVector[0]**2 + moveVector[1]**2) > 180):
            projCord = pg.math.Vector2(self.rect.center) + pg.math.Vector2(15,10).rotate(-self.angle)
            self.game.magicProjectiles.append(magic(self.game, projCord, 3000))
            self.magicTime = pg.time.get_ticks()

        #Sets up the enemies image and collision mask each update#
        self.image.blit(self.ENEMY_SPRITE, self.rect)
        self.mask = pg.mask.from_surface(self.image)

    #Used to make enemies seperate from eachother#
    def avoidEnemy(self):
        if (self.collision == True):
            for mob in self.game.all_mobs:
                if (mob != self) and (mob.collision == True):
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

    def update(self, delta):
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

def pathfindingThread(self):
    #Run the A-Star algorithm in the pathfinding class and calculates the route that should be taken to get there#
    self.nodeList = pathfinding.aStar(self.game.aiMap, pathfinding.Node(((self.rect.center[0] // 36),(self.rect.center[1] // 36)), None), pathfinding.Node(((self.game.player.rect.center[0] // 36),(self.game.player.rect.center[1] // 36)), None))    
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
        

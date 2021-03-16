import pygame as pg
import os
import entity

class Tile(pg.sprite.Sprite):

    def __init__(self, game, x, y, tileX, tileY, tileCollide):
        
        #Sets if tile can be collided with or not#
        if tileCollide == True:
            self.groups = game.all_sprites, game.all_tiles, game.all_walls
        else:
            self.groups = game.all_sprites, game.all_floor

        #Initalises sprite, sets size and texture used#
        size = game.tileSize
        pg.sprite.Sprite.__init__(self, self.groups)
        
        self.image = pg.Surface((36,36), pg.SRCALPHA, 32).convert_alpha()
        self.image.blit(game.TILE_SET,(0, 0), ((tileX)* size, (tileY)* size, size, size))
        
        self.rect = self.image.get_rect()

        #Sets tile location#
        self.rect.x = x * size
        self.rect.y = y * size

        #Creates collsion mask for tile#
        self.mask = pg.mask.from_surface(self.image)

class Shop(pg.sprite.Sprite):

    def __init__(self, game, x, y , type):
        
        self.groups = game.all_sprites, game.all_shops

        #Initalises shop and texture used#
        size = game.tileSize
        pg.sprite.Sprite.__init__(self, self.groups)
        
        self.SHOP = pg.image.load(os.path.join("Textures","World","ShopWeapons.png")).convert_alpha()
        self.image = pg.Surface((32,32)).convert_alpha()
        self.image.blit(self.SHOP, (0, 0))
        
        self.rect = self.image.get_rect()

        #Sets tile location#
        self.rect.x = (x * size) + 2
        self.rect.y = (y * size) + 2
        
        self.type = type

        #Creates collsion mask for shop#
        self.mask = pg.mask.from_surface(self.image)
        
    def update(self, delta):
        self.mask = pg.mask.from_surface(self.image)
        
class Door(pg.sprite.Sprite):

    def __init__(self, game, x, y , orientation, cost):
        
        self.groups = game.all_sprites, game.all_tiles, game.all_doors

        #Initalises door and texture used#
        size = game.tileSize
        pg.sprite.Sprite.__init__(self, self.groups)
        
        self.DOOR = pg.image.load(os.path.join("Textures","World",("Door" + orientation + ".png"))).convert_alpha()
        self.image = pg.Surface((36,36)).convert_alpha()
        self.image.blit(self.DOOR, (0, 0))
        
        self.rect = self.image.get_rect()

        #Sets door location#
        self.rect.x = (x * size)
        self.rect.y = (y * size)
        
        self.cost = cost
        
    def update(self, delta):
        
        #Creates collsion mask for door#
        self.mask = pg.mask.from_surface(self.image)
        

class Upgrade(pg.sprite.Sprite):
    
    def __init__(self, game, x, y, type):
        self.groups = game.all_sprites, game.all_upgrades

        #Initalises upgrade and texture used#
        size = game.tileSize
        pg.sprite.Sprite.__init__(self, self.groups)
        
        self.UPGRADE = pg.image.load(os.path.join("Textures","World","ShopUpgrades.png")).convert_alpha()
        self.image = pg.Surface((32,32)).convert_alpha()
        self.image.blit(self.UPGRADE, (0, 0))
        
        self.rect = self.image.get_rect()

        #Sets upgrade location#
        self.rect.x = (x * size) + 2
        self.rect.y = (y * size) + 2
        
        values = [["Fast Mag",1000],["Quick Shot",1200],["Damage Boost",1400],["Double Mag",1400],["Burst Shot",1600]]
        try:
            self.cost = values[type-1][1]
            self.type = values[type-1][0]
            self.num = type
            
        except:
            self.cost = 1000
            self.type = values[1][0]
            self.num = 1
            
        #Creates collsion mask for upgrade#
        self.mask = pg.mask.from_surface(self.image)
        
    def update(self, delta):
        self.mask = pg.mask.from_surface(self.image)


class Perks(pg.sprite.Sprite):
    
    def __init__(self, game, x, y, type):
        self.groups = game.all_sprites, game.all_perks

        #Initalises upgrade and texture used#
        size = game.tileSize
        pg.sprite.Sprite.__init__(self, self.groups)
        
        self.PERKS = pg.image.load(os.path.join("Textures","World","ShopPerks.png")).convert_alpha()
        self.image = pg.Surface((32,32)).convert_alpha()
        self.image.blit(self.PERKS, (0, 0))
        
        self.rect = self.image.get_rect()

        #Sets upgrade location#
        self.rect.x = (x * size) + 2
        self.rect.y = (y * size) + 2

        #0: +100 base health, 1: -1 seconds before health, 2: +5 points for damage and +20 points for kills, 3: gives bettween 0 and 5 ammo for a gun after kill#
        values = ["Long Life","Self Care","Pick Pocket","Salvager"]
        try:
            self.type = values[type]
            self.num = type
            
        except:
            self.type = values[0]
            self.num = 1
            
        #Creates collsion mask for upgrade#
        self.mask = pg.mask.from_surface(self.image)
        
    def update(self, delta):
        self.mask = pg.mask.from_surface(self.image)


class Spawner(pg.sprite.Sprite):

    def __init__(self, game, x, y, link):
        
        self.groups = game.all_sprites, game.all_spawners

        #Initalises spawner and texture used#
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        self.SPAWNER = pg.image.load(os.path.join("Textures","World","Spawner.png")).convert_alpha()
        self.image = pg.Surface((32,32)).convert_alpha()
        self.image.blit(self.SPAWNER, (0, 0))
        
        self.rect = self.image.get_rect()

        #Sets tile location#
        self.rect.x = (x * game.tileSize) + 2
        self.rect.y = (y * game.tileSize) + 2

        self.linkedDoors = link
        self.canSpawn = False

        #Creates collsion mask for spawner#
        self.mask = pg.mask.from_surface(self.image)
        
    def update(self, delta):

        #Used to allow enemies to spawn at if a door connected to it is open (if there is no door is allowed by default)#
        if not self.canSpawn:

            if self.linkedDoors == []:
                self.canSpawn = True
                
            else:
                for i in self.linkedDoors:
                    if list(self.game.aiMap[i[1]])[i[0]] == "*":
                        self.canSpawn = True
        
        self.mask = pg.mask.from_surface(self.image)

import pygame as pg
import random, math, time

class player(pg.sprite.Sprite):
    def __init__(self, game, x , y):

        #Allows other parts of class to grab values from main class#
        self.game = game
        
        #Sprite texture initialisation#
        self.PLAYER_SPRITE = pg.image.load("Textures\Entities\Player\PrototypeMan.png").convert_alpha()

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
        
    def update(self, delta):
        #Main player update loop, called every frame#

        #Updates the movement of the player#
        self.entityMovement(delta)

        #Creates collsion mask for player#
        self.mask = pg.mask.from_surface(self.image)
        
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

    def entityMovement(self, delta):
        #Used to detect player key input#
        keys = pg.key.get_pressed()

        #Updates the players movement per frame being greater the smaller the frame rate#
        currentSpeed = 300 * (delta / 1000)
        
        #X coordinate control
        if keys[self.game.keyList["East"][1]] and keys[self.game.keyList["West"][1]]:
            #Stops movement if both are pressed#
            self.currentSpeed[0] = 0
        
        elif keys[self.game.keyList["East"][1]]:
            #Move player east#
            self.currentSpeed[0] = currentSpeed
            
        elif keys[self.game.keyList["West"][1]]:
            #Move player west#
            self.currentSpeed[0] = -currentSpeed
        
        #Y coordinate control
        if keys[self.game.keyList["North"][1]] and keys[self.game.keyList["South"][1]]:
            #Stops movement if both are pressed#
            self.currentSpeed[1] = 0

        elif keys[self.game.keyList["North"][1]]:
            #Move player north#
            self.currentSpeed[1] = -currentSpeed
        
        elif keys[self.game.keyList["South"][1]]:
            #Move player south#
            self.currentSpeed[1] = currentSpeed
        
        #Calls code to change postion of player#
        self.updatePosition()
        #Resets the movement vector for the player#
        self.currentSpeed = [0,0]

import pygame as pg

class Tile(pg.sprite.Sprite):

    def __init__(self, game, x, y, tileX, tileY, tileCollide):
        
        #Sets if tile can be collided with or not#
        if tileCollide == True:
            self.groups = game.all_sprites, game.all_tiles
        else:
            self.groups = game.all_sprites

        #Initalises sprite, sets size and texture used#
        size = game.tileSize
        pg.sprite.Sprite.__init__(self, self.groups)
        
        self.image = pg.Surface((36,36)).convert_alpha()
        self.image.blit(game.TILE_SET,(0, 0), ((tileX)* size, (tileY)* size, size, size))
        
        self.rect = self.image.get_rect()

        #Sets tile location#
        self.rect.x = x * size
        self.rect.y = y * size

        #Creates collsion mask for tile#
        self.mask = pg.mask.from_surface(self.image)

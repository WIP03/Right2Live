import pygame as pg

class Tile(pg.sprite.Sprite):

    def __init__(self, game, x, y):
        #Sets the tile size, sprite and colour#
        self.groups = game.all_sprites, game.all_tiles
        pg.sprite.Sprite.__init__(self, self.groups)
        
        self.image = pg.Surface((36,36)).convert_alpha()
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect()

        #Sets tile location#
        self.rect.x = x
        self.rect.y = y

        #Creates collsion mask for tile#
        self.mask = pg.mask.from_surface(self.image)

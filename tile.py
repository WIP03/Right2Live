import pygame as pg

class Tile(pg.sprite.Sprite):

    def __init__(self):
        #Sets the tile size, sprite and colour#
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((300,300)).convert_alpha()
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect()

        #Sets tile location#
        self.rect.x = 0
        self.rect.y = 0

        #Creates collsion mask for tile#
        self.mask = pg.mask.from_surface(self.image)

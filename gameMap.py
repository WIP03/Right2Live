import pygame as pg

class Map():

    def __init__(self, game, mapDirectory):

        #Reads gamefile from textfile in given directory#
        self.gameboard = []
        tempboard = open(mapDirectory, "r")

        for i in tempboard:
            self.gameboard.append(i)

        #Closes textfile#
        tempboard.close()

        #Creats constants about the map#
        self.tilesX = len(self.gameboard[0]) - 1
        self.tilesY = len(self.gameboard)
        
        self.pixelX = self.tilesX * game.tileSize
        self.pixelY = self.tilesY * game.tileSize


class MapView():

    def __init__(self, x, y):
        #Sets up the game view from map data information#
        self.viewRect = pg.Rect(0,0,x,y)
        self.width = x
        self.height = y

    def createView(self, entity):
        #Function moves the sprite by offset given by the MapView#
        return entity.rect.move(self.viewRect.topleft)

    def update(self, game, player):
        #Changes the postion of the map view based on that of the player (with corner limits)#
        x = -player.rect.x + int(game.screenWidth/2)
        y = -player.rect.y + int(game.screenHeight/2)

        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - game.screenWidth), x)
        y = max(-(self.height - game.screenHeight), y)
        
        self.viewRect = pg.Rect(x, y, self.width, self.height)

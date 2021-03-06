import common.game
from common.field import Field, Place
from common.coordinates import Coord, DeltaCoord
from common.utils import distance
from tiles.tiles import TileCoins,  TileTreasure, TileArrow, \
    TileCannon, TileHorse, TileIce, TilePitfall, TileCroco,  \
    TileBalloon, TileAirplane,  TileFort, \
    TileBarrel, TileCave,  TileJungle, \
    TileEmpty, TileWhirl
# from tiles.tiles import TileRum, TileCannibal, TileFortAborigine, \
#     TileCarramba,  TileLighthouse, TileBenGunn, TileMissionary, TileFriday, \
#     TileQuake, TileGrass
from game.items import Ship, Pirate, Coin, Chest
import random
import time

FIELD_SIZE = 13
GAMERS = 4
PIRATES = 3


class Game(common.game.Game):
    def __init__(self):
        self.size = FIELD_SIZE
        self.middle = FIELD_SIZE // 2
        self.tiles = self.generateTilePack()
        self.tileCounter = 0
        field = self.generateField()
        gamers = [i for i in range(0, GAMERS)]
        items = self.generateItems(gamers)

        common.game.Game.__init__(
            self, field=field, items=items, gamers=gamers)

    def generateField(self):
        return Field(
            places={
                Coord(x, y): self.generatePlace(Coord(x, y))
                for x in range(0, self.size)
                for y in range(0, self.size)
            })

    def generatePlace(self, coord: Coord):
        placeType = self.getPlaceType(coord)
        tile = None
        if (placeType == "GROUND"):
            tile = self.nextTile()
        return Place(
            placeType=placeType,
            tile=tile,
            opened=False
        )

    def getPlaceType(self, coord: Coord):
        (dx, dy) = (
            distance(self.middle, coord.x),
            distance(self.middle, coord.y)
        )
        if dx > self.middle \
                or dy > self.middle \
                or (dx == self.middle and dy == self.middle):
            return 'EXCLUDED'
        if dx == self.middle \
                or dy == self.middle \
                or (dx == self.middle-1 and dy == self.middle-1):
            return 'SEA'
        return 'GROUND'

    def openPlace(self, coord: Coord):
        place = self.field.places[coord]
        if (not place.opened):
            place.opened = True
            if not place.tile:
                return True
            f = place.tile.onOpen(self)
            if (f):
                f(coord=coord)
            return True
        return False

    def generateItems(self, gamers):
        items = []
        for gamer in gamers:
            items += [
                Ship(gamer=gamer, coordinates=self.getStartCoord(gamer))
                for _ in range(0, 1)]
            items += [
                Pirate(gamer=gamer, coordinates=self.getStartCoord(gamer))
                for _ in range(0, PIRATES)]
        items += [Coin() for _ in range(0, 37)]
        items += [Chest() for _ in range(0, 1)]
        return {i: val for i, val in enumerate(items)}

    def getStartCoord(self, gamer):
        places = [
            Coord(self.middle, 0),
            Coord(0, self.middle),
            Coord(self.middle, self.size-1),
            Coord(self.size-1, self.middle)
        ]
        return places[gamer % GAMERS]

    def moveItem(self, itemId: int, destination: Coord):
        item = self.items.get(itemId)
        if not item:
            return False
        destination = self.checkWhirl(item, destination)
        common.game.Game.moveItem(self, itemId, destination)
        self.openPlace(Coord(destination.x, destination.y))

    def nextTile(self):
        if self.tileCounter >= len(self.tiles):
            self.tileCounter = (self.tileCounter) % len(self.tiles)
            random.shuffle(self.tiles)
        result = self.tiles[self.tileCounter]
        self.tileCounter += 1
        return result

    def generateTilePack(self):
        items = []
        items += [TileEmpty(random.randint(1, 4)) for _ in range(18)]

        items += [TileArrow([DeltaCoord(1, 0)], angle=random.randint(0, 3))
                  for _ in range(3)]
        items += [TileArrow([DeltaCoord(1, 1)], angle=random.randint(0, 3))
                  for _ in range(3)]
        items += [TileArrow(
            [DeltaCoord(1, 0), DeltaCoord(-1, 0)],
            angle=random.randint(0, 3)
        ) for _ in range(3)]
        items += [TileArrow(
            [DeltaCoord(1, 1), DeltaCoord(-1, -1)],
            angle=random.randint(0, 3)
        ) for _ in range(3)]
        items += [TileArrow(
            [DeltaCoord(1, 1), DeltaCoord(-1, 0), DeltaCoord(0, -1)],
            angle=random.randint(0, 3)
        ) for _ in range(3)]
        items += [TileArrow(
            [DeltaCoord(1, 0), DeltaCoord(-1, 0),
             DeltaCoord(0, 1), DeltaCoord(0, -1)],
            angle=random.randint(0, 3)
        ) for _ in range(3)]
        items += [TileArrow(
            [DeltaCoord(1, 1), DeltaCoord(-1, 1),
             DeltaCoord(1, -1), DeltaCoord(-1, -1)],
            angle=random.randint(0, 3)
        ) for _ in range(3)]

        items += [TileHorse() for _ in range(2)]

        items += [TileWhirl(2) for _ in range(5)]
        items += [TileWhirl(3) for _ in range(4)]
        items += [TileWhirl(4) for _ in range(2)]
        items += [TileWhirl(5) for _ in range(1)]

        items += [TileIce() for _ in range(6)]
        items += [TilePitfall() for _ in range(3)]
        items += [TileCroco() for _ in range(4)]
        # items += [TileCannibal() for _ in range(1)]
        items += [TileFort() for _ in range(2)]
        # items += [TileFortAborigine() for _ in range(1)]

        items += [TileCoins(1) for _ in range(5)]
        items += [TileCoins(2) for _ in range(5)]
        items += [TileCoins(3) for _ in range(3)]
        items += [TileCoins(4) for _ in range(2)]
        items += [TileCoins(5) for _ in range(1)]
        items += [TileTreasure()]

        items += [TileAirplane() for _ in range(1)]
        items += [TileBalloon() for _ in range(2)]
        items += [TileCannon(angle=random.randint(0, 3)) for _ in range(2)]
        items += [TileCave() for _ in range(4)]
        items += [TileJungle() for _ in range(3)]
        # items += [TileGrass() for _ in range(2)]

        # items += [TileRum(1) for _ in range(3)]
        # items += [TileRum(2) for _ in range(2)]
        # items += [TileRum(3) for _ in range(1)]

        items += [TileBarrel() for _ in range(4)]

        for i in range(10):
            random.shuffle(items)
            time.sleep(random.random()*0.5)

        return items

    def placeCoins(self, money, coord):
        coinKeys = self.getUnplacedItemKeys('Coin')
        if (len(coinKeys) < money):
            return False
        for i in range(money):
            self.items[coinKeys[i]].coordinates = coord
        return True

    def placeChest(self, coord):
        keys = self.getUnplacedItemKeys('Chest')
        if (len(keys) < 1):
            return False
        self.items[keys[0]].coordinates = coord
        return True

    def openAll(self):
        for p in self.field.places:
            self.field.places[p].opened = True

    def checkWhirl(self, item, destination: Coord):
        if not item.coordinates:
            return destination
        ship = self.items[
            [
                i for i in self.items
                if self.items[i].gamer == item.gamer
                and self.items[i].getClassName() == item.getClassName()
            ][0]
        ]
        if ship.coordinates == Coord(destination.x, destination.y):
            return destination
        currentPlace = self.field.places[Coord(item.coordinates.x, item.coordinates.y)]
        destinationPlace = self.field.places[Coord(destination.x, destination.y)]
        if currentPlace.tile and currentPlace.tile.getClassName() == 'TileWhirl':
            if (item.coordinates.z):
                return Coord(item.coordinates.x, item.coordinates.y, item.coordinates.z - 1)
            else:
                return destination
        elif destinationPlace.tile and destinationPlace.tile.getClassName() == 'TileWhirl':
            return Coord(destination.x, destination.y, destinationPlace.tile.steps - 1)
        return destination

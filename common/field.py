from common.coordinates import Coord


class Place(object):
    def __init__(self, placeType=None, tile=None, opened=False, orientation=0):
        self.type = placeType
        self.tile = tile
        self.orientation = orientation
        self.opened = opened

    def __repr__(self):
        return f"<{self.type}: {self.opened} {self.tile}>"

    def setTile(self, tile):
        self.tile = tile

    def to_json(self):
        place = {}
        if (self.type):
            place['type'] = self.type
        if (self.tile):
            if (self.opened):
                place['tile'] = self.tile
                if (self.tile.angle):
                    place['orientation'] = self.tile.angle
            else:
                place['tile'] = True
        return place


class Field(object):
    def __init__(self, places={}):
        self.places = places

    def to_json(self):
        return [
            [self.places.get(Coord(x, y))
                for x in set(key.x for key in self.places.keys())
             ]
            for y in set(key.y for key in self.places.keys())
        ]

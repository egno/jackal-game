from common.coordinates import Coord, Move


class Item(object):
    def __init__(self, coordinates: Coord = None, gamer = None):
        self.coordinates = coordinates
        self.gamer = gamer
    
    def getClassName(self):
        return self.__class__.__name__

    def go(self, coordinates: Coord):
        self.coordinates = coordinates

    def to_json(self):
        result = {
            'type': self.getClassName()
        }
        if (self.gamer is not None): result['gamer'] = self.gamer
        if (self.coordinates):
            result['x'] = self.coordinates.x
            result['y'] = self.coordinates.y
            if (self.coordinates.z):
                result['step'] = self.coordinates.z
        return result


class Character(Item):
    pass

class ItemMove(object):
    def __init__(self, item: Item, move: Move, payload=None):
        self.item = item
        self.move = move
        self.payload = payload

    def __repr__(self):
        if (self.payload):
            return f"<{self.__class__.__name__} {self.item.getClassName()}+{self.payload} {self.move}>"

        return f"<{self.__class__.__name__} {self.item.getClassName()} {self.move}>"

    def accept(self):
        self.item.go(self.move.destination)
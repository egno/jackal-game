from common.field import Field
from common.item import ItemMove, Item
from common.coordinates import Coord, Move
import json


class Game(object):
    def __init__(self, field: Field = {}, items={}, gamers=[]):
        self.field = field
        self.items = items
        self.gamers = gamers
        self.turn = 0
        self.status = None
        self.log = []

    def moveItem(self, itemId: int, destination: Coord):
        item = self.items.get(itemId)
        if not (item):
            return False
        itemMove = ItemMove(item, Move(
            start=item.coordinates, destination=destination))
        if not self.checkMove(itemMove):
            return False
        itemMove.accept()
        self.logMove(itemMove)
        return True

    def newItem(self, item: Item):
        maxKey = max(self.items.keys())
        if (maxKey):
            key = maxKey+1
        else:
            key = 0
        self.items[key] = item

    def checkMove(self, itemMove: ItemMove):
        return True

    def changeTurn(self):
        self.turn = (self.turn + 1) % len(self.gamers)
        return self

    def to_json(self):
        return {
            'field': self.field,
            'items': self.items,
            'gamers': self.gamers,
            'status': self.status,
            'turn': self.turn
        }

    def logMove(self, itemMove: ItemMove):
        logRecord = {
            'turn': self.turn,
            'item': {
                'class': itemMove.item.getClassName()
            },
            'coordinates': {
                'x': itemMove.move.destination.x,
                'y': itemMove.move.destination.y,
                'step': itemMove.move.destination.z
            }
        }
        self.log += [logRecord]
        print(logRecord)
        return logRecord

    def getUnplacedItemKeys(self, itemClass):
        return [key for key in self.items if (
            self.items[key].getClassName() == itemClass
            and (not self.items[key].coordinates)
        )]

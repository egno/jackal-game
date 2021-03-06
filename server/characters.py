from items import Item, checkPlaced
import moves

class Character(Item):
    def __init__(self, gamer=None, x=None, y=None):
        Item.__init__(self, gamer, x, y)
        self.isCharacter = True
        self.lastMove = None

    def availableMoves(self):
        return []

    def getItems(self):
        return [item for item in self.gamer.game.items if item.character == self]

    def move(self, move, force=False):
        if not force:
            moves = [m for m in self.availableMoves() if m.x == move.x and m.y == move.y and m.payload == move.payload]
            if not len(moves):
                return None
        items = [item for item in self.getPlace().getItems() if item.className() == move.payload and move.payload]
        place = self.gamer.game.field.getPlaceByCoordinates(move.x, move.y)
        if not place:
            return None
        print(place.tile)
        (self.x, self.y, self._x, self._y) = (move.x, move.y, self.x, self.y)
        openedTile = place.open()
        self.lastMove = move
        if openedTile:
            actionResult = openedTile.activate(self)
        else:
            actionResult = openedTile.action(self)
        print(actionResult)
        self.lastMove = move
        if len(items):
            (items[0].x, items[0].y) = (self.x, self.y)
            ship = self.gamer.getShip()
            if items[0].x == ship.x and items[0] == ship.y:
                items[0].gamer = self.gamer
            print(items[0])
        return self

    def getPlace(self):
        return self.gamer.game.field.getPlaceByCoordinates(self.x, self.y)


class Pirate(Character):
    def __init__(self, gamer=None, x=None, y=None):
        Character.__init__(self, gamer, x, y)
        self.burder = None
    
    @checkPlaced
    def availableMoves(self):
        result=[]
        fieldPlace = self.getPlace()
        if not fieldPlace:
            return []
        if fieldPlace.isGround():
            availablePlaces = [
                p 
                for p 
                in fieldPlace.getNeighboringPlaces(moves.directions8)
                if p and (p.isGround() or (p.isSea() and p.hasTeamShip(self.gamer.team)))
                ]
            result += [moves.Move(p.x, p.y) for p in availablePlaces]
            for payload in list(set([item.className() for item in fieldPlace.getItems() if item.moveable])):
                result += [moves.Move(p.x, p.y, payload) for p in availablePlaces if p.opened or p.hasTeamShip(self.gamer.team)]
        else:
            if fieldPlace.hasTeamShip(self.gamer.team):
                result += [moves.Move(p.x, p.y) for p in
                        [place 
                        for place 
                        in fieldPlace.getNeighboringPlaces(moves.directions4)
                        if place
                        ]
                    if p and p.isGround()
                    ]
            else:
                result +=  [moves.Move(p.x, p.y) for p in
                        [place 
                        for place 
                        in fieldPlace.getNeighboringPlaces(moves.directions8)
                        if place
                        ]
                    if p and p.isSea()
                    ]
        return list(set(result))

class Missionary(Pirate):
    pass 


class Friday(Pirate):
    pass 
         

class BenGunn(Pirate):
    pass 
         

class Ship(Character):
    def __init__(self, gamer=None, x=None, y=None):
        Character.__init__(self, gamer, x, y)
    
    @checkPlaced
    def availableMoves(self):
        result=[]
        fieldPlace = self.getPlace()
        if not fieldPlace:
            return []
        result += [moves.Move(p.x, p.y) for p in
                [place 
                for place 
                in fieldPlace.getNeighboringPlaces(moves.directions4)
                if place
                ]
            if p and not p.isGround() and 
                len([pn for pn in p.getNeighboringPlaces(moves.directions4) if pn and pn.isGround()]) > 0]
        return list(set(result))
                    

        




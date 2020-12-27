import pygame
from abc import ABC, abstractmethod
from utils import Spritesheet, Assets
from sounds import Sounds
from constants import *
from copy import deepcopy


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f'{self.x}, {self.y}'


class SavableObject(ABC):
    @abstractmethod
    def save(self):
        pass


class RenderableObject(ABC):
    def __init__(self, pos=Position(0, 0), size=TILE_SIZE):
        self._position = pos
        self.__size = size
    
    def update(self):
        pass

    def render(self, screen):
        image = self.image
        rect = image.get_rect()
        rect.topleft = self.position.x % HORIZONTAL_TILES_COUNT * TILE_SIZE[0] + LEFT_SPACE, self.position.y % VERTICAL_TILES_COUNT * TILE_SIZE[1] + TOP_SPACE
        screen.blit(image, rect)

    @property
    def position(self):
        return self._position
    
    @property
    def size(self):
        return self.__size

    @property
    @abstractmethod
    def image(self):
        pass


class AnimatedObject(ABC):
    def __init__(self, current_animation='move'):
        self._current_animation = current_animation
        self._frame = 0
    
    @property
    def frame(self):
        return self._frame


class Item(RenderableObject, SavableObject):
    def __init__(self, name='', price=0, pos=Position(0, 0)):
        super().__init__(pos)
        self.__name = name
        self.__price = price
    
    def save(self):
        data = {}
        data.update({'objtype': 'Item'})
        data.update({'name': self.name})
        data.update({'price': self.price})
        data.update({'position': self.position})
        return data
    
    @staticmethod
    def load(data):
        return Item( name=data['name'],
                     price=data['price'],
                     pos=data['position'] )
    
    @property
    def name(self):
        return self.__name
    
    @property
    def price(self):
        return self.__price

    @property
    def image(self):
        return pygame.transform.scale2x(Assets().items[self.name])


class Tile(RenderableObject, SavableObject):
    def __init__(self, type, pos=Position(0, 0)):
        super().__init__(pos)
        self._type = type
    
    def save(self):
        data = {}
        data.update({'objtype': 'Tile'})
        data.update({'type': self.type})
        data.update({'position': self.position})
        return data
    
    @staticmethod
    def load(data):
        return Tile( type=data['type'],
                     pos=data['position'] )
    
    @property
    def type(self):
        return self._type
    
    @property
    def image(self):
        return pygame.transform.scale(Assets().tiles[self._type], TILE_SIZE)


class Room(SavableObject):
    def __init__(self, tileset, objects=None):
        self._tiles = tileset
        if objects is None:
            self._objects = { 'entities': [],
                              'objects':  [],
                              'items':    [],
                              'portals':  [] }
        else:
            self._objects = objects
    
    def update(self, hero):
        for tile in self._tiles:
            tile.update()

        for category in self._objects:
            for obj in self._objects[category]:
                if isinstance(obj, Monster):
                    obj.update(hero)
                else:
                    obj.update()

    def render(self, screen):
        for tile in self._tiles:
            tile.render(screen)

        for category in self._objects:
            for obj in self._objects[category]:
                obj.render(screen)
    
    def save(self):
        data = {}
        
        tileset = []
        for tile in self._tiles:
            tileset.append(tile.save())
        data.update({'tiles': tileset})

        objects = {}
        for category in self._objects:
            category_objects = []
            for obj in self._objects[category]:
                category_objects.append(obj.save())
            objects.update({category: category_objects})
        data.update({'objects': objects})

        return data
    
    @staticmethod
    def load(data):
        tileset = []
        for tiledata in data['tiles']:
            tileset.append(Tile.load(tiledata))
        
        objects = {}
        for category in data['objects']:
            category_objects = []
            for objdata in data['objects'][category]:
                if objdata['objtype'] == 'Item':
                    category_objects.append(Item.load(objdata))
                elif objdata['objtype'] == 'Armor':
                    category_objects.append(Armor.load(objdata))
                elif objdata['objtype'] == 'Bargainer':
                    category_objects.append(Bargainer.load(objdata))
                elif objdata['objtype'] == 'Portal':
                    category_objects.append(Portal.load(objdata))
                elif objdata['objtype'] == 'Pirate':
                    category_objects.append(Pirate.load(objdata))
            objects.update({category: category_objects})
                
        return Room(tileset, objects)
        
    @staticmethod
    def create(filename):
        try:
            with open(filename) as room:
                room_data = room.readlines()
            
            tileset = []
            for y in range(len(room_data)):
                line = room_data[y].strip('\n')
                for x in range(len(line)):
                    tileset.append(Tile(line[x], Position(x, y)))
            
            return Room(tileset)
        except:
            raise SystemError(f'Unable to load room {filename}')
    
    def tileOn(self, pos: Position):
        for tile in self._tiles:
            if tile.position.x == pos.x and tile.position.y == pos.y:
                return tile
        return None


class Entity(RenderableObject, AnimatedObject, SavableObject, ABC):
    def __init__(self, name='', hlth=100, dmg=0, armor=0, pos=Position(0, 0), size=(32, 32), current_animation='move'):
        super(Entity, self).__init__(pos, size)
        super(RenderableObject, self).__init__(current_animation)
        self.__name = name
        self._health = hlth
        self._damage = dmg
        self._armor = armor

    def isDead(self):
        return self._health <= 0
    
    @property
    def name(self):
        return self.__name
    
    @property
    def health(self):
        return self._health
    


class Hero(Entity):
    MAX_HEALTH = 7

    def __init__( self, name='', health=MAX_HEALTH, damage=3, armor=0, pos=Position(0, 0), money=0, inventory=None, effects=None, side=RIGHT):
        super().__init__(name, health, damage, armor, pos)
        self._money = money
        if inventory is None:
            self._inventory = { 'items':
                                         { 1: None,
                                           2: None,
                                           3: None,
                                           4: None,
                                           5: None,
                                           6: None },
                                'equipment':
                                             { 'head':  None,
                                               'chest': None,
                                               'legs':  None,
                                               'arm':   None }
                               }
        else: 
            self._inventory = inventory
        
        if effects is None:
            self._effects = { 'strength':     0,
                              'invisibility': 0,
                              'poisoning':    0 }
        else:
            self._effects = effects
        self.__attack_count = 0
        self.__side = side
        self._image = pygame.transform.scale(Assets().hero_animations['move'][0], HERO_SIZE)

    def update(self):
        self._frame += 1

        if self._current_animation == 'attack':
            self._image = Assets().hero_animations[self._current_animation][self.frame//4%FC_HERO_ATTACK]
            if  self.frame == 9 or self.frame == 29 or self.frame == 49:
                Sounds().sword_swing.play()
            if self.frame == 4*self.__attack_count:
                self._frame = 0
                self.__attack_count = 0
                self._current_animation = 'move'
                self._image = Assets().hero_animations[self._current_animation][FC_HERO_MOVE*int(bool(self._inventory['equipment']['arm']))]

    def render(self, screen):
        image = self.image
        rect = image.get_rect()
        if self._current_animation == 'move':
            rect.topleft = self.position.x % HORIZONTAL_TILES_COUNT * TILE_SIZE[0] + LEFT_SPACE, self.position.y % VERTICAL_TILES_COUNT * TILE_SIZE[1] + TOP_SPACE
        elif self._current_animation == 'attack':
            if self.__side == RIGHT:
                rect.topleft = self.position.x % HORIZONTAL_TILES_COUNT * TILE_SIZE[0] + LEFT_SPACE - 19, self.position.y % VERTICAL_TILES_COUNT * TILE_SIZE[1] + TOP_SPACE - 29
            elif self.__side == LEFT:
                rect.topleft = self.position.x % HORIZONTAL_TILES_COUNT * TILE_SIZE[0] + LEFT_SPACE - 75, self.position.y % VERTICAL_TILES_COUNT * TILE_SIZE[1] + TOP_SPACE - 29
        screen.blit(pygame.transform.flip(image, self.__side, False), rect)

    @Entity.health.setter
    def health(self, value):
        if value >= Hero.MAX_HEALTH:
            self._health = Hero.MAX_HEALTH
        else:
            self._health = value

    def move(self, key, room: Room):
        def can_stand(step_x=0, step_y=0):
            if step_x != 0:
                return room.tileOn(Position(int(self.position.x+step_x) % HORIZONTAL_TILES_COUNT, int(self.position.y) % VERTICAL_TILES_COUNT)).type != '#' and room.tileOn(Position(int(self.position.x+step_x) % HORIZONTAL_TILES_COUNT, int(self.position.y+1) % VERTICAL_TILES_COUNT)).type != '#' and (self.position.y % 1 == 0 or (room.tileOn(Position(int(self.position.x+step_x) % HORIZONTAL_TILES_COUNT, int(self.position.y+1) % VERTICAL_TILES_COUNT)).type != '#' and room.tileOn(Position(int(self.position.x+step_x) % HORIZONTAL_TILES_COUNT, int(self.position.y+2) % VERTICAL_TILES_COUNT)).type != '#'))
            elif step_y != 0:
                return room.tileOn(Position(int(self.position.x) % HORIZONTAL_TILES_COUNT, int(self.position.y+step_y) % VERTICAL_TILES_COUNT)).type != '#' and room.tileOn(Position(int(self.position.x+1) % HORIZONTAL_TILES_COUNT, int(self.position.y+step_y) % VERTICAL_TILES_COUNT)).type != '#' and (self.position.x % 1 == 0 or (room.tileOn(Position(int(self.position.x+1) % HORIZONTAL_TILES_COUNT, int(self.position.y+step_y) % VERTICAL_TILES_COUNT)).type != '#' and room.tileOn(Position(int(self.position.x+2) % HORIZONTAL_TILES_COUNT, int(self.position.y+step_y) % VERTICAL_TILES_COUNT)).type != '#'))

        self._image = Assets().hero_animations['move'][self.frame//7%FC_HERO_MOVE+FC_HERO_MOVE*int(bool(self._inventory['equipment']['arm']))]
        if key == pygame.K_DOWN:
            if self.position.y % VERTICAL_TILES_COUNT == VERTICAL_TILES_COUNT - HERO_SIZE_IN_TILES[1]:
                self.position.y += HERO_SIZE_IN_TILES[1]
            elif can_stand(step_y=HERO_SIZE_IN_TILES[1]):
                self.position.y += 1/4
        elif key == pygame.K_UP:
            if self.position.y % VERTICAL_TILES_COUNT == 0:
                self.position.y -= 1
            elif can_stand(step_y=-1/4):
                self.position.y -= 1/4
        elif key == pygame.K_LEFT:
            if self.position.x % HORIZONTAL_TILES_COUNT == 0:
                self.position.x -= HERO_SIZE_IN_TILES[0]
            elif can_stand(step_x=-1/4):
                self.position.x -= 1/4
            self.__side = LEFT
        elif key == pygame.K_RIGHT:
            if self.position.x % HORIZONTAL_TILES_COUNT == HORIZONTAL_TILES_COUNT - HERO_SIZE_IN_TILES[0]:
                self.position.x += HERO_SIZE_IN_TILES[0]
            elif can_stand(step_x=HERO_SIZE_IN_TILES[0]):
                self.position.x += 1/4
            self.__side = RIGHT

    def attack(self, entity_lst):
        if self._inventory['equipment']['arm'] is not None:
            self._current_animation = 'attack'
            if self.__attack_count == 0:
                self._frame = 0
                self.__attack_count = 6
            elif self.__attack_count == 6:
                self.__attack_count = 12
            elif self.__attack_count == 12:
                self.__attack_count = FC_HERO_ATTACK
        
            for entity in entity_lst:
                if isinstance(entity, Monster):
                    if self.__side == RIGHT and self.position.x+64/TILE_SIZE[0] <= entity.position.x <= self.position.x+95/TILE_SIZE[0] and self.position.y-13 <= entity.position.y <= self.position.y+45/TILE_SIZE[1]:
                        entity._health -= self._damage
                        if not entity.isDead():
                            Sounds().hit.play()
                    elif self.__side == LEFT and self.position.x-61/TILE_SIZE[0] <= entity.position.x <= self.position.x-32/TILE_SIZE[0] and self.position.y-13 <= entity.position.y <= self.position.y+45/TILE_SIZE[1]:
                        entity._health -= self._damage
                        if not entity.isDead():
                            Sounds().hit.play()

    def interact(self):
        pass

    def take_item(self, item: Item, slot: int):
        self._inventory['items'][slot] = item

    def remove_item(self, slot: int):
        item = self._inventory['items'][slot]
        item.position.x = round(self.position.x+35/TILE_SIZE[0])
        item.position.y = round(self.position.y+39/TILE_SIZE[1])
        self._inventory['items'][slot] = None

    def dialogue(self):
        pass

    def empty_slot(self):
        for i in range(1, 7):
            if self._inventory['items'][i] is None:
                return i
        return False

    def save(self):
        data = {}
        data.update({'objtype': 'Hero'})
        data.update({'name': self.name})
        data.update({'health': self.health})
        data.update({'damage': self._damage})
        data.update({'armor': self._armor})
        data.update({'position': self.position})
        data.update({'money': self._money})
        inventory = deepcopy(self._inventory)
        for invtype in inventory:
            for slot in inventory[invtype]:
                if inventory[invtype][slot] is not None:
                    inventory[invtype][slot] = inventory[invtype][slot].save()
        data.update({'inventory': inventory})
        data.update({'effects': self._effects})
        data.update({'side': self.__side})
        return data
    
    @staticmethod
    def load(data):
        inventory = data['inventory']
        for invtype in inventory:
            for slot in inventory[invtype]:
                objdata = inventory[invtype][slot]
                if objdata is not None:
                    if objdata['objtype'] == 'Item':
                        inventory[invtype][slot] = Item.load(objdata)
                    elif objdata['objtype'] == 'Armor':
                        inventory[invtype][slot] = Armor.load(objdata)
        return Hero( name=data['name'],
                     health=data['health'],
                     damage=data['damage'],
                     armor=data['armor'],
                     pos=data['position'],
                     money=data['money'],
                     inventory=inventory,
                     effects=data['effects'],
                     side=data['side'] )

    @property
    def side(self):
        return self.__side

    @property
    def image(self):
        return self._image


class Bargainer(Entity):
    def __init__(self, name='', pos=Position(0, 0), items=None):
        super().__init__(name, pos=pos)
        if items is None:
            self._items = { 1: None,
                            2: None,
                            3: None,
                            4: None,
                            5: None,
                            6: None,
                            7: None,
                            8: None,
                            9: None }
        else:
            self._items = items
        self._image = pygame.transform.scale2x(Assets().bargainer)
    
    def sell(self, hero: Hero, slot: int):
        if self._items[slot] is not None and hero._money >= self._items[slot].price and hero.empty_slot():
            hero._money -= self._items[slot].price
            hero.take_item(self._items[slot], hero.empty_slot())
            self._items[slot] = None

    def buy(self, hero: Hero, item: Item):
        if self.empty_slot():
            hero._money += item.price
            self._items[self.empty_slot] = item

    def empty_slot(self):
        for i in range(1, 10):
            if self._items[i] is None:
                return i
        return False
    
    def save(self):
        data = {}
        data.update({'objtype': 'Bargainer'})
        data.update({'name': self.name})
        data.update({'position': self.position})
        items = deepcopy(self._items)
        for slot in items:
            if items[slot] is not None:
                items[slot] = items[slot].save()
        data.update({'items': items})
        return data
    
    @staticmethod
    def load(data):
        return Bargainer( name=data['name'],
                          pos=data['position'],
                          items=data['items'] )
    
    @property
    def image(self):
        return self._image


class UsableItem(ABC):
    @abstractmethod
    def use(self, hero: Hero):
        pass


class EquipableItem(ABC):
    @abstractmethod
    def equip(self, hero: Hero, active_slot):
        pass

    @abstractmethod
    def remove(self, hero: Hero, active_slot):
        pass


class HealthPotion(Item, UsableItem):
    __value = 20
    __cooldown = 20

    def use(self, hero: Hero):
        hero.health += HealthPotion.__value


class InvisibilityPotion(Item, UsableItem):
    __duration = 20
    __cooldown = 35

    def use(self, hero: Hero):
        hero._effects['invisibility'] = InvisibilityPotion.__duration


class StrengthPotion(Item, UsableItem):
    __duration = 40
    __cooldown = 60

    def use(self, hero: Hero):
        hero._effects['strength'] = StrengthPotion.__duration


class Armor(Item, EquipableItem):
    def __init__(self, name='', price=0, pos=Position(0, 0), armor=0, slot=''):
        super().__init__(name, price, pos)
        self.__armor = armor
        self.__slot = slot
    
    def equip(self, hero: Hero, active_slot):
        if hero._inventory['equipment'][self.__slot] is None:
            hero._inventory['items'][active_slot] = None
            hero._inventory['equipment'][self.__slot] = self
            hero._armor += self.__armor
        else:
            print("Slot is busy!")
    
    def remove(self, hero: Hero, active_slot):
        slot = hero.empty_slot()
        if hero._inventory['equipment'][self.__slot] is not None and slot:
            hero._inventory['equipment'][self.__slot] = None
            hero._inventory['items'][slot] = self
            hero._armor -= self.__armor
        else:
            print("Slot is empty or inventory is full")
    
    def save(self):
        data = {}
        data.update({'objtype': 'Armor'})
        data.update({'name': self.name})
        data.update({'price': self.price})
        data.update({'position': self.position})
        data.update({'armor': self.armor})
        data.update({'slot': self.slot})
        return data

    @staticmethod
    def load(data):
        return Armor( name=data['name'],
                      price=data['price'],
                      pos=data['position'],
                      armor=data['armor'],
                      slot=data['slot'] )

    @property
    def armor(self):
        return self.__armor
    
    @property
    def slot(self):
        return self.__slot


class Portal(RenderableObject, AnimatedObject, SavableObject):
    def __init__(self, pos=Position(0, 0), size=(40, 75), is_active=True, frame=0, color='blue', destination={'position': Position(0, 0), 'level': ''}):
        super(Portal, self).__init__(pos, size)
        super(RenderableObject, self).__init__()
        self.is_active = is_active
        self.__color = color
        self.__destination = destination
        self._image = Assets().portals[color][0]
    
    def update(self):
        if self.is_active:
            self._frame += 1
            self._image = Assets().portals[self.color][self.frame//5%9]
    
    def save(self):
        data = {}
        data.update({'objtype': 'Portal'})
        data.update({'is_active': self.is_active})
        data.update({'frame': self.frame})
        data.update({'color': self.color})
        data.update({'destination': self.destination})
        data.update({'position': self.position})

        return data
    
    @staticmethod
    def load(data):
        return Portal( pos=data['position'],
                       is_active=data['is_active'],
                       frame=data['frame'],
                       color=data['color'],
                       destination=data['destination'] )
    
    @property
    def color(self):
        return self.__color
    
    @property
    def destination(self):
        return self.__destination

    @property
    def image(self):
        return self._image


class Monster(ABC):
    @abstractmethod
    def move(self, hero: Hero):
        pass

    @abstractmethod
    def attack(self, hero: Hero):
        pass


class Pirate(Entity, Monster):
    def __init__(self, name='Pirate', health=15, damage=0.5, armor=0, pos=Position(0, 0), size=(32, 50), side=RIGHT):
        super(Pirate, self).__init__(name, health, damage, armor, pos, size=(32, 50))
        self.__side = side
        self._image = pygame.transform.scale(Assets().entities[self.name]['move'][0], self.size)
    
    def update(self, hero: Hero):
        self._frame += 1

        if self._current_animation == 'attack':
            self._image = Assets().entities['Pirate']['attack'][self.frame//5%7]
            
            if self.frame == 5*7:
                self._frame = 0
                self._current_animation = 'move'
        elif self._current_animation == 'move':
            self._image = Assets().entities['Pirate']['move'][0]

        if (hero.position.x <= self.position.x < hero.position.x+2 and hero.position.y-1 <= self.position.y <= hero.position.y+2) or (self.__side == RIGHT and hero.position.x-46/TILE_SIZE[0] <= self.position.x <= hero.position.x-32/TILE_SIZE[0] and hero.position.y-1/2 <= self.position.y <= hero.position.y+2+1/2) or (self.__side == LEFT and hero.position.x+64/TILE_SIZE[1] <= self.position.x <= hero.position.x+78/TILE_SIZE[1] and hero.position.y-1/2 <= self.position.y <= hero.position.y+2+1/2):
            self.attack(hero)
        elif self._current_animation == 'move':
            self.move(hero)
        
    def render(self, screen):
        image = self.image
        rect = image.get_rect()
        if self.__side == RIGHT:
            rect.topleft = self.position.x % HORIZONTAL_TILES_COUNT * TILE_SIZE[0] + LEFT_SPACE, self.position.y % VERTICAL_TILES_COUNT * TILE_SIZE[1] + TOP_SPACE
        elif self.__side == LEFT:
            rect.topleft = self.position.x % HORIZONTAL_TILES_COUNT * TILE_SIZE[0] + LEFT_SPACE - 18, self.position.y % VERTICAL_TILES_COUNT * TILE_SIZE[1] + TOP_SPACE
        screen.blit(pygame.transform.flip(image, self.__side, False), rect)

    def __move_to_hero(self, hero: Hero):
        if self.frame % 2 == 0 or self.position.y == hero.position.y:
            if self.position.x >= hero.position.x:
                self.position.x -= 1/16
                self.__side = LEFT
            else:
                self.position.x += 1/16
                self.__side = RIGHT
        elif self.frame % 2 == 1 or self.position.x == hero.position.x:
            if self.position.y >= hero.position.y:
                self.position.y -= 1/16
            else:
                self.position.y += 1/16

    def move(self, hero: Hero):  # add hero argument
        if (self.position.x-hero.position.x)**2+(self.position.y-hero.position.y)**2 <= 9**2 and self.position.x // HORIZONTAL_TILES_COUNT == hero.position.x // HORIZONTAL_TILES_COUNT and self.position.y // VERTICAL_TILES_COUNT == hero.position.y // VERTICAL_TILES_COUNT:
            self.__move_to_hero(hero)
            self._image = Assets().entities['Pirate']['move'][self.frame//5%2]

    def attack(self, hero: Hero):
        if self._current_animation != 'attack':
            self._current_animation = 'attack'
            self._frame = 0
        
        if self.frame == 24 and ((hero.position.x <= self.position.x < hero.position.x+2 and hero.position.y-1 <= self.position.y <= hero.position.y+2) or (self.__side == RIGHT and hero.position.x-46/TILE_SIZE[0] <= self.position.x <= hero.position.x-32/TILE_SIZE[0] and hero.position.y-1/2 <= self.position.y <= hero.position.y+2+1/2) or (self.__side == LEFT and hero.position.x+64/TILE_SIZE[1] <= self.position.x <= hero.position.x+78/TILE_SIZE[1] and hero.position.y-1/2 <= self.position.y <= hero.position.y+2+1/2)):
            hero.health -= self._damage

    def save(self):
        data = {}
        data.update({'objtype': 'Pirate'})
        data.update({'name': self.name})
        data.update({'health': self.health})
        data.update({'damage': self._damage})
        data.update({'armor': self._armor})
        data.update({'position': self.position})
        data.update({'side': self.__side})
        return data

    @staticmethod
    def load(data):
        return Pirate( name=data['name'],
                       health=data['health'],
                       damage=data['damage'],
                       armor=data['armor'],
                       pos=data['position'],
                       side=data['side'] )

    @property
    def image(self):
        return self._image

    @property
    def side(self):
        return self.__side
    
    @side.setter
    def side(self, value):
        self.__side = value

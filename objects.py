import pygame
from abc import ABC, abstractmethod
from utils import Spritesheet, Assets


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class RenderableObject(ABC):
    def __init__(self, pos=Position(0, 0), size=(32, 32)):
        self._position = pos
        self.__size = size
    
    def update(self):
        pass

    def render(self, screen):
        image = self.image
        rect = image.get_rect()
        rect.topleft = self.position.x % (800/32) * self.__size[0], self.position.y % (608/32) * self.__size[1]
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


class InventoryBar(RenderableObject):
    def __init__(self):
        super().__init__(pos=Position(800-45, (607-270)//2), size=(45, 270))
        self._inventory = { 1: None,
                            2: None,
                            3: None,
                            4: None,
                            5: None,
                            6: None
                          }
        self._active_slot = None
        self._image = Assets.inventory_bar
    
    def render(self, screen):
        image = pygame.transform.scale(self.image, (self.size))
        for i in range(1, 7):
            if self._inventory[i] is not None:
                image.blit(self._inventory[i].image, pygame.Rect((6, 45*(i-1)+6), self._inventory[i].size))
        if self._active_slot is not None:
            image.blit(Assets.active_slot, pygame.Rect((0, 45*(self._active_slot-1)), (45, 45)))
        rect = image.get_rect()
        rect.topleft = self.position.x, self.position.y
        screen.blit(image, rect)

    @property
    def image(self):
        return self._image


class Item(RenderableObject):
    def __init__(self, name='', description='', price=0, status=1, pos=Position(0, 0)):
        super().__init__(pos)
        self.__name = name
        self.__description = description
        self.__price = price
        self._status = status
    
    @property
    def name(self):
        return self.__name
    
    @property
    def description(self):
        return self.__description
    
    @property
    def price(self):
        return self.__price
    
    @property
    def status(self):
        return self._status
    
    @property
    def image(self):
        return pygame.transform.scale2x(Assets.items[self.name])


class Tile(RenderableObject):
    def __init__(self, type, pos=Position(0, 0)):
        super().__init__(pos)
        self._type = type
    
    @property
    def type(self):
        return self._type
    
    @property
    def image(self):
        return pygame.transform.scale2x(Assets.tiles[self._type])


class Level:
    def __init__(self, tileset, name=''):
        self._tiles = tileset
        self._name = name
        # self._objects = []

    def update(self):
        # for obj in self._objects:
        #     obj.update()
        pass

    def render(self, screen):
        for tile in self._tiles:
            tile.render(screen)

        # for obj in self._objects:
        #     obj.render(screen)

    @staticmethod
    def load(filename):
        try:
            with open(filename) as level:
                level_data = level.readlines()
            
            tileset = []
            for y in range(len(level_data)):
                line = level_data[y].strip('\n')
                for x in range(len(line)):
                    tileset.append(Tile(line[x], Position(x, y)))
            
            return Level(tileset, name=filename)
        except:
            raise SystemError(f'Unable to load level {filename}')
    
    def tileOn(self, pos: Position):
        for tile in self._tiles:
            if tile.position.x == pos.x and tile.position.y == pos.y:
                return tile


class Entity(RenderableObject, ABC):
    def __init__(self, name='', hlth=100, dmg=0, armor=0, spd=0, pos=Position(0, 0), size=(32, 32)):
        super().__init__(pos, size)
        self.__name = name
        self._health = hlth
        self._damage = dmg
        self._armor = armor
        self._speed = spd
        self.__status = 1

    @property
    def health(self):
        return self._health
    
    def isDead(self):
        if self.health <= 0:
            self.__status = 0
        
        return self.__status


class Hero(Entity):
    MAX_HEALTH = 100

    def __init__(self, name='', hlth=MAX_HEALTH, dmg=3, armor=0, spd=5, pos=Position(0, 0), phrases_list={}):
        super().__init__(name, hlth, dmg, armor, spd, pos)
        self._money = 0
        self._inventory = {
            'items': {
                       1: None,
                       2: None,
                       3: None,
                       4: None,
                       5: None,
                       6: None
                     },

            'equipment': {
                           'head':  None,
                           'chest': None,
                           'legs':  None,
                           'arm':   None
                         }
        }

        self._effects = {
                          'strength':     0,
                          'invisibility': 0,
                          'poisoning':    0
                        }
        
        self._phrases = phrases_list
        self.__tmp = pygame.transform.scale2x(Assets.hero)
        self._image = self.__tmp
    
    @Entity.health.setter
    def health(self, value):
        if self.health >= Hero.MAX_HEALTH:
            self._health = Hero.MAX_HEALTH
        else:
            self._health = value

    def move(self, key, level: Level):
        # print((self.position.x, self.position.y))
        if key == pygame.K_DOWN:
            if not (1 <= int(self.position.y % (608/32)) <= 17) or level.tileOn(Position(int(self.position.x) % (800/32), int(self.position.y+1) % (608/32))).type != '#' and (self.position.x % 1 == 0 or level.tileOn(Position(int(self.position.x+1) % (800/32), int(self.position.y+1) % (608/32))).type != '#' ):
                self.position.y += 1/4
        elif key == pygame.K_UP:
            if not (1 <= int(self.position.y % (608/32)) <= 17) or level.tileOn(Position(int(self.position.x) % (800/32), int(self.position.y-1/4) % (608/32))).type != '#' and (self.position.x % 1 == 0 or level.tileOn(Position(int(self.position.x+1) % (800/32), int(self.position.y-1/4) % (608/32))).type != '#' ):
                self.position.y -= 1/4
        elif key == pygame.K_LEFT:
            if not (1 <= int(self.position.x % (800/32)) <= 23) or level.tileOn(Position(int(self.position.x-1/4) % (800/32), int(self.position.y) % (608/32))).type != '#' and (self.position.y % 1 == 0 or level.tileOn(Position(int(self.position.x-1/4) % (800/32), int(self.position.y+1) % (608/32))).type != '#'):
                self.position.x -= 1/4
            self._image = pygame.transform.flip(self.__tmp, True, False)
        elif key == pygame.K_RIGHT:
            if not (1 <= int(self.position.x % (800/32)) <= 23) or level.tileOn(Position(int(self.position.x+1) % (800/32), int(self.position.y) % (608/32))).type != '#' and (self.position.y % 1 == 0 or level.tileOn(Position(int(self.position.x+1) % (800/32), int(self.position.y+1) % (608/32))).type != '#'):
                self.position.x += 1/4
            self._image = self.__tmp

    def attack(self):
        pass

    def interact(self):
        pass

    def take_item(self, item: Item):
        slot = self.emptySlot()
        if slot:
            item._status = 1
            self._inventory['items'][slot] = item
        else:
            print("Inventory is full")

    def remove_item(self, slot: int):
        if self._inventory['items'][slot] is not None:
            item = self._inventory['items'][slot]
            item._status = 0
            item.position.x = round(self.position.x)
            item.position.y = round(self.position.y)
            self._inventory['items'][slot] = None
        else:
            print("Slot is empty!")

    def dialogue(self):
        pass

    def emptySlot(self):
        for i in range(1, 7):
            if self._inventory['items'][i] is None:
                return i
        return False

    @property
    def image(self):
        return self._image


class Bargainer(Entity):
    def __init__(self, name='', pos=Position(0, 0), phrases_list={}):
        super().__init__(name, pos=pos)
        self._items = {}
        self._phrases = phrases_list
        self._image = pygame.transform.scale2x(Assets.bargainer)
    
    def sell(self, hero: Hero, item: Item):
        if hero._money < item.price:
            print("You are poor!!")
        
        hero.get_item(item)
        hero._money -= item.price

        self._items[item] -= 1
        if self._items[item] == 0:
            self._items.pop(item)

    def buy(self, hero: Hero, item: Item):
        hero._money += item.price
        for i in range(1, 8):
            if hero._inventory[i] == item:
                hero._inventory[i] = None
        
        if item not in self._items.keys():
            self._items.update({item: 1})
        else:
            self._items[item] += 1
    
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


class InvisiblePotion(Item, UsableItem):
    __duration = 20
    __cooldown = 35

    def use(self, hero: Hero):
        hero._effects['invisibility'] = InvisiblePotion.__duration


class StrengthPotion(Item, UsableItem):
    __duration = 40
    __cooldown = 60

    def use(self, hero: Hero):
        hero._effects['strength'] = StrengthPotion.__duration


class Armor(Item, EquipableItem):
    def __init__(self, name='', description='', price=0, armor=0, slot=''):
        super().__init__(name, description, price)
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
        slot = hero.emptySlot()
        if hero._inventory['equipment'][self.__slot] is not None and slot:
            hero._inventory['equipment'][self.__slot] = None
            hero._inventory['items'][slot] = self
            hero._armor -= self.__armor
        else:
            print("Slor is empty or inventory is full")




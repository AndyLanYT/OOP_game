import pygame
from abc import ABC, abstractmethod
from utils import Spritesheet, Assets
from constants import *


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class RenderableObject(ABC):
    def __init__(self, pos=Position(0, 0), size=TILE_SIZE):
        self._position = pos
        self.__size = size
    
    def update(self):
        pass

    def render(self, screen):
        image = self.image
        rect = image.get_rect()
        rect.topleft = self.position.x % HORIZONTAL_TILES_COUNT * self.__size[0] + LEFT_SPACE, self.position.y % VERTICAL_TILES_COUNT * self.__size[1] + TOP_SPACE
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


class Item(RenderableObject):
    def __init__(self, name='', description='', price=0, pos=Position(0, 0)):
        super().__init__(pos)
        self.__name = name
        self.__description = description
        self.__price = price
    
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


class Room:
    def __init__(self, tileset, name=''):
        self._tiles = tileset
        self._name = name
        self._objects = {
                          'entities': [],
                          'objects':  [],
                          'items':    []
                        }

    def update(self):
        # for obj in self._objects:
        #     obj.update()
        pass

    def render(self, screen):
        for tile in self._tiles:
            tile.render(screen)

        for category in self._objects:
            for obj in self._objects[category]:
                obj.render(screen)

    @staticmethod
    def load(filename):
        try:
            with open(filename) as room:
                room_data = room.readlines()
            
            tileset = []
            for y in range(len(room_data)):
                line = room_data[y].strip('\n')
                for x in range(len(line)):
                    tileset.append(Tile(line[x], Position(x, y)))
            
            return Room(tileset, name=filename)
        except:
            raise SystemError(f'Unable to load room {filename}')
    
    def tileOn(self, pos: Position):
        for tile in self._tiles:
            if tile.position.x == pos.x and tile.position.y == pos.y:
                return tile
        return None


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
        
        return not self.__status


class Hero(Entity):
    MAX_HEALTH = 7

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
        
        if value >= Hero.MAX_HEALTH:
            self._health = Hero.MAX_HEALTH
        else:
            self._health = value

    def move(self, key, room: Room):
        def canStand(step_x=0, step_y=0):
            if step_x != 0:
                return room.tileOn(Position(int(self.position.x+step_x) % HORIZONTAL_TILES_COUNT, int(self.position.y) % VERTICAL_TILES_COUNT)).type != '#' and (self.position.y % 1 == 0 or room.tileOn(Position(int(self.position.x+step_x) % HORIZONTAL_TILES_COUNT, int(self.position.y+1) % VERTICAL_TILES_COUNT)).type != '#')
            elif step_y != 0:
                return room.tileOn(Position(int(self.position.x) % HORIZONTAL_TILES_COUNT, int(self.position.y+step_y) % VERTICAL_TILES_COUNT)).type != '#' and (self.position.x % 1 == 0 or room.tileOn(Position(int(self.position.x+1) % HORIZONTAL_TILES_COUNT, int(self.position.y+step_y) % VERTICAL_TILES_COUNT)).type != '#')

        if key == pygame.K_DOWN:
            if self.position.y % VERTICAL_TILES_COUNT == VERTICAL_TILES_COUNT - 1:
                self.position.y += 1
            elif canStand(step_y=1):
                self.position.y += 1/4
        elif key == pygame.K_UP:
            if self.position.y % VERTICAL_TILES_COUNT == 0:
                self.position.y -= 1
            elif canStand(step_y=-1/4):
                self.position.y -= 1/4
        elif key == pygame.K_LEFT:
            if self.position.x % HORIZONTAL_TILES_COUNT == 0:
                self.position.x -= 1
            elif canStand(step_x=-1/4):
                self.position.x -= 1/4
            self._image = pygame.transform.flip(self.__tmp, True, False)
        elif key == pygame.K_RIGHT:
            if self.position.x % HORIZONTAL_TILES_COUNT == HORIZONTAL_TILES_COUNT - 1:
                self.position.x += 1
            elif canStand(step_x=1):
                self.position.x += 1/4
            self._image = self.__tmp

    def attack(self):
        pass

    def interact(self):
        pass

    def take_item(self, item: Item, slot: int):
        self._inventory['items'][slot] = item

    def remove_item(self, slot: int):
        item = self._inventory['items'][slot]
        item.position.x = round(self.position.x)
        item.position.y = round(self.position.y)
        if item.position.x > HORIZONTAL_TILES_COUNT-1:
            item.position.x -= 1
        if item.position.y > VERTICAL_TILES_COUNT-1:
            item.position.t -= 1
        self._inventory['items'][slot] = None

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
        
        hero._item(item)
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
    def __init__(self, name='', description='', price=0, pos=Position(0, 0), armor=0, slot=''):
        super().__init__(name, description, price, pos)
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
            print("Slot is empty or inventory is full")


class InventoryBar(RenderableObject):
    def __init__(self):
        super().__init__(pos=Position((WIDTH-INVENTORY_BAR_SIZE[0])//2, (HEIGHT-INVENTORY_BAR_SIZE[1])), size=INVENTORY_BAR_SIZE)
        self._image = Assets.inventory_bar

    def render(self, screen, active_slot, inventory):
        image = pygame.transform.scale(self.image, self.size)
        for i in range(1, 7):
            if inventory[i] is not None:
                image.blit(inventory[i].image, pygame.Rect((SLOT_SIZE[1]*(i-1)+6, 6), inventory[i].size))
        if active_slot is not None and isinstance(active_slot, int):
            image.blit(Assets.active_slot, pygame.Rect((SLOT_SIZE[1]*(active_slot-1), 0), SLOT_SIZE))
        rect = image.get_rect()
        rect.topleft = self.position.x, self.position.y
        screen.blit(image, rect)

    @property
    def image(self):
        return self._image


class EquipmentBar(RenderableObject):
    def __init__(self):
        super().__init__(pos=Position(0, (HEIGHT-EQUIPMENT_BAR_SIZE[1])//2), size=EQUIPMENT_BAR_SIZE)
        self._image = Assets.equipment_bar

    def render(self, screen, active_slot, inventory):
        image = pygame.transform.scale(self.image, self.size)
        for i in range(4):
            item = list(inventory.values())[i]
            if item is not None:
                image.blit(item.image, pygame.Rect((6, SLOT_SIZE[1]*(i)+6), item.size))
        if active_slot is not None and isinstance(active_slot, str):
            slot_number = list(inventory.keys()).index(active_slot)
            image.blit(Assets.active_slot, pygame.Rect((0, SLOT_SIZE[1]*slot_number), SLOT_SIZE))
        rect = image.get_rect()
        rect.topleft = self.position.x, self.position.y
        screen.blit(image, rect)

    @property
    def image(self):
        return self._image


class HealthBar(RenderableObject):
    def __init__(self):
        super().__init__(pos=Position(25, 15), size=HEART_SIZE)
        self._image = Assets.fullHeart
    
    def render(self, screen, health):
        image = pygame.transform.scale(self.image, self.size)
        rect = image.get_rect()
        for i in range(int(health)):
            rect.topleft = self.position.x + i*(self.size[0]+4), self.position.y
            screen.blit(image, rect)
        for i in range(int(health), Hero.MAX_HEALTH):
            rect.topleft = self.position.x + i*(self.size[0]+4), self.position.y
            screen.blit(Assets.emptyHeart, rect)
        if health % 1 != 0:
            rect.topleft = self.position.x + int(health)*(self.size[0]+4), self.position.y
            screen.blit(Assets.halfHeart, rect)
    
    @property
    def image(self):
        return self._image


class ArmorBar(RenderableObject):
    def __init__(self):
        super().__init__(pos=Position(25, 42), size=SHIELD_SIZE)
        self._image = Assets.armor
    
    def render(self, screen, armor):
        image = pygame.transform.scale(self.image, self.size)
        rect = image.get_rect()
        for i in range(armor):
            rect.topleft = self.position.x + i*(self.size[0]+4), self.position.y
            screen.blit(image, rect)

    @property
    def image(self):
        return self._image


class Coin(RenderableObject):
    def __init__(self):
        super().__init__(pos=Position(230, 17), size=COIN_SIZE)
        self._image = Assets.coin

    def render(self, screen, money):
        font = pygame.font.SysFont('Bahnschrift', 14)
        text = font.render(f': {money}', True, (255, 255, 255))
        screen.blit(self._image, pygame.Rect((self.position.x, self.position.y), self.size))
        screen.blit(text, (self.position.x+20, self.position.y-1))

    @property
    def image(self):
        return self._image


class Interface:
    def __init__(self):
        self._active_slot = None
        self._inventory_bar = InventoryBar()
        self._equipment_bar = EquipmentBar()
        self._health_bar = HealthBar()
        self._armor_bar = ArmorBar()
        self._coin = Coin()
    
    def render(self, screen, hero: Hero):
        self._inventory_bar.render(screen, self._active_slot, hero._inventory['items'])
        self._equipment_bar.render(screen, self._active_slot, hero._inventory['equipment'])
        self._health_bar.render(screen, hero.health)
        self._armor_bar.render(screen, hero._armor)
        self._coin.render(screen, hero._money)
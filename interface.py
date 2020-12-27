import pygame
from pygame.locals import *
from Singleton import SingletonMeta
from objects import RenderableObject, Hero, Position
from utils import Assets
from constants import *


class InventoryBar(RenderableObject):
    def __init__(self):
        super().__init__(pos=Position((WIDTH-INVENTORY_BAR_SIZE[0])//2, (HEIGHT-INVENTORY_BAR_SIZE[1])), size=INVENTORY_BAR_SIZE)
        self._image = Assets().inventory_bar

    def render(self, screen, active_slot, inventory):
        image = pygame.transform.scale(self.image, self.size)
        for i in range(1, 7):
            if inventory[i] is not None:
                image.blit(inventory[i].image, pygame.Rect((SLOT_SIZE[1]*(i-1)+6, 6), inventory[i].size))
        if active_slot is not None and isinstance(active_slot, int):
            image.blit(Assets().active_slot, pygame.Rect((SLOT_SIZE[1]*(active_slot-1), 0), SLOT_SIZE))
        rect = image.get_rect()
        rect.topleft = self.position.x, self.position.y
        screen.blit(image, rect)

    @property
    def image(self):
        return self._image


class EquipmentBar(RenderableObject):
    def __init__(self):
        super().__init__(pos=Position(0, (HEIGHT-EQUIPMENT_BAR_SIZE[1])//2), size=EQUIPMENT_BAR_SIZE)
        self._image = Assets().equipment_bar

    def render(self, screen, active_slot, inventory):
        image = pygame.transform.scale(self.image, self.size)
        for i in range(4):
            item = list(inventory.values())[i]
            if item is not None:
                image.blit(item.image, pygame.Rect((6, SLOT_SIZE[1]*(i)+6), item.size))
        if active_slot is not None and isinstance(active_slot, str):
            slot_number = list(inventory.keys()).index(active_slot)
            image.blit(Assets().active_slot, pygame.Rect((0, SLOT_SIZE[1]*slot_number), SLOT_SIZE))
        rect = image.get_rect()
        rect.topleft = self.position.x, self.position.y
        screen.blit(image, rect)

    @property
    def image(self):
        return self._image


class HealthBar(RenderableObject):
    def __init__(self):
        super().__init__(pos=Position(25, 15), size=HEART_SIZE)
        self._image = Assets().fullHeart
    
    def render(self, screen, health):
        image = pygame.transform.scale(self.image, self.size)
        rect = image.get_rect()
        for i in range(int(health)):
            rect.topleft = self.position.x + i*(self.size[0]+4), self.position.y
            screen.blit(image, rect)
        for i in range(int(health), Hero.MAX_HEALTH):
            rect.topleft = self.position.x + i*(self.size[0]+4), self.position.y
            screen.blit(Assets().emptyHeart, rect)
        if health % 1 != 0:
            rect.topleft = self.position.x + int(health)*(self.size[0]+4), self.position.y
            screen.blit(Assets().halfHeart, rect)
    
    @property
    def image(self):
        return self._image


class ArmorBar(RenderableObject):
    def __init__(self):
        super().__init__(pos=Position(25, 42), size=SHIELD_SIZE)
        self._image = Assets().armor
    
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
        self._image = Assets().coin

    def render(self, screen, money):
        font = pygame.font.SysFont('Bahnschrift', 14)
        text = font.render(f': {money}', True, WHITE)
        screen.blit(self._image, pygame.Rect((self.position.x, self.position.y), self.size))
        screen.blit(text, (self.position.x+20, self.position.y-1))

    @property
    def image(self):
        return self._image


class UserInterface(metaclass=SingletonMeta):
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
    
    @property
    def active_slot(self):
        return self._active_slot
    
    @active_slot.setter
    def active_slot(self, val):
        self._active_slot = val

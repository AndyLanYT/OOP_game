import pygame
from constants import *
from Singleton import SingletonMeta
from abc import ABC, abstractmethod


class Spritesheet:
    def __init__(self, filename):
        try:
            self.__sheet = pygame.image.load(filename).convert_alpha()
        except:
            raise SystemExit(f'Unable to open file {filename}')
    
    def get_image(self, area):
        rect = pygame.Rect(area)
        image = pygame.Surface(rect.size, pygame.SRCALPHA)
        image.blit(self.__sheet, (0, 0), rect)
        
        return image


class Assets(metaclass=SingletonMeta):
    def __init__(self):
        self.spritesheets = {
            'tmp':       Spritesheet('OOP_game/assets/hero.png'),
            'hero1':     Spritesheet('OOP_game/assets/move.png'),
            'hero2':     Spritesheet('OOP_game/assets/attack.png'),
            'inventory': Spritesheet('OOP_game/assets/inventory1.png'),
            'slot':      Spritesheet('OOP_game/assets/activeslot.png'),
            'health':    Spritesheet('OOP_game/assets/health.png'),
            'armor':     Spritesheet('OOP_game/assets/armor.png'),
            'coin':      Spritesheet('OOP_game/assets/coin.png'),
            'pause':     Spritesheet('OOP_game/assets/pause.png'),
            'shop':      Spritesheet('OOP_game/assets/shop.png'),
            'savename':  Spritesheet('OOP_game/assets/savename.png'),
            'portals':   Spritesheet('OOP_game/assets/portals.png'),
            'pirate1':    Spritesheet('OOP_game/assets/pirate move.png'),
            'pirate2':    Spritesheet('OOP_game/assets/pirate attack.png')
        }

        self.tiles = {
            '#': self.spritesheets['tmp'].get_image(( 0*16,  1*16, 16, 16)),
            '_': self.spritesheets['tmp'].get_image(( 1*16,  0*16, 16, 16)),
            ']': pygame.transform.rotate(self.spritesheets['tmp'].get_image(( 1*16,  0*16, 16, 16)), 90),
            '[': pygame.transform.rotate(self.spritesheets['tmp'].get_image(( 1*16,  0*16, 16, 16)), -90),
            '.': self.spritesheets['tmp'].get_image(( 0*16,  5*16, 16, 16)),
            '*': self.spritesheets['tmp'].get_image(( 0*16, 15*16, 16, 16))
        }

        self.items = {
            'Sword': self.spritesheets['tmp'].get_image((13*16,  3*16, 16, 16))
        }
        
        self.hero_animations = {
                                 'move':   [self.spritesheets['hero1'].get_image((64*(i%FC_HERO_MOVE), 64*(i//FC_HERO_MOVE), 64, 64)) for i in range(FC_HERO_MOVE*2)],
                                 'attack': [self.spritesheets['hero2'].get_image((158*(i%FC_HERO_ATTACK), 0, 158, 112)) for i in range(FC_HERO_ATTACK)]
                                }

        self.entities = {'Pirate': {
                                     'move': [self.spritesheets['pirate1'].get_image((50*i, 0, 50, 32)) for i in range(2)],
                                     'attack': [self.spritesheets['pirate2'].get_image((50*i, 0, 50, 32)) for i in range(7)]
                                    }
                        }
        self.bargainer = self.spritesheets['tmp'].get_image((9*16, 15*16, 16, 16))

        self.inventory_bar = pygame.transform.rotate(self.spritesheets['inventory'].get_image((0, 0, INVENTORY_BAR_SIZE[1], INVENTORY_BAR_SIZE[0])), 90)
        self.equipment_bar = self.spritesheets['inventory'].get_image((0, 0, 45, 180))
        self.active_slot = self.spritesheets['slot'].get_image((0, 0, 45, 45))
        self.fullHeart = self.spritesheets['health'].get_image((0, 0, 23, 21))
        self.halfHeart = self.spritesheets['health'].get_image((23, 0, 23, 21))
        self.emptyHeart = self.spritesheets['health'].get_image((46, 0, 23, 21))
        self.armor = self.spritesheets['armor'].get_image((0, 0, 23, 21))
        self.coin = self.spritesheets['coin'].get_image((0, 0, 16, 16))

        self.pause_menu = self.spritesheets['pause'].get_image((0, 0, PAUSE_MENU_SIZE[0],  PAUSE_MENU_SIZE[1]))
        self.shop_menu = self.spritesheets['shop'].get_image((0, 0, SHOP_MENU_SIZE[0], SHOP_MENU_SIZE[1]))
        self.savename_input = self.spritesheets['savename'].get_image((0, 0, SAVENAME_INPUT[0],  SAVENAME_INPUT[1]))

        self.portals = {
                         'blue': [self.spritesheets['portals'].get_image((40*i, 0, 40, 75)) for i in range(9)],
                         'red':  [pygame.transform.flip(self.spritesheets['portals'].get_image((40*i, 75, 40, 75)), True, False) for i in range(9)]
                        }

import pygame
from abc import ABC, abstractmethod

class Spritesheet:
    def __init__(self, filename):
        try:
            self.__sheet = pygame.image.load(filename).convert()
        except:
            raise SystemExit(f'Unable to open file {filename}')
    
    def get_image(self, area, colorkey=None, pos=(0, 0)):
        rect = pygame.Rect(area)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.__sheet, (0, 0), rect)

        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at(pos)
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        
        return image


class Assets:
    spritesheets = None
    tiles = None
    items = None
    hero = None
    bargainer = None
    inventory_bar = None
    active_slot = None

    @staticmethod
    def load():
        Assets.spritesheets = {
            # 'tiles':    Spritesheet('assets\\blocks.png'),
            # 'items':    Spritesheet('assets\\items.png'),
            # 'entities': Spritesheet('assets\\entities.png'),
            'tmp':       Spritesheet('OOP_game/assets/hero.png'),
            'inventory': Spritesheet('OOP_game/assets/inventory.png'),
            'slot': Spritesheet('OOP_game/assets/activeslot.png')
        }

        Assets.tiles = {
            '#': Assets.spritesheets['tmp'].get_image(( 0*16,  1*16, 16, 16)),
            '|': Assets.spritesheets['tmp'].get_image(( 1*16,  0*16, 16, 16)),
            '.': Assets.spritesheets['tmp'].get_image(( 3*16,  3*16, 16, 16)),
            '*': Assets.spritesheets['tmp'].get_image((10*16,  1*16, 16, 16)),
            ' ': Assets.spritesheets['tmp'].get_image(( 0*16,  15*16, 16, 16))
        }

        Assets.items = {
            # 'Invisibility potion': Assets.spritesheets['items'].get_image((0*16, 0*16, 16, 16)),
            # 'Health potion':       Assets.spritesheets['items'].get_image((0*16, 0*16, 16, 16)),
            # 'Strength potion':     Assets.spritesheets['items'].get_image((0*16, 0*16, 16, 16)),
            'Sword':               Assets.spritesheets['tmp'].get_image((10*16,  1*16, 16, 16), colorkey=-1)
            # 'Helmet':              Assets.spritesheets['items'].get_image((0*16, 0*16, 16, 16)),
            # 'Chestplate':          Assets.spritesheets['items'].get_image((0*16, 0*16, 16, 16)),
            # 'Leggins':             Assets.spritesheets['items'].get_image((0*16, 0*16, 16, 16)),
            # 'Key':                 Assets.spritesheets['items'].get_image((0*16, 0*16, 16, 16)),
            # 'Shuriken':            Assets.spritesheets['items'].get_image((0*16, 0*16, 16, 16))
        }

        Assets.hero = Assets.spritesheets['tmp'].get_image((11*16, 15*16, 16, 16), colorkey=-1)
        Assets.bargainer = Assets.spritesheets['tmp'].get_image((9*16, 15*16, 16, 16), colorkey=-1)
        
        Assets.inventory_bar = Assets.spritesheets['inventory'].get_image((0, 0, 45, 270))
        Assets.active_slot = Assets.spritesheets['slot'].get_image((0, 0, 45, 45), colorkey=-1, pos=(5, 5))


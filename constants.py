from pygame.locals import *


WIDTH = 864
HEIGHT = 544

PLAYABLE_WIDTH = 768 # 24 tiles
PLAYABLE_HEIGHT = 416 # 13 tiles
LEFT_SPACE = (WIDTH - PLAYABLE_WIDTH) / 2
TOP_SPACE = HEIGHT-PLAYABLE_HEIGHT-50

TILE_SIZE = (32, 32)
HERO_SIZE = (64, 64)
HERO_SIZE_IN_TILES = (HERO_SIZE[0]/TILE_SIZE[0], HERO_SIZE[1]/TILE_SIZE[1])
INVENTORY_BAR_SIZE = (270, 45)
EQUIPMENT_BAR_SIZE = (45, 180)
SLOT_SIZE = (45, 45)
HEART_SIZE = (23, 21)
SHIELD_SIZE = (23, 21)
COIN_SIZE = (16, 16)
PAUSE_MENU_SIZE = (200, 125)
SHOP_MENU_SIZE = (235, 215)
SAVENAME_INPUT = (800, 50)

FC_HERO_MOVE = 8
FC_HERO_ATTACK = 17

HORIZONTAL_TILES_COUNT = PLAYABLE_WIDTH / TILE_SIZE[0]
VERTICAL_TILES_COUNT = PLAYABLE_HEIGHT / TILE_SIZE[1]

RIGHT = 0
LEFT = 1

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

KEYBINDS = {
        'movement': {
                      'down':  K_DOWN,
                      'up':    K_UP,
                      'left':  K_LEFT,
                      'right': K_RIGHT
                    },

        'attack':   K_f,
        'interact': K_e,

        'items': {
                   'use':    K_r,
                   'take':   K_q,
                   'remove': K_g
                 },
        
        'inventory': {
                       1:       K_1,
                       2:       K_2,
                       3:       K_3,
                       4:       K_4,
                       5:       K_5,
                       6:       K_6,
                       'head':  K_7,
                       'chest': K_8,
                       'legs':  K_9,
                       'arm':   K_0
                     }
    }

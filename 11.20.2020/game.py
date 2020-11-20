import pygame
from pygame.locals import *
import objects
from utils import Spritesheet, Assets
from constants import *

class Game:
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

    def __init__(self, width, height, fps=60):
        self.__fps = fps

        pygame.init()
        self.__screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Andy's Game")
        self.__camera_pos = (0, 0)
        self.__clock = pygame.time.Clock()

        Assets.load()

        self.__levels = { 'level1': {
                                      (0, 0): objects.Room.load('OOP_game/levels/test.txt'),
                                      (0, 1): objects.Room.load('OOP_game/levels/temp.txt'),
                                      (1, 0): objects.Room.load('OOP_game/levels/tree.txt'),
                                      (1, 1): objects.Room.load('OOP_game/levels/teen.txt')
                                    },

                          'level2': {
                                      (0, 0): None,
                                      (0, 1): None,
                                      (1, 0): None,
                                      (1, 1): None
                                    },

                          'level3': {
                                      (0, 0): None,
                                      (0, 1): None,
                                      (1, 0): None,
                                      (1, 1): None
                                    }
                           # ... and so on
                        }
        self.__level = 'level1'
        self.__room = self.__levels[self.__level][self.__camera_pos]

        self.__hero = objects.Hero(pos=objects.Position(7, 5))
        self.__room._objects['entities'].append(self.__hero)

        self.__bargainer = objects.Bargainer(name='Cleven', pos=objects.Position(6, 7))
        self.__room._objects['entities'].append(self.__bargainer)

        self.__room._objects['items'].append(objects.Armor('Sword', pos=objects.Position(16, 8), armor=3, slot='arm'))

        self.__interface = objects.Interface()

    def __process_input(self, key, active_slot):
        if key in Game.KEYBINDS['movement'].values():
            self.__hero.move(key, self.__room)
        elif key == Game.KEYBINDS['attack']:
            self.__hero.attack()
        elif key == Game.KEYBINDS['interact']:
            self.__hero.interact()
        elif key == Game.KEYBINDS['items']['use'] and isinstance(active_slot, int):
            if isinstance(self.__hero._inventory['items'][active_slot], objects.UsableItem):
                self.__hero._inventory['items'][active_slot].use(active_slot)
            elif isinstance(self.__hero._inventory['items'][active_slot], objects.EquipableItem):
                self.__hero._inventory['items'][active_slot].equip(self.__hero, active_slot)
        elif key == Game.KEYBINDS['items']['take']:
            for item in self.__room._objects['items']:
                if self.__hero.emptySlot() and (self.__hero.position.x - item.position.x) ** 2 + (self.__hero.position.y - item.position.y) ** 2 <= 1:
                    self.__room._objects['items'].remove(item)
                    self.__hero.take_item(item, self.__hero.emptySlot())
                    break
        elif key == Game.KEYBINDS['items']['remove']:
            if isinstance(active_slot, int) and self.__hero._inventory['items'][active_slot] is not None:
                self.__room._objects['items'].append(self.__hero._inventory['items'][active_slot])
                self.__hero.remove_item(active_slot)
            elif isinstance(active_slot, str) and self.__hero._inventory['equipment'][active_slot] is not None:
                self.__hero._inventory['equipment'][active_slot].remove(self.__hero, active_slot)
        elif key == pygame.K_i:
            self.__hero._money += 1
        elif key == pygame.K_o:
            self.__hero.health -= 0.5

    def __update(self):
        self.__camera_pos = self.__hero.position.x // HORIZONTAL_TILES_COUNT, self.__hero.position.y // VERTICAL_TILES_COUNT
        try:
            self.__room = self.__levels[self.__level][self.__camera_pos]
        except:
            raise SystemExit("Inaccessible territory!")
        self.__room.update()


# Andy Lancelot, listen to me!! It is you in the past (11.20.2020. 02:20)...
# Check void tiles!! It can help you to create better camera.
#       Thank You for Your attention <3


    def __render(self):
        self.__screen.fill((39, 39, 39))
        self.__room.render(self.__screen)
        self.__hero.render(self.__screen)
        self.__interface.render(self.__screen, self.__hero)
        pygame.display.flip()

    def run(self):
        running = True
        key = 0

        while running:
            self.__clock.tick(self.__fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    key = event.key
                    if key in Game.KEYBINDS['inventory'].values():
                        self.__interface._active_slot = list(Game.KEYBINDS['inventory'].keys())[list(Game.KEYBINDS['inventory'].values()).index(key)]
                    elif key in Game.KEYBINDS['movement'].values():
                        self.__interface._active_slot = None
            
            if pygame.key.get_pressed()[key]:
                self.__process_input(key, self.__interface._active_slot)
            self.__update()
            self.__render()

        pygame.quit()

Game(WIDTH, HEIGHT).run()

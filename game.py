import pygame
from pygame.locals import *
import objects
from utils import Spritesheet, Assets

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
        self.__camera_pos = (0, 0)
        self.__clock = pygame.time.Clock()
        self.__objects = []
        self.__items = []

        Assets.load()

        self.__levels = {
                          (0, 0): objects.Level.load('OOP_game/levels/test.txt'),
                          (0, 1): objects.Level.load('OOP_game/levels/temp.txt'),
                          (1, 0): objects.Level.load('OOP_game/levels/tree.txt'),
                          (1, 1): objects.Level.load('OOP_game/levels/teen.txt')
                        }
        self.__level = self.__levels[self.__camera_pos]

        # phrases = []
        # try:
        #     with open('phrases\\hero.txt') as phrases_list:
        #         phrases = phrases_list.readlines()
        #     for i in range(len(phrases)):
        #         phrases[i] = phrases[i].strip('\n')
        # except:
        #     raise SystemExit("Unable to open file 'phrases\\hero.txt'")
        self.__hero = objects.Hero(pos=objects.Position(7, 5))
        self.__objects.append(self.__hero)

        # try:
        #     with open('phrases\\bargainer.txt') as phrases_list:
        #         phrases = phrases_list.readlines()
        #     for i in range(len(phrases)):
        #         phrases[i] = phrases[i].strip('\n')
        # except:
        #     raise SystemExit("Unable to open file 'phrases\\bargainer.txt'")
        self.__bargainer = objects.Bargainer(name='Cleven', pos=objects.Position(6, 7))
        self.__objects.append(self.__bargainer)

        self.__items.append(objects.Item('Sword', status=0, pos=objects.Position(16, 8)))

        self.__inv_bar = objects.InventoryBar()


    def __process_input(self, key, active_slot):
        if key in Game.KEYBINDS['movement'].values():
            self.__hero.move(key, self.__level)
        elif key == Game.KEYBINDS['attack']:
            self.__hero.attack()
        elif key == Game.KEYBINDS['interact']:
            self.__hero.interact()
        elif key == Game.KEYBINDS['items']['use'] and active_slot in self.__hero._inventory['items']:
            if isinstance(self.__hero._inventory['items'][active_slot], objects.UsableItem):
                self.__hero._inventory['items'][active_slot].use(active_slot)
            elif isinstance(self.__hero._inventory['items'][active_slot], objects.EquipableItem):
                self.__hero._inventory['items'][active_slot].equip(active_slot)
        elif key == Game.KEYBINDS['items']['take']:
            for item in self.__items:
                if (self.__hero.position.x - item.position.x) ** 2 + (self.__hero.position.y - item.position.y) ** 2 <= 1 and item.status == 0:
                    self.__hero.take_item(item)
                    break
        elif key == Game.KEYBINDS['items']['remove']:
            if active_slot in self.__hero._inventory['items']:
                self.__hero.remove_item(active_slot)
            elif active_slot in self.__hero._inventory['equipment']:
                self.__hero._inventory['equipment'][active_slot].remove(active_slot)
        elif key == pygame.K_i:
            # print(self.__hero._inventory)
            # print(self.__inv_bar._active_slot)
            pass

    def __update(self):
        # for obj in self.__objects:
        #     obj.update()
        self.__camera_pos = self.__hero.position.x // (800/32), self.__hero.position.y // (608/32)
        try:
            self.__level = self.__levels[self.__camera_pos]
        except:
            raise SystemExit("Inaccessible territory!")
        self.__level.update()
        self.__inv_bar._inventory = self.__hero._inventory['items']

    def __render(self):
        self.__screen.fill((0, 0, 0))
        self.__level.render(self.__screen)
        for item in self.__items:
            if (item.position.x // (800/32) == self.__camera_pos[0]) and (item.position.y // (608//32) == self.__camera_pos[1]) and (item.status == 0):
                item.render(self.__screen)

        for obj in self.__objects:
            if obj.position.x // (800/32) == self.__camera_pos[0] and obj.position.y // (608/32) == self.__camera_pos[1]:
                obj.render(self.__screen)
        
        self.__inv_bar.render(self.__screen)

        pygame.display.flip()

    def run(self):
        running = True
        key = 0
        self.__inv_bar._active_slot = None

        while running:
            self.__clock.tick(self.__fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    key = event.key
                    if key in Game.KEYBINDS['inventory'].values():
                        self.__inv_bar._active_slot = list(Game.KEYBINDS['inventory'].keys())[list(Game.KEYBINDS['inventory'].values()).index(key)]
                    elif key in Game.KEYBINDS['movement'].values():
                        self.__inv_bar._active_slot = None
            
            if pygame.key.get_pressed()[key]:
                self.__process_input(key, self.__inv_bar._active_slot)
            self.__update()
            self.__render()

        pygame.quit()

Game(800, 608).run()

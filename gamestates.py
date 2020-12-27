import pygame
import pickle
from pygame.locals import *
from objects import *
from constants import *
from interface import UserInterface
from Memento import *
from sounds import Sounds
from utils import *


class GameState:
    def __init__(self, fps=60):
        Caretaker()
        pygame.mixer.music.load('OOP_game/sounds/background2.mp3')
        pygame.mixer.music.set_volume(0.2)
        self.__fps = fps
        self.__camera_pos = (1, 1)
        self.__levels = { 'level1': {
                                      (0, 0): Room.create('OOP_game/levels/test.txt'),
                                      (0, 1): Room.create('OOP_game/levels/temp.txt'),
                                      (1, 0): Room.create('OOP_game/levels/tree.txt'),
                                      (1, 1): Room.create('OOP_game/levels/teen.txt')
                                    },

                          'level2': {
                                      (0, 0): Room.create('OOP_game/levels/omga.txt'),
                                      (0, 1): None,
                                      (1, 0): Room.create('OOP_game/levels/true.txt'),
                                      (1, 1): None
                                    },

                          'level3': {
                                      (0, 0): Room.create('OOP_game/levels/teen.txt'),
                                      (0, 1): None,
                                      (1, 0): None,
                                      (1, 1): None
                                    }
                           # ... and so on
                        }
        self.__level = 'level1'
        self.__room = self.__levels[self.__level][self.__camera_pos]
        self.__bargainer = Bargainer(name='Cleven', pos=Position(30, 20))
        self.__bargainer._items[4] = Armor('Sword', 239, pos=Position(16, 8), armor=3, slot='arm')
        self.__room._objects['entities'].append(self.__bargainer)
        self.__levels['level1'][(1, 0)]._objects['entities'].append(Pirate(pos=Position(37, 7)))
        self.__room._objects['items'].append(Armor('Sword', pos=Position(16+HORIZONTAL_TILES_COUNT, 8+VERTICAL_TILES_COUNT), armor=3, slot='arm'))
        self.__levels['level1'][(0, 0)]._objects['portals'].append(Portal(pos=Position(20, 3), color='blue', destination={'position': Position(25, 3), 'level': 'level1'}))
        self.__levels['level1'][(0, 0)]._objects['portals'].append(Portal(pos=Position(15, 3), color='red', destination={'position': Position(5, 7), 'level': 'level2'}))
        self.__hero = Hero(pos=Position(39, 17))
        self.__interface = UserInterface()

    def process_input(self, key, active_slot, pause_menu, shop_menu):
        self.__hero._image = Assets().hero_animations['move'][FC_HERO_MOVE*int(bool(self.__hero._inventory['equipment']['arm']))]
        if key in KEYBINDS['inventory'].values():
            self.interface.active_slot = list(KEYBINDS['inventory'].keys())[list(KEYBINDS['inventory'].values()).index(key)]
        elif key in KEYBINDS['movement'].values():
            self.__hero.move(key, self.__room)
            self.interface.active_slot = None
        elif key == KEYBINDS['attack']:
            self.__hero.attack(self.__room._objects['entities'])
        elif key == KEYBINDS['interact']:
            if (self.__hero.position.x-self.__bargainer.position.x)**2 + (self.__hero.position.y-self.__bargainer.position.y)**2 <= 2**2:
                shop_menu.is_active = True
        elif key == KEYBINDS['items']['use'] and isinstance(active_slot, int):
            if isinstance(self.__hero._inventory['items'][active_slot], UsableItem):
                self.__hero._inventory['items'][active_slot].use(active_slot)
            elif isinstance(self.__hero._inventory['items'][active_slot], EquipableItem):
                self.__hero._inventory['items'][active_slot].equip(self.__hero, active_slot)
        elif key == KEYBINDS['items']['take']:
            for item in self.__room._objects['items']:
                if self.__hero.empty_slot() and (item.position.x-43/TILE_SIZE[0] <= self.__hero.position.x <= item.position.x and item.position.y-50/TILE_SIZE[1] <= self.__hero.position.y <= item.position.y+7/TILE_SIZE[1]):
                    self.__room._objects['items'].remove(item)
                    self.__hero.take_item(item, self.__hero.empty_slot())
                    break
        elif key == KEYBINDS['items']['remove']:
            if isinstance(active_slot, int) and self.__hero._inventory['items'][active_slot] is not None:
                self.__room._objects['items'].append(self.__hero._inventory['items'][active_slot])
                self.__hero.remove_item(active_slot)
            elif isinstance(active_slot, str) and self.__hero._inventory['equipment'][active_slot] is not None:
                self.__hero._inventory['equipment'][active_slot].remove(self.__hero, active_slot)
        elif key == K_ESCAPE:
            pause_menu.is_active = True
            pygame.mixer.music.pause()
        elif key == K_i:
            self.__hero._money += 1

    def update(self):
        self.__kill_entities(self.__room._objects['entities'])
        for portal in self.__room._objects['portals']:
            if portal.is_active and (portal.position.x-31/TILE_SIZE[0] <= self.__hero.position.x <= portal.position.x+4/TILE_SIZE[0]) and (portal.position.y-27/TILE_SIZE[1] <= self.__hero.position.y <= portal.position.y+20/TILE_SIZE[1]):
                self.__hero._position = deepcopy(portal.destination['position'])
                self.__level = deepcopy(portal.destination['level'])
                Sounds().teleportation.play()
        
        self.__camera_pos = self.__hero.position.x // HORIZONTAL_TILES_COUNT, self.__hero.position.y // VERTICAL_TILES_COUNT
        try:
            self.__room = self.__levels[self.__level][self.__camera_pos]
        except:
            raise SystemExit("Inaccessible territory!")
        self.__room.update(self.__hero)
        self.__hero.update()
    
    def render(self, screen):
        screen.fill((35, 35, 35))
        self.__room.render(screen)
        self.__interface.render(screen, self.__hero)
        self.__hero.render(screen)
        pygame.display.flip()
    
    def save(self, savename):
        with open('OOP_game/saves/'+savename, 'wb') as save:
            data = {}

            data.update({'hero':  self.__hero.save()})

            levels = {}
            for levelname in self.__levels:
                leveldata = {}
                for roomidx in self.__levels[levelname]:
                    if self.__levels[levelname][roomidx] is not None:
                        leveldata.update({roomidx: self.__levels[levelname][roomidx].save()})
                    else:
                        leveldata.update({roomidx: None})
                levels.update({levelname: leveldata})

            data.update({'map': levels})
            data.update({'level': self.__level})
            data.update({'room': self.__room.save()})

            pickle.dump(data, save)
            Caretaker().add_save(Memento(savename, data))
    
    def load(self, data: dict):
        levels = data['map']
        for levelname in levels:
            for roomidx in levels[levelname]:
                if levels[levelname][roomidx] is not None:
                    levels[levelname][roomidx] = Room.load(levels[levelname][roomidx])
        self.__levels = levels
        self.__level = data['level']
        self.__room = Room.load(data['room'])
        self.__hero = Hero.load(data['hero'])
    
    def __kill_entities(self, entity_lst, i=0):
        if i == len(entity_lst):
            return
        
        if entity_lst[i].isDead():
            entity_lst.remove(entity_lst[i])
            Sounds().death.play()
            self.__kill_entities(entity_lst, i)
        else:
            self.__kill_entities(entity_lst, i+1)
    
    @property
    def fps(self):
        return self.__fps

    @property
    def hero(self):
        return self.__hero
    
    @property
    def bargainer(self):
        return self.__bargainer

    @property
    def interface(self):
        return self.__interface


class Menu(RenderableObject):
    def __init__(self):
        super().__init__(size=(WIDTH, HEIGHT))
        self.is_active = True
        self.__choice = 0
        self.section = 'Main menu'
        self.__savename = ''
        self._image = pygame.transform.scale(Assets().pause_menu, self.size)
    
    def process_input(self, key, state: GameState):
        if self.section == 'Main menu':
            if key == K_DOWN:
                self.__choice += 1
                Sounds().menu_selection.play()
                if self.__choice > 4:
                    self.__choice = 0
            elif key == K_UP:
                self.__choice -= 1
                Sounds().menu_selection.play()
                if self.__choice < 0:
                    self.__choice = 4
            elif key == K_RETURN:
                self.__select(state)
        elif self.section == 'Load save':
            if key == K_DOWN:
                self.__choice += 1
                Sounds().menu_selection.play()
                if self.__choice > len(Caretaker().saves)-1:
                    self.__choice = 0
            elif key == K_UP:
                self.__choice -= 1
                Sounds().menu_selection.play()
                if self.__choice < 0:
                    self.__choice = len(Caretaker().saves)-1
            elif key == K_RETURN:
                state.load(Caretaker().get_save(self.__savename))
                self.__choice = 0
                self.section = 'Main menu'
                self.is_active = False
                pygame.mixer.music.play(loops=-1, start=2)
            elif key == K_ESCAPE:
                self.__choice = 0
                self.section = 'Main menu'
        elif self.section == 'Hotkeys':
            pass
        elif self.section == 'Authors':
            pass
    
    def update(self):
        pass
    
    def render(self, screen):
        font = pygame.font.SysFont('Bahnschrift', 24)
        sections = ['New game', 'Load save', 'Hotkeys', 'Authors', 'Exit']
        pointer = font.render('<', False, WHITE)
        
        screen.fill(BLACK)
        if self.section == 'Main menu':
            for i in range(len(sections)):
                text = font.render(sections[i], False, WHITE)
                screen.blit(text, pygame.Rect((15, HEIGHT//2-100+30*i), (text.get_width(), text.get_height())))
                if i == self.__choice:
                    screen.blit(pointer, pygame.Rect((40+text.get_width(), HEIGHT//2-100+30*i), (pointer.get_width(), pointer.get_height())))
        elif self.section == 'Load save':
            for i in range(len(Caretaker().saves)):
                text = font.render(list(Caretaker().saves.keys())[i], False, WHITE)
                screen.blit(text, pygame.Rect((25, 15+30*i), (text.get_width(), text.get_height())))
                if i == self.__choice:
                    self.__savename = list(Caretaker().saves.keys())[i]
                    screen.blit(pointer, pygame.Rect((50+text.get_width(), 15+30*i), (pointer.get_width(), pointer.get_height())))
        elif self.section == 'Hotkeys':
            pass
        elif self.section == 'Authors':
            pass
        
        pygame.display.flip()
        
    def __select(self, state: GameState):
        if self.__choice == 0:
            state.__init__()
            pygame.mixer.music.play(loops=-1, start=2)
            self.is_active = False
        elif self.__choice == 1:
            self.section = 'Load save'
        elif self.__choice == 2:
            self.section = 'Hotkeys'
        elif self.__choice == 3:
            self.section = 'Authors'
        elif self.__choice == 4:
            exit()
        self.__choice = 0
        Sounds().select.play()
    
    @property
    def image(self):
        return self._image


class PauseMenu(RenderableObject):
    def __init__(self):
        super().__init__(pos=Position(WIDTH//2-PAUSE_MENU_SIZE[0]//2, HEIGHT//2-PAUSE_MENU_SIZE[1]//2), size=PAUSE_MENU_SIZE)
        self.is_active = False
        self.__choice = 0
        self.section = 'pause'
        self.__savename = ''
        self._image = Assets().pause_menu
    
    def process_input(self, key, symbol, state: GameState, menu: Menu):
        if self.section == 'pause':
            if key == K_DOWN:
                self.__choice += 1
                Sounds().menu_selection.play()
                if self.__choice > 2:
                    self.__choice = 0
            elif key == K_UP:
                self.__choice -= 1
                Sounds().menu_selection.play()
                if self.__choice < 0:
                    self.__choice = 2
            elif key == K_RETURN:
                self.__select(menu)
            elif key == K_ESCAPE:
                self.__choice = 0
                self.is_active = False
                pygame.mixer.music.unpause()
        elif self.section == 'save':
            if key == K_RETURN:
                state.save(self.__savename)
                self.__savename = ''
                self.section = 'pause'
                self.is_active = False
                Sounds().menu_selection.play()
                pygame.mixer.music.unpause()
            elif key == K_BACKSPACE:
                self.__savename = self.__savename[:-1]
            else:
                self.__savename += symbol

    def update(self):
        pass

    def render(self, screen):
        font = pygame.font.SysFont('Bahnschrift', 24)
        if self.section == 'pause':
            sections = ['Continue', 'Save', 'Main menu']
            pointer = font.render('<', False, WHITE)

            screen.blit(self.image, pygame.Rect((self.position.x, self.position.y), self.size))        
            for i in range(len(sections)):
                text = font.render(sections[i], False, WHITE)
                screen.blit(text, pygame.Rect((self.position.x+(self.size[0]-text.get_width())//2, self.position.y+15+30*i), (text.get_width(), text.get_height())))
                if i == self.__choice:
                    screen.blit(pointer, pygame.Rect((self.position.x+self.size[0]//2+text.get_width()//2+15, self.position.y+15+30*i), (pointer.get_width(), pointer.get_height())))
        elif self.section == 'save':
            text = font.render('Save: '+self.__savename, False, WHITE)

            screen.blit(Assets().savename_input, pygame.Rect(((WIDTH-SAVENAME_INPUT[0])//2, HEIGHT-SAVENAME_INPUT[1]-10), SAVENAME_INPUT))
            screen.blit(text, pygame.Rect(((WIDTH-text.get_width())//2, HEIGHT-SAVENAME_INPUT[1]), (text.get_width(), text.get_height())))
        
        pygame.display.flip()

    def __select(self, menu: Menu):
        if self.__choice == 0:
            self.is_active = False
            pygame.mixer.music.unpause()
        elif self.__choice == 1:
            self.section = 'save'
        elif self.__choice == 2:
            menu.is_active = True
            self.is_active = False
        self.__choice = 0
        Sounds().select.play()
    
    @property
    def image(self):
        return self._image


class ShopMenu(RenderableObject):
    def __init__(self):
        super().__init__(pos=Position(WIDTH//2-SHOP_MENU_SIZE[0]//2, HEIGHT//2-SHOP_MENU_SIZE[1]//2), size=SHOP_MENU_SIZE)
        self.is_active = False
        self.__slot = 1
        self._image = Assets().shop_menu
    
    def process_input(self, key, state: GameState):
        if key == K_DOWN:
            self.__slot += 3
            if self.__slot > 9:
                self.__slot -= 9
        elif key == K_UP:
            self.__slot -= 3
            if self.__slot < 1:
                self.__slot += 9
        elif key == K_LEFT:
            self.__slot -= 1
            if self.__slot < 1:
                self.__slot = 9
        elif key == K_RIGHT:
            self.__slot += 1
            if self.__slot > 9:
                self.__slot = 1
        elif key == K_RETURN:
            state.bargainer.sell(state.hero, self.__slot)
        elif key == K_ESCAPE:
            self.is_active = False

    def update(self):
        pass

    def render(self, screen, inventory):
        image = pygame.transform.scale(self.image, self.size)
        for i in inventory:
            if inventory[i] is not None:
                image.blit(inventory[i].image, pygame.Rect(((SLOT_SIZE[0]+27)*((i-1)%3)+23+6, (SLOT_SIZE[1]+18)*((i-1)//3)+22+6), inventory[i].size))
        image.blit(Assets().active_slot, pygame.Rect(((SLOT_SIZE[0]+27)*((self.__slot-1)%3)+23, (SLOT_SIZE[1]+18)*((self.__slot-1)//3)+22), SLOT_SIZE))
        rect = image.get_rect()
        rect.topleft = self.position.x, self.position.y
        screen.blit(image, rect)

        pygame.display.flip()

    @property
    def image(self):
        return self._image



import pygame
from pygame.locals import *
from constants import WIDTH, HEIGHT, KEYBINDS
from gamestates import GameState, Menu, PauseMenu, ShopMenu


class Game:
    def __init__(self, width=WIDTH, height=HEIGHT):
        pygame.mixer.init()
        pygame.init()
        self.__screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Andy's Game")

        self.__clock = pygame.time.Clock()
        self.__state = GameState()
        self.__menu = Menu()
        self.__pause_menu = PauseMenu()
        self.__shop_menu = ShopMenu()

    def run(self):
        running = True
        key = 0
        symbol = ''

        while running:
            symbol = ''
            self.__clock.tick(self.__state.fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    key = event.key
                    symbol = event.unicode
            
            if self.__menu.is_active:
                self.__menu.process_input(key, self.__state)
                self.__menu.update()
                self.__menu.render(self.__screen)
                key = 0
            elif self.__pause_menu.is_active:
                self.__pause_menu.process_input(key, symbol, self.__state, self.__menu)
                self.__pause_menu.update()
                self.__pause_menu.render(self.__screen)
                key = 0
            elif self.__shop_menu.is_active:
                self.__shop_menu.process_input(key, self.__state)
                self.__shop_menu.update()
                self.__shop_menu.render(self.__screen, self.__state.bargainer._items)
                key = 0
            else:
                if not pygame.key.get_pressed()[key]:
                    key = 0
                self.__state.process_input(key, self.__state.interface.active_slot, self.__pause_menu, self.__shop_menu)
                self.__state.update()
                self.__state.render(self.__screen)
                if key == KEYBINDS['attack']:
                    key = 0
                if self.__pause_menu.is_active:
                    key = 0
                if key == K_o:
                    key = 0

        pygame.quit()
    
    @property
    def state(self):
        return self.__state


Game().run()

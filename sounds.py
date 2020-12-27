import pygame
from Singleton import SingletonMeta


class Sounds(metaclass=SingletonMeta):
    def __init__(self):
        self.menu_selection = pygame.mixer.Sound('OOP_game/sounds/menu selection.mp3')
        self.menu_selection.set_volume(0.85)
        self.select = pygame.mixer.Sound('OOP_game/sounds/select2.mp3')
        self.select.set_volume(0.35)
        # self.footstep = pygame.mixer.Sound('OOP_game/sounds/footstep.wav')
        self.sword_swing = pygame.mixer.Sound('OOP_game/sounds/sword.mp3')
        self.sword_swing.set_volume(0.40)
        self.teleportation = pygame.mixer.Sound('OOP_game/sounds/teleport1.mp3')
        self.teleportation.set_volume(0.20)
        self.hit = pygame.mixer.Sound('OOP_game/sounds/hit.wav')
        self.death = pygame.mixer.Sound('OOP_game/sounds/death.mp3')
        self.death.set_volume(0.49)

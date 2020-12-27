import pickle
import os
from copy import deepcopy
from Singleton import SingletonMeta


class Memento:
    def __init__(self, name, data):
        self.savename = name
        self.data = data


class Caretaker(metaclass=SingletonMeta):
    def __init__(self):
        files = list(os.walk('OOP_game/saves'))[0][2]
        
        self.saves = {}
        for filename in files:
            with open('OOP_game/saves/'+filename, 'rb') as save:
                self.saves.update({filename: pickle.load(save)})

    def add_save(self, save: Memento):
        self.saves.update({save.savename: save.data})

    def get_save(self, filename):
        return deepcopy(self.saves[filename])

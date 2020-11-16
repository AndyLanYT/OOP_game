import pygame
from utils import *


pygame.init()

class A:
    def __init__(self, a, b):
        self.a = a
        self.b = b


# a = [A(1, 2), A(0, 0)]
# print(A(1, 2) in a)

# obj = a(3, 2)
# b = a(5, 2)
# c = a(5, 2)

# print(b == c, b == obj)


def num(a):
    return a


# a = {
#     (0, 0): '1',
#     (1.0, 0.0): '2',
#     # (1, 0): '3',
#     # (1.0, 0.0): '4',
#     # (1, 0): '5'
# }

# print(1.0 == 1)

# E = [  -2, -1.5,  -1, -0.5,    0,   1,    2, 2.5]
# p = [0.15, 0.15, 0.3,  0.1, 0.05, 0.1, 0.05, 0.1]

# M = 0
# D = 0
# for i in range(len(E)):
#     M += E[i] * p[i]
#     D += E[i]**2 * p[i]

# D -= M**2

# print(M)
# print(D)


if 6 > 5: 
    print('1')
else:
    print('2')

# importações necessárias
import pygame
from pygame.locals import *
import sys
import random
import os

pygame.init()

vec = pygame.math.Vector2  # 2 para cálculos em 2 dimensões

# tamanho da janela
WIDTH = 800
HEIGHT = 600

# configura o framerate
FPS = 60
FramePerSec = pygame.time.Clock()

font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyBall")

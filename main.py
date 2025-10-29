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

# Definição das classes dos principais objetos

# -------------------- PLAYER --------------------
class Jogador(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((40, 80))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=pos)
        self.chutando = False

    def chutar(self, forca, destino):
        self.chutando = True
        # O destino será uma tupla (x, y) no gol
        # A força será traduzida para velocidade da bola
        return Bola(self.rect.center, destino, forca)

    def update(self):
        pass

# -------------------- BOLA --------------------
class Bola(pygame.sprite.Sprite):
    def __init__(self, pos_inicial, destino, forca):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), (10, 10), 10)
        self.rect = self.image.get_rect(center=pos_inicial)

        # Vetores de movimento
        self.pos = vec(pos_inicial)
        self.destino = vec(destino)
        direcao = (self.destino - self.pos).normalize()
        self.velocidade = direcao * forca

    def update(self):
        self.pos += self.velocidade
        self.rect.center = self.pos

        # Verifica se passou do gol (simples, depois refinamos)
        if self.pos.y < 50:
            self.kill()

# -------------------- GOLEIRO --------------------
class Goleiro(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((60, 80))
        self.image.fill((255, 165, 0))
        self.rect = self.image.get_rect(center=pos)
        self.direcao = 1
        self.vel = 3

    def mover(self):
        # Movimento lateral simples de vai-e-volta
        self.rect.x += self.vel * self.direcao
        if self.rect.left < 250 or self.rect.right > 550:
            self.direcao *= -1

    def update(self):
        self.mover()

# -------------------- GOL --------------------
class Gol(pygame.sprite.Sprite):
    def __init__(self, pos, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=pos)

# -------------------- SLIDER --------------------
class Slider:
    def __init__(self, x, y, width, height, speed=200, color=(0, 0, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.indicador_pos = x
        self.speed = speed
        self.direction = 1
        self.color = color
        self.active = True
        self.value = None  # valor travado (0.0 a 1.0)

    def update(self, dt):
        # Atualiza o movimento do indicador se o slider ainda estiver ativo.
        if not self.active:
            return
        self.indicador_pos += self.speed * self.direction * dt
        if self.indicador_pos <= self.rect.left or self.indicador_pos >= self.rect.right:
            self.direction *= -1  # inverte o movimento nas bordas

    def lock_value(self):
        # Trava o valor atual do slider
        rel_pos = (self.indicador_pos - self.rect.left) / self.rect.width
        self.value = max(0.0, min(1.0, rel_pos))
        self.active = False

    def draw(self, surface):
        # Desenha a barra e o indicador
        pygame.draw.rect(surface, (180, 180, 180), self.rect, border_radius=5)
        pygame.draw.rect(surface, self.color, self.rect, 3, border_radius=5)
        indicador_x = int(self.indicador_pos)
        indicador_y = self.rect.centery
        pygame.draw.circle(surface, (255, 255, 255), (indicador_x, indicador_y), self.rect.height // 2)

        # Mostra valor se estiver travado
        if self.value is not None:
            val_text = small_font.render(f"{self.value:.2f}", True, (255, 255, 255))
            surface.blit(val_text, (self.rect.x + self.rect.width + 15, self.rect.y))

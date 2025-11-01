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

# Classe do JGADOR 
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

# Classe da BOLA 
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

# Classe do GOLEIRO 
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

# Classe do GOL 
class Gol(pygame.sprite.Sprite):
    def __init__(self, pos, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=pos)

# Classe de um SLIDER 
class Slider:
    def __init__(self, x, y, width, height,  speed_range=(150, 300), color=(0, 0, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.indicador_pos = random.uniform(self.rect.left, self.rect.right) # Coloca o pontinho num lugar aleatorio
        self.speed = random.uniform(*speed_range) # Randomiza uma velocidade qualquer para o pontinho 
        self.direction = self.direction = random.choice([-1, 1]) # 1 -> Direita e -1-> Esquerda
        self.color = color
        self.active = True
        self.value = None  # valor travado de 0 a 1

    def update(self, dt):
        if not self.active:
            return

        # Atualiza a posição
        self.indicador_pos += self.speed * self.direction * dt

        # Verifica ultrapassagem e reflete suavemente
        if self.indicador_pos < self.rect.left:
            excesso = self.rect.left - self.indicador_pos
            self.indicador_pos = self.rect.left + excesso
            self.direction *= -1
        elif self.indicador_pos > self.rect.right:
            excesso = self.indicador_pos - self.rect.right
            self.indicador_pos = self.rect.right - excesso
            self.direction *= -1

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

# sliders de teste
slider_x = Slider(45, 450, 200, 20, color=(255, 0, 0))   # posição horizontal
slider_y = Slider(45, 500, 200, 20, color=(0, 255, 0))   # altura
slider_force = Slider(45, 550, 200, 20, color=(0, 0, 255))  # força

sliders = [slider_x, slider_y, slider_force]
slider_labels = ["POSIÇÃO", "ALTURA", "FORÇA"]
current_slider = 0

running = True
while running:
    dt = FramePerSec.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_SPACE:
            # trava o slider atual
            sliders[current_slider].lock_value()
            current_slider += 1
            if current_slider >= len(sliders):
                # todos travados
                valores = [s.value for s in sliders]
                print(f"VALORES FINAIS: posição={valores[0]:.2f}, altura={valores[1]:.2f}, força={valores[2]:.2f}")
                running = False

    # atualiza apenas o slider ativo
    if current_slider < len(sliders):
        sliders[current_slider].update(dt)

    # desenha
    displaysurface.fill((0, 100, 0))

    if current_slider < len(sliders):
        label = font.render(slider_labels[current_slider], True, (255, 255, 255))

        # Condicionais para cada slider que garamtem q eles fiquem
        if slider_labels[current_slider] == "POSIÇÃO":
            displaysurface.blit(label, (WIDTH // 2 - label.get_width() // 2, 440))
        if slider_labels[current_slider] == "ALTURA":
            displaysurface.blit(label, (WIDTH // 2 - label.get_width() // 2, 490))
        if slider_labels[current_slider] == "FORÇA":
            displaysurface.blit(label, (WIDTH // 2 - label.get_width() // 2, 540))

        sliders[current_slider].draw(displaysurface)
    else:
        done_text = font.render("Todos os sliders definidos!", True, (255, 255, 255))
        displaysurface.blit(done_text, (WIDTH // 2 - done_text.get_width() // 2, 300))

    pygame.display.update()
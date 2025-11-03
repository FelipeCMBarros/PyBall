# importações
import pygame
from pygame.locals import *
import sys
import random
import os

# inicialização
pygame.init()
vec = pygame.math.Vector2

# tamanho da tela
WIDTH = 800
HEIGHT = 600

# framerate
FPS = 60
FramePerSec = pygame.time.Clock()

# fontes
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)

# janela
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyBall - Pênaltis")

# classe do JOGADOR
class Jogador(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((40, 80))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=pos)
        self.chutando = False
    def chutar(self, forca, destino):
        self.chutando = True
        return Bola(self.rect.center, destino, forca)
    def update(self, dt):
        return

# classe da BOLA
class Bola(pygame.sprite.Sprite):
    def __init__(self, pos_inicial, destino, forca):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), (10, 10), 10)
        self.rect = self.image.get_rect(center=pos_inicial)
        self.pos = vec(pos_inicial)
        self.destino = vec(destino)
        dir_vec = (self.destino - self.pos)
        if dir_vec.length() == 0:
            direcao = vec(0, -1)
        else:
            direcao = dir_vec.normalize()
        self.velocidade = direcao * (forca * 400)
        self.alive_time = 0
    def update(self, dt):
        self.alive_time += dt
        self.pos += self.velocidade * dt
        self.rect.center = self.pos
        if self.pos.y < -50 or self.pos.y > HEIGHT + 50 or self.pos.x < -100 or self.pos.x > WIDTH + 100:
            self.kill()

# classe do GOLEIRO
class Goleiro(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((60, 80))
        self.image.fill((255, 165, 0))
        self.rect = self.image.get_rect(center=pos)
        self.direcao = 1
        self.vel = 150
        self.range_left = 250
        self.range_right = 550
        self.dive_target_x = None
        self.diving = False
        self.dive_speed = 600
    def mover(self, dt):
        if not self.diving:
            self.rect.x += int(self.vel * self.direcao * dt)
            if self.rect.left < self.range_left or self.rect.right > self.range_right:
                self.direcao *= -1
        else:
            if self.dive_target_x is not None:
                dir_x = self.dive_target_x - self.rect.centerx
                if abs(dir_x) > 5:
                    step = self.dive_speed * dt * (1 if dir_x > 0 else -1)
                    self.rect.centerx += int(step)
    def attempt_dive(self, target_x, chance):
        if random.random() < chance:
            self.diving = True
            self.dive_target_x = target_x
        else:
            self.diving = False
            self.dive_target_x = None
    def reset(self):
        self.diving = False
        self.dive_target_x = None
        self.rect.centerx = (self.range_left + self.range_right) // 2
    def update(self, dt):
        self.mover(dt)

# classe do GOL
class Gol(pygame.sprite.Sprite):
    def __init__(self, pos, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 255, 255), (0, 0, largura, altura), 6)
        self.rect = self.image.get_rect(center=pos)

# classe do SLIDER
class Slider:
    def __init__(self, x, y, width, height, speed_range=(150, 300), color=(0, 0, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.indicador_pos = random.uniform(self.rect.left, self.rect.right)
        self.speed = random.uniform(*speed_range)
        self.direction = random.choice([-1, 1])
        self.color = color
        self.active = True
        self.value = None
    def update(self, dt):
        if not self.active:
            return
        self.indicador_pos += self.speed * self.direction * dt
        if self.indicador_pos < self.rect.left:
            excesso = self.rect.left - self.indicador_pos
            self.indicador_pos = self.rect.left + excesso
            self.direction *= -1
        elif self.indicador_pos > self.rect.right:
            excesso = self.indicador_pos - self.rect.right
            self.indicador_pos = self.rect.right - excesso
            self.direction *= -1
    def lock_value(self):
        rel_pos = (self.indicador_pos - self.rect.left) / self.rect.width
        self.value = max(0.0, min(1.0, rel_pos))
        self.active = False
    def draw(self, surface):
        pygame.draw.rect(surface, (100, 100, 100), self.rect, border_radius=5)
        pygame.draw.rect(surface, self.color, self.rect, 3, border_radius=5)
        indicador_x = int(self.indicador_pos)
        indicador_y = self.rect.centery
        pygame.draw.circle(surface, (255, 255, 255), (indicador_x, indicador_y), self.rect.height // 2)
        if self.value is not None:
            val_text = small_font.render(f"{self.value:.2f}", True, (255, 255, 255))
            surface.blit(val_text, (self.rect.x + self.rect.width + 15, self.rect.y))

# sliders
slider_x = Slider(45, 450, 200, 20, color=(255, 0, 0))
slider_y = Slider(45, 500, 200, 20, color=(0, 255, 0))
slider_force = Slider(45, 550, 200, 20, color=(0, 0, 255))
sliders = [slider_x, slider_y, slider_force]
slider_labels = ["POSIÇÃO", "ALTURA", "FORÇA"]
current_slider = 0

# objetos principais
player = Jogador((WIDTH//2, HEIGHT - 80))
goleiro = Goleiro((400, 150))
gol = Gol((400, 90), 300, 120)
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(goleiro)
bola_group = pygame.sprite.Group()

# placar e estados
placar = {"gols": 0, "tentativas": 0}
resultado_text = ""
resultado_timer = 0.0
resultado_duration = 1.5
estado_em_chute = False

# loop principal
running = True
while running:
    dt = FramePerSec.tick(FPS) / 1000
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_SPACE:
            if current_slider < len(sliders):
                sliders[current_slider].lock_value()
                current_slider += 1
                if current_slider >= len(sliders) and not estado_em_chute:
                    pos_rel, altura_rel, forca_rel = [s.value for s in sliders]
                    gol_interior_left = gol.rect.left + 10
                    gol_interior_right = gol.rect.right - 10
                    gol_top = gol.rect.top + 10
                    gol_bottom = gol.rect.bottom - 10
                    destino_x = gol_interior_left + pos_rel * (gol_interior_right - gol_interior_left)
                    destino_y = gol_bottom - altura_rel * (gol_bottom - gol_top)
                    bola = player.chutar(forca_rel, (destino_x, destino_y))
                    bola_group.add(bola)
                    base_chance = 0.5
                    altura_factor = 1.0 - altura_rel
                    forca_factor = max(0.0, 1.0 - forca_rel)
                    pos_factor = 1.0 - abs(0.5 - pos_rel) * 2
                    chance = base_chance * (0.6 * altura_factor + 0.4 * forca_factor) * pos_factor
                    chance = max(0.05, min(0.95, chance))
                    goleiro.attempt_dive(destino_x, chance)
                    estado_em_chute = True
                    placar["tentativas"] += 1
    if current_slider < len(sliders):
        sliders[current_slider].update(dt)
    all_sprites.update(dt)
    bola_group.update(dt)
    if estado_em_chute:
        for b in bola_group:
            if goleiro.rect.colliderect(b.rect):
                resultado_text = "DEFESA!"
                resultado_timer = resultado_duration
                for bb in bola_group:
                    bb.kill()
                estado_em_chute = False
                goleiro.reset()
                break
            if gol.rect.left + 10 < b.rect.centerx < gol.rect.right - 10 and gol.rect.top + 10 < b.rect.centery < gol.rect.bottom - 10:
                resultado_text = "GOOOOOL!"
                resultado_timer = resultado_duration
                placar["gols"] += 1
                for bb in bola_group:
                    bb.kill()
                estado_em_chute = False
                goleiro.reset()
                break
            if b.pos.y < gol.rect.top - 40:
                resultado_text = "FORA!"
                resultado_timer = resultado_duration
                for bb in bola_group:
                    bb.kill()
                estado_em_chute = False
                goleiro.reset()
                break
    if resultado_timer > 0:
        resultado_timer -= dt
        if resultado_timer <= 0:
            current_slider = 0
            for s in sliders:
                s.active = True
                s.indicador_pos = random.uniform(s.rect.left, s.rect.right)
                s.value = None
            resultado_text = ""
    displaysurface.fill((12, 120, 40))
    displaysurface.blit(gol.image, gol.rect)
    displaysurface.blit(player.image, player.rect)
    displaysurface.blit(goleiro.image, goleiro.rect)
    if current_slider < len(sliders):
        label = font.render(slider_labels[current_slider], True, (255, 255, 255))
        if slider_labels[current_slider] == "POSIÇÃO":
            displaysurface.blit(label, (WIDTH // 2 - label.get_width() // 2, 440))
        if slider_labels[current_slider] == "ALTURA":
            displaysurface.blit(label, (WIDTH // 2 - label.get_width() // 2, 490))
        if slider_labels[current_slider] == "FORÇA":
            displaysurface.blit(label, (WIDTH // 2 - label.get_width() // 2, 540))
        sliders[current_slider].draw(displaysurface)
    else:
        done_text = small_font.render("Chute em andamento...", True, (255, 255, 255))
        displaysurface.blit(done_text, (WIDTH // 2 - done_text.get_width() // 2, 520))
    for b in bola_group:
        displaysurface.blit(b.image, b.rect)
    placar_text = small_font.render(f"Gols: {placar['gols']}  Tentativas: {placar['tentativas']}", True, (255,255,255))
    displaysurface.blit(placar_text, (10, 10))
    if resultado_text:
        r = font.render(resultado_text, True, (255, 255, 0))
        displaysurface.blit(r, (WIDTH // 2 - r.get_width() // 2, 300))
    pygame.display.update()
    

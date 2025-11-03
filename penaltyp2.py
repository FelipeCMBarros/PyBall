# main.py — Joguinho de pênalti em Pygame (continuação do seu código)
import pygame
from pygame.locals import *
import sys
import random
import os

pygame.init()

vec = pygame.math.Vector2  # 2D vector

# tamanho da janela
WIDTH = 800
HEIGHT = 600

# configura o framerate
FPS = 60
FramePerSec = pygame.time.Clock()

font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyBall - Pênaltis")

# --- Classes (mantive e adaptei as suas) ---

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

    # aceitar dt porque o Group.update(dt) passa dt a todos os sprites
    def update(self, dt):
        # por enquanto não precisa fazer nada
        # mas se quiser animar o jogador (ex: recuar ao chutar), faça aqui
        return


class Bola(pygame.sprite.Sprite):
    def __init__(self, pos_inicial, destino, forca):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), (10, 10), 10)
        self.rect = self.image.get_rect(center=pos_inicial)

        self.pos = vec(pos_inicial)
        self.destino = vec(destino)
        # evita divisão por zero
        dir_vec = (self.destino - self.pos)
        if dir_vec.length() == 0:
            direcao = vec(0, -1)
        else:
            direcao = dir_vec.normalize()
        # forca mapeada para velocidade (ajustável)
        self.velocidade = direcao * (forca * 400)  # constante para sensibilidade
        self.alive_time = 0

    def update(self, dt):
        self.alive_time += dt
        # movimento
        # aplicar desaceleração leve para realismo (opcional)
        self.pos += self.velocidade * dt
        self.rect.center = self.pos

        # se passar muito pra cima (além do gol), mantenha como "fora"
        if self.pos.y < -50 or self.pos.y > HEIGHT + 50 or self.pos.x < -100 or self.pos.x > WIDTH + 100:
            self.kill()

class Goleiro(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((60, 80))
        self.image.fill((255, 165, 0))
        self.rect = self.image.get_rect(center=pos)
        self.direcao = 1
        self.vel = 150  # velocidade em px/s para usar com dt
        self.range_left = 250
        self.range_right = 550
        self.dive_target_x = None
        self.diving = False
        self.dive_speed = 600  # px/s quando mergulha

    def mover(self, dt):
        if not self.diving:
            self.rect.x += int(self.vel * self.direcao * dt)
            if self.rect.left < self.range_left or self.rect.right > self.range_right:
                self.direcao *= -1
        else:
            # movimento de mergulho horizontal em direção ao alvo
            if self.dive_target_x is not None:
                dir_x = self.dive_target_x - self.rect.centerx
                if abs(dir_x) > 5:
                    step = self.dive_speed * dt * (1 if dir_x > 0 else -1)
                    self.rect.centerx += int(step)
                else:
                    # terminou o mergulho (ficar um pouquinho)
                    pass

    def attempt_dive(self, target_x, chance):
        # chance entre 0 e 1
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

class Gol(pygame.sprite.Sprite):
    def __init__(self, pos, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura), pygame.SRCALPHA)
        # desenha só a moldura do gol
        pygame.draw.rect(self.image, (255, 255, 255), (0, 0, largura, altura), 6)
        self.rect = self.image.get_rect(center=pos)

# Slider (mantive o seu, com pequenos ajustes)
class Slider:
    def __init__(self, x, y, width, height,  speed_range=(150, 300), color=(0, 0, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.indicador_pos = random.uniform(self.rect.left, self.rect.right)
        self.speed = random.uniform(*speed_range)
        self.direction = random.choice([-1, 1])
        self.color = color
        self.active = True
        self.value = None  # valor travado de 0 a 1

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

# --- Setup inicial ---
# Sliders: posição, altura, força
slider_x = Slider(45, 450, 200, 20, color=(255, 0, 0))   # posição horizontal no gol
slider_y = Slider(45, 500, 200, 20, color=(0, 255, 0))   # altura do chute
slider_force = Slider(45, 550, 200, 20, color=(0, 0, 255))  # força (velocidade)
sliders = [slider_x, slider_y, slider_force]
slider_labels = ["POSIÇÃO", "ALTURA", "FORÇA"]
current_slider = 0

# Sprites e objetos de jogo
player = Jogador((WIDTH//2, HEIGHT - 80))
goleiro = Goleiro((400, 150))
gol = Gol((400, 90), 300, 120)  # largura do gol 300, altura 120
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(goleiro)
# bola estará em uma sprite group separada quando criado
bola_group = pygame.sprite.Group()

# placar e estado
placar = {"gols": 0, "tentativas": 0}
resultado_text = ""
resultado_timer = 0.0
resultado_duration = 1.5  # segundos para mostrar resultado antes de reiniciar
estado_em_chute = False

running = True
while running:
    dt = FramePerSec.tick(FPS) / 1000  # dt em segundos

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_SPACE:
            # trava o slider atual e avança
            if current_slider < len(sliders):
                sliders[current_slider].lock_value()
                current_slider += 1

                # se travou o último slider, inicia o chute
                if current_slider >= len(sliders) and not estado_em_chute:
                    # captura valores
                    pos_rel, altura_rel, forca_rel = [s.value for s in sliders]
                    # calcula destino no gol
                    # gol.rect é a moldura, mapeia pos_rel ao intervalo interno do gol
                    gol_interior_left = gol.rect.left + 10
                    gol_interior_right = gol.rect.right - 10
                    gol_top = gol.rect.top + 10
                    gol_bottom = gol.rect.bottom - 10

                    destino_x = gol_interior_left + pos_rel * (gol_interior_right - gol_interior_left)
                    # altura: 0.0 -> mais alto (top), 1.0 -> mais baixo (centro do gol)
                    destino_y = gol_bottom - altura_rel * (gol_bottom - gol_top)

                    # cria bola
                    bola = player.chutar(forca_rel, (destino_x, destino_y))
                    bola_group.add(bola)

                    # goleiro tenta mergulho: chance depende da força/altura (ex.: bolas mais fracas + médias são mais fáceis)
                    # estratégia simples: bolas muito centrais e rápidas são mais difíceis de defender
                    # vamos definir uma chance base e ajustar por fatores
                    base_chance = 0.5
                    # se chute alto, goleiro tem menos chance
                    altura_factor = 1.0 - altura_rel  # quanto maior valor->mais baixo, mais chance
                    forca_factor = max(0.0, 1.0 - forca_rel)  # chute fraco -> goleiro tem mais tempo
                    # pos factor: quanto mais lateral, mais chance de goleiro errar
                    pos_factor = 1.0 - abs(0.5 - pos_rel) * 2  # 1.0 se central, 0 se nas pontas
                    chance = base_chance * (0.6 * altura_factor + 0.4 * forca_factor) * pos_factor
                    # limita
                    chance = max(0.05, min(0.95, chance))

                    # goleiro tenta mergulho para x do chute
                    goleiro.attempt_dive(destino_x, chance)
                    estado_em_chute = True
                    placar["tentativas"] += 1

    # atualiza sliders se não travados
    if current_slider < len(sliders):
        sliders[current_slider].update(dt)

    # atualiza sprites
    all_sprites.update(dt)
    bola_group.update(dt)

    # colisões / lógica de fim de chute
    if estado_em_chute:
        # checar colisão bola x goleiro (retângulos)
        for b in bola_group:
            if goleiro.rect.colliderect(b.rect):
                # defesa!
                resultado_text = "DEFESA!"
                resultado_timer = resultado_duration
                # limpa bola(s)
                for bb in bola_group:
                    bb.kill()
                estado_em_chute = False
                goleiro.reset()
                break
            # checar se bola passou pela linha do gol (y menor que top) e entrou na área horizontal do gol
            # aqui consideramos gol se centro da bola entra dentro do retângulo interior do gol
            if gol.rect.left + 10 < b.rect.centerx < gol.rect.right - 10 and gol.rect.top + 10 < b.rect.centery < gol.rect.bottom - 10:
                resultado_text = "GOOOOOL!"
                resultado_timer = resultado_duration
                placar["gols"] += 1
                for bb in bola_group:
                    bb.kill()
                estado_em_chute = False
                goleiro.reset()
                break
            # se bola passou além do gol sem entrar -> fora
            if b.pos.y < gol.rect.top - 40:
                resultado_text = "FORA!"
                resultado_timer = resultado_duration
                for bb in bola_group:
                    bb.kill()
                estado_em_chute = False
                goleiro.reset()
                break

    # decrementa timer de resultado e reinicia sliders quando acabar
    if resultado_timer > 0:
        resultado_timer -= dt
        if resultado_timer <= 0:
            # reinicia sliders para próxima tentativa
            current_slider = 0
            for s in sliders:
                # reativa e sorteia posição inicial
                s.active = True
                s.indicador_pos = random.uniform(s.rect.left, s.rect.right)
                s.value = None
            resultado_text = ""

    # desenha
    displaysurface.fill((12, 120, 40))  # gramado

    # desenhar gol
    displaysurface.blit(gol.image, gol.rect)

    # desenhar jogador e goleiro
    displaysurface.blit(player.image, player.rect)
    displaysurface.blit(goleiro.image, goleiro.rect)

    # desenhar sliders e labels
    if current_slider < len(sliders):
        label = font.render(slider_labels[current_slider], True, (255, 255, 255))
        # posicionamento
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

    # desenhar bola(s)
    for b in bola_group:
        displaysurface.blit(b.image, b.rect)

    # desenhar placar
    placar_text = small_font.render(f"Gols: {placar['gols']}  Tentativas: {placar['tentativas']}", True, (255,255,255))
    displaysurface.blit(placar_text, (10, 10))

    # desenhar resultado se houver
    if resultado_text:
        r = font.render(resultado_text, True, (255, 255, 0))
        displaysurface.blit(r, (WIDTH // 2 - r.get_width() // 2, 300))

    pygame.display.update()

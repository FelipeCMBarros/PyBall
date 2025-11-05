import pygame
import sys
import os
import random
import subprocess  # para rodar outro script

pygame.init()
pygame.mixer.init()

# Dimensões da janela
LARGURA, ALTURA = 1000, 700

# Inicializa a janela
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("PyBall")

# Define o ícone (caso exista)
try:
    pygame.display.set_icon(pygame.image.load('icon_pyball.png'))
except pygame.error:
    print("Warning: icon_pyball.png not found.")

# Carrega e redimensiona o fundo
fundo = pygame.image.load('stadium.jpg')
fundo = pygame.transform.scale(fundo, (LARGURA, ALTURA))

# Carrega e redimensiona a logo
logo = pygame.image.load('pyball_logo.png')
# Aqui ajustei para não ocupar toda a tela, apenas uma parte central
logo_largura = 700
logo_altura = 400
logo = pygame.transform.scale(logo, (logo_largura, logo_altura))
logo_rect = logo.get_rect(center=(LARGURA // 2, ALTURA // 2))

# Caminho do áudio
musica_nome = 'Audio/game_intro.mp3'

def tocar_musica(caminho, loop=-1):
    pygame.mixer.music.load(caminho)
    pygame.mixer.music.play(loop)

def parar_musica():
    pygame.mixer.music.stop()

def tela_inicial():
    tocar_musica(musica_nome)
    waiting = True
    clock = pygame.time.Clock()

    fonte = pygame.font.Font(None, 50)
    texto_press = fonte.render("Pressione ENTER para jogar", True, (255, 255, 255))
    texto_rect = texto_press.get_rect(center=(LARGURA // 2, ALTURA - 100))

    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False

        # Desenha elementos na tela
        tela.blit(fundo, (0, 0))
        tela.blit(logo, logo_rect)
        tela.blit(texto_press, texto_rect)
        pygame.display.flip()

        clock.tick(60)

    parar_musica()
    pygame.quit()

    # Executa o jogo principal (penaltyp3.py)
    subprocess.run([sys.executable, "penaltyp3.py"])

# Executa a tela inicial
if __name__ == "__main__":
    tela_inicial()

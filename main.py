import pygame
import sys
import random

pygame.init()

LARGURA, ALTURA = 1000, 700
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("PyBall")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (50, 200, 50)
VERMELHO = (200, 50, 50)
CINZA = (100, 100, 100)
AMARELO = (255, 255, 0)

relogio = pygame.time.Clock()
FPS = 60

# Opções do jogo
OPCAO_ESCOLHER = "escolher"
OPCAO_CHUTAR = "chutar"
OPCAO_RESULTADO = "resultado"
OPCAO_FIM_JOGO = "fim_jogo"

# Variáveis
estado_jogo = OPCAO_ESCOLHER
pontuacao_jogador = 0
pontuacao_goleiro = 0
numero_rodada = 0
rodadas_maximas = 5

escolha_jogador = None
escolha_goleiro = None
temporizador_resultado = 0
cor_flash = None
GOLEIRO_OFFSET_FIM = 60  # quanto mais alto o número, mais para BAIXO ele termina (25 ~ encostar no chão)

# VARIÁVEL DE AJUSTE VERTICAL - Altere este valor para mover tudo para cima/baixo
AJUSTE_VERTICAL_GOL = -165  # Negativo sobe, positivo desce

# --- NEW: single goalie baseline used everywhere to avoid inconsistent Y across rounds ---
GOLEIRO_BASE_Y = 650 + AJUSTE_VERTICAL_GOL  # keep same as original first-round value
# Threshold used to decide inferior vs superior dives (keeps it tied to AJUSTE)
GOLEIRO_INFERIOR_THRESHOLD = 580 + AJUSTE_VERTICAL_GOL
GOLEIRO_CHAO_Y = 600 + AJUSTE_VERTICAL_GOL

# Animação da bola
bola_x = LARGURA // 2
bola_y = (ALTURA) + AJUSTE_VERTICAL_GOL + 100
bola_alvo_x = LARGURA // 2
bola_alvo_y = ALTURA // 2
bola_animando = False
progresso_animacao_bola = 0

# Animação do goleiro - use baseline
goleiro_x = LARGURA // 2
goleiro_y = GOLEIRO_BASE_Y
goleiro_alvo_x = LARGURA // 2
goleiro_alvo_y = 500 + AJUSTE_VERTICAL_GOL
goleiro_animando = False
progresso_animacao_goleiro = 0
goleiro_no_chao = False

# Confete
confete = []

# Zonas do gol (4 cantos) - posicionadas na parte inferior da tela
# Ajustadas para alinhar visualmente com o gol maior e mais baixo
zonas_gol = [
    pygame.Rect(220, 460 + AJUSTE_VERTICAL_GOL, 200, 150),  # superior-esquerdo
    pygame.Rect(580, 460 + AJUSTE_VERTICAL_GOL, 200, 150),  # superior-direito
    pygame.Rect(220, 610 + AJUSTE_VERTICAL_GOL, 200, 150),  # inferior-esquerdo
    pygame.Rect(580, 610 + AJUSTE_VERTICAL_GOL, 200, 150)   # inferior-direito
]

# Carregar recursos
def carregar_recursos():
    global imagem_fundo, imagem_gol, imagem_bola
    global goleiro_parado, goleiro_superior_esquerdo, goleiro_superior_direito
    global goleiro_inferior_esquerdo, goleiro_inferior_direito, goleiro_topo, goleiro_baixo

    try:
        # Fundo
        imagem_fundo = pygame.image.load("bgpropostagpt.png")
        imagem_fundo = pygame.transform.scale(imagem_fundo, (LARGURA, ALTURA))

        # Gol (maior)
        imagem_gol = pygame.image.load("goalp1.png")
        # Gol mais largo + mais alto — ajuste esses números se quiser maior/menor
        imagem_gol = pygame.transform.scale(imagem_gol, (1200, 1000))

        # Bola
        imagem_bola = pygame.image.load("ballp1.png")
        imagem_bola = pygame.transform.scale(imagem_bola, (50, 50))

        # Sprites do goleiro (aumentados um pouco para combinar com o gol maior)
        goleiro_parado = pygame.image.load("goalkeeperstillp1.png")
        goleiro_parado = pygame.transform.scale(goleiro_parado, (140, 200))

        goleiro_topo = pygame.image.load("goalkeepertop.png")
        goleiro_topo = pygame.transform.scale(goleiro_topo, (240, 170))
        goleiro_superior_esquerdo = goleiro_topo
        goleiro_superior_direito = pygame.transform.flip(goleiro_topo, True, False)

        goleiro_baixo = pygame.image.load("goalkeeperbottomp1.png")
        goleiro_baixo = pygame.transform.scale(goleiro_baixo, (260, 150))
        goleiro_inferior_direito = goleiro_baixo
        goleiro_inferior_esquerdo = pygame.transform.flip(goleiro_baixo, True, False)

        print("Todos os recursos carregados com sucesso!")
        return True

    except Exception as e:
        print(f"Erro ao carregar recursos: {e}")
        print("Certifique-se de que todos os arquivos de imagem estão na mesma pasta do arquivo .py")
        return False

# Carregar todos os recursos
recursos_carregados = carregar_recursos()

def criar_confete():
    particulas = []
    for _ in range(60):
        x = random.randint(0, LARGURA)
        y = random.randint(-100, 0)
        cor = random.choice([VERDE, AMARELO, (255, 165, 0), BRANCO])
        velocidade = random.randint(3, 8)
        tamanho = random.randint(4, 8)
        particulas.append([x, y, cor, velocidade, tamanho])
    return particulas

def atualizar_confete():
    global confete
    novo_confete = []
    for particula in confete:
        particula[1] += particula[3]
        if particula[1] < ALTURA:
            novo_confete.append(particula)
    confete = novo_confete

def desenhar_confete():
    for particula in confete:
        pygame.draw.circle(tela, particula[2], (int(particula[0]), int(particula[1])), particula[4])

def desenhar_zonas_gol():
    """Desenhar zonas clicáveis do gol"""
    for i, zona in enumerate(zonas_gol):
        if estado_jogo == OPCAO_ESCOLHER:
            pos_mouse = pygame.mouse.get_pos()
            if zona.collidepoint(pos_mouse):
                # Destaque ao passar o mouse
                s = pygame.Surface((zona.width, zona.height), pygame.SRCALPHA)
                s.fill((255, 255, 100, 80))
                tela.blit(s, zona.topleft)
                pygame.draw.rect(tela, AMARELO, zona, 4)
            else:
                pygame.draw.rect(tela, BRANCO, zona, 2)
        elif estado_jogo == OPCAO_RESULTADO and not bola_animando:
            # Mostrar escolha do jogador
            if i == escolha_jogador:
                pygame.draw.rect(tela, VERDE, zona, 6)

def desenhar_goleiro():
    """Desenhar sprite do goleiro"""
    if not recursos_carregados:
        # Retângulo de fallback
        pygame.draw.rect(tela, (255, 140, 0), (int(goleiro_x - 30), int(goleiro_y - 60), 60, 120))
        return

    if goleiro_no_chao or goleiro_animando:
        # Escolher sprite de mergulho baseado na zona
        if escolha_goleiro == 0:  # superior-esquerdo
            sprite = goleiro_superior_esquerdo
        elif escolha_goleiro == 1:  # superior-direito
            sprite = goleiro_superior_direito
        elif escolha_goleiro == 2:  # inferior-esquerdo
            sprite = goleiro_inferior_esquerdo
        elif escolha_goleiro == 3:  # inferior-direito
            sprite = goleiro_inferior_direito
        else:
            sprite = goleiro_parado
    else:
        sprite = goleiro_parado

    ret = sprite.get_rect(center=(int(goleiro_x), int(goleiro_y)))
    tela.blit(sprite, ret)

def desenhar_bola():
    """Desenhar sprite da bola"""
    if not recursos_carregados:
        pygame.draw.circle(tela, BRANCO, (int(bola_x), int(bola_y)), 20)
        return

    ret = imagem_bola.get_rect(center=(int(bola_x), int(bola_y)))
    tela.blit(imagem_bola, ret)

def desenhar_interface():
    """Desenhar pontuação e elementos da interface"""
    fonte = pygame.font.Font(None, 56)
    fonte_pequena = pygame.font.Font(None, 36)

    # Pontuação com fundo
    texto_pontuacao = fonte.render(f"VOCÊ {pontuacao_jogador} - {pontuacao_goleiro} GOLEIRO", True, BRANCO)
    ret_pontuacao = texto_pontuacao.get_rect(center=(LARGURA // 2, 40))

    # Fundo semi-transparente
    ret_fundo = pygame.Rect(ret_pontuacao.left - 20, ret_pontuacao.top - 10,
                          ret_pontuacao.width + 40, ret_pontuacao.height + 20)
    s = pygame.Surface((ret_fundo.width, ret_fundo.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    tela.blit(s, ret_fundo.topleft)
    tela.blit(texto_pontuacao, ret_pontuacao)

    # Rodada
    texto_rodada = fonte_pequena.render(f"Rodada {numero_rodada}/{rodadas_maximas}", True, BRANCO)
    ret_rodada = texto_rodada.get_rect(center=(LARGURA // 2, 90))
    ret_fundo2 = pygame.Rect(ret_rodada.left - 15, ret_rodada.top - 5,
                           ret_rodada.width + 30, ret_rodada.height + 10)
    s2 = pygame.Surface((ret_fundo2.width, ret_fundo2.height), pygame.SRCALPHA)
    s2.fill((0, 0, 0, 150))
    tela.blit(s2, ret_fundo2.topleft)
    tela.blit(texto_rodada, ret_rodada)

    # Instruções
    if estado_jogo == OPCAO_ESCOLHER:
        texto_inst = fonte_pequena.render("Clique em um canto para chutar!", True, BRANCO)
        ret_inst = texto_inst.get_rect(center=(LARGURA // 2, ALTURA - 475))
        ret_fundo3 = pygame.Rect(ret_inst.left - 15, ret_inst.top - 5,
                               ret_inst.width + 30, ret_inst.height + 10)
        s3 = pygame.Surface((ret_fundo3.width, ret_fundo3.height), pygame.SRCALPHA)
        s3.fill((0, 0, 0, 180))
        tela.blit(s3, ret_fundo3.topleft)
        tela.blit(texto_inst, ret_inst)

def desenhar_resultado():
    """Desenhar resultado de gol/defesa"""
    fonte = pygame.font.Font(None, 80)
    if escolha_jogador == escolha_goleiro:
        texto = fonte.render("DEFENDEU!", True, VERMELHO)
    else:
        texto = fonte.render("GOOOOL!", True, VERDE)

    ret_texto = texto.get_rect(center=(LARGURA // 2, ALTURA - 80))

    # Fundo
    ret_fundo = pygame.Rect(ret_texto.left - 20, ret_texto.top - 10,
                          ret_texto.width + 40, ret_texto.height + 20)
    s = pygame.Surface((ret_fundo.width, ret_fundo.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 200))
    tela.blit(s, ret_fundo.topleft)
    tela.blit(texto, ret_texto)

def desenhar_fim_jogo():
    """Desenhar tela de fim de jogo"""
    fonte = pygame.font.Font(None, 90)
    fonte_pequena = pygame.font.Font(None, 40)

    if pontuacao_jogador > pontuacao_goleiro:
        texto_resultado = fonte.render("VOCÊ VENCEU!", True, VERDE)
    elif pontuacao_goleiro > pontuacao_jogador:
        texto_resultado = fonte.render("VOCÊ PERDEU!", True, VERMELHO)
    else:
        texto_resultado = fonte.render("EMPATE!", True, AMARELO)

    ret_resultado = texto_resultado.get_rect(center=(LARGURA // 2, ALTURA // 2))

    # Fundo
    ret_fundo = pygame.Rect(ret_resultado.left - 30, ret_resultado.top - 20,
                          ret_resultado.width + 60, ret_fundo.height + 40) if False else pygame.Rect(ret_resultado.left - 30, ret_resultado.top - 20, ret_resultado.width + 60, ret_resultado.height + 40)
    s = pygame.Surface((ret_fundo.width, ret_fundo.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 220))
    tela.blit(s, ret_fundo.topleft)
    tela.blit(texto_resultado, ret_resultado)

    texto_reiniciar = fonte_pequena.render("Pressione ESPAÇO para jogar novamente", True, BRANCO)
    ret_reiniciar = texto_reiniciar.get_rect(center=(LARGURA // 2, ALTURA // 2 + 80))
    ret_fundo2 = pygame.Rect(ret_reiniciar.left - 20, ret_reiniciar.top - 10,
                           ret_reiniciar.width + 40, ret_reiniciar.height + 20)
    s2 = pygame.Surface((ret_fundo2.width, ret_fundo2.height), pygame.SRCALPHA)
    s2.fill((0, 0, 0, 220))
    tela.blit(s2, ret_fundo2.topleft)
    tela.blit(texto_reiniciar, ret_reiniciar)

def resetar_jogo():
    global estado_jogo, pontuacao_jogador, pontuacao_goleiro, numero_rodada
    global escolha_jogador, escolha_goleiro, temporizador_resultado, confete
    global bola_x, bola_y, bola_animando, progresso_animacao_bola
    global goleiro_x, goleiro_y, goleiro_animando, progresso_animacao_goleiro, goleiro_no_chao

    estado_jogo = OPCAO_ESCOLHER
    pontuacao_jogador = 0
    pontuacao_goleiro = 0
    numero_rodada = 0
    escolha_jogador = None
    escolha_goleiro = None
    temporizador_resultado = 0
    confete = []

    bola_x = LARGURA // 2
    bola_y = ALTURA - 100
    bola_animando = False
    progresso_animacao_bola = 0

    goleiro_x = LARGURA // 2
    goleiro_y = GOLEIRO_BASE_Y  # <-- consistent baseline
    goleiro_animando = False
    progresso_animacao_goleiro = 0
    goleiro_no_chao = False

# Loop principal do jogo
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.MOUSEBUTTONDOWN and estado_jogo == OPCAO_ESCOLHER:
            pos_mouse = pygame.mouse.get_pos()
            for i, zona in enumerate(zonas_gol):
                if zona.collidepoint(pos_mouse):
                    escolha_jogador = i
                    escolha_goleiro = random.randint(0, 3)
                    estado_jogo = OPCAO_CHUTAR

                    # Iniciar animações
                    bola_animando = True
                    progresso_animacao_bola = 0
                    bola_alvo_x = zonas_gol[escolha_jogador].centerx
                    bola_alvo_y = zonas_gol[escolha_jogador].centery

                    goleiro_animando = True
                    progresso_animacao_goleiro = 0
                    goleiro_alvo_x = zonas_gol[escolha_goleiro].centerx
                    goleiro_alvo_y = zonas_gol[escolha_goleiro].centery

                    temporizador_resultado = 180

                    if escolha_jogador == escolha_goleiro:
                        pontuacao_goleiro += 1
                        cor_flash = VERMELHO
                    else:
                        pontuacao_jogador += 1
                        cor_flash = VERDE
                        confete = criar_confete()

                    numero_rodada += 1
                    estado_jogo = OPCAO_RESULTADO

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and estado_jogo == OPCAO_FIM_JOGO:
                resetar_jogo()

    # Atualizar animação da bola
    if bola_animando:
        progresso_animacao_bola += 0.06
        if progresso_animacao_bola >= 1.0:
            progresso_animacao_bola = 1.0
            bola_animando = False

        # Movimento da bola com arco
        t = progresso_animacao_bola
        inicio_x, inicio_y = LARGURA // 2, (ALTURA - 100) + AJUSTE_VERTICAL_GOL
        bola_x = inicio_x + (bola_alvo_x - inicio_x) * t

        # Arco parabólico
        altura_arco = -150
        bola_y = inicio_y + (bola_alvo_y - inicio_y) * t + altura_arco * (4 * t * (1 - t))

    # Atualizar animação do goleiro
    if goleiro_animando:
        progresso_animacao_goleiro += 0.08
        if progresso_animacao_goleiro >= 1.0:
            progresso_animacao_goleiro = 1.0
            goleiro_animando = False
            goleiro_no_chao = True

        t = progresso_animacao_goleiro
        inicio_x, inicio_y = LARGURA // 2, GOLEIRO_BASE_Y  # <-- use baseline everywhere
        goleiro_x = inicio_x + (goleiro_alvo_x - inicio_x) * t

        # Arco do mergulho: determinar se está mirando para cima ou para baixo
        # --- Reduced magnitudes so dives are lower (less high) ---
        if goleiro_alvo_y > GOLEIRO_INFERIOR_THRESHOLD:  # Inferior
            altura_arco = -12
            chao_y = GOLEIRO_CHAO_Y + GOLEIRO_OFFSET_FIM  # <- desloca o final do mergulho
        else:  # Superior
            altura_arco = -22
            chao_y = goleiro_alvo_y + GOLEIRO_OFFSET_FIM*0.5  # <- idem para os de cima

        goleiro_y = inicio_y + (chao_y - inicio_y) * t + altura_arco * (4 * t * (1 - t))

    # Atualizar temporizador de resultado
    if estado_jogo == OPCAO_RESULTADO:
        temporizador_resultado -= 1
        atualizar_confete()
        if temporizador_resultado <= 0:
            if numero_rodada >= rodadas_maximas:
                estado_jogo = OPCAO_FIM_JOGO
            else:
                estado_jogo = OPCAO_ESCOLHER
                escolha_jogador = None
                escolha_goleiro = None
                bola_x = LARGURA // 2
                bola_y = ALTURA - 100
                goleiro_x = LARGURA // 2
                goleiro_y = GOLEIRO_BASE_Y   # <-- reset to same baseline
                goleiro_no_chao = False

    # Desenhar tudo
    if estado_jogo == OPCAO_RESULTADO and cor_flash and temporizador_resultado > 150:
        tela.fill(cor_flash)
    else:
        if recursos_carregados:
            tela.blit(imagem_fundo, (0, 0))
        else:
            tela.fill((0, 100, 0))

    # Desenhar gol (abaixado para y=620)
    if recursos_carregados:
        ret_gol = imagem_gol.get_rect(center=(LARGURA // 2, 620 + AJUSTE_VERTICAL_GOL * 0.8))
        tela.blit(imagem_gol, ret_gol)

    # Desenhar zonas do gol
    desenhar_zonas_gol()

    # Desenhar goleiro
    desenhar_goleiro()

    # Desenhar bola
    desenhar_bola()

    # Desenhar interface
    desenhar_interface()

    # Desenhar resultado
    if estado_jogo == OPCAO_RESULTADO and not bola_animando:
        desenhar_resultado()
        desenhar_confete()

    # Desenhar fim de jogo
    if estado_jogo == OPCAO_FIM_JOGO:
        desenhar_fim_jogo()

    pygame.display.flip()
    relogio.tick(FPS)

pygame.quit()
sys.exit()

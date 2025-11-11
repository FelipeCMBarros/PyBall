import pygame
import sys
import random

pygame.init()

LARGURA, ALTURA = 1000, 700
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("PyBall - Modo difícil")

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
GOLEIRO_OFFSET_FIM = 60

AJUSTE_VERTICAL_GOL = -165

GOLEIRO_BASE_Y = 650 + AJUSTE_VERTICAL_GOL
GOLEIRO_INFERIOR_THRESHOLD = 580 + AJUSTE_VERTICAL_GOL
GOLEIRO_CHAO_Y = 600 + AJUSTE_VERTICAL_GOL

carregando_potencia = False
potencia_atual = 0
potencia_maxima = 100

# --- ADICIONADO: ping-pong para a força ---
potencia_dir = 1  # 1 = aumentando, -1 = diminuindo

# --- ADICIONADO: slider de direção ---
carregando_direcao = False
direcao_atual = 0.0         # varia entre -1 (esquerda) e 1 (direita)
direcao_dir = 1             # direção do oscilador (-1 ou 1)
# --- ALTERADO: direcao_velocidade agora será recalculada ao entrar no modo direção ---
direcao_velocidade = 0.02   # valor inicial — será sobrescrito ao iniciar seleção de direção
direcao_max_offset = 80     # deslocamento máximo em pixels aplicado ao alvo

# --- ADICIONADO: parâmetros de velocidade mínima e máxima do slider (para escalar pela força) ---
direcao_vel_min = 0.008
direcao_vel_max = 0.06

# Animação da bola
bola_x = LARGURA // 2
bola_y = (ALTURA) + AJUSTE_VERTICAL_GOL + 120
bola_alvo_x = LARGURA // 2
bola_alvo_y = ALTURA // 2
bola_animando = False
progresso_animacao_bola = 0

# Animação do goleiro
goleiro_x = LARGURA // 2
goleiro_y = GOLEIRO_BASE_Y
goleiro_alvo_x = LARGURA // 2
goleiro_alvo_y = 500 + AJUSTE_VERTICAL_GOL
goleiro_animando = False
progresso_animacao_goleiro = 0
goleiro_no_chao = False

# Confete
confete = []

# Zonas do gol como círculos (centro_x, centro_y, raio)
zonas_gol_circulos = [
    (280, 500 + AJUSTE_VERTICAL_GOL, 25),  # superior-esquerdo
    (730, 500 + AJUSTE_VERTICAL_GOL, 25),  # superior-direito
    (260, 660 + AJUSTE_VERTICAL_GOL, 25),  # inferior-esquerdo
    (750, 660 + AJUSTE_VERTICAL_GOL, 25),  # inferior-direito
    (505, 500 + AJUSTE_VERTICAL_GOL, 25),  # superior-central
    (505, 660 + AJUSTE_VERTICAL_GOL, 25)   # inferior-central
]

# Carregar recursos
def carregar_recursos():
    global imagem_fundo, imagem_gol, imagem_bola
    global goleiro_parado, goleiro_superior_esquerdo, goleiro_superior_direito
    global goleiro_inferior_esquerdo, goleiro_inferior_direito, goleiro_topo, goleiro_baixo
    global goleiro_superior_centro, goleiro_inferior_centro

    try:
        imagem_fundo = pygame.image.load("bgpropostagpt.png")
        imagem_fundo = pygame.transform.scale(imagem_fundo, (LARGURA, ALTURA))

        imagem_gol = pygame.image.load("goalp1.png")
        imagem_gol = pygame.transform.scale(imagem_gol, (1200, 1000))

        imagem_bola = pygame.image.load("ballp1.png")
        imagem_bola = pygame.transform.scale(imagem_bola, (50, 50))

        goleiro_parado = pygame.image.load("goalkeeperstillp1.png")
        goleiro_parado = pygame.transform.scale(goleiro_parado, (140, 200))

        goleiro_topo = pygame.image.load("goalkeepertop.png")
        goleiro_topo = pygame.transform.scale(goleiro_topo, (240, 230))
        goleiro_superior_esquerdo = goleiro_topo
        goleiro_superior_direito = pygame.transform.flip(goleiro_topo, True, False)

        goleiro_baixo = pygame.image.load("goalkeeperbottomp1.png")
        goleiro_baixo = pygame.transform.scale(goleiro_baixo, (260, 150))
        goleiro_inferior_direito = goleiro_baixo
        goleiro_inferior_esquerdo = pygame.transform.flip(goleiro_baixo, True, False)

        # Sprites do meio
        goleiro_superior_centro = pygame.image.load("goalietmiddletop.png")
        goleiro_superior_centro = pygame.transform.scale(goleiro_superior_centro, (130, 230))

        goleiro_inferior_centro = pygame.image.load("goaliemiddlebottom.png")
        goleiro_inferior_centro = pygame.transform.scale(goleiro_inferior_centro, (160, 150))

        print("Todos os recursos carregados com sucesso!")
        return True

    except Exception as e:
        print(f"Erro ao carregar recursos: {e}")
        print("Certifique-se de que todos os arquivos de imagem estão na mesma pasta do arquivo .py")
        return False

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

def ponto_dentro_circulo(px, py, cx, cy, raio):
    """Verifica se um ponto está dentro de um círculo"""
    distancia = ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5
    return distancia <= raio

def desenhar_zonas_gol():
    """Desenhar zonas clicáveis do gol como círculos"""
    for i, (cx, cy, raio) in enumerate(zonas_gol_circulos):
        if estado_jogo == OPCAO_ESCOLHER:
            pos_mouse = pygame.mouse.get_pos()
            if ponto_dentro_circulo(pos_mouse[0], pos_mouse[1], cx, cy, raio):
                # Destaque ao passar o mouse - círculo amarelo preenchido semi-transparente
                s = pygame.Surface((raio * 2 + 10, raio * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 255, 100, 120), (raio + 5, raio + 5), raio + 3)
                tela.blit(s, (cx - raio - 5, cy - raio - 5))
                pygame.draw.circle(tela, AMARELO, (cx, cy), raio, 4)
            else:
                # Círculo branco normal
                pygame.draw.circle(tela, BRANCO, (cx, cy), raio, 3)
        elif estado_jogo == OPCAO_RESULTADO and not bola_animando:
            # Mostrar escolha do jogador
            if i == escolha_jogador:
                pygame.draw.circle(tela, VERDE, (cx, cy), raio, 6)

def desenhar_goleiro():
    """Desenhar sprite do goleiro"""
    if not recursos_carregados:
        pygame.draw.rect(tela, (255, 140, 0), (int(goleiro_x - 30), int(goleiro_y - 60), 60, 120))
        return

    if goleiro_no_chao or goleiro_animando:
        if escolha_goleiro == 0:
            sprite = goleiro_superior_esquerdo
        elif escolha_goleiro == 1:
            sprite = goleiro_superior_direito
        elif escolha_goleiro == 2:
            sprite = goleiro_inferior_esquerdo
        elif escolha_goleiro == 3:
            sprite = goleiro_inferior_direito
        elif escolha_goleiro == 4:
            sprite = goleiro_superior_centro
        elif escolha_goleiro == 5:
            sprite = goleiro_inferior_centro
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

    texto_pontuacao = fonte.render(f"VOCÊ {pontuacao_jogador} - {pontuacao_goleiro} GOLEIRO", True, BRANCO)
    ret_pontuacao = texto_pontuacao.get_rect(center=(LARGURA // 2, 40))

    ret_fundo = pygame.Rect(ret_pontuacao.left - 20, ret_pontuacao.top - 10,
                          ret_pontuacao.width + 40, ret_pontuacao.height + 20)
    s = pygame.Surface((ret_fundo.width, ret_fundo.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    tela.blit(s, ret_fundo.topleft)
    tela.blit(texto_pontuacao, ret_pontuacao)

    texto_rodada = fonte_pequena.render(f"Rodada {numero_rodada}/{rodadas_maximas}", True, BRANCO)
    ret_rodada = texto_rodada.get_rect(center=(LARGURA // 2, 90))
    ret_fundo2 = pygame.Rect(ret_rodada.left - 15, ret_rodada.top - 5,
                           ret_rodada.width + 30, ret_rodada.height + 10)
    s2 = pygame.Surface((ret_fundo2.width, ret_fundo2.height), pygame.SRCALPHA)
    s2.fill((0, 0, 0, 150))
    tela.blit(s2, ret_fundo2.topleft)
    tela.blit(texto_rodada, ret_rodada)

    if estado_jogo == OPCAO_ESCOLHER:
        texto_inst = fonte_pequena.render("Clique e segure para carregar FORÇA. Solte para escolher DIREÇÃO. Clique novamente para chutar!", True, BRANCO)
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

    ret_fundo = pygame.Rect(ret_texto.left - 20, ret_texto.top - 10,
                          ret_texto.width + 40, ret_texto.height + 20)
    s = pygame.Surface((ret_fundo.width, ret_fundo.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 200))
    tela.blit(s, ret_fundo.topleft)
    tela.blit(texto, ret_texto)

def desenhar_barra_potencia():
    if estado_jogo != OPCAO_ESCOLHER:
        return

    largura_barra = 300
    altura_barra = 25
    x = (LARGURA - largura_barra) // 2
    y = ALTURA - 100

    pygame.draw.rect(tela, BRANCO, (x, y, largura_barra, altura_barra), 3)

    if carregando_potencia:
        proporcao = potencia_atual / potencia_maxima
        cor = (min(255, int(255 * proporcao)), min(255, int(255 * (1 - proporcao))), 0)
        pygame.draw.rect(tela, cor, (x + 3, y + 3, int((largura_barra - 6) * proporcao), altura_barra - 6))

    # --- ADICIONADO: slider de direção abaixo da barra de potência ---
    largura_dir = 260
    altura_dir = 16
    x_dir = (LARGURA - largura_dir) // 2
    y_dir = y + altura_barra + 12

    # fundo
    pygame.draw.rect(tela, (50, 50, 50), (x_dir, y_dir, largura_dir, altura_dir), border_radius=6)
    # linha central
    meio_x = x_dir + largura_dir // 2
    pygame.draw.line(tela, BRANCO, (meio_x, y_dir), (meio_x, y_dir + altura_dir), 2)

    # marcador (direcao_atual varia -1..1 -> mapear para x)
    marcador_x = int(x_dir + (direcao_atual + 1) / 2 * largura_dir)
    marcador_y = y_dir + altura_dir // 2
    pygame.draw.circle(tela, AMARELO if carregando_direcao else BRANCO, (marcador_x, marcador_y), 8)

    # rótulo
    fonte_peq = pygame.font.Font(None, 24)
    texto_dir = fonte_peq.render("Direção", True, BRANCO)
    tela.blit(texto_dir, (x_dir - 70, y_dir - 2))

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

    ret_fundo = pygame.Rect(ret_resultado.left - 30, ret_resultado.top - 20,
                          ret_resultado.width + 60, ret_resultado.height + 40)
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
    global carregando_potencia, potencia_atual, zona_clicada
    # --- ADICIONADO: resetar variáveis de direção e ping-pong ---
    global potencia_dir, carregando_direcao, direcao_atual, direcao_dir, direcao_velocidade

    estado_jogo = OPCAO_ESCOLHER
    pontuacao_jogador = 0
    pontuacao_goleiro = 0
    numero_rodada = 0
    escolha_jogador = None
    escolha_goleiro = None
    temporizador_resultado = 0
    confete = []

    bola_x = LARGURA // 2
    bola_y = (ALTURA + AJUSTE_VERTICAL_GOL + 120)
    bola_animando = False
    progresso_animacao_bola = 0

    goleiro_x = LARGURA // 2
    goleiro_y = GOLEIRO_BASE_Y
    goleiro_animando = False
    progresso_animacao_goleiro = 0
    goleiro_no_chao = False

    carregando_potencia = False
    potencia_atual = 0
    zona_clicada = None

    # ping-pong força
    potencia_dir = 1

    # direção
    carregando_direcao = False
    direcao_atual = 0.0
    direcao_dir = 1
    direcao_velocidade = 0.02

# Loop principal do jogo
rodando = True
zona_clicada = None  # controla qual zona foi iniciada
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        # --- FLUXO ADAPTADO: primeiro força, depois direção ---
        if evento.type == pygame.MOUSEBUTTONDOWN and estado_jogo == OPCAO_ESCOLHER:
            pos_mouse = pygame.mouse.get_pos()

            # Se já estivermos no modo seleção de direção, um clique confirma a direção e inicia o chute
            if carregando_direcao:
                # confirmar direção e executar chute
                deslocamento_direcao = direcao_atual * direcao_max_offset

                # Garante que o jogador só chute se tinha começado dentro de uma zona válida (zona_clicada armazenada)
                if zona_clicada is None:
                    carregando_direcao = False
                    continue

                escolha_jogador = zona_clicada
                # calcula força baseada no que foi carregado antes
                forca_chute = potencia_atual / potencia_maxima
                if forca_chute < 0.2:
                    forca_chute = 0.2
                elif forca_chute > 1:
                    forca_chute = 1

                # Modo difícil: 4 chances de defesa
                escolha_goleiro1 = random.randint(0, 5)
                escolha_goleiro2 = random.randint(0, 5)
                escolha_goleiro3 = random.randint(0, 5)
                escolha_goleiro4 = random.randint(0, 5)

                estado_jogo = OPCAO_CHUTAR

                # Define o ponto de destino da bola com base na zona clicada e deslocamento de direção
                BolaZoneX = zonas_gol_circulos[escolha_jogador][0]
                bola_alvo_x = BolaZoneX + deslocamento_direcao
                bola_alvo_y = zonas_gol_circulos[escolha_jogador][1]

                # Iniciar animações
                bola_animando = True
                progresso_animacao_bola = 0

                goleiro_animando = True
                progresso_animacao_goleiro = 0

                temporizador_resultado = 180

                # Probabilidade base de defesa (em 0 a 1)
                prob_defesa_base = 0.66  # equivalente a 4 em 6 zonas

                # Reduz a chance de defesa proporcionalmente à força
                prob_defesa_real = prob_defesa_base * (1 - 0.7 * forca_chute)

                # Decide se o goleiro acerta com base nessa chance
                defesa_ocorre = random.random() < prob_defesa_real

                # Escolha do goleiro e pontuação
                if defesa_ocorre:
                    # Goleiro tenta adivinhar
                    escolha_goleiro = random.choice([escolha_goleiro1, escolha_goleiro2, escolha_goleiro3, escolha_goleiro4])
                    pontuacao_goleiro += 1
                    cor_flash = VERMELHO
                else:
                    # Gol
                    escolha_goleiro = random.choice([escolha_goleiro1, escolha_goleiro2, escolha_goleiro3, escolha_goleiro4])
                    pontuacao_jogador += 1
                    if forca_chute > 0.8:
                        tela_flash_timer = 5
                        tela_flash_cor = (255, 255, 100)  # amarelado, simulando brilho do chute

                    cor_flash = VERDE
                    confete = criar_confete()

                goleiro_alvo_x = zonas_gol_circulos[escolha_goleiro][0]
                goleiro_alvo_y = zonas_gol_circulos[escolha_goleiro][1]
                numero_rodada += 1
                estado_jogo = OPCAO_RESULTADO
                zona_clicada = None
                carregando_direcao = False
                carregando_potencia = False

                continue  # não iniciar novo carregamento aqui

            # Se não estamos em seleção de direção: iniciar carregamento de potência (se clicar dentro de zona)
            zona_clicada_temp = None
            for i, (cx, cy, raio) in enumerate(zonas_gol_circulos):
                if ponto_dentro_circulo(pos_mouse[0], pos_mouse[1], cx, cy, raio):
                    zona_clicada_temp = i
                    break

            if zona_clicada_temp is not None:
                zona_clicada = zona_clicada_temp
                carregando_potencia = True
                potencia_atual = 0
                potencia_dir = 1
                # garantir que direção só inicie depois de soltar
                carregando_direcao = False

        # Quando soltar o mouse após carregar potência: entra modo seleção de direção
        if evento.type == pygame.MOUSEBUTTONUP and estado_jogo == OPCAO_ESCOLHER:
            # Se estava carregando força, ao soltar passamos para seleção de direção (não chutamos ainda)
            if carregando_potencia:
                carregando_potencia = False
                carregando_direcao = True
                direcao_atual = 0.0
                direcao_dir = 1

                # --- ADICIONADO: ajustar velocidade do slider de direção com base na força carregada ---
                proporcao_forca = potencia_atual / potencia_maxima
                # mapeia proporcao_forca (0..1) para direcao_vel_min..direcao_vel_max
                direcao_velocidade = direcao_vel_min + proporcao_forca * (direcao_vel_max - direcao_vel_min)

                # manter zona_clicada para saber onde será o chute
                continue

            # Se não estava carregando_potencia, ignorar (o chute agora é confirmado por novo clique em MOUSEBUTTONDOWN)

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and estado_jogo == OPCAO_FIM_JOGO:
                resetar_jogo()

    # Atualizar animação da bola
    if bola_animando:
        velocidade_base = 0.03
        fator_desacel = 0.8
        progresso_animacao_bola += (velocidade_base * (1 + forca_chute)) * fator_desacel
        if progresso_animacao_bola >= 1.0:
            progresso_animacao_bola = 1.0
            bola_animando = False

        t = progresso_animacao_bola
        inicio_x, inicio_y = LARGURA // 2, (ALTURA - 100) + AJUSTE_VERTICAL_GOL

        # O arco do chute aumenta com a força
        altura_arco = -150 * (0.7 + forca_chute * 1.2)
        bola_x = inicio_x + (bola_alvo_x - inicio_x) * t
        bola_y = inicio_y + (bola_alvo_y - inicio_y) * t + altura_arco * (4 * t * (1 - t))

    # Atualizar animação do goleiro
    if goleiro_animando:
        progresso_animacao_goleiro += 0.08
        if progresso_animacao_goleiro >= 1.0:
            progresso_animacao_goleiro = 1.0
            goleiro_animando = False
            goleiro_no_chao = True

        t = progresso_animacao_goleiro
        inicio_x, inicio_y = LARGURA // 2, GOLEIRO_BASE_Y
        
        # Limitar movimento horizontal do goleiro para não sair do gol
        alvo_x_limitado = max(300, min(700, goleiro_alvo_x))
        
        # Ajustar movimento baseado na zona
        if escolha_goleiro in [0, 1]:  # Superior lateral
            goleiro_x = inicio_x + (alvo_x_limitado - inicio_x) * t * 0.75
            altura_arco = -12
            chao_y = goleiro_alvo_y + GOLEIRO_OFFSET_FIM
        elif escolha_goleiro == 4:  # Superior centro
            goleiro_x = inicio_x + (alvo_x_limitado - inicio_x) * t * 0.2
            altura_arco = -15
            chao_y = goleiro_alvo_y + GOLEIRO_OFFSET_FIM
        elif escolha_goleiro == 5:  # Inferior centro
            goleiro_x = inicio_x + (alvo_x_limitado - inicio_x) * t * 0.2
            altura_arco = -8
            chao_y = GOLEIRO_CHAO_Y + GOLEIRO_OFFSET_FIM
        else:  # Inferior lateral (2, 3)
            goleiro_x = inicio_x + (alvo_x_limitado - inicio_x) * t
            altura_arco = -12
            chao_y = GOLEIRO_CHAO_Y + GOLEIRO_OFFSET_FIM

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
                bola_y = (ALTURA + AJUSTE_VERTICAL_GOL + 120)
                goleiro_x = LARGURA // 2
                goleiro_y = GOLEIRO_BASE_Y
                goleiro_no_chao = False

    # Desenhar tudo
    if recursos_carregados:
        tela.blit(imagem_fundo, (0, 0))
    else:
        tela.fill((0, 100, 0))

    # Flash transparente sobre o fundo
    if estado_jogo == OPCAO_RESULTADO and cor_flash and temporizador_resultado > 150:
        s_flash = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s_flash.fill((*cor_flash, 100))
        tela.blit(s_flash, (0, 0))


    # --- ADICIONADO: atualização da direção enquanto no modo seleção de direção ---
    if carregando_direcao:
        direcao_atual += direcao_velocidade * direcao_dir
        if direcao_atual >= 1.0:
            direcao_atual = 1.0
            direcao_dir = -1
        elif direcao_atual <= -1.0:
            direcao_atual = -1.0
            direcao_dir = 1

    # --- ADICIONADO: ping-pong da potência enquanto segurando ---
    if carregando_potencia:
        potencia_atual += 1.5 * potencia_dir
        if potencia_atual >= potencia_maxima:
            potencia_atual = potencia_maxima
            potencia_dir = -1
        elif potencia_atual <= 0:
            potencia_atual = 0
            potencia_dir = 1
    if potencia_atual > potencia_maxima:
        potencia_atual = potencia_maxima

    # Desenhar gol
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

    # Desenhar barra de potência e direção
    desenhar_barra_potencia()

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

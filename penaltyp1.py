import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Penalty Shootout")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)

clock = pygame.time.Clock()
FPS = 60

# Game states
STATE_CHOOSE = "choose"
STATE_SHOOT = "shoot"
STATE_RESULT = "result"
STATE_GAME_OVER = "game_over"

# Game variables
game_state = STATE_CHOOSE
player_score = 0
goalie_score = 0
round_num = 0
max_rounds = 5

player_choice = None
goalie_choice = None
result_timer = 0
flash_color = None

# Ball animation
ball_x = WIDTH // 2
ball_y = HEIGHT - 100
ball_target_x = WIDTH // 2
ball_target_y = HEIGHT // 2
ball_animating = False
ball_animation_progress = 0

# Goalie animation (updated starting Y to match bigger / lower goal)
goalie_x = WIDTH // 2
goalie_y = 560  # adjusted down to align with the lowered/larger goal
goalie_target_x = WIDTH // 2
goalie_target_y = 500
goalie_animating = False
goalie_animation_progress = 0
goalie_on_ground = False

# Confetti
confetti = []

# Goal zones (4 corners) - positioned at bottom of screen
# Updated to visually align with the lowered, larger goal.
goal_zones = [
    pygame.Rect(220, 460, 200, 150),  # top-left
    pygame.Rect(580, 460, 200, 150),  # top-right
    pygame.Rect(220, 610, 200, 150),  # bottom-left
    pygame.Rect(580, 610, 200, 150)   # bottom-right
]

# Load assets
def load_assets():
    global bg_image, goal_image, ball_image
    global goalie_still, goalie_top_left, goalie_top_right
    global goalie_bottom_left, goalie_bottom_right

    try:
        # Background
        bg_image = pygame.image.load("estadiobg.jpg")
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

        # Goal (made bigger)
        goal_image = pygame.image.load("goalp1.png")
        # Wider + taller goal — tweak these numbers if you'd like it larger/smaller
        goal_image = pygame.transform.scale(goal_image, (1200, 1000))

        # Ball
        ball_image = pygame.image.load("ballp1.png")
        ball_image = pygame.transform.scale(ball_image, (50, 50))

        # Goalkeeper sprites (scaled up slightly to match bigger goal)
        goalie_still = pygame.image.load("goalkeeperstillp1.png")
        goalie_still = pygame.transform.scale(goalie_still, (140, 200))

        goalie_top = pygame.image.load("goalkeepertop.png")
        goalie_top = pygame.transform.scale(goalie_top, (240, 170))
        goalie_top_left = goalie_top
        goalie_top_right = pygame.transform.flip(goalie_top, True, False)

        goalie_bottom = pygame.image.load("goalkeeperbottomp1.png")
        goalie_bottom = pygame.transform.scale(goalie_bottom, (260, 150))
        goalie_bottom_right = goalie_bottom
        goalie_bottom_left = pygame.transform.flip(goalie_bottom, True, False)

        print("All assets loaded successfully!")
        return True

    except Exception as e:
        print(f"Error loading assets: {e}")
        print("Make sure all image files are in the same folder as the .py file")
        return False

# Load all assets
assets_loaded = load_assets()

def create_confetti():
    particles = []
    for _ in range(60):
        x = random.randint(0, WIDTH)
        y = random.randint(-100, 0)
        color = random.choice([GREEN, YELLOW, (255, 165, 0), WHITE])
        speed = random.randint(3, 8)
        size = random.randint(4, 8)
        particles.append([x, y, color, speed, size])
    return particles

def update_confetti():
    global confetti
    new_confetti = []
    for particle in confetti:
        particle[1] += particle[3]
        if particle[1] < HEIGHT:
            new_confetti.append(particle)
    confetti = new_confetti

def draw_confetti():
    for particle in confetti:
        pygame.draw.circle(screen, particle[2], (int(particle[0]), int(particle[1])), particle[4])

def draw_goal_zones():
    """Draw clickable goal zones"""
    for i, zone in enumerate(goal_zones):
        if game_state == STATE_CHOOSE:
            mouse_pos = pygame.mouse.get_pos()
            if zone.collidepoint(mouse_pos):
                # Highlight on hover
                s = pygame.Surface((zone.width, zone.height), pygame.SRCALPHA)
                s.fill((255, 255, 100, 80))
                screen.blit(s, zone.topleft)
                pygame.draw.rect(screen, YELLOW, zone, 4)
            else:
                pygame.draw.rect(screen, WHITE, zone, 2)
        elif game_state == STATE_RESULT and not ball_animating:
            # Show player's choice
            if i == player_choice:
                pygame.draw.rect(screen, GREEN, zone, 6)

def draw_goalie():
    """Draw goalkeeper sprite"""
    if not assets_loaded:
        # Fallback rectangle
        pygame.draw.rect(screen, (255, 140, 0), (int(goalie_x - 30), int(goalie_y - 60), 60, 120))
        return

    if goalie_on_ground or goalie_animating:
        # Choose diving sprite based on zone
        if goalie_choice == 0:  # top-left
            sprite = goalie_top_left
        elif goalie_choice == 1:  # top-right
            sprite = goalie_top_right
        elif goalie_choice == 2:  # bottom-left
            sprite = goalie_bottom_left
        elif goalie_choice == 3:  # bottom-right
            sprite = goalie_bottom_right
        else:
            sprite = goalie_still
    else:
        sprite = goalie_still

    rect = sprite.get_rect(center=(int(goalie_x), int(goalie_y)))
    screen.blit(sprite, rect)

def draw_ball():
    """Draw ball sprite"""
    if not assets_loaded:
        pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), 20)
        return

    rect = ball_image.get_rect(center=(int(ball_x), int(ball_y)))
    screen.blit(ball_image, rect)

def draw_ui():
    """Draw score and UI elements"""
    font = pygame.font.Font(None, 56)
    small_font = pygame.font.Font(None, 36)

    # Score with background
    score_text = font.render(f"YOU {player_score} - {goalie_score} GOALIE", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, 40))

    # Semi-transparent background
    bg_rect = pygame.Rect(score_rect.left - 20, score_rect.top - 10,
                          score_rect.width + 40, score_rect.height + 20)
    s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    screen.blit(s, bg_rect.topleft)
    screen.blit(score_text, score_rect)

    # Round
    round_text = small_font.render(f"Round {round_num}/{max_rounds}", True, WHITE)
    round_rect = round_text.get_rect(center=(WIDTH // 2, 90))
    bg_rect2 = pygame.Rect(round_rect.left - 15, round_rect.top - 5,
                           round_rect.width + 30, round_rect.height + 10)
    s2 = pygame.Surface((bg_rect2.width, bg_rect2.height), pygame.SRCALPHA)
    s2.fill((0, 0, 0, 150))
    screen.blit(s2, bg_rect2.topleft)
    screen.blit(round_text, round_rect)

    # Instructions
    if game_state == STATE_CHOOSE:
        inst_text = small_font.render("Click a corner to shoot!", True, WHITE)
        inst_rect = inst_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        bg_rect3 = pygame.Rect(inst_rect.left - 15, inst_rect.top - 5,
                               inst_rect.width + 30, inst_rect.height + 10)
        s3 = pygame.Surface((bg_rect3.width, bg_rect3.height), pygame.SRCALPHA)
        s3.fill((0, 0, 0, 180))
        screen.blit(s3, bg_rect3.topleft)
        screen.blit(inst_text, inst_rect)

def draw_result():
    """Draw goal/save result"""
    font = pygame.font.Font(None, 80)
    if player_choice == goalie_choice:
        text = font.render("SAVED!", True, RED)
    else:
        text = font.render("GOAL!", True, GREEN)

    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 80))

    # Background
    bg_rect = pygame.Rect(text_rect.left - 20, text_rect.top - 10,
                          text_rect.width + 40, text_rect.height + 20)
    s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 200))
    screen.blit(s, bg_rect.topleft)
    screen.blit(text, text_rect)

def draw_game_over():
    """Draw game over screen"""
    font = pygame.font.Font(None, 90)
    small_font = pygame.font.Font(None, 40)

    if player_score > goalie_score:
        result_text = font.render("YOU WIN!", True, GREEN)
    elif goalie_score > player_score:
        result_text = font.render("YOU LOSE!", True, RED)
    else:
        result_text = font.render("DRAW!", True, YELLOW)

    result_rect = result_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    # Background
    bg_rect = pygame.Rect(result_rect.left - 30, result_rect.top - 20,
                          result_rect.width + 60, result_rect.height + 40)
    s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 220))
    screen.blit(s, bg_rect.topleft)
    screen.blit(result_text, result_rect)

    restart_text = small_font.render("Press SPACE to play again", True, WHITE)
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
    bg_rect2 = pygame.Rect(restart_rect.left - 20, restart_rect.top - 10,
                           restart_rect.width + 40, restart_rect.height + 20)
    s2 = pygame.Surface((bg_rect2.width, bg_rect2.height), pygame.SRCALPHA)
    s2.fill((0, 0, 0, 220))
    screen.blit(s2, bg_rect2.topleft)
    screen.blit(restart_text, restart_rect)

def reset_game():
    global game_state, player_score, goalie_score, round_num
    global player_choice, goalie_choice, result_timer, confetti
    global ball_x, ball_y, ball_animating, ball_animation_progress
    global goalie_x, goalie_y, goalie_animating, goalie_animation_progress, goalie_on_ground

    game_state = STATE_CHOOSE
    player_score = 0
    goalie_score = 0
    round_num = 0
    player_choice = None
    goalie_choice = None
    result_timer = 0
    confetti = []

    ball_x = WIDTH // 2
    ball_y = HEIGHT - 100
    ball_animating = False
    ball_animation_progress = 0

    goalie_x = WIDTH // 2
    goalie_y = 560  # reset to the adjusted value
    goalie_animating = False
    goalie_animation_progress = 0
    goalie_on_ground = False

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and game_state == STATE_CHOOSE:
            mouse_pos = pygame.mouse.get_pos()
            for i, zone in enumerate(goal_zones):
                if zone.collidepoint(mouse_pos):
                    player_choice = i
                    goalie_choice = random.randint(0, 3)
                    game_state = STATE_SHOOT

                    # Start animations
                    ball_animating = True
                    ball_animation_progress = 0
                    ball_target_x = goal_zones[player_choice].centerx
                    ball_target_y = goal_zones[player_choice].centery

                    goalie_animating = True
                    goalie_animation_progress = 0
                    goalie_target_x = goal_zones[goalie_choice].centerx
                    goalie_target_y = goal_zones[goalie_choice].centery

                    result_timer = 180

                    if player_choice == goalie_choice:
                        goalie_score += 1
                        flash_color = RED
                    else:
                        player_score += 1
                        flash_color = GREEN
                        confetti = create_confetti()

                    round_num += 1
                    game_state = STATE_RESULT

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state == STATE_GAME_OVER:
                reset_game()

    # Update ball animation
    if ball_animating:
        ball_animation_progress += 0.06
        if ball_animation_progress >= 1.0:
            ball_animation_progress = 1.0
            ball_animating = False

        # Ball movement with arc
        t = ball_animation_progress
        start_x, start_y = WIDTH // 2, HEIGHT - 100
        ball_x = start_x + (ball_target_x - start_x) * t

        # Parabolic arc
        arc_height = -150
        ball_y = start_y + (ball_target_y - start_y) * t + arc_height * (4 * t * (1 - t))

    # Update goalie animation
    if goalie_animating:
        goalie_animation_progress += 0.08
        if goalie_animation_progress >= 1.0:
            goalie_animation_progress = 1.0
            goalie_animating = False
            goalie_on_ground = True

        t = goalie_animation_progress
        start_x, start_y = WIDTH // 2, 560  # start from the adjusted goalie_y
        goalie_x = start_x + (goalie_target_x - start_x) * t

        # Dive arc: determine if aiming for top or bottom based on target center
        if goalie_target_y > 580:  # Bottom (use higher threshold because zones moved down)
            arc_height = -20
            ground_y = 600
        else:  # Top
            arc_height = -35
            ground_y = goalie_target_y

        goalie_y = start_y + (ground_y - start_y) * t + arc_height * (4 * t * (1 - t))

    # Update result timer
    if game_state == STATE_RESULT:
        result_timer -= 1
        update_confetti()
        if result_timer <= 0:
            if round_num >= max_rounds:
                game_state = STATE_GAME_OVER
            else:
                game_state = STATE_CHOOSE
                player_choice = None
                goalie_choice = None
                ball_x = WIDTH // 2
                ball_y = HEIGHT - 100
                goalie_x = WIDTH // 2
                goalie_y = 560
                goalie_on_ground = False

    # Draw everything
    if game_state == STATE_RESULT and flash_color and result_timer > 150:
        screen.fill(flash_color)
    else:
        if assets_loaded:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill((0, 100, 0))

    # Draw goal (lowered to y=620)
    if assets_loaded:
        goal_rect = goal_image.get_rect(center=(WIDTH // 2, 620))
        screen.blit(goal_image, goal_rect)

    # Draw goal zones
    draw_goal_zones()

    # Draw goalie
    draw_goalie()

    # Draw ball
    draw_ball()

    # Draw UI
    draw_ui()

    # Draw result
    if game_state == STATE_RESULT and not ball_animating:
        draw_result()
        draw_confetti()

    # Draw game over
    if game_state == STATE_GAME_OVER:
        draw_game_over()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

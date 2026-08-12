import pygame
import random
import os
import sys
import math

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 700
FPS = 60

PLAYER_SPEED = 17
BULLET_SPEED = 18
BOSS_SPEED = 2

PLAYER_LIVES = 10
BOSS_HP = 50

BLACK = (10, 10, 20)
WHITE = (240, 240, 240)
RED = (255, 60, 60)
CYAN = (0, 255, 255)
YELLOW = (255, 220, 50)
PURPLE = (170, 0, 255)

HIGHSCORE_FILE = "highscore.txt"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Pixel Shooter")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 22)

# Starfield
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1,3)] for _ in range(120)]


# =============================
# SAFE HIGHSCORE
# =============================
def load_highscore():
    try:
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip() or 0)
    except:
        pass
    return 0


def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
    except:
        pass


# =============================
# SPAWNERS
# =============================
def spawn_enemy():
    enemy_type = random.choice(["normal", "fast", "tank"])
    if enemy_type == "normal":
        return {"rect": pygame.Rect(random.randint(0, WIDTH-30), -40, 30, 30),
                "hp": 1, "speed": 2, "color": RED}
    if enemy_type == "fast":
        return {"rect": pygame.Rect(random.randint(0, WIDTH-25), -40, 25, 25),
                "hp": 1, "speed": 4, "color": YELLOW}
    return {"rect": pygame.Rect(random.randint(0, WIDTH-40), -40, 40, 40),
            "hp": 3, "speed": 1, "color": PURPLE}


def spawn_boss():
    return {"rect": pygame.Rect(300, 40, 200, 80), "hp": BOSS_HP, "dir": 1}


def move_boss(b):
    b["rect"].x += b["dir"] * BOSS_SPEED
    if b["rect"].left <= 0 or b["rect"].right >= WIDTH:
        b["dir"] *= -1

    if random.randint(0, 50) == 0:
        boss_bullets.append(
            pygame.Rect(b["rect"].centerx - 4, b["rect"].bottom, 8, 15)
        )


# =============================
# SHOOTING
# =============================
def shoot():
    x, y = player.centerx, player.top

    patterns = {
        "single": [0],
        "triple": [-15, 0, 15],
        "five": [-30, -15, 0, 15, 30],
        "seven": [-45, -30, -15, 0, 15, 30, 45],
        "seven_rapid": [-45, -30, -15, 0, 15, 30, 45],
    }

    base_shots = 2 if rapid_timer > 0 else 1
    total_shots = base_shots * 2 if fire_mode == "seven_rapid" else base_shots

    for _ in range(total_shots):
        if fire_mode == "laser":
            bullets.append({
                "rect": pygame.Rect(x-4, y, 8, 30),
                "hit": set(),
                "pierce": 999
            })
        else:
            for o in patterns[fire_mode]:
                bullets.append({
                    "rect": pygame.Rect(x+o-3, y, 6, 12),
                    "hit": set(),
                    "pierce": 3
                })


def create_explosion(pos):
    global shake_timer
    explosions.append({"pos": pos, "timer": 15})
    shake_timer = 8


# =============================
# RESET
# =============================
def reset_game():
    global player, bullets, enemies, boss, boss_bullets
    global explosions, score, lives, fire_mode, game_state
    global enemy_timer, combo, combo_timer, shake_timer
    global highscore, shoot_cooldown, rapid_timer

    player = pygame.Rect(WIDTH//2 - 20, HEIGHT - 60, 40, 40)
    bullets = []
    enemies = []
    boss = None
    boss_bullets = []
    explosions = []

    score = 0
    combo = 0
    combo_timer = 0
    shake_timer = 0
    shoot_cooldown = 0
    rapid_timer = 0

    lives = PLAYER_LIVES
    fire_mode = "single"
    game_state = "menu"
    enemy_timer = 0
    highscore = load_highscore()


def check_game_over():
    global game_state, highscore
    if lives <= 0:
        if score > highscore:
            highscore = score
            save_highscore(score)
        game_state = "game_over"


# =============================
# START
# =============================
reset_game()
running = True

while running:
    clock.tick(FPS)

    # timers
    if rapid_timer > 0:
        rapid_timer -= 1

    if combo_timer > 0:
        combo_timer -= 1
    else:
        combo = 0

    offset_x = random.randint(-4,4) if shake_timer > 0 else 0
    offset_y = random.randint(-4,4) if shake_timer > 0 else 0
    if shake_timer > 0:
        shake_timer -= 1

    surface = pygame.Surface((WIDTH, HEIGHT))
    surface.fill(BLACK)

    # starfield
    for star in stars:
        star[1] += star[2]
        if star[1] > HEIGHT:
            star[0] = random.randint(0, WIDTH)
            star[1] = 0
        pygame.draw.circle(surface, WHITE, (star[0], star[1]), star[2])

    # events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: fire_mode = "single"
            if event.key == pygame.K_2: fire_mode = "triple"
            if event.key == pygame.K_3: fire_mode = "five"
            if event.key == pygame.K_4: fire_mode = "seven"
            if event.key == pygame.K_5: fire_mode = "laser"
            if event.key == pygame.K_6: fire_mode = "seven_rapid"
            if event.key == pygame.K_r and game_state == "game_over":
                reset_game()

    # ================= MENU
    if game_state == "menu":
        surface.blit(font.render("RETRO PIXEL SHOOTER", True, WHITE), (260,250))
        surface.blit(font.render("Press SPACE to Start", True, CYAN), (260,290))
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            game_state = "play"
        screen.blit(surface, (0,0))
        pygame.display.flip()
        continue

    # ================= GAME OVER
    if game_state == "game_over":
        surface.blit(font.render("GAME OVER", True, RED), (320,240))
        surface.blit(font.render(f"Final Score: {score}", True, WHITE), (290,280))
        surface.blit(font.render(f"High Score: {highscore}", True, CYAN), (290,310))
        surface.blit(font.render("Press R to Restart", True, CYAN), (280,350))
        screen.blit(surface, (0,0))
        pygame.display.flip()
        continue

    # ================= PLAYER
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: player.x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT]: player.x += PLAYER_SPEED
    player.x = max(0, min(WIDTH-player.width, player.x))

    # shooting cooldown
    if shoot_cooldown > 0:
        shoot_cooldown -= 1

    fire_rate = 6 if rapid_timer > 0 else 10
    if keys[pygame.K_SPACE] and shoot_cooldown == 0:
        shoot()
        shoot_cooldown = fire_rate

    # bullets move
    for b in bullets[:]:
        b["rect"].y -= BULLET_SPEED
        if b["rect"].bottom < 0:
            bullets.remove(b)

    # boss bullets move
    for bb in boss_bullets[:]:
        bb.y += 6
        if bb.top > HEIGHT:
            boss_bullets.remove(bb)
        elif bb.colliderect(player):
            boss_bullets.remove(bb)
            lives -= 1
            check_game_over()

    # enemies spawn
    enemy_timer += 1
    spawn_rate = max(10, 40 - score // 40)

    if enemy_timer > spawn_rate and not boss:
        for _ in range(1 + score // 150):
            enemies.append(spawn_enemy())
        enemy_timer = 0

    # boss spawn
    if score >= 200 and not boss:
        boss = spawn_boss()

    # enemies move
    for e in enemies[:]:
        e["rect"].y += e["speed"]

        if e["rect"].y > HEIGHT:
            if e in enemies:
                enemies.remove(e)
            lives -= 1
            check_game_over()
            continue

        for b in bullets[:]:
            if id(e) not in b["hit"] and b["rect"].colliderect(e["rect"]):
                e["hp"] -= 1
                b["hit"].add(id(e))
                b["pierce"] -= 1

                if b["pierce"] <= 0 and b in bullets:
                    bullets.remove(b)

                if e["hp"] <= 0:
                    if e in enemies:
                        enemies.remove(e)
                    combo += 1
                    combo_timer = 120
                    score += 10 * combo
                    create_explosion(e["rect"].center)
                    break

    # boss logic
    if boss:
        move_boss(boss)
        for b in bullets[:]:
            if "boss" not in b["hit"] and b["rect"].colliderect(boss["rect"]):
                boss["hp"] -= 1
                b["hit"].add("boss")
                b["pierce"] -= 1

                create_explosion(b["rect"].center)

                if boss["hp"] <= 0:
                    boss = None
                    score += 500
                    break

                if b["pierce"] <= 0 and b in bullets:
                    bullets.remove(b)

    # ================= DRAW
    pygame.draw.rect(surface, CYAN, player)
    for b in bullets:
        pygame.draw.rect(surface, WHITE, b["rect"])
    for bb in boss_bullets:
        pygame.draw.rect(surface, RED, bb)
    for e in enemies:
        pygame.draw.rect(surface, e["color"], e["rect"])
    if boss:
        pygame.draw.rect(surface, PURPLE, boss["rect"])

    hud = font.render(
        f"Score:{score} High:{highscore} Lives:{lives} Mode:{fire_mode} Combo:{combo}",
        True, WHITE
    )
    surface.blit(hud, (10, HEIGHT-30))

    screen.blit(surface, (offset_x, offset_y))
    pygame.display.flip()

pygame.quit()
sys.exit()
import pygame
import random
import sys
import math

pygame.init()

# =============================
# SCREEN
# =============================
WIDTH, HEIGHT = 950, 550
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Elemental Arsenal")
clock = pygame.time.Clock()
FPS = 60

# =============================
# COLORS
# =============================
BLACK=(15,15,20)
WHITE=(240,240,240)
RED=(255,80,80)
BLUE=(80,150,255)
CYAN=(120,220,255)
YELLOW=(255,220,80)
GREEN=(80,255,150)
ORANGE=(255,150,50)
PURPLE=(200,80,255)

# =============================
# PLAYER
# =============================
px, py = WIDTH//2, HEIGHT-150
vel_y=0
gravity=1
jump_power=-18
on_ground=True
facing=1
player_hp=100
MAX_HP=100

# =============================
# WEAPONS & ELEMENTS
# =============================
weapons=["normal","triple","big","laser","boomerang","grenade"]
weapon_index=0
weapon=weapons[weapon_index]

element="fire"   # fire / ice / shock

ATTACK_COOLDOWN=15
attack_timer=0

# =============================
# PROJECTILES
# =============================
balls=[]
boomerangs=[]
grenades=[]
lasers=[]
explosions=[]

# =============================
# ENEMIES
# =============================
enemies=[]
enemy_timer=0
boss=None
score=0
level=1

font=pygame.font.SysFont("consolas",20)
game_over=False

# =============================
# BUTTONS
# =============================
btns=[]
for i,w in enumerate(weapons):
    btns.append({
        "rect":pygame.Rect(WIDTH-150,40+i*45,130,35),
        "weapon":w
    })

# =============================
# FUNCTIONS
# =============================
def draw_stickman(x,y):
    pygame.draw.circle(screen,WHITE,(x,y),15,2)
    pygame.draw.line(screen,WHITE,(x,y+15),(x,y+60),2)
    pygame.draw.line(screen,WHITE,(x,y+25),(x+facing*20,y+40),2)
    pygame.draw.line(screen,WHITE,(x,y+25),(x-facing*20,y+40),2)
    pygame.draw.line(screen,WHITE,(x,y+60),(x-15,y+95),2)
    pygame.draw.line(screen,WHITE,(x,y+60),(x+15,y+95),2)

def spawn_enemy():
    return {
        "x":random.randint(40,WIDTH-200),
        "y":-20,
        "r":14,
        "hp":3,
        "spd":3+level,
        "burn":0,
        "slow":0
    }

def draw_hp(x,y,hp,maxhp):
    pygame.draw.rect(screen,RED,(x,y,180,15))
    pygame.draw.rect(screen,GREEN,(x,y,int(180*(hp/maxhp)),15))
    pygame.draw.rect(screen,WHITE,(x,y,180,15),2)

def explode(x,y,r,elem):
    explosions.append({"x":x,"y":y,"r":r,"life":10,"elem":elem})

# =============================
# MAIN LOOP
# =============================
running=True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)
    mx,my=pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_1: weapon_index=0
            if event.key==pygame.K_2: weapon_index=1
            if event.key==pygame.K_3: weapon_index=2
            if event.key==pygame.K_4: weapon_index=3
            if event.key==pygame.K_5: weapon_index=4
            if event.key==pygame.K_6: weapon_index=5

            if event.key==pygame.K_f: element="fire"
            if event.key==pygame.K_i: element="ice"
            if event.key==pygame.K_o: element="shock"

        if event.type==pygame.MOUSEBUTTONDOWN:
            for b in btns:
                if b["rect"].collidepoint(mx,my):
                    weapon_index=weapons.index(b["weapon"])

    weapon=weapons[weapon_index]
    keys=pygame.key.get_pressed()
    attack=keys[pygame.K_SPACE]

    # =============================
    # MOVEMENT
    # =============================
    if keys[pygame.K_a]: px-=6; facing=-1
    if keys[pygame.K_d]: px+=6; facing=1
    px=max(20,min(WIDTH-200,px))

    if keys[pygame.K_w] and on_ground:
        vel_y=jump_power
        on_ground=False

    vel_y+=gravity
    py+=vel_y
    if py>=HEIGHT-150:
        py=HEIGHT-150
        vel_y=0
        on_ground=True

    # =============================
    # ATTACK
    # =============================
    dx=mx-px
    dy=my-(py+35)
    dist=max(1,math.hypot(dx,dy))
    vx,vy=dx/dist*10,dy/dist*10

    if attack and attack_timer==0:
        attack_timer=ATTACK_COOLDOWN

        if weapon=="laser":
            lasers.append({"x":px,"y":py+35,"dx":dx,"dy":dy})
        elif weapon=="grenade":
            grenades.append({"x":px,"y":py,"vx":vx,"vy":vy,"t":40,"elem":element})
        else:
            balls.append({"x":px,"y":py+35,"vx":vx,"vy":vy,"big":weapon=="big","elem":element})

    if attack_timer>0: attack_timer-=1

    # =============================
    # PROJECTILES
    # =============================
    for b in balls[:]:
        b["x"]+=b["vx"]; b["y"]+=b["vy"]
        for e in enemies[:]:
            if abs(b["x"]-e["x"])<e["r"]:
                e["hp"]-=1
                if b["elem"]=="fire": e["burn"]=60
                if b["elem"]=="ice": e["slow"]=60
                explode(b["x"],b["y"],40 if b["big"] else 25,b["elem"])
                balls.remove(b)
                break

    for g in grenades[:]:
        g["vy"]+=1
        g["x"]+=g["vx"]; g["y"]+=g["vy"]
        g["t"]-=1
        if g["t"]<=0:
            explode(g["x"],g["y"],60,g["elem"])
            grenades.remove(g)

    # =============================
    # EXPLOSIONS
    # =============================
    for ex in explosions[:]:
        ex["life"]-=1
        for e in enemies[:]:
            if abs(ex["x"]-e["x"])<ex["r"]:
                e["hp"]-=1
        if ex["life"]<=0:
            explosions.remove(ex)

    # =============================
    # ENEMIES
    # =============================
    enemy_timer+=1
    if enemy_timer>50:
        enemies.append(spawn_enemy())
        enemy_timer=0

    for e in enemies[:]:
        spd=e["spd"]*(0.4 if e["slow"]>0 else 1)
        e["y"]+=spd
        if e["burn"]>0: e["burn"]-=1; e["hp"]-=0.02
        if e["slow"]>0: e["slow"]-=1
        if e["hp"]<=0:
            enemies.remove(e)
            score+=3

    # =============================
    # DRAW
    # =============================
    for e in enemies:
        pygame.draw.circle(screen,RED,(int(e["x"]),int(e["y"])),e["r"])

    for b in balls:
        col=ORANGE if b["elem"]=="fire" else CYAN if b["elem"]=="ice" else YELLOW
        pygame.draw.circle(screen,col,(int(b["x"]),int(b["y"])),8 if b["big"] else 5)

    for g in grenades:
        pygame.draw.circle(screen,ORANGE,(int(g["x"]),int(g["y"])),7)

    for ex in explosions:
        col=ORANGE if ex["elem"]=="fire" else CYAN if ex["elem"]=="ice" else YELLOW
        pygame.draw.circle(screen,col,(int(ex["x"]),int(ex["y"])),ex["r"],2)

    draw_stickman(px,py)
    draw_hp(20,20,player_hp,MAX_HP)

    screen.blit(font.render(f"Weapon: {weapon.upper()}",True,WHITE),(20,45))
    screen.blit(font.render(f"Element: {element.upper()}",True,WHITE),(20,70))
    screen.blit(font.render(f"Score: {score}",True,WHITE),(20,95))

    for b in btns:
        pygame.draw.rect(screen,WHITE,b["rect"],2)
        screen.blit(font.render(b["weapon"].upper(),True,WHITE),(b["rect"].x+10,b["rect"].y+8))

    pygame.display.flip()

pygame.quit()
sys.exit()

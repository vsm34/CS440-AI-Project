import pygame
import random
import math

# --- Configuration ---
WIDTH, HEIGHT = 450, 750
FPS = 60
ELIXIR_MAX = 10
ELIXIR_REGEN_RATE = 700 

# Colors
BLACK = (20, 20, 20)
GRAY = (50, 50, 50)
WHITE = (255, 255, 255)
GREEN_HP = (50, 205, 50)
RED_HP = (220, 20, 60)
PURPLE = (148, 0, 211)
GOLD = (255, 215, 0)
SHADOW = (0, 0, 0, 100) # Transparent shadow

# --- FIX: Re-added missing Team Colors for Towers ---
TEAM_PLAYER = (50, 150, 255) 
TEAM_ENEMY = (255, 50, 50)

# Team Tints (Multiplicative blending for Sprites)
TINT_PLAYER = (100, 150, 255) 
TINT_ENEMY = (255, 100, 100)

# --- PIXEL ART DEFINITIONS (12x12 grids) ---
# 0=Clear, 1=Primary Color, 2=Skin/Secondary, 3=Detail
PIXEL_GRIDS = {
    0: [ # Mario (M)
        [0,0,0,1,1,1,1,0,0,0,0,0],
        [0,0,1,1,1,1,1,1,1,0,0,0],
        [0,0,1,2,2,2,1,2,0,0,0,0],
        [0,0,1,2,2,2,1,2,2,2,0,0],
        [0,0,1,1,2,2,2,2,1,1,1,0],
        [0,0,1,1,1,1,1,1,1,1,1,0],
        [0,0,0,1,1,1,1,1,1,0,0,0],
        [0,0,0,2,2,1,1,2,2,0,0,0],
        [0,0,2,2,2,1,1,2,2,2,0,0],
        [0,0,2,2,2,1,1,2,2,2,0,0],
        [0,0,0,0,1,1,1,1,0,0,0,0],
        [0,0,0,0,1,1,1,1,0,0,0,0]
    ],
    1: [ # DK (Big Ape)
        [0,0,1,1,1,1,1,1,0,0,0,0],
        [0,1,1,2,2,2,2,2,1,0,0,0],
        [0,1,2,2,2,2,2,2,2,1,0,0],
        [1,1,2,2,2,2,2,2,2,1,1,0],
        [1,1,2,2,2,3,3,2,2,1,1,0],
        [1,2,2,2,2,2,2,2,2,2,1,0],
        [1,2,2,2,2,2,2,2,2,2,1,0],
        [1,1,2,2,2,2,2,2,2,1,1,0],
        [0,1,1,1,2,2,2,2,1,1,0,0],
        [0,0,0,1,1,1,1,1,1,0,0,0],
        [0,0,0,1,1,0,0,1,1,0,0,0],
        [0,0,0,1,1,0,0,1,1,0,0,0]
    ],
    2: [ # Peach (Crown & Dress)
        [0,0,0,0,3,3,3,0,0,0,0,0],
        [0,0,0,3,3,3,3,3,0,0,0,0],
        [0,0,2,2,2,2,2,2,2,0,0,0],
        [0,0,2,2,2,2,2,2,2,0,0,0],
        [0,0,0,2,2,2,2,2,0,0,0,0],
        [0,0,0,1,1,1,1,1,0,0,0,0],
        [0,0,1,1,1,1,1,1,1,0,0,0],
        [0,1,1,1,1,1,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,1,1,1,0,0],
        [1,1,1,1,1,1,1,1,1,1,1,0],
        [1,1,1,1,1,1,1,1,1,1,1,0],
        [1,1,1,1,1,1,1,1,1,1,1,0]
    ],
    3: [ # Yoshi (Dino)
        [0,0,0,1,1,1,0,0,0,0,0,0],
        [0,0,1,1,1,1,1,0,0,0,0,0],
        [0,0,1,1,3,3,1,1,0,0,0,0],
        [0,0,1,1,1,1,1,1,1,1,0,0],
        [0,0,0,1,1,1,1,1,1,1,0,0],
        [0,0,0,0,1,1,2,2,2,1,0,0],
        [0,0,0,0,1,1,2,2,2,1,0,0],
        [0,0,0,1,1,1,2,2,2,1,0,0],
        [0,0,1,1,1,1,1,1,1,1,0,0],
        [0,0,1,1,0,0,0,1,1,0,0,0],
        [0,1,1,0,0,0,0,0,1,1,0,0],
        [0,1,1,0,0,0,0,0,1,1,0,0]
    ]
}

UNIT_PALETTES = {
    0: {1: (200,0,0), 2: (255,200,150), 3: (0,0,0)},       # Mario
    1: {1: (100,50,0), 2: (150,100,50), 3: (255,200,150)}, # DK
    2: {1: (255,100,180), 2: (255,200,150), 3: GOLD},      # Peach
    3: {1: (50,200,50), 2: (255,255,255), 3: (200,0,0)}    # Yoshi
}

UNIT_STATS = {
    0: {"name": "Mario", "hp": 450, "dmg": 4, "speed": 1.5, "range": 30, "cost": 3, "target": "all", "is_flying": False, "can_hit_air": False, "scale": 2.5},
    1: {"name": "D. Kong","hp": 1200,"dmg": 6, "speed": 0.8, "range": 35, "cost": 5, "target": "building", "is_flying": False, "can_hit_air": False, "scale": 3.5},
    2: {"name": "Peach", "hp": 140, "dmg": 3, "speed": 2.0, "range": 130,"cost": 2, "target": "all", "is_flying": False, "can_hit_air": True, "scale": 2.0},
    3: {"name": "Yoshi", "hp": 650, "dmg": 20,"speed": 1.3, "range": 30, "cost": 4, "target": "building", "is_flying": True, "can_hit_air": False, "scale": 2.8}
}

SPRITE_ASSETS = {}

def generate_sprites():
    # 1. Generate base pixel art surfaces
    base_sprites = {}
    for idx, grid in PIXEL_GRIDS.items():
        surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        palette = UNIT_PALETTES[idx]
        for r in range(12):
            for c in range(12):
                val = grid[r][c]
                if val > 0:
                    surf.set_at((c, r), palette[val])
        base_sprites[idx] = surf

    # 2. Create scaled and tinted versions for teams
    for team in ["player", "enemy"]:
        SPRITE_ASSETS[team] = {}
        tint = TINT_PLAYER if team == "player" else TINT_ENEMY
        
        for idx, base_surf in base_sprites.items():
            scale = UNIT_STATS[idx]["scale"]
            new_size = (int(12 * scale), int(12 * scale))
            scaled_surf = pygame.transform.scale(base_surf, new_size)
            
            tinted_surf = scaled_surf.copy()
            tint_overlay = pygame.Surface(new_size, pygame.SRCALPHA)
            tint_overlay.fill(tint)
            tinted_surf.blit(tint_overlay, (0,0), special_flags=pygame.BLEND_MULT)
            
            SPRITE_ASSETS[team][idx] = tinted_surf

class Entity:
    def __init__(self, x, y, hp, team):
        self.x = x
        self.y = y
        self.max_hp = hp
        self.hp = hp
        self.team = team
        self.dead = False
        self.rect = None 
        self.radius = 20

    def draw_health(self, screen, cx, top_y):
        if self.hp < self.max_hp:
            ratio = max(0, self.hp / self.max_hp)
            w = 40
            h = 6
            pygame.draw.rect(screen, BLACK, (cx - w//2 - 1, top_y - h - 10 -1, w+2, h+2)) 
            pygame.draw.rect(screen, RED_HP, (cx - w//2, top_y - h - 10, w, h))
            pygame.draw.rect(screen, GREEN_HP, (cx - w//2, top_y - h - 10, w * ratio, h))

class Tower(Entity):
    def __init__(self, x, y, team, is_king=False):
        hp = 2500 if is_king else 1200
        super().__init__(x, y, hp, team)
        self.is_king = is_king
        self.range = 150
        self.damage = 4 if is_king else 3
        self.attack_cooldown = 0
        self.max_cooldown = 20 if is_king else 15
        
        size = 70 if is_king else 50
        self.image = pygame.Surface((size, size))
        
        # --- FIX: Ensure TEAM_PLAYER/ENEMY are defined ---
        base_color = TEAM_PLAYER if team == "player" else TEAM_ENEMY
        self.image.fill(base_color)
        if is_king:
            pygame.draw.rect(self.image, GOLD, (size//4, 0, size//2, size//4)) 

        self.rect = self.image.get_rect(center=(x, y))
        self.radius = size // 2 

    def update(self, targets):
        if self.hp <= 0:
            self.dead = True
            return
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            return

        closest = None
        min_dist = float('inf')
        my_cx, my_cy = self.rect.center
        for t in targets:
            dist = math.hypot(t.rect.centerx - my_cx, t.rect.centery - my_cy)
            if dist < self.range and dist < min_dist:
                min_dist = dist
                closest = t
        
        if closest:
            closest.hp -= self.damage
            tower_color = TEAM_PLAYER if self.team == "player" else TEAM_ENEMY
            pygame.draw.line(screen, tower_color, self.rect.center, closest.rect.center, 3)
            self.attack_cooldown = self.max_cooldown

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self.draw_health(screen, self.rect.centerx, self.rect.top)

class Unit(Entity):
    def __init__(self, x, y, team, stats_idx):
        stats = UNIT_STATS[stats_idx]
        super().__init__(x, y, stats["hp"], team)
        
        self.speed = stats["speed"]
        self.damage = stats["dmg"]
        self.range = stats["range"]
        self.target_pref = stats["target"] 
        self.is_flying = stats["is_flying"]
        self.can_hit_air = stats["can_hit_air"]
        self.state = "move"
        
        self.base_image = SPRITE_ASSETS[team][stats_idx]
        self.image = self.base_image 
        self.rect = self.image.get_rect(center=(x, y))
        self.facing_right = True
        self.radius = self.rect.width // 2 

    def update(self, enemy_units, enemy_towers):
        if self.hp <= 0:
            self.dead = True
            return

        possible_targets = []
        possible_targets.extend(enemy_towers)
        
        if self.target_pref == "all":
            for e in enemy_units:
                if e.is_flying and not self.can_hit_air: continue 
                possible_targets.append(e)

        if not possible_targets:
            self.state = "idle"
            return

        target = None
        min_dist = float('inf')
        my_cx, my_cy = self.rect.center

        for t in possible_targets:
            d = math.hypot(t.rect.centerx - my_cx, t.rect.centery - my_cy) - t.radius
            if d < min_dist:
                min_dist = d
                target = t

        if target and min_dist <= self.range:
            self.state = "attack"
            target.hp -= self.damage
            
            if target.rect.centerx < self.rect.centerx: self.facing_right = False
            else: self.facing_right = True

            if self.range > 40: 
                pygame.draw.line(screen, WHITE, self.rect.center, target.rect.center, 1)
        elif target:
            self.state = "move"
            dx = target.rect.centerx - self.rect.centerx
            dy = target.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            
            if dx < 0: self.facing_right = False
            elif dx > 0: self.facing_right = True

            if dist != 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
                self.rect.center = (self.x, self.y)

    def draw(self, screen):
        if self.is_flying:
            shadow_surf = pygame.Surface((self.rect.width, 12), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, SHADOW, (0,0, self.rect.width, 12))
            screen.blit(shadow_surf, (self.rect.x, self.rect.bottom - 6))

        if self.facing_right:
            self.image = self.base_image
        else:
            self.image = pygame.transform.flip(self.base_image, True, False)

        screen.blit(self.image, self.rect)
        self.draw_health(screen, self.rect.centerx, self.rect.top)

class AIController:
    def __init__(self):
        self.elixir = 5.0
        self.last_update = pygame.time.get_ticks()
        self.spawn_cooldown = 0 

    def update(self, current_time, enemy_units, player_units):
        if current_time - self.last_update > ELIXIR_REGEN_RATE:
            if self.elixir < ELIXIR_MAX: self.elixir += 1
            self.last_update = current_time
        
        if self.spawn_cooldown > 0:
            self.spawn_cooldown -= 1
            return None

        if self.elixir >= 8:
            unit_choice = random.choice([1, 3]) 
            side_x = random.choice([80, 370])
            return {"id": unit_choice, "x": side_x, "y": 60, "cost": UNIT_STATS[unit_choice]["cost"]}
        
        for u in player_units:
            if u.y < HEIGHT // 2 and self.elixir >= 3:
                if u.is_flying: return {"id": 2, "x": u.x, "y": 150, "cost": 2}
                else: return {"id": random.choice([0, 2]), "x": u.x, "y": 150, "cost": 3}
        return None

# --- Main Game Setup ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mario Royale - Pixel Art Fixed")
generate_sprites()

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)
large_font = pygame.font.SysFont("Arial bold", 24)
ui_font = pygame.font.Font(None, 20) 

def create_towers(team, y_princess, y_king):
    towers = []
    towers.append(Tower(80, y_princess, team, is_king=False))
    towers.append(Tower(WIDTH-80, y_princess, team, is_king=False))
    towers.append(Tower(WIDTH//2, y_king, team, is_king=True))
    return towers

player_towers = create_towers("player", HEIGHT - 180, HEIGHT - 80)
enemy_towers = create_towers("enemy", 150, 50)

player_units = []
enemy_units = []
ai = AIController()

player_elixir = 5.0
player_last_elixir_update = pygame.time.get_ticks()
selected_card = 0

UI_HEIGHT = 100
PLAY_HEIGHT = HEIGHT - UI_HEIGHT

running = True
game_over = False
winner_text = ""

while running:
    screen.fill(BLACK)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if not game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: selected_card = 0
                if event.key == pygame.K_2: selected_card = 1
                if event.key == pygame.K_3: selected_card = 2
                if event.key == pygame.K_4: selected_card = 3

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if my > PLAY_HEIGHT:
                    card_width = WIDTH // 4
                    selected_card = int(mx // card_width)
                    if selected_card > 3: selected_card = 3
                elif my > PLAY_HEIGHT // 2:
                    cost = UNIT_STATS[selected_card]["cost"]
                    if player_elixir >= cost:
                        player_units.append(Unit(mx, my, "player", selected_card))
                        player_elixir -= cost

    if not game_over:
        if current_time - player_last_elixir_update > ELIXIR_REGEN_RATE:
            if player_elixir < ELIXIR_MAX: player_elixir += 1
            player_last_elixir_update = current_time

        ai_move = ai.update(current_time, enemy_units, player_units)
        if ai_move:
            enemy_units.append(Unit(ai_move["x"], ai_move["y"], "enemy", ai_move["id"]))
            ai.elixir -= ai_move["cost"]
            ai.spawn_cooldown = 100

        player_units = [u for u in player_units if not u.dead]
        enemy_units = [u for u in enemy_units if not u.dead]
        player_towers = [t for t in player_towers if not t.dead]
        enemy_towers = [t for t in enemy_towers if not t.dead]

        if not any(t.is_king for t in player_towers):
            game_over = True
            winner_text = "ENEMY WINS!"
        if not any(t.is_king for t in enemy_towers):
            game_over = True
            winner_text = "YOU WIN!"

        for t in player_towers: t.update(enemy_units)
        for t in enemy_towers: t.update(player_units)
        for u in player_units: u.update(enemy_units, enemy_towers)
        for u in enemy_units: u.update(player_units, player_towers)

    # --- Draw Environment ---
    pygame.draw.rect(screen, (40, 100, 40), (0, 0, WIDTH, HEIGHT)) 
    pygame.draw.rect(screen, (30, 30, 150), (0, PLAY_HEIGHT//2 - 20, WIDTH, 40)) 
    pygame.draw.rect(screen, (120, 80, 40), (60, PLAY_HEIGHT//2 - 25, 40, 50)) 
    pygame.draw.rect(screen, (120, 80, 40), (WIDTH - 100, PLAY_HEIGHT//2 - 25, 40, 50)) 

    for t in player_towers: t.draw(screen)
    for t in enemy_towers: t.draw(screen)
    for u in enemy_units: u.draw(screen)
    for u in player_units: u.draw(screen)

    # --- UI ---
    pygame.draw.rect(screen, (50, 30, 10), (0, PLAY_HEIGHT, WIDTH, UI_HEIGHT)) 
    card_w = WIDTH // 4
    for i in range(4):
        stats = UNIT_STATS[i]
        x_pos = i * card_w
        bg_color = (100, 80, 60) if i == selected_card else (70, 50, 30)
        pygame.draw.rect(screen, bg_color, (x_pos, PLAY_HEIGHT, card_w, UI_HEIGHT))
        pygame.draw.rect(screen, (30,10,0), (x_pos, PLAY_HEIGHT, card_w, UI_HEIGHT), 3) 
        
        if i == selected_card:
            pygame.draw.rect(screen, GOLD, (x_pos + 3, PLAY_HEIGHT + 3, card_w - 6, UI_HEIGHT - 6), 3)
        
        ui_sprite = pygame.transform.scale(SPRITE_ASSETS["player"][i], (40, 40))
        screen.blit(ui_sprite, (x_pos + card_w//2 - 20, PLAY_HEIGHT + 15))

        cost_txt = large_font.render(str(stats["cost"]), True, PURPLE)
        screen.blit(cost_txt, (x_pos + 10, PLAY_HEIGHT + 10))
        name_txt = ui_font.render(stats["name"], True, WHITE)
        screen.blit(name_txt, (x_pos + card_w//2 - name_txt.get_width()//2, PLAY_HEIGHT + 65))

    pygame.draw.rect(screen, BLACK, (5, PLAY_HEIGHT - 40, 150, 35))
    elixir_bar_w = 140 * (player_elixir / ELIXIR_MAX)
    pygame.draw.rect(screen, PURPLE, (10, PLAY_HEIGHT - 35, elixir_bar_w, 25))
    elixir_display = large_font.render(f"{int(player_elixir)}", True, WHITE)
    screen.blit(elixir_display, (160, PLAY_HEIGHT - 35))

    if game_over:
        win_msg = large_font.render(winner_text, True, WHITE)
        pygame.draw.rect(screen, BLACK, (WIDTH//2 - 100, HEIGHT//2 - 30, 200, 60))
        screen.blit(win_msg, (WIDTH//2 - win_msg.get_width()//2, HEIGHT//2 - 15))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

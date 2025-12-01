from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame

BLACK = (20, 20, 20)
GREEN_HP = (50, 205, 50)
RED_HP = (220, 20, 60)
TEAM_PLAYER = (50, 150, 255)
TEAM_ENEMY = (255, 50, 50)
GOLD = (255, 215, 0)


@dataclass
class Tower:
    """
    Combat-capable tower ported from the original smash2.py implementation.

    Responsibilities:
    - Own its own HP and death state.
    - Choose a target among nearby enemy troops and apply damage.
    - Expose a lightweight `to_render_dict()` for the main loop / UI layer.
    """

    x: float
    y: float
    team: str  # "player" or "ai"
    is_king: bool = True

    max_hp: int = 2500
    hp: int = 2500
    range: float = 150.0
    damage: float = 4.0
    max_cooldown: int = 20

    # Runtime state (not part of constructor API)
    attack_cooldown: int = 0
    dead: bool = False

    # Rendering helpers
    radius: int = 35
    _size: int = 70
    _rect: Optional[pygame.Rect] = None
    _last_attack_line: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None

    def __post_init__(self) -> None:
        if not self.is_king:
            # Side-tower style stats – kept for future extension / parity
            self.max_hp = self.hp = 1200
            self.damage = 3
            self.max_cooldown = 15
            self._size = 50
        else:
            self.max_hp = self.hp = 2500
            self.damage = 4
            self.max_cooldown = 20
            self._size = 70

        self.radius = self._size // 2
        self._rect = pygame.Rect(0, 0, self._size, self._size)
        self._rect.center = (int(self.x), int(self.y))

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------
    def update(self, enemy_troops: List["Troop"]) -> None:
        """
        Attack the closest enemy troop in range, if any.

        Pure game logic – no drawing calls here.
        """
        self._last_attack_line = None

        if self.hp <= 0:
            self.dead = True
            return

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            return

        if not enemy_troops:
            return

        my_cx, my_cy = self._rect.center
        closest = None
        min_dist = float("inf")

        for troop in enemy_troops:
            tx, ty = troop.get_center()
            dist = math.hypot(tx - my_cx, ty - my_cy)
            if dist < self.range and dist < min_dist and troop.hp > 0:
                min_dist = dist
                closest = troop

        if closest is None:
            return

        # Apply damage
        closest.hp -= self.damage
        if closest.hp <= 0:
            closest.dead = True

        # Remember line to draw during render
        self._last_attack_line = (self._rect.center, closest.get_center())
        self.attack_cooldown = self.max_cooldown

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    def _draw_health_bar(self, screen: pygame.Surface) -> None:
        if self.hp >= self.max_hp:
            return

        ratio = max(0.0, self.hp / self.max_hp)
        w, h = 60, 8
        cx = self._rect.centerx
        
        # Team-aware HP bar positioning:
        # Enemy (top) tower: bar below the tower
        # Player (bottom) tower: bar above the tower
        if self.team == "ai":  # Enemy tower at top
            bar_y = self._rect.bottom + 4
        else:  # Player tower at bottom
            bar_y = self._rect.top - h - 4

        # Consistent health bar styling: 1px black border, red background, green fill
        bg_rect = pygame.Rect(cx - w // 2 - 1, bar_y - 1, w + 2, h + 2)
        hp_back_rect = pygame.Rect(cx - w // 2, bar_y, w, h)
        hp_rect = pygame.Rect(cx - w // 2, bar_y, int(w * ratio), h)

        pygame.draw.rect(screen, BLACK, bg_rect)
        pygame.draw.rect(screen, RED_HP, hp_back_rect)
        pygame.draw.rect(screen, GREEN_HP, hp_rect)

    def draw(self, screen: pygame.Surface) -> None:
        # Core body with darker outline for better readability
        base_color = TEAM_PLAYER if self.team == "player" else TEAM_ENEMY
        outline_color = (20, 60, 120) if self.team == "player" else (120, 20, 20)
        
        # Draw outline (slightly larger rect)
        outline_rect = self._rect.inflate(2, 2)
        pygame.draw.rect(screen, outline_color, outline_rect)
        
        # Draw main body
        pygame.draw.rect(screen, base_color, self._rect)

        # Simple "front face" for king tower - mirrored based on team position
        if self.is_king:
            # Front face dimensions (yellow window)
            front_w = int(self._size * 0.6)
            front_h = int(self._size * 0.25)
            front_x = self._rect.left + int(self._size * 0.2)
            
            # For enemy (top) tower: front faces downward (toward center)
            # For player (bottom) tower: front faces upward (toward center)
            if self.team == "ai":  # Enemy tower at top
                front_y = self._rect.top + int(self._size * 0.55)
            else:  # Player tower at bottom
                front_y = self._rect.top + int(self._size * 0.2)
            
            front_rect = pygame.Rect(front_x, front_y, front_w, front_h)
            
            # Front face outline (darker)
            pygame.draw.rect(screen, (200, 150, 0), front_rect.inflate(1, 1))
            # Front face fill (gold/yellow)
            pygame.draw.rect(screen, GOLD, front_rect)

        # Attack beam (if we attacked this frame)
        if self._last_attack_line is not None:
            tower_color = TEAM_PLAYER if self.team == "player" else TEAM_ENEMY
            pygame.draw.line(
                screen,
                tower_color,
                self._last_attack_line[0],
                self._last_attack_line[1],
                3,
            )

        self._draw_health_bar(screen)

    # ------------------------------------------------------------------
    # Public snapshots
    # ------------------------------------------------------------------
    def get_center(self) -> Tuple[int, int]:
        return self._rect.center

    def to_render_dict(self) -> dict:
        """
        Return a small, JSON-serialisable snapshot for UI/AI if needed.
        """
        return {
            "x": float(self._rect.x),
            "y": float(self._rect.y),
            "width": int(self._rect.width),
            "height": int(self._rect.height),
            "team": self.team,
            "hp": float(self.hp),
            "max_hp": float(self.max_hp),
            "is_king": self.is_king,
        }

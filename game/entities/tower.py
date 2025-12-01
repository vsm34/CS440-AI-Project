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
        cx, top_y = self._rect.centerx, self._rect.top

        bg_rect = pygame.Rect(cx - w // 2 - 1, top_y - h - 12 - 1, w + 2, h + 2)
        hp_back_rect = pygame.Rect(cx - w // 2, top_y - h - 12, w, h)
        hp_rect = pygame.Rect(cx - w // 2, top_y - h - 12, int(w * ratio), h)

        pygame.draw.rect(screen, BLACK, bg_rect)
        pygame.draw.rect(screen, RED_HP, hp_back_rect)
        pygame.draw.rect(screen, GREEN_HP, hp_rect)

    def draw(self, screen: pygame.Surface) -> None:
        # Core body
        base_color = TEAM_PLAYER if self.team == "player" else TEAM_ENEMY
        pygame.draw.rect(screen, base_color, self._rect)

        # Simple "crown" for king tower
        if self.is_king:
            crown_h = self._size // 4
            crown_rect = pygame.Rect(
                self._rect.left + self._size // 4,
                self._rect.top,
                self._size // 2,
                crown_h,
            )
            pygame.draw.rect(screen, GOLD, crown_rect)

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

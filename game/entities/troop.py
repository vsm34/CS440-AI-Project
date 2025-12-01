from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pygame

from game.data.loader import load_troops

BLACK = (20, 20, 20)
GREEN_HP = (50, 205, 50)
RED_HP = (220, 20, 60)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
SHADOW = (0, 0, 0, 100)

TEAM_PLAYER = (50, 150, 255)
TEAM_ENEMY = (255, 50, 50)
TINT_PLAYER = (100, 150, 255)
TINT_ENEMY = (255, 100, 100)


# ---------------------------------------------------------------------------
# Pixel-art based sprites + stats, ported from smash2.py
# ---------------------------------------------------------------------------

PIXEL_GRIDS: Dict[int, List[List[int]]] = {
    0: [  # Mario
        [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 1, 2, 2, 2, 1, 2, 0, 0, 0, 0],
        [0, 0, 1, 2, 2, 2, 1, 2, 2, 2, 0, 0],
        [0, 0, 1, 1, 2, 2, 2, 2, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 2, 2, 1, 1, 2, 2, 0, 0, 0],
        [0, 0, 2, 2, 2, 1, 1, 2, 2, 2, 0, 0],
        [0, 0, 2, 2, 2, 1, 1, 2, 2, 2, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
    ],
    1: [  # DK
        [0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
        [0, 1, 1, 2, 2, 2, 2, 2, 1, 0, 0, 0],
        [0, 1, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0],
        [1, 1, 2, 2, 2, 2, 2, 2, 2, 1, 1, 0],
        [1, 1, 2, 2, 2, 3, 3, 2, 2, 1, 1, 0],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],
        [1, 1, 2, 2, 2, 2, 2, 2, 2, 1, 1, 0],
        [0, 1, 1, 1, 2, 2, 2, 2, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0],
    ],
    2: [  # Peach
        [0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0],
        [0, 0, 0, 3, 3, 3, 3, 3, 0, 0, 0, 0],
        [0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0],
        [0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0],
        [0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    ],
    3: [  # Yoshi
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 3, 3, 1, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 1, 1, 2, 2, 2, 1, 0, 0],
        [0, 0, 0, 0, 1, 1, 2, 2, 2, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 2, 2, 2, 1, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
    ],
}

UNIT_PALETTES: Dict[int, Dict[int, Tuple[int, int, int]]] = {
    0: {1: (200, 0, 0), 2: (255, 200, 150), 3: (0, 0, 0)},  # Mario
    1: {1: (100, 50, 0), 2: (150, 100, 50), 3: (255, 200, 150)},  # DK
    2: {1: (255, 100, 180), 2: (255, 200, 150), 3: GOLD},  # Peach
    3: {1: (50, 200, 50), 2: (255, 255, 255), 3: (200, 0, 0)},  # Yoshi
}

def _build_unit_stats_from_data() -> Dict[int, Dict[str, float | int | str | bool]]:
    """
    Load troop stats from `game/data/troops.json` so balance is data-driven.

    Balance philosophy (high level):
    - Mario: mid-cost melee brawler / general-purpose DPS.
    - Bowser (DK sprite): slow, expensive front-line tank / tower sieger.
    - Peach: cheap-ish, fragile ranged support with air targeting.
    - Yoshi: fast flying building-hunter for split pushes.
    """
    unit_stats: Dict[int, Dict[str, float | int | str | bool]] = {}
    for entry in load_troops():
        idx = int(entry["id"])
        unit_stats[idx] = {
            "name": entry.get("name", f"Troop {idx}"),
            "hp": float(entry["hp"]),
            "dmg": float(entry["damage"]),
            "speed": float(entry["speed"]),
            "range": float(entry["range"]),
            "target": str(entry.get("target", "all")),
            "is_flying": bool(entry.get("is_flying", False)),
            "can_hit_air": bool(entry.get("can_hit_air", False)),
            "scale": float(entry.get("scale", 2.5)),
            # Coins cost + role are intentionally ignored here and consumed
            # by World / AI instead of the Troop simulation itself.
        }
    return unit_stats


UNIT_STATS: Dict[int, Dict[str, float | int | str | bool]] = _build_unit_stats_from_data()

SPRITE_ASSETS: Dict[str, Dict[int, pygame.Surface]] = {}


def generate_sprites() -> None:
    """
    Generate the per-unit, per-team sprite surfaces.

    Must be called once after pygame.init() and before any Troop is drawn.
    """
    base_sprites: Dict[int, pygame.Surface] = {}
    for idx, grid in PIXEL_GRIDS.items():
        surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        palette = UNIT_PALETTES[idx]
        for r in range(12):
            for c in range(12):
                val = grid[r][c]
                if val > 0:
                    surf.set_at((c, r), palette[val])
        base_sprites[idx] = surf

    for team in ["player", "ai"]:
        SPRITE_ASSETS[team] = {}
        tint = TINT_PLAYER if team == "player" else TINT_ENEMY

        for idx, base_surf in base_sprites.items():
            scale = float(UNIT_STATS[idx]["scale"])
            new_size = (int(12 * scale), int(12 * scale))
            scaled_surf = pygame.transform.scale(base_surf, new_size)

            tinted_surf = scaled_surf.copy()
            tint_overlay = pygame.Surface(new_size, pygame.SRCALPHA)
            tint_overlay.fill(tint)
            tinted_surf.blit(tint_overlay, (0, 0), special_flags=pygame.BLEND_MULT)

            SPRITE_ASSETS[team][idx] = tinted_surf


@dataclass
class Troop:
    """
    Battle troop with movement, targeting, and drawing logic.

    Closely mirrors `Unit` from smash2.py but is decoupled from globals
    and draws via `draw(screen)` instead of writing to a global `screen`.
    """

    x: float
    y: float
    team: str  # "player" or "ai"
    lane_index: int
    stats_idx: int

    hp: float = 0.0
    max_hp: float = 0.0
    speed: float = 0.0
    damage: float = 0.0
    range: float = 0.0
    target_pref: str = "all"
    is_flying: bool = False
    can_hit_air: bool = False

    state: str = "move"
    facing_right: bool = True

    # rendering
    _base_image: Optional[pygame.Surface] = None
    _image: Optional[pygame.Surface] = None
    _rect: Optional[pygame.Rect] = None
    radius: int = 20
    _last_attack_line: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None

    def __post_init__(self) -> None:
        stats = UNIT_STATS[self.stats_idx]

        self.max_hp = self.hp = float(stats["hp"])
        self.speed = float(stats["speed"])
        self.damage = float(stats["dmg"])
        self.range = float(stats["range"])
        self.target_pref = str(stats["target"])
        self.is_flying = bool(stats["is_flying"])
        self.can_hit_air = bool(stats["can_hit_air"])

        # Attach sprite
        self._base_image = SPRITE_ASSETS.get(self.team, {}).get(self.stats_idx)
        if self._base_image is None:
            # Fallback: simple rectangle
            size = 32
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            surf.fill(TEAM_PLAYER if self.team == "player" else TEAM_ENEMY)
            self._base_image = surf

        self._image = self._base_image
        self._rect = self._base_image.get_rect(center=(int(self.x), int(self.y)))
        self.radius = self._rect.width // 2

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------
    def update(self, enemy_units: List["Troop"], enemy_towers: List["Tower"]) -> None:
        """
        Update movement & combat vs. enemy units and towers.
        """
        from game.entities.tower import Tower  # local import to avoid cycles

        self._last_attack_line = None

        if self.hp <= 0:
            self.state = "dead"
            return

        # Choose potential targets
        possible_targets: List[object] = []
        possible_targets.extend(enemy_towers)

        if self.target_pref == "all":
            for e in enemy_units:
                if e.is_flying and not self.can_hit_air:
                    continue
                possible_targets.append(e)

        if not possible_targets:
            self.state = "idle"
            return

        # Find closest target
        target: Optional[object] = None
        min_dist = float("inf")
        my_cx, my_cy = self.get_center()

        for t in possible_targets:
            tx, ty = (t.get_center() if hasattr(t, "get_center") else (t.x, t.y))
            radius = getattr(t, "radius", 0)
            d = math.hypot(tx - my_cx, ty - my_cy) - radius
            if d < min_dist:
                min_dist = d
                target = t

        if target is not None and min_dist <= self.range:
            # In range: attack
            self.state = "attack"
            target.hp -= self.damage
            if target.hp <= 0:
                target.dead = True

            tx, ty = (
                target.get_center() if hasattr(target, "get_center") else (target.x, target.y)
            )
            if tx < my_cx:
                self.facing_right = False
            else:
                self.facing_right = True

            if self.range > 40:
                self._last_attack_line = (self.get_center(), (int(tx), int(ty)))
        elif target is not None:
            # Move toward target
            self.state = "move"
            tx, ty = (
                target.get_center() if hasattr(target, "get_center") else (target.x, target.y)
            )
            dx = tx - my_cx
            dy = ty - my_cy
            dist = math.hypot(dx, dy)

            if dx < 0:
                self.facing_right = False
            elif dx > 0:
                self.facing_right = True

            if dist > 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
                self._rect.center = (int(self.x), int(self.y))

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def _draw_health(self, screen: pygame.Surface) -> None:
        if self.hp >= self.max_hp:
            return

        ratio = max(0.0, self.hp / self.max_hp)
        w, h = 40, 6
        cx, top_y = self._rect.centerx, self._rect.top

        bg_rect = pygame.Rect(cx - w // 2 - 1, top_y - h - 10 - 1, w + 2, h + 2)
        hp_back_rect = pygame.Rect(cx - w // 2, top_y - h - 10, w, h)
        hp_rect = pygame.Rect(cx - w // 2, top_y - h - 10, int(w * ratio), h)

        pygame.draw.rect(screen, BLACK, bg_rect)
        pygame.draw.rect(screen, RED_HP, hp_back_rect)
        pygame.draw.rect(screen, GREEN_HP, hp_rect)

    def draw(self, screen: pygame.Surface) -> None:
        # Shadow for flying units
        if self.is_flying:
            shadow_surf = pygame.Surface((self._rect.width, 12), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, SHADOW, (0, 0, self._rect.width, 12))
            screen.blit(shadow_surf, (self._rect.x, self._rect.bottom - 6))

        # Orientation
        if self.facing_right:
            self._image = self._base_image
        else:
            self._image = pygame.transform.flip(self._base_image, True, False)

        screen.blit(self._image, self._rect)
        self._draw_health(screen)

        # Attack line (for ranged units)
        if self._last_attack_line is not None:
            pygame.draw.line(
                screen, WHITE, self._last_attack_line[0], self._last_attack_line[1], 1
            )

    # ------------------------------------------------------------------
    # Public snapshots
    # ------------------------------------------------------------------
    def get_center(self) -> Tuple[int, int]:
        return self._rect.center

    def to_render_dict(self) -> dict:
        """Small snapshot for AI / UI layers."""
        return {
            "x": float(self.x),
            "y": float(self.y),
            "team": self.team,
            "lane_index": int(self.lane_index),
            "hp": float(self.hp),
            "max_hp": float(self.max_hp),
            "stats_idx": int(self.stats_idx),
        }


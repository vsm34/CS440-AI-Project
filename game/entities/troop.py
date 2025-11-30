# game/entities/troop.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Troop:
    """
    Basic troop entity.

    x, y: position in pixels
    owner: "player" or "ai"
    lane_index: 0, 1, or 2
    troop_id: which kind of troop (e.g. "mario", "bowser", "dry_bones", "red_shell")
    hp: current health
    max_hp: maximum health
    """
    x: float
    y: float
    owner: str
    lane_index: int
    troop_id: str

    # Class-wide size constants for drawing/spawning offsets
    WIDTH: int = 40
    HEIGHT: int = 40

    # Simple combat stats; can be overridden per troop_id
    hp: float = 100.0
    max_hp: float = 100.0
    speed: float = 60.0  # pixels per second toward enemy base

    def __post_init__(self) -> None:
        # If max_hp wasn't set explicitly, sync it with hp
        if self.max_hp <= 0:
            self.max_hp = self.hp

        # Optionally adjust stats based on troop_id
        if self.troop_id == "bowser":
            self.hp = self.max_hp = 250.0
            self.speed = 40.0
        elif self.troop_id == "mario":
            self.hp = self.max_hp = 100.0
            self.speed = 80.0
        elif self.troop_id == "dry_bones":
            self.hp = self.max_hp = 40.0
            self.speed = 80.0
        elif self.troop_id == "red_shell":
            # Could behave more like a spell than a unit; keep simple for now
            self.hp = self.max_hp = 1.0
            self.speed = 120.0

    def update(self, dt: float) -> None:
        """
        Move the troop toward the enemy base.
        - 'player' troops move upward (toward y decreasing).
        - 'ai' troops move downward (toward y increasing).
        """
        direction = -1 if self.owner == "player" else 1
        self.y += direction * self.speed * dt

        # TODO: clamp at tower positions, trigger attacks, etc.

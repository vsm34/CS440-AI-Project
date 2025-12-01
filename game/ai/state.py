# game/ai/state.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional

# Owner IDs match Varun's world/tower: "player" and "ai"
PlayerId = Literal["player", "ai"]


@dataclass(frozen=True)
class TroopView:
    """
    Lightweight view of a troop for AI.
    All fields have defaults so you can safely construct this even
    if World hasn't filled everything in yet.
    """
    owner: PlayerId = "player"
    lane_index: int = 0
    y: float = 0.0
    hp: float = 100.0
    max_hp: float = 100.0
    troop_id: str = "unknown"


@dataclass(frozen=True)
class LaneView:
    """
    All troops in a single lane.
    """
    index: int = 0
    troops: List[TroopView] = field(default_factory=list)


@dataclass(frozen=True)
class GameState:
    """
    Abstract game state snapshot for AI.

    IMPORTANT:
    - All fields have default values so Varun's current
      `return GameState()` compiles and runs.
    """
    # King towers
    player_base_hp: float = 1000.0
    ai_base_hp: float = 1000.0

    # Resources (Mario coins)
    player_coins: float = 5.0
    ai_coins: float = 5.0
    max_coins: float = 10.0

    # Board
    lanes: List[LaneView] = field(default_factory=list)

    # Time / tick
    tick: int = 0

    # Terminal info
    is_terminal: bool = False
    winner: Optional[PlayerId] = None

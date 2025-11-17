# game/ai/state.py

from dataclasses import dataclass
from typing import List

@dataclass
class TroopSnapshot:
    x: float
    y: float
    hp: int
    owner: str  # "player" or "ai"
    troop_type: str  # e.g. "drybones", "mario"

@dataclass
class GameState:
    troops: List[TroopSnapshot] = None
    player_elixir: int = 0
    ai_elixir: int = 0
    # later: base HP, time remaining, etc.

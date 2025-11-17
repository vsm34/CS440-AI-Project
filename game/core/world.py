# game/core/world.py

from dataclasses import dataclass
from typing import List, Optional

from game.core.actions import PlayCardAction
from game.entities.troop import Troop


class World:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # for now: single lane rect info
        self.lane_width = 220
        self.lane_x = self.screen_width // 2 - self.lane_width // 2

        # troops on the field
        self.troops: List[Troop] = []

        # temporary: spawn one Drybones so something happens
        self._spawn_initial_troop()

    def _spawn_initial_troop(self):
        x = self.lane_x + self.lane_width // 2 - 20
        y = self.screen_height - 60
        self.troops.append(Troop(x, y))

    def apply_player_action(self, action: PlayCardAction) -> None:
        """Called when the human plays a card."""
        # TODO: later: check elixir, lane_index, etc.
        pass

    def apply_ai_action(self, action: PlayCardAction) -> None:
        """Called when the AI plays a card."""
        # TODO: later: same as above, but for AI
        pass

    def step(self, dt: float) -> None:
        """Advance the world simulation by dt seconds."""
        for troop in self.troops:
            troop.update(dt)

        # TODO: later: call combat, elixir, AI, etc.

    def get_public_state(self) -> "GameState":
        """Return an abstract game state view for the AI."""
        # TODO: later: construct from troop positions, hp, elixir, etc.
        from game.ai.state import GameState
        return GameState()  # placeholder


@dataclass
class RenderInfo:
    lane_x: int
    lane_width: int

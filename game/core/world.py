# game/core/world.py

import pygame
from dataclasses import dataclass
from typing import List

from game.core.actions import PlayCardAction
from game.entities.tower import Tower
from game.entities.troop import Troop


@dataclass
class Lane:
    index: int  # 0 = left, 1 = center, 2 = right
    x: int
    width: int


@dataclass
class WorldRenderInfo:
    lane_rects: List[pygame.Rect]
    top_boundary: pygame.Rect
    bottom_boundary: pygame.Rect


class World:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.lanes: List[Lane] = self._create_lanes()
        self.troops: List[Troop] = []
        self.towers: List[Tower] = []

        self._create_king_towers()

        # temporary: spawn one Drybones so something happens
        self.spawn_troop_in_lane(1, owner="player")

    def _create_lanes(self) -> List[Lane]:
        num_lanes = 3
        base_lane_width = self.screen_width // num_lanes
        total_lane_width = base_lane_width * num_lanes
        horizontal_margin = (self.screen_width - total_lane_width) // 2

        lanes: List[Lane] = []
        for index in range(num_lanes):
            x = horizontal_margin + index * base_lane_width
            lanes.append(Lane(index=index, x=x, width=base_lane_width))
        return lanes

    def _create_king_towers(self) -> None:
        center_lane = self.get_lane(1)
        tower_width = int(center_lane.width * 0.45)
        tower_height = 110
        bottom_margin = 40
        top_margin = 40

        player_x = center_lane.x + center_lane.width // 2 - tower_width // 2
        player_y = self.screen_height - bottom_margin - tower_height

        ai_x = player_x
        ai_y = top_margin

        self.player_king_tower = Tower(player_x, player_y, tower_width, tower_height, "player")
        self.ai_king_tower = Tower(ai_x, ai_y, tower_width, tower_height, "ai")
        self.towers = [self.player_king_tower, self.ai_king_tower]

    def spawn_troop_in_lane(self, lane_index: int, owner: str = "player") -> Troop:
        lane = self.get_lane(lane_index)
        x = lane.x + lane.width // 2 - Troop.WIDTH // 2
        if owner == "player":
            y = self.screen_height - 60
        else:
            y = 60
        troop = Troop(x, y)
        self.troops.append(troop)
        return troop

    def get_lane(self, index: int) -> Lane:
        if index < 0 or index >= len(self.lanes):
            raise ValueError(f"Lane index {index} is out of range.")
        return self.lanes[index]

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

    def get_render_info(self, screen_height: int) -> WorldRenderInfo:
        lane_rects = [
            pygame.Rect(lane.x, 0, lane.width, screen_height)
            for lane in self.lanes
        ]

        boundary_thickness = 8
        boundary_margin = 24

        top_boundary = pygame.Rect(
            0,
            boundary_margin,
            self.screen_width,
            boundary_thickness,
        )
        bottom_boundary = pygame.Rect(
            0,
            screen_height - boundary_margin - boundary_thickness,
            self.screen_width,
            boundary_thickness,
        )

        return WorldRenderInfo(
            lane_rects=lane_rects,
            top_boundary=top_boundary,
            bottom_boundary=bottom_boundary,
        )

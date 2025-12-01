import pygame
from dataclasses import dataclass
from typing import List, Dict, Tuple

from game.core.actions import PlayCardAction
from game.entities.tower import Tower
from game.entities.troop import Troop, generate_sprites
from game.ai.policy import choose_ai_action
from game.ai.state import GameState, LaneView, TroopView
from game.data.loader import load_cards, load_troops


COINS_MAX = 10
COINS_REGEN_MS = 700  # match smash2.py pacing


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
    """
    Owns all mutable game state: troops, towers, coins, and timers.

    This is a modularised port of the original smash2.py game rules,
    with AI control delegated through GameState + PlayCardAction.
    """

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Lanes
        self.lanes: List[Lane] = self._create_lanes()

        # Combat entities
        self.player_troops: List[Troop] = []
        self.ai_troops: List[Troop] = []
        self.player_towers: List[Tower] = []
        self.ai_towers: List[Tower] = []

        # Coins + timers
        self.player_coins: float = 5.0
        self.ai_coins: float = 5.0
        self._player_coins_timer: float = 0.0
        self._ai_coins_timer: float = 0.0

        # AI decision timer
        self._ai_decision_timer: float = 0.0
        self._tick: int = 0

        # Game over state
        self.game_over: bool = False
        self.winner: str | None = None  # "player" or "ai"

        # Card → troop mapping, now data‑driven from JSON.
        # See `game/data/cards.json` and `game/data/troops.json`.
        self.card_defs: Dict[str, Dict[str, int | float]] = self._build_card_defs()

        # Initialise sprites (requires pygame to be initialised already)
        generate_sprites()

        self._create_king_towers()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
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
        size = int(center_lane.width * 0.45)
        bottom_margin = 80
        top_margin = 80

        cx = center_lane.x + center_lane.width // 2
        player_y = self.screen_height - bottom_margin
        ai_y = top_margin

        self.player_king_tower = Tower(cx, player_y, team="player", is_king=True)
        self.ai_king_tower = Tower(cx, ai_y, team="ai", is_king=True)

        self.player_towers = [self.player_king_tower]
        self.ai_towers = [self.ai_king_tower]

    def _build_card_defs(self) -> Dict[str, Dict[str, int | float]]:
        """
        Build per-card metadata from JSON.

        Each card knows:
        - which troop stats index it spawns (stats_idx),
        - how many coins it costs to play (cost).
        """
        # Map troop_id -> stats_idx so card data does not need to repeat it.
        troops = {int(t["id"]): t for t in load_troops()}

        card_defs: Dict[str, Dict[str, int | float]] = {}
        for card in load_cards():
            card_id = str(card["id"])
            troop_id = int(card["troop_id"])
            coins_cost = float(card["coins_cost"])

            if troop_id not in troops:
                # If data is inconsistent, skip rather than crash the whole game.
                continue

            card_defs[card_id] = {
                "stats_idx": troop_id,
                "cost": coins_cost,
            }

        return card_defs

    def get_lane(self, index: int) -> Lane:
        if index < 0 or index >= len(self.lanes):
            raise ValueError(f"Lane index {index} is out of range.")
        return self.lanes[index]

    @property
    def troops(self) -> List[Troop]:
        return self.player_troops + self.ai_troops

    @property
    def towers(self) -> List[Tower]:
        return self.player_towers + self.ai_towers

    def _spawn_troop(self, lane_index: int, team: str, stats_idx: int) -> None:
        lane = self.get_lane(lane_index)
        x = lane.x + lane.width // 2

        # Spawn near each side's king tower vertically
        if team == "player":
            y = self.player_king_tower.get_center()[1] - 60
        else:
            y = self.ai_king_tower.get_center()[1] + 60

        troop = Troop(x=float(x), y=float(y), team=team, lane_index=lane_index, stats_idx=stats_idx)
        if team == "player":
            self.player_troops.append(troop)
        else:
            self.ai_troops.append(troop)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _apply_action_generic(self, action: PlayCardAction, team: str) -> None:
        if action is None:
            return

        card = self.card_defs.get(action.card_id)
        if not card:
            return

        cost = float(card["cost"])
        stats_idx = int(card["stats_idx"])

        if team == "player":
            if self.player_coins < cost:
                return
            self.player_coins -= cost
        else:
            if self.ai_coins < cost:
                return
            self.ai_coins -= cost

        lane_index = max(0, min(len(self.lanes) - 1, action.lane_index))
        self._spawn_troop(lane_index=lane_index, team=team, stats_idx=stats_idx)

    def apply_player_action(self, action: PlayCardAction) -> None:
        """Called when the human plays a card."""
        if self.game_over:
            return
        self._apply_action_generic(action, team="player")

    def apply_ai_action(self, action: PlayCardAction) -> None:
        """Called when the AI plays a card."""
        if self.game_over:
            return
        self._apply_action_generic(action, team="ai")

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------
    def _regen_coins(self, dt: float) -> None:
        ms = dt * 1000.0

        self._player_coins_timer += ms
        self._ai_coins_timer += ms

        while self._player_coins_timer >= COINS_REGEN_MS:
            if self.player_coins < COINS_MAX:
                self.player_coins += 1
            self._player_coins_timer -= COINS_REGEN_MS

        while self._ai_coins_timer >= COINS_REGEN_MS:
            if self.ai_coins < COINS_MAX:
                self.ai_coins += 1
            self._ai_coins_timer -= COINS_REGEN_MS

    def _update_combat(self) -> None:
        # Towers attack first
        for tower in list(self.player_towers):
            tower.update(self.ai_troops)
        for tower in list(self.ai_towers):
            tower.update(self.player_troops)

        # Troops fight troops + towers
        for troop in list(self.player_troops):
            troop.update(self.ai_troops, self.ai_towers)
        for troop in list(self.ai_troops):
            troop.update(self.player_troops, self.player_towers)

        # Remove dead entities
        self.player_troops = [t for t in self.player_troops if not getattr(t, "dead", False)]
        self.ai_troops = [t for t in self.ai_troops if not getattr(t, "dead", False)]
        self.player_towers = [t for t in self.player_towers if not getattr(t, "dead", False)]
        self.ai_towers = [t for t in self.ai_towers if not getattr(t, "dead", False)]

        # Win/loss conditions: king towers destroyed
        if not any(getattr(t, "is_king", False) for t in self.player_towers) and not self.game_over:
            self.game_over = True
            self.winner = "ai"
        if not any(getattr(t, "is_king", False) for t in self.ai_towers) and not self.game_over:
            self.game_over = True
            self.winner = "player"

    def step(self, dt: float) -> None:
        """Advance the world simulation by dt seconds."""
        if self.game_over:
            return

        self._tick += 1
        self._regen_coins(dt)
        self._update_combat()

        # AI decision once per ~1 second
        self._ai_decision_timer += dt
        if self._ai_decision_timer >= 1.0 and not self.game_over:
            self._ai_decision_timer = 0.0
            state = self.get_public_state()
            action = choose_ai_action(state)
            if action is not None:
                self.apply_ai_action(action)

    # ------------------------------------------------------------------
    # AI state view
    # ------------------------------------------------------------------
    def _build_lane_views_from_ai_perspective(self) -> List[LaneView]:
        lanes: List[List[TroopView]] = [[] for _ in self.lanes]

        def add_troops(source: List[Troop], owner_label: str) -> None:
            for troop in source:
                lane_idx = max(0, min(len(self.lanes) - 1, troop.lane_index))
                # From the AI policy's perspective, it is always "player"
                owner = "player" if owner_label == "ai" else "ai"
                lanes[lane_idx].append(
                    TroopView(
                        owner=owner,  # type: ignore[arg-type]
                        lane_index=lane_idx,
                        y=float(troop.y),
                        hp=float(troop.hp),
                        max_hp=float(troop.max_hp),
                        troop_id=str(troop.stats_idx),
                    )
                )

        add_troops(self.player_troops, "player")
        add_troops(self.ai_troops, "ai")

        return [
            LaneView(index=i, troops=lane_troops)
            for i, lane_troops in enumerate(lanes)
        ]

    def get_public_state(self) -> GameState:
        """
        Return an abstract game state view for the AI.

        IMPORTANT: we present the world from the AI's perspective as the
        "player" in GameState so that the baseline policy can be reused
        without modification.
        """
        lanes = self._build_lane_views_from_ai_perspective()

        player_base_hp = float(self.ai_king_tower.hp)
        ai_base_hp = float(self.player_king_tower.hp)

        return GameState(
            player_base_hp=player_base_hp,
            ai_base_hp=ai_base_hp,
            player_coins=float(self.ai_coins),
            ai_coins=float(self.player_coins),
            max_coins=float(COINS_MAX),
            lanes=lanes,
            tick=self._tick,
            is_terminal=self.game_over,
            winner=("player" if self.winner == "ai" else "ai") if self.winner else None,
        )

    # ------------------------------------------------------------------
    # Rendering info
    # ------------------------------------------------------------------
    def get_render_info(self, screen_height: int) -> WorldRenderInfo:
        lane_rects = [
            pygame.Rect(lane.x, 0, lane.width, screen_height) for lane in self.lanes
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

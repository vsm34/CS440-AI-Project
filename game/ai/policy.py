# game/ai/policy.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .state import GameState, LaneView, TroopView
from .policy_baseline import choose_baseline_action
from game.core.actions import PlayCardAction
from game.data.loader import load_cards, load_troops


# ---------------------------------------------------------------------------
# Card metadata for heuristic policy
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CardInfo:
    card_id: str
    cost: float
    role: str  # "tank", "dps", "ranged", "air", "support"
    troop_id: int
    hp: float
    damage: float
    speed: float
    range: float


def _build_ai_card_pool() -> Dict[str, CardInfo]:
    """
    Build AI-visible card + troop stats from JSON data.

    This keeps AI decisions in sync with troop balance without
    hard-coding numbers in the policy itself.
    """
    troops_raw = {int(t["id"]): t for t in load_troops()}

    pool: Dict[str, CardInfo] = {}
    for card in load_cards():
        card_id = str(card["id"])
        troop_id = int(card["troop_id"])
        coins_cost = float(card["coins_cost"])

        troop = troops_raw.get(troop_id)
        if troop is None:
            continue

        # Map data-driven role strings into a smaller set for the heuristic.
        raw_role = str(troop.get("role", "brawler_dps"))
        if "tank" in raw_role:
            role = "tank"
        elif "ranged" in raw_role:
            role = "ranged"
        elif "air" in raw_role:
            role = "air"
        elif "support" in raw_role:
            role = "support"
        else:
            role = "dps"

        pool[card_id] = CardInfo(
            card_id=card_id,
            cost=coins_cost,
            role=role,
            troop_id=troop_id,
            hp=float(troop["hp"]),
            damage=float(troop["damage"]),
            speed=float(troop["speed"]),
            range=float(troop["range"]),
        )

    return pool


AI_CARD_POOL: Dict[str, CardInfo] = _build_ai_card_pool()

LANE_INDICES = (0, 1, 2)


def choose_ai_action(state: GameState) -> Optional[PlayCardAction]:
    """
    Main entry point for the AI.

    World will call:
        state = world.get_public_state()
        action = choose_ai_action(state)

    This implementation is a heuristic, smash2-inspired policy that:
      - Generates all legal actions (all cards AI can afford in all lanes).
      - Scores each action based on lane pressure, base HP, coins, and card stats.
      - Picks the highest scoring action.

    All logic is based purely on GameState + data-loaded troop/card stats
    so we remain compatible with future search-based (minimax/MCTS) upgrades.
    """

    if state.is_terminal:
        return None

    # Quick coins check – if we're too poor, do nothing.
    if state.player_coins < 1.0:
        return None

    # If we don't have lane information yet (early in development),
    # fall back to the original baseline policy.
    if not state.lanes:
        return choose_baseline_action(state)

    legal_actions = _generate_legal_actions(state)
    if not legal_actions:
        return None

    lane_metrics = _compute_lane_metrics(state)
    my_troop_counts = _count_my_troops_by_type(state)

    best_score = float("-inf")
    best_action: Optional[PlayCardAction] = None

    for action in legal_actions:
        score = _score_action(state, action, lane_metrics, my_troop_counts)
        if score > best_score:
            best_score = score
            best_action = action

    return best_action


# ---------------------------------------------------------------------------
# Legal action generation
# ---------------------------------------------------------------------------

def _generate_legal_actions(state: GameState) -> List[PlayCardAction]:
    """
    Enumerate all legal card + lane combinations the AI can afford.

    We only look at:
      - AI's coins (state.player_coins – by construction in World.get_public_state)
      - Known cards in AI_CARD_POOL
      - The 3 standard lanes (0, 1, 2)
    """
    actions: List[PlayCardAction] = []

    for card_id, info in AI_CARD_POOL.items():
        if state.player_coins < info.cost:
            continue

        for lane_index in LANE_INDICES:
            actions.append(PlayCardAction(card_id=card_id, lane_index=lane_index))

    return actions


# ---------------------------------------------------------------------------
# Lane analysis helpers
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LaneMetrics:
    lane_index: int
    my_hp: float
    enemy_hp: float
    pressure: float  # enemy_hp - my_hp (positive => we are behind)
    enemy_min_y: float  # smallest enemy y (closest to our base at the top)
    my_min_y: float  # my front line y (closest to enemy base)


def _compute_lane_metrics(state: GameState) -> Dict[int, LaneMetrics]:
    """
    Summarise each lane from the AI's perspective.

    In GameState, the AI is always the logical 'player' and the human
    opponent is 'ai'. Smaller y is closer to the AI base (top).
    """
    metrics: Dict[int, LaneMetrics] = {}

    for lane in state.lanes:
        my_hp = 0.0
        enemy_hp = 0.0
        enemy_min_y = float("inf")
        my_min_y = float("inf")

        for t in lane.troops:
            if t.owner == "player":  # AI's own troops (by construction)
                my_hp += t.hp
                my_min_y = min(my_min_y, t.y)
            else:  # "ai" => human opponent
                enemy_hp += t.hp
                enemy_min_y = min(enemy_min_y, t.y)

        if enemy_min_y == float("inf"):
            enemy_min_y = 9999.0
        if my_min_y == float("inf"):
            my_min_y = 9999.0

        pressure = enemy_hp - my_hp

        metrics[lane.index] = LaneMetrics(
            lane_index=lane.index,
            my_hp=my_hp,
            enemy_hp=enemy_hp,
            pressure=pressure,
            enemy_min_y=enemy_min_y,
            my_min_y=my_min_y,
        )

    return metrics


def _count_my_troops_by_type(state: GameState) -> Dict[int, int]:
    """
    Count how many troops of each type the AI (logical 'player') currently has
    on the board. Uses TroopView.troop_id, which is aligned with troop stats_idx.
    """
    counts: Dict[int, int] = {}
    for lane in state.lanes:
        for t in lane.troops:
            if t.owner == "player":  # by construction GameState treats AI as 'player'
                try:
                    key = int(getattr(t, "troop_id"))
                except (TypeError, ValueError):
                    continue
                counts[key] = counts.get(key, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Heuristic evaluation
# ---------------------------------------------------------------------------

def _score_action(
    state: GameState,
    action: PlayCardAction,
    lane_metrics: Dict[int, LaneMetrics],
    my_troop_counts: Dict[int, int],
) -> float:
    """
    Assign a heuristic score to a candidate action.

    High-level intuition (smash2-inspired):
      - Defend lanes where we are under pressure (enemy_hp >> my_hp).
      - Use tanky cards to defend or to push when we're ahead.
      - Use cheaper cards to avoid floating coins near max.
      - Prefer attacking lanes where the opponent has little presence
        when we are comfortably ahead.
    """
    base_score = 0.0

    info = AI_CARD_POOL.get(action.card_id)
    if info is None:
        return float("-inf")

    lane = lane_metrics.get(action.lane_index)

    # 1) Base coins efficiency
    # Spend coins if we're close to capping out.
    coins = state.player_coins
    if coins >= state.max_coins - 1:
        base_score += 5.0  # strongly encouraged to spend something
    elif coins - info.cost < 1:
        base_score -= 1.5  # mild penalty for going almost dry

    # 2) Lane pressure & threat
    if lane is not None:
        # Pressure > 0 => enemy advantage, we should defend
        if lane.pressure > 0:
            base_score += 3.0 * min(lane.pressure / 200.0, 3.0)

        # If enemy troops are close to our base (small y), prioritize that lane
        if lane.enemy_min_y < 200.0:
            base_score += 4.0

        # If we are far ahead in this lane, offensive bonus
        if lane.pressure < -100.0:
            base_score += 2.0

    # 3) Troop stat awareness (normalised by cost)
    # Simple notions of "tanky", "high damage", and "fast response".
    cost = max(info.cost, 1.0)
    effective_hp = info.hp / cost
    effective_dmg = info.damage / cost
    move_speed = info.speed

    if lane is not None:
        # Defensive use: if under heavy pressure, value tanks and fast units.
        if lane.pressure > 200:
            base_score += min(effective_hp / 400.0, 4.0)
            if move_speed > 1.4:
                base_score += 1.5

        # Offensive push: if we're ahead in this lane, value damage output.
        if lane.pressure < -150:
            base_score += min(effective_dmg / 4.0, 4.0)

        # Empty / low-traffic lane: prefer fast, higher-damage pushes.
        if lane.enemy_hp < 50 and lane.my_hp < 50:
            if move_speed > 1.3:
                base_score += 1.0
            if effective_dmg > 5:
                base_score += 1.0

    # 4) Card role specific tweaks
    if info.role == "tank":
        # Tanks are best when under pressure or when base is low.
        if state.player_base_hp < state.ai_base_hp:
            base_score += 4.0
        if lane is not None and lane.pressure > 0:
            base_score += 3.0

    elif info.role == "ranged":
        # Ranged units are great behind some existing board presence.
        if lane is not None and lane.my_hp > 0:
            base_score += 3.0
        # Bonus when defending: ranged behind tower line
        if lane is not None and lane.enemy_min_y < 250.0:
            base_score += 1.5

    elif info.role == "air":
        # Air units: prefer lanes with many enemy troops.
        if lane is not None and lane.enemy_hp > 150.0:
            base_score += 3.5

    elif info.role in ("dps", "support"):
        # General-purpose DPS / support: bonus when pushing winning lanes.
        if lane is not None and lane.pressure < 0:
            base_score += 1.5

    # 5) Cheap cycle bonus – if coins are high, we're fine cycling cheap cards.
    if info.cost <= 2 and coins >= 5:
        base_score += 1.0

    # 6) Anti-spam penalty: discourage flooding the board with the same troop
    existing_count = my_troop_counts.get(info.troop_id, 0)
    if existing_count >= 2:
        # The more we already have of this troop, the less attractive it is.
        base_score -= 2.0 * (existing_count - 1)

    # Optional: extra anti-spam specifically for Peach (id == 2)
    if info.troop_id == 2 and existing_count >= 1:
        base_score -= 3.0

    return base_score

# game/ai/policy_baseline.py

from __future__ import annotations

from typing import Optional

from .state import GameState
from game.core.actions import PlayCardAction

# Placeholder costs; later you can sync with Gian's card data.
CARD_COSTS = {
    "bowser": 5,
    "mario": 3,
    "dry_bones": 2,
    "red_shell": 4,
}


def choose_baseline_action(state: GameState) -> Optional[PlayCardAction]:
    """
    Simple rule-based AI:

    - If base is low and we can afford Bowser, play Bowser in the weakest lane.
    - Otherwise, play Mario / Dry Bones / Red Shell if affordable.
    - If we can't do anything, return None (do nothing).
    """

    if state.player_elixir < 2:
        return None

    # If we don't know about lanes yet (placeholder state), assume lane 0.
    if not state.lanes:
        for cid in ["mario", "dry_bones", "red_shell", "bowser"]:
            cost = CARD_COSTS.get(cid, 99)
            if state.player_elixir >= cost:
                return PlayCardAction(card_id=cid, lane_index=0)
        return None

    # Compute per-lane "advantage"
    lane_scores = []
    for lane in state.lanes:
        player_hp = sum(t.hp for t in lane.troops if t.owner == "player")
        enemy_hp = sum(t.hp for t in lane.troops if t.owner == "ai")
        lane_scores.append(player_hp - enemy_hp)

    # Weakest lane = one where we are most behind
    target_lane = 0
    if lane_scores:
        target_lane = min(range(len(lane_scores)), key=lambda i: lane_scores[i])

    def can_play(card_id: str) -> bool:
        return state.player_elixir >= CARD_COSTS.get(card_id, 99)

    # Defend low base with Bowser
    if state.player_base_hp < 400 and can_play("bowser"):
        return PlayCardAction(card_id="bowser", lane_index=target_lane)

    # Otherwise, try other cards
    for cid in ["mario", "dry_bones", "red_shell"]:
        if can_play(cid):
            return PlayCardAction(card_id=cid, lane_index=target_lane)

    return None

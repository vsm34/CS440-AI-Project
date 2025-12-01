# game/ai/heuristic.py

from __future__ import annotations

from .state import GameState


def evaluate_state(state: GameState) -> float:
    """
    Turn a GameState into a single number.
    Positive = good for 'player', negative = good for 'ai'.

    Safe even if lanes are empty and everything is default.
    """

    # Terminal states get big scores
    if state.is_terminal:
        if state.winner == "player":
            return 1e9
        elif state.winner == "ai":
            return -1e9
        else:
            return 0.0

    score = 0.0

    # 1. Base HP difference
    base_diff = state.player_base_hp - state.ai_base_hp
    score += base_diff * 1.0

    # 2. Lane control and troop HP
    total_player_troops = 0.0
    total_ai_troops = 0.0
    lane_control_score = 0.0

    for lane in state.lanes:
        lane_player_hp = 0.0
        lane_ai_hp = 0.0

        player_front_y = None
        ai_front_y = None

        for t in lane.troops:
            if t.owner == "player":
                lane_player_hp += t.hp
                total_player_troops += t.hp
                if player_front_y is None or t.y < player_front_y:
                    player_front_y = t.y
            else:
                lane_ai_hp += t.hp
                total_ai_troops += t.hp
                if ai_front_y is None or t.y > ai_front_y:
                    ai_front_y = t.y

        lane_control_score += (lane_player_hp - lane_ai_hp) * 0.5

        if player_front_y is not None:
            lane_control_score += (1000.0 - player_front_y) * 0.002
        if ai_front_y is not None:
            lane_control_score -= (ai_front_y) * 0.002

    score += lane_control_score

    # 3. Global troop HP advantage
    troop_hp_diff = total_player_troops - total_ai_troops
    score += troop_hp_diff * 0.5

    # 4. Coin advantage
    coins_diff = state.player_coins - state.ai_coins
    score += coins_diff * 2.0

    # 5. Small bias for progressing time
    score += state.tick * 0.01

    return score

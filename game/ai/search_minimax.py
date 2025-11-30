# game/ai/search_minimax.py

from __future__ import annotations

from typing import Callable, List, Optional, Tuple

from .state import GameState
from .heuristic import evaluate_state
from .policy_baseline import choose_baseline_action, CARD_COSTS
from game.core.actions import PlayCardAction

EnemyPolicy = Callable[[GameState], Optional[PlayCardAction]]


def get_legal_actions(state: GameState) -> List[Optional[PlayCardAction]]:
    """
    Legal actions for the 'player' side:
    any affordable card in any lane, plus 'do nothing' (None).
    """
    actions: List[Optional[PlayCardAction]] = [None]  # do nothing

    if not state.lanes:
        lane_indices = [0]
    else:
        lane_indices = [lane.index for lane in state.lanes]

    for card_id, cost in CARD_COSTS.items():
        if state.player_elixir >= cost:
            for lane_idx in lane_indices:
                actions.append(PlayCardAction(card_id=card_id, lane_index=lane_idx))

    return actions


def simulate_one_step(
    state: GameState,
    player_action: Optional[PlayCardAction],
    enemy_policy: EnemyPolicy,
) -> GameState:
    """
    TODO: To be implemented later when you & Varun decide how to simulate
    a GameState one step forward for search.

    For now, this is unused; minimax won't be called by policy.py,
    so it won't crash your game.
    """
    raise NotImplementedError("simulate_one_step is not implemented yet.")


def minimax(
    state: GameState,
    depth: int,
    enemy_policy: EnemyPolicy,
    alpha: float = float("-inf"),
    beta: float = float("inf"),
) -> Tuple[float, Optional[PlayCardAction]]:
    if depth == 0 or state.is_terminal:
        return evaluate_state(state), None

    best_value = float("-inf")
    best_action: Optional[PlayCardAction] = None

    for action in get_legal_actions(state):
        next_state = simulate_one_step(state, action, enemy_policy)
        value, _ = minimax(next_state, depth - 1, enemy_policy, alpha, beta)

        if value > best_value:
            best_value = value
            best_action = action

        alpha = max(alpha, value)
        if beta <= alpha:
            break

    return best_value, best_action

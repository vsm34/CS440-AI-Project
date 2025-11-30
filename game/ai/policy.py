# game/ai/policy.py

from __future__ import annotations

from typing import Optional

from .state import GameState
from .policy_baseline import choose_baseline_action
from game.core.actions import PlayCardAction


def choose_ai_action(state: GameState) -> Optional[PlayCardAction]:
    """
    Main entry point for the AI.

    Varun's World will call:
        state = world.get_public_state()
        action = choose_ai_action(state)

    For now, this just uses the baseline policy (no minimax),
    so there are no NotImplemented errors.
    """

    if state.is_terminal:
        return None

    return choose_baseline_action(state)

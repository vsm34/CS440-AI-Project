# game/ai/policy.py

from typing import Optional
from game.ai.state import GameState
from game.core.actions import PlayCardAction

def choose_ai_action(state: GameState) -> Optional[PlayCardAction]:
    """
    Placeholder AI policy.
    Later: implement minimax / MCTS here.
    """
    # For now, just do nothing.
    return None

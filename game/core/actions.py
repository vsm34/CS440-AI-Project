# game/core/actions.py

from dataclasses import dataclass

@dataclass
class PlayCardAction:
    card_id: str
    lane_index: int  # later we can extend if we add more lanes

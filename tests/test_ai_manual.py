# tests/test_ai_manual.py

from game.ai.state import GameState, LaneView, TroopView
from game.ai.policy import choose_ai_action

def main():
    # Fake simple state
    lane = LaneView(
        index=0,
        troops=[
            TroopView(owner="player", lane_index=0, y=800, hp=40, max_hp=40, troop_id="dry_bones"),
            TroopView(owner="ai", lane_index=0, y=200, hp=80, max_hp=80, troop_id="mario"),
        ],
    )
    state = GameState(
        player_base_hp=800,
        ai_base_hp=800,
        player_elixir=5,
        ai_elixir=3,
        max_elixir=10,
        lanes=[lane],
        tick=10,
    )

    action = choose_ai_action(state)
    print("AI chose:", action)

if __name__ == "__main__":
    main()

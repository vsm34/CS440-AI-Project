## Module Ownership

- Varun: core game loop, `game/main.py`, `game/core/world.py`, integration.
- Bhupesh: troops + combat, `game/entities/`, `game/systems/combat_system.py`.
- Gian: cards + elixir + player input, `game/core/actions.py`, `game/ui/card_bar.py`, uses `load_cards()`.
- Sarin: AI, `game/ai/state.py`, `game/ai/policy.py`, `game/ai/minimax.py`, uses `GameState` from World.
- Amogh: UI/HUD + data + assets, `game/ui/hud.py`, `game/data/*.json`, `assets/`.

## Git Workflow

- Each person works on their own branch:
  - feature/varun-core
  - feature/gian-cards
  - feature/sarin-ai
  - feature/bhupesh-combat
  - feature/amogh-ui-data
- PRs go into `main` after tests / local run.

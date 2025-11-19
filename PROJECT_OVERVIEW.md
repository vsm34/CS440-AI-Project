🚀 Smash Royale – CS440 AI Project

A real-time, lane-based 2D card battler with a full AI opponent.
Built using Python + Pygame, designed for clean modularity and parallel team development.

🧩 1. Project Summary

Smash Royale is a simplified, Clash Royale-inspired game where:

The player deploys troops from the bottom of the arena.

The AI deploys troops from the top.

Troops move vertically along 3 lanes.

Both sides have exactly ONE central king tower.

The AI uses GameState abstraction → adversarial algorithms (minimax/MCTS later).

This project is heavily focused on:

proper software architecture

game simulation correctness

adversarial search

smooth rendering & input handling

📦 2. Project Directory Structure
CS440-AI-Project/
│
├── game/
│   ├── main.py                # Entry point for Pygame window & render loop
│   │
│   ├── core/
│   │   ├── world.py           # World class (lanes, towers, troops, simulation)
│   │   └── actions.py         # PlayCardAction dataclass
│   │
│   ├── entities/
│   │   ├── troop.py           # Troop (Drybones placeholder)
│   │   └── tower.py           # King tower entity
│   │
│   ├── ai/
│   │   ├── state.py           # GameState + TroopSnapshot
│   │   └── policy.py          # choose_ai_action (stub)
│   │
│   ├── data/
│   │   ├── loader.py          # Loads JSON card/troop data
│   │   ├── cards.json         # Card definitions (placeholder)
│   │   └── troops.json        # Troop definitions (placeholder)
│   │
│   └── ui/
│       └── (future UI modules)
│
├── assets/
│   ├── sprites/
│   └── sounds/
│
├── tests/
│
├── requirements.txt
└── PROJECT_OVERVIEW.md

🎮 3. Implemented Features (So Far)
✔ Game Startup & Loop

python -m game.main starts the game successfully.

Pygame window, FPS clock, and main loop are established.

✔ World Class (simulation core)

Owns troops, lanes, towers.

Has step(dt) for updating world state.

✔ Lane System

3 vertical lanes: left (0), center (1), right (2).

Lanes are rendered based on lane rects from get_render_info().

✔ King Towers

Exactly one player king tower (bottom).

Exactly one AI king tower (top).

Positioned in the center lane.

No side towers (unlike real Clash Royale).

✔ Troops

Placeholder Drybones troop:

Spawns in center lane

Walks upward (toward AI tower)

✔ Arena Boundaries

Simple top and bottom boundary markers.

✔ JSON Data System

cards.json + troops.json + loader.py for flexible data-driven design.

✔ GameState + AI Stub

AI receives a clean abstract GameState.

choose_ai_action(state) exists (returns None for now).

🧠 4. Architecture Overview
4.1 Rendering Pipeline
main.py
   ↓
World.step(dt)
   ↓
World.get_render_info()
   ↓
Draw lanes, towers, troops

4.2 Simulation Pipeline

World.step(dt) orchestrates:

troop movement

(future) combat system

(future) elixir regeneration

(future) AI polling

4.3 AI Pipeline
World.get_public_state()
    → GameState
AI.choose_ai_action(GameState)
    → PlayCardAction
World.apply_ai_action(action)

4.4 Card → Action Pipeline
UI → PlayCardAction → World.apply_player_action()

🧑‍🤝‍🧑 5. Team Responsibilities

Each team member works on their own branch:

feature/varun-core
feature/gian-cards
feature/sarin-ai
feature/bhupesh-combat
feature/amogh-ui

🔹 Varun — Engine Lead & Integrator

Files:

game/main.py

game/core/world.py

Responsibilities:

Overall architecture & integration

Maintain World, action routing, render info

Wire in card logic, combat system, AI system

Merge everyone's modules

Keep main branch stable

🔹 Gian — Cards, Elixir, Input → Action

Files:

game/ui/card_bar.py

game/core/actions.py

game/data/cards.json

Responsibilities:

Card bar (clickable UI)

Elixir system + regen

Cooldowns

Convert clicks → PlayCardAction

🔹 Sarin — AI Logic (CS440)

Files:

game/ai/state.py

game/ai/policy.py

future: minimax.py / mcts.py

Responsibilities:

Define legal actions

Construct next states

Implement minimax/MCTS

Heuristic evaluation

🔹 Bhupesh — Troop & Combat Systems

Files:

game/entities/

game/systems/combat_system.py (new)

Responsibilities:

Troop classes (Mario, Bowser, Yoshi, etc.)

Movement logic

Attack range, DPS, targeting

Combat resolution

🔹 Amogh — UI/HUD + Data + Assets

Files:

game/ui/

game/data/*.json

assets/

Responsibilities:

HUD (elixir bar, timers, AI notifications)

Sprites, icons, effects

Load image assets

Card UI textures

Packaging into .exe (PyInstaller)

📌 6. Features Still Needed
Gameplay

Full troop combat system

Tower HP + destruction

Game-over conditions

Spell cards

Multiple unit types

UI

Card bar

Elixir meter

Victory/defeat overlay

Start screen

AI

Implement minimax/MCTS

State transition model

Heuristic scoring

Time-limited search

🧪 7. How to Run the Game
Activate virtual environment:
venv\Scripts\activate

Run the game:
python -m game.main

🧭 8. Using Cursor for Development

Cursor understands your code based on:

This file (PROJECT_OVERVIEW.md)

Your directory structure

Code near your cursor

Your written prompts

Whenever you need Cursor to modify code, start your prompt with:

Read PROJECT_OVERVIEW.md before making changes. Follow its architecture exactly.
Game must run with python -m game.main.

This ensures consistency even after switching Cursor accounts.

🔀 9. Branching Workflow

Each teammate:

git checkout -b feature/<name-topic>


Examples:

feature/gian-cards

feature/sarin-ai

etc.

When done:

git add .

git commit -m "message"

git push origin feature/<branch>

Open Pull Request → into main

Varun merges after testing

🏁 10. Summary

This project is now fully structured for:

parallel team development

clean AI integration

clear separation of concerns

stable incremental updates

Smash Royale has the foundation: lanes, towers, troops, simulation loop.
Each teammate can now build their sub-system independently and safely.

✅ End of PROJECT_OVERVIEW.md
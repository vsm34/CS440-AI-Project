# 🧠 Smash Royale — Internal Architecture Document

This document explains the internal architecture of the game so that developers & AI tools (Cursor) can safely modify the project.

# 🔷 1. High-Level System Diagram
- +----------------+
- |   main.py      |
- |  (Pygame loop) |
- +--------+-------+
         |
         v
- +----------------------+
- |       World          |
- |  lanes, towers,      |
- |  troops, simulation  |
- +----+----+----+-------+
     |    |    |
     |    |    |
     |    |    +----------+
     |    +---------------+-----+
     v                          |
- +-----------+             +-----------+
- | card UI   |             |    AI     |
- | (Gian)    |             | (Sarin)   |
- +-----------+             +-----------+
     |                          |
     v                          v
- +--------------+        +----------------+
- | PlayCardAction| ----> | apply_ai_action|
- +--------------+        +----------------+


# 🔶 2. Core Concepts
World

The central orchestrator of gameplay.

Stores:

lanes

towers

troops

timers

Methods:

step(dt)

apply_player_action(action)

apply_ai_action(action)

get_render_info()

get_public_state()

World must not contain UI or AI logic.

GameState

A clean, abstract representation of the world for AI.

Contains:

troop snapshots

positions

hp

elixir

lane info

owner info

AI never touches Pygame, only GameState.

PlayCardAction

Unified action for both player and AI:

card_id: str
lane_index: int


This is the bridge between UI, AI, and the game engine.

# 🔷 3. Rendering Architecture
main.py:

Runs Pygame loop

Calls world.step(dt)

Calls world.get_render_info()

Draws:

lanes

towers

troops

UI overlays (HUD, card bar) will be added later.

# 🔶 4. Simulation Architecture
World.step(dt):

Updates troop positions

Later:

calls combat system

calls AI decision timer

calls elixir regen system

Simulation is deterministic and frame-based.

# 🔷 5. Lane System

Three vertical lanes:

Lane 0 → left

Lane 1 → center

Lane 2 → right

A Lane dataclass stores:

index

x

width

# 🔶 6. Towers

Every side has exactly one king tower:

Player king tower at bottom center

AI king tower at top center

Towers currently have:

x, y

width & height

owner

draw() method

No HP or combat logic yet.

# 🔷 7. Entity System
Troop

Base movement + draw.
Will be extended into:

Mario

Bowser

Drybones
etc.

Combat system (future)

Lives in game/systems/combat_system.py.

World calls it during step().

# 🔶 8. Card System

UI translates user input → PlayCardAction.

Elixir + cooldown rules are inside Gian’s module.

World simply:

validates

spawns troop

# 🔷 9. AI System

AI logic lives entirely in:

game/ai/


AI never reads World directly.
It reads GameState only.

# 🔶 10. Data-Driven Design

Troops and cards are loaded from:

game/data/troops.json
game/data/cards.json


No hardcoded stats in code.
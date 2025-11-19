# 🚀 Contributing Guidelines — Smash Royale (CS440 AI Project)

Welcome to the team!
This document explains how all development must be done to keep the project stable, modular, and compatible with our architecture.

# 📦 1. Running the Project
Activate virtual environment (Windows):
venv\Scripts\activate

Run the game:
python -m game.main


The game must always run successfully after any PR is merged.

# 🌿 2. Branching Model

Each teammate must work on their own feature branch:

feature/<name-topic>


Examples:

feature/varun-core

feature/gian-cards

feature/sarin-ai

feature/bhupesh-combat

feature/amogh-ui

NEVER push directly to main.

# 🔀 3. Workflow

Create a new branch:

git checkout -b feature/<name-topic>


Make changes.

Stage + commit:

git add .
git commit -m "Clear, descriptive message"


Push:

git push origin feature/<name-topic>


Create a PR → into main.

Assign Varun as reviewer (integration lead).

# 🧩 4. Module Boundaries (Very Important)

To prevent merge conflicts and spaghetti code, each teammate must stay within their assigned folders.

## Varun — Engine + Integration

game/main.py

game/core/world.py

game/core/actions.py (shared)

No UI code

No AI code

No combat code

## Bhupesh — Troops + Combat

game/entities/

game/systems/

Should not modify World, AI, or UI code

## Gian — Cards + Elixir + Player Input

game/ui/card_bar.py

game/core/actions.py (add fields if needed)

game/data/cards.json

Should not modify AI logic or combat logic

## Sarin — AI Logic

game/ai/state.py

game/ai/policy.py

game/ai/minimax.py

Should not modify Pygame code

## Amogh — UI/HUD + Assets + Data

game/ui/

assets/

game/data/loader.py

Should not modify AI or combat logic

# 🧱 5. Rules for Editing Shared Files

Shared modules include:

actions.py

GameState in state.py

world.py

main.py

RULES:

✔ Discuss changes in the group chat first
✔ Update PROJECT_OVERVIEW.md if interfaces change
✔ Make PRs small and well-documented
✔ Never break backward compatibility

# 🧪 6. Testing Before PR

Every PR must:

✔ Run without crashes
✔ Maintain the ability to spawn a troop
✔ Maintain lane + tower rendering
✔ Preserve python -m game.main functionality
✔ Keep AI stub functional
✔ Keep World consistent

# ⛔ 7. DO NOT EDIT These Without Group Approval

PROJECT_OVERVIEW.md

CONTRIBUTING.md

Core architecture files (world.py, state.py, actions.py)

JSON format shape (cards.json, troops.json)

These determine how ALL modules integrate.

# ❤️ 8. Team Communication

Use group chat to:

Declare what file you’re editing

Ask for interface clarifications

Warn before any architecture changes

Avoid overlapping on the same file

✨ Thank you!

Following these rules keeps our project stable, testable, and modular — and ensures we finish smoothly.
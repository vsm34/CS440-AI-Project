import json
from pathlib import Path

DATA_DIR = Path(__file__).parent

def load_cards():
    with open(DATA_DIR / "cards.json", "r") as f:
        return json.load(f)

def load_troops():
    with open(DATA_DIR / "troops.json", "r") as f:
        return json.load(f)

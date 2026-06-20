"""
main.py
=======
Launches the playable graphical RPG Battle Arena.

Controls:
    Mouse  - click "Attack" / "Special" buttons during your turn
    Keys   - press 1 for Attack, 2 for Special, Enter to start from the title screen

Run with:  python main.py
"""

from ui.game import Game

if __name__ == "__main__":
    Game().run()

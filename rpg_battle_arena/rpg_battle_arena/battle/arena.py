"""
arena.py
--------
Pure game-logic controller (no pygame here). The UI layer (ui/game.py)
drives this turn by turn in response to button clicks / frame updates.

OOP CONCEPT: POLYMORPHISM in practice
    `boss_action()` and the hero-attack calls made by the UI both just
    call `.attack(target)` / `.special_ability(target)` on a Character
    reference. Arena never checks "is this a Warrior or a Mage" -- each
    object already knows how to behave correctly on its own.
"""

import random


class Arena:
    """Tracks turn order and round count for a Heroes-vs-Boss battle."""

    def __init__(self, heroes: list, boss):
        self.heroes = heroes
        self.boss = boss
        self.round_num = 0

    def alive_heroes(self) -> list:
        return [h for h in self.heroes if h.is_alive]

    def is_battle_over(self) -> bool:
        return not self.boss.is_alive or not self.alive_heroes()

    def winner(self):
        if not self.boss.is_alive:
            return "Heroes"
        if not self.alive_heroes():
            return "Boss"
        return None

    def start_round(self):
        self.round_num += 1

    def boss_action(self) -> str:
        """The boss's automatic AI turn. Returns a log message."""
        alive = self.alive_heroes()
        if not alive:
            return ""
        if self.round_num % 3 == 0:
            # Polymorphism: same call signature, AOE-specific behavior
            return self.boss.special_ability(alive)
        target = random.choice(alive)
        return self.boss.attack(target)

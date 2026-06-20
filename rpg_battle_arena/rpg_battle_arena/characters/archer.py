"""
archer.py
INHERITANCE + POLYMORPHISM: crit-chance basic attack, multi-hit special.
"""

import random
import pygame
from characters.base_character import Character

TUNIC = (70, 150, 90)
TUNIC_DARK = (45, 105, 65)
SKIN = (235, 195, 160)
WOOD = (120, 85, 50)


class Archer(Character):
    """Fast, crit-focused ranged attacker."""

    def __init__(self, name: str):
        super().__init__(name, max_hp=100, attack_power=18, defense=6, color=TUNIC)
        self.__crit_chance = 0.25  # private internal tuning value

    def attack(self, target: Character) -> str:
        is_crit = random.random() < self.__crit_chance
        base = self._attack_power * (2 if is_crit else 1)
        damage = base + random.randint(-2, 3)
        dealt = target.take_damage(damage)
        tag = " CRITICAL HIT!" if is_crit else ""
        return f"{self.name} shoots {target.name} for {dealt} damage.{tag}"

    def special_ability(self, target: Character = None) -> str:
        if not target:
            return f"{self.name} has no target for Triple Shot."
        total = 0
        for _ in range(3):
            total += target.take_damage(self._attack_power)
        return f"{self.name} fires a TRIPLE SHOT at {target.name} for {total} total damage!"

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        # legs
        pygame.draw.rect(surface, TUNIC_DARK, (x - 18, y - 50, 14, 50), border_radius=4)
        pygame.draw.rect(surface, TUNIC_DARK, (x + 4, y - 50, 14, 50), border_radius=4)
        # tunic
        pygame.draw.rect(surface, TUNIC, (x - 24, y - 108, 48, 60), border_radius=10)
        # head
        pygame.draw.circle(surface, SKIN, (x, y - 124), 16)
        pygame.draw.rect(surface, TUNIC_DARK, (x - 16, y - 142, 32, 10), border_radius=4)  # hood band
        # bow (arc)
        pygame.draw.arc(surface, WOOD, (x + 18, y - 130, 36, 70), -1.3, 1.3, 4)
        pygame.draw.line(surface, (230, 230, 220), (x + 21, y - 100), (x + 21, y - 60), 1)
        # quiver
        pygame.draw.line(surface, WOOD, (x - 20, y - 100), (x - 8, y - 130), 5)

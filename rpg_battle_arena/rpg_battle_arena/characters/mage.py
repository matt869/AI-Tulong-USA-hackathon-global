"""
mage.py
INHERITANCE + POLYMORPHISM + ENCAPSULATION (__mana is private).
"""

import random
import pygame
from characters.base_character import Character

ROBE = (130, 70, 200)
ROBE_DARK = (90, 45, 150)
SKIN = (235, 200, 170)
ORB = (140, 220, 255)


class Mage(Character):
    """Fragile, high-damage spellcaster that depends on Mana."""

    def __init__(self, name: str):
        super().__init__(name, max_hp=90, attack_power=25, defense=4, color=ROBE)
        self.__mana = 100
        self.__max_mana = 100

    @property
    def mana(self) -> int:
        return self.__mana

    def attack(self, target: Character) -> str:
        damage = self._attack_power + random.randint(-2, 2)
        dealt = target.take_damage(damage)
        return f"{self.name} casts Arcane Bolt on {target.name} for {dealt} damage."

    def special_ability(self, target: Character = None) -> str:
        cost = 40
        if target and self.__mana >= cost:
            self.__mana -= cost
            dealt = target.take_damage(self._attack_power * 3)
            return f"{self.name} casts FIREBALL on {target.name} for {dealt} damage! (Mana {self.__mana}/{self.__max_mana})"
        return f"{self.name} doesn't have enough Mana ({self.__mana}/{cost}) for Fireball."

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        # robe (trapezoid)
        pygame.draw.polygon(
            surface, ROBE,
            [(x - 14, y - 115), (x + 14, y - 115), (x + 32, y), (x - 32, y)],
        )
        pygame.draw.polygon(
            surface, ROBE_DARK,
            [(x - 14, y - 115), (x + 14, y - 115), (x + 20, y - 40), (x - 20, y - 40)],
            3,
        )
        # head + hat
        pygame.draw.circle(surface, SKIN, (x, y - 128), 16)
        pygame.draw.polygon(surface, ROBE_DARK, [(x - 22, y - 138), (x + 22, y - 138), (x, y - 178)])
        pygame.draw.circle(surface, (255, 230, 120), (x, y - 178), 4)  # hat tip glow
        # staff
        pygame.draw.line(surface, (120, 90, 60), (x + 34, y - 10), (x + 44, y - 140), 5)
        pygame.draw.circle(surface, ORB, (x + 44, y - 146), 9)

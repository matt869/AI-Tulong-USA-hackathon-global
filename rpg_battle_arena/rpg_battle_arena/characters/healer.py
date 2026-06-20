"""
healer.py
INHERITANCE + POLYMORPHISM: a support class whose special_ability() heals
instead of damaging -- proving polymorphism can mean different BEHAVIOR,
not just different numbers.
"""

import pygame
from characters.base_character import Character

ROBE = (245, 240, 225)
ROBE_TRIM = (220, 180, 80)
SKIN = (235, 200, 170)
HALO = (255, 225, 130)


class Healer(Character):
    """Support class that restores HP to allies."""

    def __init__(self, name: str):
        super().__init__(name, max_hp=110, attack_power=8, defense=7, color=ROBE)
        self.__mana = 80

    @property
    def mana(self) -> int:
        return self.__mana

    def attack(self, target: Character) -> str:
        dealt = target.take_damage(self._attack_power + 1)
        return f"{self.name} smites {target.name} for {dealt} damage (weak attack)."

    def special_ability(self, target: Character = None) -> str:
        cost = 30
        heal_target = target if target else self
        if self.__mana >= cost:
            self.__mana -= cost
            healed = heal_target.heal(35)
            return f"{self.name} casts Heal on {heal_target.name}, restoring {healed} HP! (Mana {self.__mana})"
        return f"{self.name} doesn't have enough Mana to heal."

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        # halo
        pygame.draw.ellipse(surface, HALO, (x - 16, y - 168, 32, 10), 3)
        # robe (trapezoid)
        pygame.draw.polygon(
            surface, ROBE,
            [(x - 14, y - 112), (x + 14, y - 112), (x + 30, y), (x - 30, y)],
        )
        pygame.draw.polygon(
            surface, ROBE_TRIM,
            [(x - 14, y - 112), (x + 14, y - 112), (x + 20, y - 40), (x - 20, y - 40)],
            3,
        )
        # head
        pygame.draw.circle(surface, SKIN, (x, y - 126), 16)
        # staff with cross
        pygame.draw.line(surface, ROBE_TRIM, (x - 36, y - 10), (x - 36, y - 140), 5)
        pygame.draw.line(surface, ROBE_TRIM, (x - 44, y - 150), (x - 28, y - 150), 5)
        pygame.draw.line(surface, ROBE_TRIM, (x - 36, y - 158), (x - 36, y - 142), 5)

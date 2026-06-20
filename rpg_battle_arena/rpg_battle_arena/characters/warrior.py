"""
warrior.py
INHERITANCE: extends Character, reuses HP/render/template-method system.
POLYMORPHISM: attack(), special_ability(), and draw() all behave uniquely.
"""

import random
import pygame
from characters.base_character import Character

STEEL = (180, 190, 205)
STEEL_DARK = (110, 120, 140)
SKIN = (235, 195, 160)
BLADE = (220, 225, 230)


class Warrior(Character):
    """Melee fighter that builds Rage and unleashes a heavy finisher."""

    def __init__(self, name: str):
        super().__init__(name, max_hp=150, attack_power=20, defense=10, color=STEEL)
        self.__rage = 0  # private resource, unique to Warrior

    @property
    def rage(self) -> int:
        return self.__rage

    def attack(self, target: Character) -> str:
        damage = self._attack_power + random.randint(-3, 5)
        dealt = target.take_damage(damage)
        self.__rage = min(100, self.__rage + 10)
        return f"{self.name} slashes {target.name} for {dealt} damage! (Rage {self.__rage}/100)"

    def special_ability(self, target: Character = None) -> str:
        if target and self.__rage >= 50:
            self.__rage = 0
            dealt = target.take_damage(self._attack_power * 2)
            return f"{self.name} unleashes BERSERKER STRIKE on {target.name} for {dealt} damage!"
        return f"{self.name} needs more Rage ({self.__rage}/50) to use Berserker Strike."

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        # legs
        pygame.draw.rect(surface, STEEL_DARK, (x - 22, y - 50, 16, 50), border_radius=4)
        pygame.draw.rect(surface, STEEL_DARK, (x + 6, y - 50, 16, 50), border_radius=4)
        # torso
        pygame.draw.rect(surface, STEEL, (x - 28, y - 110, 56, 65), border_radius=8)
        # head
        pygame.draw.circle(surface, SKIN, (x, y - 128), 18)
        pygame.draw.arc(surface, (90, 60, 40), (x - 18, y - 142, 36, 24), 3.4, 6.0, 4)  # hair
        # shield arm
        pygame.draw.circle(surface, STEEL_DARK, (x - 38, y - 80), 16)
        pygame.draw.circle(surface, (90, 100, 120), (x - 38, y - 80), 16, 3)
        # sword
        pygame.draw.line(surface, BLADE, (x + 30, y - 60), (x + 58, y - 130), 7)
        pygame.draw.line(surface, (120, 80, 40), (x + 26, y - 50), (x + 36, y - 64), 6)

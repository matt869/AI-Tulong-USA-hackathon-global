"""
dragon_boss.py
INHERITANCE + POLYMORPHISM: a boss enemy whose special_ability() hits an
entire list of targets (AOE) instead of one, and whose draw() produces a
much larger, more menacing shape than the heroes.
"""

import random
import pygame
from characters.base_character import Character

HIDE = (150, 35, 35)
HIDE_DARK = (100, 20, 20)
WING = (90, 15, 15)
EYE = (255, 220, 60)


class DragonBoss(Character):
    """A powerful enemy boss with an area-of-effect breath attack."""

    def __init__(self, name: str = "Ancient Dragon"):
        super().__init__(name, max_hp=320, attack_power=30, defense=12, color=HIDE)
        self.BAR_OFFSET = 245

    def attack(self, target: Character) -> str:
        damage = self._attack_power + random.randint(0, 10)
        dealt = target.take_damage(damage)
        return f"{self.name} claws {target.name} for {dealt} damage!"

    def special_ability(self, target=None):
        """target is a LIST of characters (area-of-effect breath attack)."""
        if not target:
            return f"{self.name} has nothing to breathe fire on."
        total = 0
        hit_names = []
        for member in target:
            if member.is_alive:
                dealt = member.take_damage(self._attack_power - 5)
                total += dealt
                hit_names.append(f"{member.name}(-{dealt})")
        return f"{self.name} breathes DRAGON FIRE! " + ", ".join(hit_names)

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        # back legs (clawed feet)
        pygame.draw.rect(surface, HIDE_DARK, (x - 38, y - 36, 18, 36), border_radius=4)
        pygame.draw.rect(surface, HIDE_DARK, (x + 14, y - 36, 18, 36), border_radius=4)

        # tail, curving out behind the body
        pygame.draw.lines(surface, HIDE_DARK, False,
                           [(x + 35, y - 60), (x + 90, y - 50), (x + 120, y - 80)], 9)

        # wings (spread wide above the body for a dramatic silhouette)
        pygame.draw.polygon(surface, WING, [(x - 25, y - 120), (x - 145, y - 195), (x - 35, y - 90),
                                             (x - 80, y - 110)])
        pygame.draw.polygon(surface, WING, [(x + 25, y - 120), (x + 145, y - 195), (x + 35, y - 90),
                                             (x + 80, y - 110)])

        # body
        pygame.draw.ellipse(surface, HIDE, (x - 48, y - 145, 96, 105))
        pygame.draw.ellipse(surface, HIDE_DARK, (x - 48, y - 145, 96, 105), 3)

        # neck + head, offset forward
        pygame.draw.polygon(surface, HIDE, [(x - 18, y - 150), (x + 12, y - 150), (x + 4, y - 185)])
        pygame.draw.ellipse(surface, HIDE, (x - 30, y - 215, 56, 50))
        # snout
        pygame.draw.polygon(surface, HIDE, [(x - 30, y - 196), (x - 58, y - 188), (x - 28, y - 178)])
        pygame.draw.line(surface, HIDE_DARK, (x - 56, y - 188), (x - 30, y - 192), 2)
        # horns
        pygame.draw.line(surface, HIDE_DARK, (x - 6, y - 212), (x - 14, y - 238), 5)
        pygame.draw.line(surface, HIDE_DARK, (x + 12, y - 212), (x + 20, y - 238), 5)
        # eye
        pygame.draw.circle(surface, EYE, (x - 8, y - 198), 5)
        pygame.draw.circle(surface, (40, 0, 0), (x - 8, y - 198), 2)

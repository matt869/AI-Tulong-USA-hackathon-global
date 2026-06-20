"""
base_character.py
------------------
The abstract blueprint every fighter in the game must follow.

OOP CONCEPT: ABSTRACTION
    `Character` inherits from ABC and marks attack(), special_ability(),
    and draw() as @abstractmethod. You can NEVER create a plain
    Character() object -- every subclass is FORCED to define its own
    combat behavior AND its own on-screen appearance.

OOP CONCEPT: ENCAPSULATION
    `__current_hp` / `__max_hp` are name-mangled private attributes.
    Outside code cannot do `character.__current_hp = 9999` to cheat --
    HP can only change through validated methods (take_damage / heal),
    and can only be read through a read-only @property.

OOP CONCEPT: INHERITANCE + TEMPLATE METHOD
    `render()` is NOT abstract -- every subclass inherits the exact same
    render() for free. It calls self.draw() (which IS abstract, so it
    runs the correct subclass version) and then draws the shared HP bar
    / name tag chrome that looks identical for every character. This is
    "inherit what's common, override what's unique."
"""

from abc import ABC, abstractmethod
import pygame


class Character(ABC):
    """Abstract base class for every fighter in the arena."""

    FONT_NAME = None
    FONT_SMALL = None

    def __init__(self, name: str, max_hp: int, attack_power: int, defense: int, color):
        self._name = name
        self.__max_hp = max_hp          # private -> encapsulated
        self.__current_hp = max_hp      # private -> encapsulated
        self._attack_power = attack_power
        self._defense = defense
        self._level = 1
        self._is_alive = True
        self._color = color             # used by subclasses when drawing

    # ------------------------------------------------------------------
    # ENCAPSULATION: controlled, read-only access to private state
    # ------------------------------------------------------------------
    @property
    def name(self) -> str:
        return self._name

    @property
    def current_hp(self) -> int:
        return self.__current_hp

    @property
    def max_hp(self) -> int:
        return self.__max_hp

    @property
    def is_alive(self) -> bool:
        return self._is_alive

    @property
    def hp_ratio(self) -> float:
        return self.__current_hp / self.__max_hp

    def take_damage(self, amount: int) -> int:
        """The ONLY way HP can decrease. Validates and applies defense."""
        if amount < 0:
            raise ValueError("Damage cannot be negative.")
        actual_damage = max(1, amount - self._defense) if amount > 0 else 0
        self.__current_hp = max(0, self.__current_hp - actual_damage)
        if self.__current_hp == 0:
            self._is_alive = False
        return actual_damage

    def heal(self, amount: int) -> int:
        """The ONLY way HP can increase. Cannot exceed max_hp or revive the dead."""
        if not self._is_alive:
            return 0
        healed = min(amount, self.__max_hp - self.__current_hp)
        self.__current_hp += healed
        return healed

    # ------------------------------------------------------------------
    # ABSTRACTION: every subclass MUST implement these
    # ------------------------------------------------------------------
    @abstractmethod
    def attack(self, target: "Character") -> str:
        """Perform a basic attack. Returns a log message. Subclass-specific."""
        raise NotImplementedError

    @abstractmethod
    def special_ability(self, target=None) -> str:
        """Perform the class's unique special move. Subclass-specific."""
        raise NotImplementedError

    @abstractmethod
    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Draw this character's unique shape, anchored at bottom-center (x, y)."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # INHERITANCE / TEMPLATE METHOD: shared by every subclass, untouched
    # ------------------------------------------------------------------
    def render(self, surface: pygame.Surface, x: int, y: int,
               x_offset: int = 0, y_offset: int = 0, display_ratio: float = None) -> None:
        """Draws the character (polymorphic) + HP bar/name (identical for all).

        x_offset / y_offset let the UI layer animate position (e.g. a lunge
        toward an enemy, or a subtle idle bob) WITHOUT this class knowing
        anything about animation -- it just draws wherever it's told.

        display_ratio lets the UI layer animate the HP bar tweening smoothly
        toward the real value instead of snapping instantly; pass None to
        use the real current value.
        """
        dx, dy = x + x_offset, y + y_offset
        if not self._is_alive:
            self._draw_defeated(surface, dx, dy)
        else:
            self.draw(surface, dx, dy)
        self._draw_chrome(surface, dx, dy, display_ratio)

    BAR_OFFSET = 150  # vertical distance above the anchor point; subclasses may override

    def _draw_chrome(self, surface: pygame.Surface, x: int, y: int, display_ratio: float = None) -> None:
        bar_w, bar_h = 96, 12
        bar_x, bar_y = x - bar_w // 2, y - self.BAR_OFFSET

        pygame.draw.rect(surface, (30, 30, 35), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        ratio = max(0.0, display_ratio if display_ratio is not None else self.hp_ratio)
        fill_w = int(bar_w * ratio)
        if ratio > 0.5:
            color = (90, 220, 110)
        elif ratio > 0.2:
            color = (240, 200, 60)
        else:
            color = (220, 70, 70)
        if fill_w > 0:
            pygame.draw.rect(surface, color, (bar_x, bar_y, fill_w, bar_h), border_radius=4)
        pygame.draw.rect(surface, (235, 235, 235), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=4)

        if Character.FONT_SMALL:
            label = Character.FONT_SMALL.render(
                f"{self._name}  {self.current_hp}/{self.max_hp}", True, (255, 255, 255)
            )
            surface.blit(label, label.get_rect(center=(x, bar_y - 12)))

    def _draw_defeated(self, surface, x, y):
        pygame.draw.circle(surface, (60, 60, 65), (x, y - 30), 36)
        if Character.FONT_SMALL:
            label = Character.FONT_SMALL.render("DEFEATED", True, (255, 120, 120))
            surface.blit(label, label.get_rect(center=(x, y - 30)))

    def __str__(self) -> str:
        status = "ALIVE" if self._is_alive else "DEFEATED"
        return f"{self._name} (Lv.{self._level}) [{status}] {self.current_hp}/{self.max_hp} HP"

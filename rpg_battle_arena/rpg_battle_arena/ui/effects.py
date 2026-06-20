"""
effects.py
----------
A small, self-contained animation system. Every visual effect (a floating
damage number, a flying fireball, an impact ring, a timed callback) is a
subclass of `Effect` with the same two methods: update(dt) and draw(surface).

OOP CONCEPT: POLYMORPHISM (again, but in the animation layer this time)
    `Game` keeps one flat list of Effect objects and calls `.update(dt)`
    and `.draw(surface)` on each one every frame WITHOUT caring which
    concrete type it is. A DamageNumber animates totally differently from
    a Projectile, yet the game loop treats them identically -- exactly
    the same lesson as Warrior/Mage/Archer, applied to animation instead
    of combat.
"""

from abc import ABC, abstractmethod
import random
import pygame


class Effect(ABC):
    """Base class for every transient visual effect."""

    def __init__(self):
        self.finished = False

    @abstractmethod
    def update(self, dt: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        raise NotImplementedError


class DamageNumber(Effect):
    """Floating combat text ('-14', '+35', '...') that rises and fades."""

    def __init__(self, x, y, text, color, font, rise=46, duration=0.7):
        super().__init__()
        self.x = x + random.randint(-18, 18)
        self.y0 = y + random.randint(-10, 10)
        self.text = text
        self.color = color
        self.font = font
        self.rise = rise
        self.duration = duration
        self.t = 0.0

    def update(self, dt: float) -> None:
        self.t += dt
        if self.t >= self.duration:
            self.finished = True

    def draw(self, surface: pygame.Surface) -> None:
        progress = min(1.0, self.t / self.duration)
        y = self.y0 - self.rise * progress
        alpha = max(0, 255 - int(255 * progress))
        label = self.font.render(self.text, True, self.color)
        label.set_alpha(alpha)
        surface.blit(label, label.get_rect(center=(self.x, y)))


class FlashRing(Effect):
    """An expanding, fading ring used for hit impacts and heal pulses."""

    def __init__(self, x, y, color, max_radius=44, duration=0.4):
        super().__init__()
        self.x, self.y = x, y
        self.color = color
        self.max_radius = max_radius
        self.duration = duration
        self.t = 0.0

    def update(self, dt: float) -> None:
        self.t += dt
        if self.t >= self.duration:
            self.finished = True

    def draw(self, surface: pygame.Surface) -> None:
        progress = min(1.0, self.t / self.duration)
        radius = int(self.max_radius * progress) + 4
        alpha = max(0, 220 - int(220 * progress))
        ring = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(ring, (*self.color, alpha), (radius + 2, radius + 2), radius, 4)
        surface.blit(ring, (self.x - radius - 2, self.y - radius - 2))


class Projectile(Effect):
    """A small bolt that flies from (x0,y0) to (x1,y1), then fires a callback."""

    def __init__(self, x0, y0, x1, y1, color, duration=0.3, radius=7, on_arrive=None):
        super().__init__()
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.color = color
        self.duration = duration
        self.radius = radius
        self.on_arrive = on_arrive
        self.t = 0.0

    def update(self, dt: float) -> None:
        self.t += dt
        if self.t >= self.duration:
            if self.on_arrive:
                self.on_arrive()
            self.finished = True

    def draw(self, surface: pygame.Surface) -> None:
        progress = min(1.0, self.t / self.duration)
        x = self.x0 + (self.x1 - self.x0) * progress
        y = self.y0 + (self.y1 - self.y0) * progress
        pygame.draw.circle(surface, self.color, (int(x), int(y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(x), int(y)), max(2, self.radius - 3))


class DelayedCall(Effect):
    """Fires a callback once after `delay` seconds. Used to time impacts."""

    def __init__(self, delay, callback):
        super().__init__()
        self.delay = delay
        self.callback = callback
        self.t = 0.0

    def update(self, dt: float) -> None:
        self.t += dt
        if self.t >= self.delay:
            self.callback()
            self.finished = True

    def draw(self, surface: pygame.Surface) -> None:
        pass  # invisible -- this effect only carries timing, nothing to draw

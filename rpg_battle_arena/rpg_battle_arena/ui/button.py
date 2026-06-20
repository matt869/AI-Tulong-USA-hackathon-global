"""
button.py
---------
A small, reusable UI control. This is plain OOP encapsulation applied to
UI: a Button hides its own rect/state and exposes a clean draw()/is_clicked()
interface -- the rest of the game never pokes at its internals directly.
"""

import pygame
from ui import colors


class Button:
    def __init__(self, rect, text, font, base_color=colors.BTN_BASE,
                 hover_color=colors.BTN_HOVER, text_color=colors.TEXT):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.enabled = True

    def draw(self, surface: pygame.Surface):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.enabled and self.rect.collidepoint(mouse_pos)
        if not self.enabled:
            color = colors.BTN_DISABLED
        else:
            color = self.hover_color if hovered else self.base_color

        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, colors.PANEL_BORDER, self.rect, 2, border_radius=10)

        text_color = self.text_color if self.enabled else colors.TEXT_DIM
        label = self.font.render(self.text, True, text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def is_clicked(self, event) -> bool:
        return (
            self.enabled
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

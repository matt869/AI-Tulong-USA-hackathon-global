"""
game.py
=======
The actual playable game: a window, mouse-driven buttons, animated HP
bars, lunge attacks, flying projectiles, screen shake, and a title /
battle / game-over flow.

This file is intentionally UI-only -- it never decides combat math itself.
It just calls methods on Character/Arena objects and displays whatever
they return. That separation is good OOP design: combat RULES live in
characters/ and battle/, PRESENTATION (including all animation) lives
here in ui/.
"""

import sys
import math
import random
import pygame

from ui import colors
from ui.button import Button
from ui.effects import DamageNumber, FlashRing, Projectile, DelayedCall
from characters import Warrior, Mage, Archer, Healer, DragonBoss, Character
from battle import Arena

WIDTH, HEIGHT = 1040, 680

STATE_TITLE = "title"
STATE_PLAYER_TURN = "player_turn"
STATE_PAUSE = "pause"
STATE_BOSS_TURN = "boss_turn"
STATE_GAME_OVER = "game_over"

PAUSE_MS = 950
HERO_XS = [150, 320, 490, 660]
BOSS_POS = (880, 470)


class Game:
    """Owns the pygame window, the turn-based state machine, and all animation."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("RPG Battle Arena - OOP Final Project")
        self.clock = pygame.time.Clock()
        self.frame_surface = pygame.Surface((WIDTH, HEIGHT))

        self.font_title = pygame.font.SysFont("arial", 48, bold=True)
        self.font_big = pygame.font.SysFont("arial", 28, bold=True)
        self.font_ui = pygame.font.SysFont("arial", 20)
        self.font_small = pygame.font.SysFont("arial", 15)
        self.font_log = pygame.font.SysFont("consolas", 17)

        # Shared fonts used by every Character instance for its HP bar/name
        Character.FONT_NAME = self.font_small
        Character.FONT_SMALL = self.font_small

        self.title_btn = Button((WIDTH // 2 - 110, 430, 220, 56), "Start Battle", self.font_big)
        self.attack_btn = Button((WIDTH // 2 - 230, HEIGHT - 70, 200, 50), "Attack (1)", self.font_ui)
        self.special_btn = Button((WIDTH // 2 + 30, HEIGHT - 70, 200, 50),
                                   "Special (2)", self.font_ui,
                                   base_color=colors.BTN_SPECIAL, hover_color=colors.BTN_SPECIAL_HOVER)
        self.restart_btn = Button((WIDTH // 2 - 110, 430, 220, 56), "Play Again", self.font_big)

        self.log = []          # rolling combat log shown in the bottom panel
        self.state = STATE_TITLE
        self.message_timer = 0
        self.active_hero = None
        self.turn_queue = []
        self.turn_index = 0

        # ---- animation state ----
        self.effects = []                 # flat list of active Effect objects (polymorphic)
        self.display_hp = {}              # character -> smoothed HP value for bar tweening
        self.lunge_actor = None
        self.lunge_t = 0.0
        self.lunge_duration = 0.32
        self.lunge_dx = 0
        self.shake_t = 0.0
        self.shake_duration = 0.0
        self.shake_magnitude = 0

        self._new_battle()

    # ------------------------------------------------------------------
    def _new_battle(self):
        self.heroes = [Warrior("Aldric"), Mage("Lyra"), Archer("Robin"), Healer("Selene")]
        self.boss = DragonBoss("Ancient Dragon")
        self.arena = Arena(self.heroes, self.boss)
        self.log = ["A wild Ancient Dragon blocks the path!"]
        self.state = STATE_TITLE
        self.effects = []
        self.display_hp = {c: float(c.current_hp) for c in self.heroes + [self.boss]}

    def _start_round(self):
        self.arena.start_round()
        self.turn_queue = list(self.arena.alive_heroes())
        self.turn_index = 0
        self._advance_hero_turn()

    def _advance_hero_turn(self):
        """Move to the next alive hero in the queue, or hand off to the boss."""
        while self.turn_index < len(self.turn_queue):
            hero = self.turn_queue[self.turn_index]
            if hero.is_alive:
                self.active_hero = hero
                self.state = STATE_PLAYER_TURN
                return
            self.turn_index += 1
        # queue exhausted -> boss's turn
        self.active_hero = None
        self.state = STATE_BOSS_TURN
        self.message_timer = pygame.time.get_ticks()

    def _push_log(self, message: str):
        if message:
            self.log.append(message)
            self.log = self.log[-6:]

    def _resolve_and_pause(self, message: str):
        self._push_log(message)
        self.message_timer = pygame.time.get_ticks()
        self.state = STATE_PAUSE

    # ------------------------------------------------------------------
    # Positions + small animation helpers
    # ------------------------------------------------------------------
    def _position_of(self, character):
        if character is self.boss:
            return BOSS_POS
        if character in self.heroes:
            return (HERO_XS[self.heroes.index(character)], 470)
        return (WIDTH // 2, 470)

    def _idle_bob(self, seed: int) -> float:
        return math.sin(pygame.time.get_ticks() / 350 + seed) * 4

    def _trigger_shake(self, magnitude=8, duration=0.25):
        self.shake_magnitude = magnitude
        self.shake_duration = duration
        self.shake_t = duration

    def _shake_offset(self):
        if self.shake_t <= 0 or self.shake_duration <= 0:
            return (0, 0)
        mag = self.shake_magnitude * (self.shake_t / self.shake_duration)
        return (random.randint(-int(mag), int(mag)), random.randint(-int(mag), int(mag)))

    def _trigger_lunge(self, actor, target):
        ax, _ = self._position_of(actor)
        tx, _ = self._position_of(target)
        self.lunge_actor = actor
        self.lunge_t = 0.0
        self.lunge_dx = 26 if tx > ax else -26

    def _lunge_offset(self, character) -> int:
        if character is not self.lunge_actor:
            return 0
        progress = min(1.0, self.lunge_t / self.lunge_duration)
        return int(self.lunge_dx * math.sin(progress * math.pi))

    def _projectile_color(self, attacker):
        if isinstance(attacker, Mage):
            return (170, 120, 255)
        if isinstance(attacker, Archer):
            return (210, 180, 110)
        if isinstance(attacker, Healer):
            return (255, 225, 130)
        return (255, 255, 255)

    # ------------------------------------------------------------------
    # Spawning combat animation: lunges, projectiles, impact numbers
    # ------------------------------------------------------------------
    def _animate_single_action(self, attacker, target, diff, failed):
        ax, ay = self._position_of(attacker)
        tx, ty = self._position_of(target)

        if failed:
            self.effects.append(DamageNumber(ax, ay - 160, "...", colors.TEXT_DIM,
                                              self.font_ui, rise=20, duration=0.6))
            return

        is_heal = diff > 0
        color = colors.GREEN if is_heal else colors.RED
        text = f"{diff:+d}"

        def land(tx=tx, ty=ty, color=color, text=text, is_heal=is_heal, diff=diff):
            self.effects.append(FlashRing(tx, ty - 90, color, max_radius=52 if is_heal else 44))
            self.effects.append(DamageNumber(tx, ty - 130, text, color, self.font_big))
            if not is_heal and abs(diff) >= 40:
                self._trigger_shake(magnitude=6, duration=0.2)

        if isinstance(attacker, (Warrior, DragonBoss)) and not is_heal:
            self._trigger_lunge(attacker, target)
            self.effects.append(DelayedCall(0.16, land))
        else:
            proj_color = self._projectile_color(attacker)
            start_y = ay - (190 if attacker is self.boss else 150)
            self.effects.append(Projectile(ax, start_y, tx, ty - 90, proj_color,
                                            duration=0.3, on_arrive=land))

    def _animate_aoe(self, attacker, diffs: dict):
        self._trigger_shake(magnitude=10, duration=0.35)
        for i, (hero, diff) in enumerate(diffs.items()):
            tx, ty = self._position_of(hero)
            color = colors.RED if diff < 0 else colors.GREEN
            text = f"{diff:+d}"
            delay = 0.12 + i * 0.05

            def land(tx=tx, ty=ty, color=color, text=text):
                self.effects.append(FlashRing(tx, ty - 90, color, max_radius=44))
                self.effects.append(DamageNumber(tx, ty - 130, text, color, self.font_big))

            self.effects.append(DelayedCall(delay, land))

    # ------------------------------------------------------------------
    def _pick_wounded_ally(self):
        wounded = [h for h in self.heroes if h.is_alive and h.current_hp < h.max_hp]
        if not wounded:
            return None
        return min(wounded, key=lambda h: h.hp_ratio)

    def _do_hero_action(self, special: bool):
        hero = self.active_hero
        if special and isinstance(hero, Healer):
            target = self._pick_wounded_ally() or hero
        else:
            target = self.boss
        before = target.current_hp
        # POLYMORPHISM: identical call shape for every hero subclass
        message = hero.special_ability(target) if special else hero.attack(target)
        after = target.current_hp
        diff = after - before
        failed = diff == 0 and ("doesn't have enough" in message or "needs more" in message)
        self._animate_single_action(hero, target, diff, failed)
        self.turn_index += 1
        self._resolve_and_pause(message)

    def _do_boss_action(self):
        before = {h: h.current_hp for h in self.heroes if h.is_alive}
        message = self.arena.boss_action()
        affected = {h: h.current_hp - hp for h, hp in before.items() if h.current_hp != hp}
        if len(affected) > 1:
            self._animate_aoe(self.boss, affected)
        elif len(affected) == 1:
            hero, diff = next(iter(affected.items()))
            self._animate_single_action(self.boss, hero, diff, failed=False)
        self._resolve_and_pause(message)

    def _after_pause(self):
        if self.arena.is_battle_over():
            self.state = STATE_GAME_OVER
            return
        if self.active_hero is not None:
            self._advance_hero_turn()
        else:
            self._start_round()

    # ------------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if self.state == STATE_TITLE:
            if self.title_btn.is_clicked(event):
                self._start_round()
            return

        if self.state == STATE_GAME_OVER:
            if self.restart_btn.is_clicked(event):
                self._new_battle()
                self._start_round()
            return

        if self.state == STATE_PLAYER_TURN:
            keydown = event.type == pygame.KEYDOWN
            if self.attack_btn.is_clicked(event) or (keydown and event.key == pygame.K_1):
                self._do_hero_action(special=False)
            elif self.special_btn.is_clicked(event) or (keydown and event.key == pygame.K_2):
                self._do_hero_action(special=True)

    def update(self, dt: float):
        if self.state == STATE_PAUSE and pygame.time.get_ticks() - self.message_timer > PAUSE_MS:
            self._after_pause()
        elif self.state == STATE_BOSS_TURN and pygame.time.get_ticks() - self.message_timer > 600:
            self._do_boss_action()

        # smoothly ease every HP bar toward its real value
        for character in self.heroes + [self.boss]:
            current = self.display_hp.get(character, float(character.current_hp))
            self.display_hp[character] = current + (character.current_hp - current) * min(1.0, dt * 8)

        if self.lunge_actor is not None:
            self.lunge_t += dt
            if self.lunge_t >= self.lunge_duration:
                self.lunge_actor = None
                self.lunge_t = 0.0

        if self.shake_t > 0:
            self.shake_t = max(0.0, self.shake_t - dt)

        for effect in self.effects:
            effect.update(dt)
        self.effects = [e for e in self.effects if not e.finished]

    # ------------------------------------------------------------------
    def draw(self):
        target = self.frame_surface
        self._draw_background(target)

        if self.state == STATE_TITLE:
            self._draw_title(target)
        else:
            self._draw_battlefield(target)
            self._draw_effects(target)
            self._draw_log_panel(target)
            if self.state == STATE_PLAYER_TURN:
                self._draw_action_buttons(target)
            if self.state == STATE_GAME_OVER:
                self._draw_game_over(target)

        self.screen.fill((8, 6, 16))
        self.screen.blit(target, self._shake_offset())
        pygame.display.flip()

    def _draw_background(self, surface):
        for i in range(HEIGHT):
            t = i / HEIGHT
            r = int(colors.BG_TOP[0] + (colors.BG_BOTTOM[0] - colors.BG_TOP[0]) * t)
            g = int(colors.BG_TOP[1] + (colors.BG_BOTTOM[1] - colors.BG_TOP[1]) * t)
            b = int(colors.BG_TOP[2] + (colors.BG_BOTTOM[2] - colors.BG_TOP[2]) * t)
            pygame.draw.line(surface, (r, g, b), (0, i), (WIDTH, i))

    def _draw_title(self, surface):
        title = self.font_title.render("RPG BATTLE ARENA", True, colors.GOLD)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 220)))
        sub = self.font_ui.render("A Python OOP Demonstration: Inheritance | Polymorphism | Abstraction | Encapsulation",
                                   True, colors.TEXT_DIM)
        surface.blit(sub, sub.get_rect(center=(WIDTH // 2, 270)))

        hint = self.font_small.render("Click below or press ENTER to begin", True, colors.TEXT_DIM)
        surface.blit(hint, hint.get_rect(center=(WIDTH // 2, 320)))

        preview = [Warrior("Warrior"), Mage("Mage"), Archer("Archer"), Healer("Healer")]
        xs = [WIDTH // 2 - 240, WIDTH // 2 - 80, WIDTH // 2 + 80, WIDTH // 2 + 240]
        for i, (char, px) in enumerate(zip(preview, xs)):
            char.draw(surface, px, int(400 + self._idle_bob(i)))

        self.title_btn.draw(surface)

    def _draw_battlefield(self, surface):
        floor_rect = pygame.Rect(0, 470, WIDTH, 90)
        pygame.draw.rect(surface, (35, 30, 50), floor_rect)
        pygame.draw.line(surface, colors.PANEL_BORDER, (0, 470), (WIDTH, 470), 2)

        for idx, (hero, hx) in enumerate(zip(self.heroes, HERO_XS)):
            if hero is self.active_hero and self.state == STATE_PLAYER_TURN:
                pygame.draw.polygon(surface, colors.GOLD, [(hx, 290), (hx - 12, 270), (hx + 12, 270)])
            bob = int(self._idle_bob(idx)) if hero.is_alive else 0
            ratio = self.display_hp.get(hero, hero.current_hp) / hero.max_hp
            hero.render(surface, hx, 470, x_offset=self._lunge_offset(hero), y_offset=bob,
                        display_ratio=ratio)

        boss_bob = int(self._idle_bob(7)) if self.boss.is_alive else 0
        boss_ratio = self.display_hp.get(self.boss, self.boss.current_hp) / self.boss.max_hp
        self.boss.render(surface, BOSS_POS[0], BOSS_POS[1], x_offset=self._lunge_offset(self.boss),
                          y_offset=boss_bob, display_ratio=boss_ratio)

        round_label = self.font_ui.render(f"Round {self.arena.round_num}", True, colors.TEXT_DIM)
        surface.blit(round_label, (20, 16))

    def _draw_effects(self, surface):
        for effect in self.effects:
            effect.draw(surface)

    def _draw_log_panel(self, surface):
        panel = pygame.Rect(20, 480, WIDTH - 40, 78)
        pygame.draw.rect(surface, colors.PANEL, panel, border_radius=10)
        pygame.draw.rect(surface, colors.PANEL_BORDER, panel, 2, border_radius=10)
        y = panel.y + 8
        for line in self.log[-4:]:
            label = self.font_log.render(line, True, colors.TEXT)
            surface.blit(label, (panel.x + 14, y))
            y += 17

    def _draw_action_buttons(self, surface):
        name_label = self.font_ui.render(f"{self.active_hero.name}'s turn -- choose an action:",
                                          True, colors.GOLD)
        surface.blit(name_label, name_label.get_rect(center=(WIDTH // 2, 580)))
        self.special_btn.text = "Heal (2)" if isinstance(self.active_hero, Healer) else "Special (2)"
        self.attack_btn.draw(surface)
        self.special_btn.draw(surface)

    def _draw_game_over(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 8, 20, 200))
        surface.blit(overlay, (0, 0))

        winner = self.arena.winner()
        text = "VICTORY!" if winner == "Heroes" else "DEFEATED..."
        color = colors.GREEN if winner == "Heroes" else colors.RED
        label = self.font_title.render(text, True, color)
        surface.blit(label, label.get_rect(center=(WIDTH // 2, 300)))

        sub = self.font_ui.render(f"Battle lasted {self.arena.round_num} rounds.", True, colors.TEXT_DIM)
        surface.blit(sub, sub.get_rect(center=(WIDTH // 2, 350)))

        self.restart_btn.draw(surface)

    # ------------------------------------------------------------------
    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.state == STATE_TITLE and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self._start_round()
                self.handle_event(event)

            self.update(dt)
            self.draw()

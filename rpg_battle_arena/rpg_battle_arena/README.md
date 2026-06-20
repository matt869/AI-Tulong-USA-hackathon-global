# RPG Battle Arena — Python OOP Final Project

A real, playable, windowed turn-based RPG battle game built with **Python +
Pygame**, made to demonstrate the four pillars of Object-Oriented
Programming: **Inheritance, Polymorphism, Abstraction, and Encapsulation.**

> **Source / Inspiration:** Built from scratch for this assignment,
> following the classic turn-based RPG character-class pattern (Warrior /
> Mage / Archer / Healer / Boss) commonly used to teach OOP.
> *(If your instructor specifically requires a link to a pre-existing
> public repository, replace this line with that repo's URL.)*

## Screenshots

The game has a title screen, a live battle screen with clickable action
buttons and animated HP bars, and a victory/defeat screen.

## How to Run

```bash
git clone <this-repo-url>
cd rpg_battle_arena
pip install -r requirements.txt
python main.py
```

**Controls:**
- Mouse — click "Attack" or "Special" during your turn
- Keyboard — `1` = Attack, `2` = Special, `Enter` = start from title screen

For the **video recording**, also run `python oop_demo.py` — it's a
console script that prints clear, narrated proof of all four OOP pillars
one section at a time, perfect to pause on and explain.

## Project Structure

```
rpg_battle_arena/
├── main.py                     # Launches the graphical game
├── oop_demo.py                  # Console script that narrates all 4 pillars
├── characters/
│   ├── base_character.py       # Abstract base class (Abstraction + Encapsulation)
│   ├── warrior.py               # Inheritance + Polymorphism
│   ├── mage.py
│   ├── archer.py
│   ├── healer.py
│   └── dragon_boss.py
├── battle/
│   └── arena.py                 # Turn-order / win-condition logic (no UI code)
└── ui/
    ├── button.py                 # Reusable clickable Button component
    ├── colors.py
    ├── effects.py                 # Polymorphic animation system (damage numbers, projectiles, screen shake)
    └── game.py                   # Pygame window, state machine, rendering
```

## Animations

- **Lunge attacks** — melee classes (Warrior, Dragon) physically dash toward their target and back
- **Flying projectiles** — ranged classes (Mage, Archer, Healer) fire a bolt that travels to its target
- **Floating damage/heal numbers** that rise and fade (`-14`, `+35`)
- **Impact rings** that flash and expand on every hit
- **Screen shake** on big hits and the dragon's AOE breath attack
- **Smoothly-draining HP bars** that ease toward the real value instead of snapping instantly
- **Idle bobbing** so characters feel alive even when nothing's happening

All of this lives in `ui/effects.py` as a small polymorphic `Effect` class
hierarchy (`DamageNumber`, `Projectile`, `FlashRing`, `DelayedCall`) — the
game loop keeps one flat list and calls `.update(dt)` / `.draw(surface)`
on each one without caring which concrete type it is. Same polymorphism
lesson as the combat classes, applied to animation.

## Where Each OOP Pillar Lives

### 1. Abstraction — `characters/base_character.py`
`Character(ABC)` declares `attack()`, `special_ability()`, and `draw()` as
`@abstractmethod`. `Character(...)` can **never** be instantiated directly
— every subclass is **forced** to implement its own combat behavior *and*
its own on-screen appearance.

### 2. Encapsulation — `characters/base_character.py`
`__current_hp` / `__max_hp` are private (name-mangled) attributes. They
can't be changed from outside the class — only through validated methods
(`take_damage()`, `heal()`) that enforce game rules (HP can't go below 0
or above max). Reading is only allowed through a read-only `@property`.

### 3. Inheritance — `characters/warrior.py`, `mage.py`, `archer.py`, `healer.py`, `dragon_boss.py`
Every class extends `Character` (`class Warrior(Character):`) and calls
`super().__init__(...)` to reuse the shared HP/level system. They also
inherit `render()` for free — a **Template Method** that draws the
subclass-specific shape *and* the identical HP bar/name tag chrome.

### 4. Polymorphism — `battle/arena.py` and `ui/game.py`
The UI calls `hero.attack(target)` or `hero.special_ability(target)` on
whatever `Character` object is active **without checking its type** —
Python automatically runs the correct version (sword slash, fireball,
arrow shot, heal, dragon claw/breath). The same is true visually: every
class's `draw()` produces a completely different sprite from the same
`render()` call — that's why the Warrior, Mage, Archer, Healer, and
Dragon all *look* different even though the game code treats them
identically.

## Author

Final project for OOP / Python course requirements — demonstrates
Inheritance, Polymorphism, Abstraction, and Encapsulation with a real,
working, playable game.

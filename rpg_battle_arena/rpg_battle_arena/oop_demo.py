"""
oop_demo.py
===========
Run this for your VIDEO RECORDING: python oop_demo.py

It uses the exact same Character classes as the real game (main.py) but
prints clear, narrated proof of all four OOP pillars to the console,
one section at a time. Pause on each section while you explain it.
"""

from characters import Warrior, Mage, Archer, Healer, DragonBoss, Character


def section(title: str):
    print("\n" + "#" * 64)
    print(f"#  {title}")
    print("#" * 64)


def demo_inheritance():
    section("1. INHERITANCE")
    print("Warrior, Mage, Archer, Healer, and DragonBoss all inherit from")
    print("the Character base class via `class Warrior(Character):`, so")
    print("they get HP tracking, take_damage(), heal(), and render() for")
    print("free instead of rewriting them in every class.\n")

    hero = Warrior("Aldric")
    print(f"isinstance(hero, Warrior)   -> {isinstance(hero, Warrior)}")
    print(f"isinstance(hero, Character) -> {isinstance(hero, Character)}")
    print(f"str(hero) [inherited]       -> {hero}")


def demo_abstraction():
    section("2. ABSTRACTION")
    print("Character declares attack(), special_ability(), and draw() as")
    print("@abstractmethod. You can NEVER create a plain Character():\n")
    try:
        Character("Generic", 100, 10, 5, (0, 0, 0))
    except TypeError as e:
        print(f"TypeError raised, as expected -> {e}")
    print("\nEvery subclass MUST implement all three methods or Python")
    print("will refuse to let it be instantiated either.")


def demo_encapsulation():
    section("3. ENCAPSULATION")
    mage = Mage("Lyra")
    print(f"mage.current_hp (public, read-only property) -> {mage.current_hp}")

    print("\nTrying to directly overwrite the private attribute:")
    mage.__current_hp = 99999  # creates an unrelated new attribute, doesn't touch real HP
    print(f"mage.current_hp is STILL -> {mage.current_hp}  (protected! unaffected)")

    print("\nThe ONLY correct way to change HP is through validated methods:")
    dealt = mage.take_damage(20)
    print(f"mage.take_damage(20) -> dealt {dealt} actual dmg, current_hp={mage.current_hp}")
    healed = mage.heal(5)
    print(f"mage.heal(5)         -> healed {healed} HP, current_hp={mage.current_hp}")


def demo_polymorphism():
    section("4. POLYMORPHISM")
    print("Calling the exact SAME method, .attack(), on different object")
    print("types -- each one responds in its own unique way:\n")

    dummy = Warrior("Training Dummy")
    fighters = [Warrior("Aldric"), Mage("Lyra"), Archer("Robin"),
                Healer("Selene"), DragonBoss("Ancient Dragon")]

    for fighter in fighters:
        print(" -", fighter.attack(dummy))

    print("\nPolymorphism also drives the GAME'S VISUALS: every subclass")
    print("implements draw() differently, so the exact same render() call")
    print("produces a sword-and-shield knight, a robed mage, a bow-wielding")
    print("archer, a haloed healer, or a giant dragon -- run `python main.py`")
    print("to see this rendered live in the actual game window.")


if __name__ == "__main__":
    demo_inheritance()
    demo_abstraction()
    demo_encapsulation()
    demo_polymorphism()
    print("\nAll four pillars demonstrated. Run `python main.py` for the full game.\n")
